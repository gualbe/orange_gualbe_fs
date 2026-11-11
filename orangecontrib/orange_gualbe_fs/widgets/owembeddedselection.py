# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Gualberto Asencio Cortés
# Part of orange_gualbe_fs. See the LICENSE and NOTICE files for details.

from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import (
    LogisticRegression, SGDClassifier,
    LinearRegression, Ridge, Lasso, ElasticNet, SGDRegressor,
)
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import (
    RandomForestClassifier, ExtraTreesClassifier,
    GradientBoostingClassifier, AdaBoostClassifier,
    RandomForestRegressor, ExtraTreesRegressor,
    GradientBoostingRegressor, AdaBoostRegressor,
)

from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from Orange.widgets.utils.widgetpreview import WidgetPreview

from orangecontrib.orange_gualbe_fs.widgets.utils import problem_type, reduce_domain, rebuild_combo

# (etiqueta visible, fabrica del estimador de sklearn) por tipo de problema.
# Todos exponen coef_ (modelos lineales) o feature_importances_ (arboles y
# ensambles), que es lo que SelectFromModel necesita tras el ajuste.
ESTIMATORS = {
    "classification": [
        ("Regresión Logística", lambda: LogisticRegression(max_iter=1000)),
        ("SVM Lineal", lambda: LinearSVC(max_iter=5000)),
        ("Descenso de Gradiente Estocástico (SGD)",
         lambda: SGDClassifier(random_state=0)),
        ("Árbol de Decisión", lambda: DecisionTreeClassifier(random_state=0)),
        ("Bosque Aleatorio",
         lambda: RandomForestClassifier(n_estimators=100, random_state=0)),
        ("Extra Trees",
         lambda: ExtraTreesClassifier(n_estimators=100, random_state=0)),
        ("Potenciación del Gradiente (Gradient Boosting)",
         lambda: GradientBoostingClassifier(random_state=0)),
        ("AdaBoost", lambda: AdaBoostClassifier(random_state=0)),
    ],
    "regression": [
        ("Regresión Lineal", lambda: LinearRegression()),
        ("Ridge", lambda: Ridge()),
        ("Lasso", lambda: Lasso()),
        ("ElasticNet", lambda: ElasticNet()),
        ("Descenso de Gradiente Estocástico (SGD)",
         lambda: SGDRegressor(random_state=0)),
        ("Árbol de Decisión", lambda: DecisionTreeRegressor(random_state=0)),
        ("Bosque Aleatorio",
         lambda: RandomForestRegressor(n_estimators=100, random_state=0)),
        ("Extra Trees",
         lambda: ExtraTreesRegressor(n_estimators=100, random_state=0)),
        ("Potenciación del Gradiente (Gradient Boosting)",
         lambda: GradientBoostingRegressor(random_state=0)),
        ("AdaBoost", lambda: AdaBoostRegressor(random_state=0)),
    ],
}

MEAN, MEDIAN, CUSTOM = range(3)
THRESHOLD_LABELS = ["Media (mean)", "Mediana (median)", "Valor personalizado"]
THRESHOLD_VALUES = ["mean", "median", None]  # None -> se usa threshold_value


