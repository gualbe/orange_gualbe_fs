# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Gualberto Asencio Cortés
# Part of orange_gualbe_fs. See the LICENSE and NOTICE files for details.

from AnyQt.QtWidgets import QApplication

from sklearn.feature_selection import RFE, RFECV, SequentialFeatureSelector
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from Orange.widgets.utils.widgetpreview import WidgetPreview

from orangecontrib.orange_gualbe_fs.widgets.utils import problem_type, reduce_domain, rebuild_combo

RFE_METHOD, RFECV_METHOD, SFS_METHOD = range(3)
METHOD_LABELS = [
    "Eliminación Recursiva (RFE)",
    "Eliminación Recursiva con Validación Cruzada (RFECV)",
    "Selección Secuencial (SFS)",
]

# (etiqueta visible, fabrica del estimador de sklearn) por tipo de problema
ESTIMATORS = {
    "classification": [
        ("Regresión Logística", lambda: LogisticRegression(max_iter=1000)),
        ("Bosque Aleatorio",
         lambda: RandomForestClassifier(n_estimators=100, random_state=0)),
    ],
    "regression": [
        ("Regresión Lineal", lambda: LinearRegression()),
        ("Bosque Aleatorio",
         lambda: RandomForestRegressor(n_estimators=100, random_state=0)),
    ],
}

# (etiqueta visible, valor de "scoring" de sklearn) por tipo de problema
SCORING = {
    "classification": [
        ("(automática)", None),
        ("Exactitud (accuracy)", "accuracy"),
        ("F1 (macro)", "f1_macro"),
        ("Exactitud balanceada", "balanced_accuracy"),
    ],
    "regression": [
        ("(automática)", None),
        ("R²", "r2"),
        ("Error cuadrático medio (neg.)", "neg_mean_squared_error"),
        ("Error absoluto medio (neg.)", "neg_mean_absolute_error"),
    ],
}

DIRECTIONS = [
    ("Hacia adelante (forward)", "forward"),
    ("Hacia atrás (backward)", "backward"),
]


