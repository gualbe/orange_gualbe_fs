from Orange.data import Domain


def problem_type(data):
    """Devuelve "classification", "regression" o None segun el target de data."""
    if data is None or data.domain.class_var is None:
        return None
    class_var = data.domain.class_var
    if class_var.is_discrete:
        return "classification"
    if class_var.is_continuous:
        return "regression"
    return None


def reduce_domain(data, mask):
    """Proyecta data a los atributos marcados en mask (booleanos), conservando
    la variable objetivo y los metadatos. Devuelve (tabla_reducida, atributos_seleccionados)."""
    selected = [attr for attr, keep in zip(data.domain.attributes, mask) if keep]
    new_domain = Domain(selected, data.domain.class_var, data.domain.metas)
    return data.transform(new_domain), selected


def rebuild_combo(combo, widget, attr_name, items):
    """Reemplaza los items de un QComboBox (etiqueta, ...) segun una lista que
    cambia con los datos de entrada (p.ej. estimadores validos para el tipo de
    problema), y ajusta el Setting `attr_name` de `widget` si el indice
    seleccionado ha dejado de ser valido."""
    combo.clear()
    combo.addItems([item[0] for item in items])
    combo.setEnabled(bool(items))
    if not items:
        return
    index = getattr(widget, attr_name)
    if index >= len(items):
        index = 0
    setattr(widget, attr_name, index)
    combo.setCurrentIndex(index)