class OWEmbeddedSelection(OWWidget):
    name = "Selección Embebida"
    description = ("Selecciona atributos según la importancia o los "
                    "coeficientes que les asigna un modelo predictivo ya "
                    "entrenado (SelectFromModel).")
    icon = "icons/owembeddedselection.svg"
    priority = 120
    keywords = "feature selection, seleccion de atributos, embebida, selectfrommodel"
    want_main_area = False
    resizing_enabled = False

    class Inputs:
        data = Input("Data", Table)

    class Outputs:
        data = Output("Data", Table)

    estimator_index = Setting(0)
    threshold_mode = Setting(MEAN)
    threshold_value = Setting(0.0)
    limit_max_features = Setting(False)
    max_features = Setting(10)
    auto_apply = Setting(True)

    class Error(OWWidget.Error):
        no_class = Msg("Los datos no tienen una variable objetivo (target).")
        selection_failed = Msg("No se pudo aplicar la selección: {}")

    class Warning(OWWidget.Warning):
        no_features_selected = Msg(
            "Ningún atributo cumple el criterio de selección elegido.")

    def __init__(self):
        super().__init__()
        self.data = None

        box = gui.vBox(self.controlArea, "Datos de entrada")
        self.problem_type_label = gui.widgetLabel(box, "Sin datos de entrada.")

        estimator_box = gui.vBox(self.controlArea, "Modelo base (estimador)")
        self.estimator_combo = gui.comboBox(
            estimator_box, self, "estimator_index", items=[],
            callback=self._on_param_changed)

        threshold_box = gui.vBox(self.controlArea, "Umbral de selección")
        gui.comboBox(
            threshold_box, self, "threshold_mode", items=THRESHOLD_LABELS,
            label="Modo:", callback=self._on_threshold_mode_changed)
        self.threshold_value_box = gui.doubleSpin(
            threshold_box, self, "threshold_value", minv=0.0, maxv=1000.0,
            step=0.01, decimals=4, label="Valor del umbral:",
            controlWidth=100, callback=self._on_param_changed)

        limit_box = gui.vBox(self.controlArea, "Límite de atributos (opcional)")
        _, self.max_features_spin = gui.spin(
            limit_box, self, "max_features", minv=1, maxv=10000, step=1,
            label="Número máximo de atributos:", controlWidth=80,
            checked="limit_max_features", checkCallback=self._on_param_changed,
            callback=self._on_param_changed)

        info_box = gui.vBox(self.controlArea, "Resultado")
        self.info_label = gui.widgetLabel(info_box, "Ningún dato procesado todavía.")

        gui.auto_apply(self.buttonsArea, self)

        self._update_threshold_visibility()
        self._update_domain_dependent_controls()

    def _on_param_changed(self):
        self.commit.deferred()

    def _on_threshold_mode_changed(self):
        self._update_threshold_visibility()
        self.commit.deferred()

    def _update_threshold_visibility(self):
        self.threshold_value_box.box.setVisible(self.threshold_mode == CUSTOM)

    def _update_domain_dependent_controls(self):
        self.Error.no_class.clear()
        ptype = problem_type(self.data)

        if self.data is None:
            self.problem_type_label.setText("Sin datos de entrada.")
        elif ptype is None:
            self.problem_type_label.setText(
                "Datos sin variable objetivo compatible.")
            self.Error.no_class()
        elif ptype == "classification":
            n_classes = len(self.data.domain.class_var.values)
            self.problem_type_label.setText(
                f"Target categórico detectado: clasificación "
                f"({n_classes} clases).")
        else:
            self.problem_type_label.setText(
                "Target numérico detectado: regresión.")

        rebuild_combo(self.estimator_combo, self, "estimator_index",
                      ESTIMATORS.get(ptype, []))

        if self.data is not None:
            n_attrs = max(1, len(self.data.domain.attributes))
            self.controls.max_features.setMaximum(n_attrs)
            if self.max_features > n_attrs:
                self.max_features = n_attrs

    @Inputs.data
    def set_data(self, data):
        self.data = data
        self._update_domain_dependent_controls()
        self.commit.now()

    def _threshold_arg(self):
        value = THRESHOLD_VALUES[self.threshold_mode]
        return self.threshold_value if value is None else value

    @gui.deferred
    def commit(self):
        self.Error.selection_failed.clear()
        self.Warning.no_features_selected.clear()

        ptype = problem_type(self.data)
        if self.data is None or ptype is None:
            self.info_label.setText("Ningún dato procesado todavía.")
            self.Outputs.data.send(None)
            return

        _, make_estimator = ESTIMATORS[ptype][self.estimator_index]
        estimator = make_estimator()

        n_attrs = len(self.data.domain.attributes)
        max_features = (min(self.max_features, n_attrs)
                        if self.limit_max_features else None)

        selector = SelectFromModel(
            estimator,
            threshold=self._threshold_arg(),
            max_features=max_features)

        try:
            selector.fit(self.data.X, self.data.Y)
        except ValueError as ex:
            self.Error.selection_failed(str(ex))
            self.info_label.setText("Ningún dato procesado todavía.")
            self.Outputs.data.send(None)
            return

        mask = selector.get_support()
        reduced, selected = reduce_domain(self.data, mask)

        if not selected:
            self.Warning.no_features_selected()

        self.info_label.setText(
            f"{len(selected)} de {n_attrs} atributos seleccionados.")
        self.Outputs.data.send(reduced)

    def send_report(self):
        ptype = problem_type(self.data)
        estimator_label = (ESTIMATORS[ptype][self.estimator_index][0]
                            if ptype else "—")
        self.report_items("Configuración", [
            ("Estimador", estimator_label),
            ("Umbral", THRESHOLD_LABELS[self.threshold_mode]),
        ])


if __name__ == "__main__":  # pragma: no cover
    WidgetPreview(OWEmbeddedSelection).run(Table("iris"))
