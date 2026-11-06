import os

NAME = "Selección de Atributos"
DESCRIPTION = "Widgets para seleccionar los atributos (features) más relevantes de un conjunto de datos."
ICON = "icons/category.svg"
BACKGROUND = "#FFA85C"

# Ruta absoluta a la documentacion HTML generada con Sphinx a partir de las
# fuentes en doc/ (ver README: "Ayuda de los widgets"). Se empaqueta DENTRO
# del propio paquete (orangecontrib/orange_gualbe_fs/_help/html) para que
# funcione igual en instalacion editable que instalado desde PyPI - una ruta
# fuera del paquete (p.ej. apuntando a doc/build/html en la raiz del
# proyecto) solo existiria en este checkout de desarrollo, no en el wheel
# publicado. Se calcula con __file__ en lugar del marcador {DEVELOP_ROOT}. de
# WIDGET_HELP_PATH, ya que su resolucion depende de que importlib.metadata
# localice el .dist-info correcto y no el .egg-info que tambien crea
# `pip install -e .` en la raiz del proyecto (no es fiable).
_HELP_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "_help", "html")
)

WIDGET_HELP_PATH = (
    (_HELP_DIR + os.sep, None),
)