class OWWrapperSelection(OWWidget):
    name = "Selección Wrapper"
    description = ("Selecciona atributos mediante métodos wrapper (RFE, "
                    "RFECV, Selección Secuencial) evaluando un modelo "
                    "predictivo.")
    icon = "icons/owwrapperselection.svg"
    priority = 110
    keywords = "feature selection, seleccion de atributos, wrapper, rfe, rfecv, sfs"
    want_main_area = False
    resizing_enabled = False

    class Inputs:
        data = Input("Data", Table)

    class Outputs:
        data = Output("Data", Table)

    method_index = Setting(RFE_METHOD)
    estimator_index = Setting(0)
    n_features = Setting(5)
    step = Setting(1)
    min_features = Setting(1)
    cv = Setting(5)
    direction_index = Setting(0)
    scoring_index = Setting(0)
    auto_apply = Setting(False)

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

        method_box = gui.vBox(self.controlArea, "Método wrapper")
        gui.comboBox(
            method_box, self, "method_index",
            items=METHOD_LABELS,
            callback=self._on_method_changed)

        estimator_box = gui.vBox(self.controlArea, "Modelo base (estimador)")
        self.estimator_combo = gui.comboBox(
            estimator_box, self, "estimator_index", items=[],
            callback=self._on_param_changed)

        params_box = gui.vBox(self.controlArea, "Parámetros")
        self.n_features_box = gui.spin(
            params_box, self, "n_features", minv=1, maxv=10000, step=1,
            label="Número de atributos a seleccionar:", controlWidth=80,
            callback=self._on_param_changed)
        self.step_box = gui.spin(
            params_box, self, "step", minv=1, maxv=1000, step=1,
            label="Paso (atributos eliminados por iteración):",
            controlWidth=80, callback=self._on_param_changed)
        self.min_features_box = gui.spin(
            params_box, self, "min_features", minv=1, maxv=10000, step=1,
            label="Mínimo de atributos a conservar:", controlWidth=80,
            callback=self._on_param_changed)
        self.cv_box = gui.spin(
            params_box, self, "cv", minv=2, maxv=20, step=1,
            label="Pliegues de validación cruzada (cv):", controlWidth=80,
            callback=self._on_param_changed)
        self.direction_group = gui.radioButtons(
            params_box, self, "direction_index",
            btnLabels=[d[0] for d in DIRECTIONS], label="Dirección:",
            callback=self._on_param_changed)
        self.scoring_combo = gui.comboBox(
            params_box, self, "scoring_index", items=[],
            label="Métrica (scoring):", callback=self._on_param_changed)

        info_box = gui.vBox(self.controlArea, "Resultado")
        self.info_label = gui.widgetLabel(info_box, "Ningún dato procesado todavía.")

        gui.auto_apply(self.buttonsArea, self)

        self._update_param_visibility()
        self._update_domain_dependent_controls()

    def _on_method_changed(self):
        self._update_param_visibility()
        self.commit.deferred()

    def _on_param_changed(self):
        self.commit.deferred()

    def _update_param_visibility(self):
        m = self.method_index
        self.n_features_box.box.setVisible(m in (RFE_METHOD, SFS_METHOD))
        self.step_box.box.setVisible(m in (RFE_METHOD, RFECV_METHOD))
        self.min_features_box.box.setVisible(m == RFECV_METHOD)
        self.cv_box.box.setVisible(m in (RFECV_METHOD, SFS_METHOD))
        self.direction_group.setVisible(m == SFS_METHOD)
        self.scoring_combo.box.setVisible(m in (RFECV_METHOD, SFS_METHOD))

    def _rebuild_estimator_combo(self, ptype):
        rebuild_combo(self.estimator_combo, self, "estimator_index",
                      ESTIMATORS.get(ptype, []))

    def _rebuild_scoring_combo(self, ptype):
        rebuild_combo(self.scoring_combo, self, "scoring_index",
                      SCORING.get(ptype, []))

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

        self._rebuild_estimator_combo(ptype)
        self._rebuild_scoring_combo(ptype)

        if self.data is not None:
            n_attrs = len(self.data.domain.attributes)
            max_select = max(1, n_attrs - 1)
            self.controls.n_features.setMaximum(max_select)
            if self.n_features > max_select:
                self.n_features = max_select
            self.controls.min_features.setMaximum(max(1, n_attrs))
            if self.min_features > n_attrs:
                self.min_features = max(1, n_attrs)

    @Inputs.data
    def set_data(self, data):
        self.data = data
        self._update_domain_dependent_controls()
        self.commit.now()

    def _make_selector(self, ptype, n_attrs):
        _, make_estimator = ESTIMATORS[ptype][self.estimator_index]
        estimator = make_estimator()
        max_select = max(1, n_attrs - 1)

        if self.method_index == RFE_METHOD:
            return RFE(
                estimator,
                n_features_to_select=min(self.n_features, max_select),
                step=self.step)

        _, scoring = SCORING[ptype][self.scoring_index]
        if self.method_index == RFECV_METHOD:
            return RFECV(
                estimator,
                step=self.step,
                min_features_to_select=min(self.min_features, n_attrs),
                cv=self.cv,
                scoring=scoring)

        _, direction = DIRECTIONS[self.direction_index]
        return SequentialFeatureSelector(
            estimator,
            n_features_to_select=min(self.n_features, max_select),
            direction=direction,
            scoring=scoring,
            cv=self.cv)

    @gui.deferred
    def commit(self):
        self.Error.selection_failed.clear()
        self.Warning.no_features_selected.clear()

        ptype = problem_type(self.data)
        if self.data is None or ptype is None:
            self.info_label.setText("Ningún dato procesado todavía.")
            self.Outputs.data.send(None)
            return

        n_attrs = len(self.data.domain.attributes)
        selector = self._make_selector(ptype, n_attrs)

        self.info_label.setText("Calculando (puede tardar unos segundos)...")
        QApplication.processEvents()

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
            ("Método", METHOD_LABELS[self.method_index]),
            ("Estimador", estimator_label),
        ])


if __name__ == "__main__":  # pragma: no cover
    WidgetPreview(OWWrapperSelection).run(Table("iris"))
