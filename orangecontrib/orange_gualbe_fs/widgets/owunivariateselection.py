# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Gualberto Asencio Cortés
# Part of orange_gualbe_fs. See the LICENSE and NOTICE files for details.

from sklearn.feature_selection import (
    SelectKBest, SelectPercentile, SelectFpr, SelectFdr, SelectFwe,
    chi2, f_classif, f_regression, r_regression,
)

from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from Orange.widgets.utils.widgetpreview import WidgetPreview

from orangecontrib.orange_gualbe_fs.widgets.utils import problem_type, reduce_domain

# (etiqueta visible, clase de sklearn, nombre del parametro que configura)
METHODS = [
    ("K mejores (SelectKBest)", SelectKBest, "k"),
    ("Mejor percentil (SelectPercentile)", SelectPercentile, "percentile"),
    ("Tasa de falsos positivos (SelectFpr)", SelectFpr, "alpha"),
    ("Tasa de descubrimientos falsos (SelectFdr)", SelectFdr, "alpha"),
    ("Error familiar (SelectFwe)", SelectFwe, "alpha"),
]

# (etiqueta visible, funcion de puntuacion de sklearn, tipo de problema compatible)
SCORES = [
    ("Chi-cuadrado (chi2)", chi2, "classification"),
    ("ANOVA F (f_classif)", f_classif, "classification"),
    ("Regresión F (f_regression)", f_regression, "regression"),
    ("Correlación de Pearson (r_regression)", r_regression, "regression"),
]


class OWUnivariateSelection(OWWidget):
    name = "Filtro Univariante"
    description = ("Selecciona atributos mediante métodos de filtro "
                    "univariante (SelectKBest, SelectPercentile, SelectFpr, "
                    "SelectFdr, SelectFwe).")
    icon = "icons/owunivariateselection.svg"
    priority = 100
    keywords = "feature selection, seleccion de atributos, filtro, univariante"
    want_main_area = False
    resizing_enabled = False

    class Inputs:
        data = Input("Data", Table)

    class Outputs:
        data = Output("Data", Table)

    method_index = Setting(0)
    scoring_index = Setting(0)
    k = Setting(10)
    percentile = Setting(10)
    alpha = Setting(0.05)
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

        method_box = gui.vBox(self.controlArea, "Método de selección")
        gui.comboBox(
            method_box, self, "method_index",
            items=[m[0] for m in METHODS],
            callback=self._on_method_changed)

        self.k_box = gui.spin(
            method_box, self, "k", minv=1, maxv=10000, step=1,
            label="Número de atributos (k):", controlWidth=80,
            callback=self._on_param_changed)
        self.percentile_box = gui.spin(
            method_box, self, "percentile", minv=1, maxv=100, step=1,
            label="Percentil (%):", controlWidth=80,
            callback=self._on_param_changed)
        self.alpha_box = gui.doubleSpin(
            method_box, self, "alpha", minv=0.0, maxv=1.0, step=0.01,
            decimals=2, label="Alpha:", controlWidth=80,
            callback=self._on_param_changed)

        scoring_box = gui.vBox(self.controlArea, "Función de puntuación (scoring)")
        self.scoring_group = gui.radioButtons(
            scoring_box, self, "scoring_index",
            btnLabels=[s[0] for s in SCORES],
            callback=self._on_scoring_changed)

        info_box = gui.vBox(self.controlArea, "Resultado")
        self.info_label = gui.widgetLabel(info_box, "Ningún dato procesado todavía.")

        gui.auto_apply(self.buttonsArea, self)

        self._update_param_visibility()
        self._update_domain_dependent_controls()

    def _on_method_changed(self):
        self._update_param_visibility()
        self.commit.deferred()

    def _on_scoring_changed(self):
        self.commit.deferred()

    def _on_param_changed(self):
        self.commit.deferred()

    def _update_param_visibility(self):
        _, _, param_name = METHODS[self.method_index]
        self.k_box.box.setVisible(param_name == "k")
        self.percentile_box.box.setVisible(param_name == "percentile")
        self.alpha_box.box.setVisible(param_name == "alpha")

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

        if self.data is not None:
            n_attrs = max(1, len(self.data.domain.attributes))
            self.controls.k.setMaximum(n_attrs)
            if self.k > n_attrs:
                self.k = n_attrs

        compatible = [i for i, (_, _, score_ptype) in enumerate(SCORES)
                      if score_ptype == ptype]
        for i, button in enumerate(self.scoring_group.buttons):
            button.setEnabled(i in compatible)

        if compatible and self.scoring_index not in compatible:
            self._set_scoring_index(compatible[0])

    def _set_scoring_index(self, index):
        self.scoring_index = index
        self.scoring_group.buttons[index].setChecked(True)

    @Inputs.data
    def set_data(self, data):
        self.data = data
        self._update_domain_dependent_controls()
        self.commit.now()

    @gui.deferred
    def commit(self):
        self.Error.selection_failed.clear()
        self.Warning.no_features_selected.clear()

        ptype = problem_type(self.data)
        if self.data is None or ptype is None:
            self.info_label.setText("Ningún dato procesado todavía.")
            self.Outputs.data.send(None)
            return

        _, method_cls, param_name = METHODS[self.method_index]
        _, score_func, _ = SCORES[self.scoring_index]

        if param_name == "alpha" and score_func is r_regression:
            self.Error.selection_failed(
                "r_regression no calcula p-valores, que necesita este método: "
                "elige K mejores o Percentil, u otra función de puntuación.")
            self.info_label.setText("Ningún dato procesado todavía.")
            self.Outputs.data.send(None)
            return

        kwargs = {}
        if param_name == "k":
            kwargs["k"] = min(self.k, len(self.data.domain.attributes))
        elif param_name == "percentile":
            kwargs["percentile"] = self.percentile
        elif param_name == "alpha":
            kwargs["alpha"] = self.alpha

        selector = method_cls(score_func, **kwargs)

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
            f"{len(selected)} de {len(self.data.domain.attributes)} "
            f"atributos seleccionados.")
        self.Outputs.data.send(reduced)

    def send_report(self):
        method_label, _, _ = METHODS[self.method_index]
        score_label, _, _ = SCORES[self.scoring_index]
        self.report_items("Configuración", [
            ("Método", method_label),
            ("Función de puntuación", score_label),
        ])


if __name__ == "__main__":  # pragma: no cover
    WidgetPreview(OWUnivariateSelection).run(Table("iris"))
