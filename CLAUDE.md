# orange_gualbe_fs — Selección de Atributos

Add-on de Orange Data Mining con widgets de selección de atributos (feature
selection) basados en `sklearn.feature_selection`. Responde siempre en español de
España. Esta carpeta es la de la sesión de trabajo `fs-mant`; la coordinadora del
grupo vive en `../orange-hub` y te manda las peticiones.

**Es la piloto del grupo**: los cambios comunes a todos los add-ons se hacen y
verifican primero aquí, y luego se propagan a los demás.

Antes de tocar widgets, ayuda o empaquetado lee
`../orange-hub/conocimiento/trampas-orange.md`.

## Identidad

- Distribución y namespace: `orange_gualbe_fs` / `orangecontrib.orange_gualbe_fs`
  (en PyPI normalizado como `orange-gualbe-fs`).
- Categoría: «Selección de Atributos», color `#FFA85C`.
- Dependencias: `Orange3>=3.32.0`, `scikit-learn>=1.0`.
- Repo público https://github.com/gualbe/orange_gualbe_fs (rama `main`, fuente de
  verdad) · PyPI https://pypi.org/project/orange-gualbe-fs/
- Ayuda en castellano (`doc/conf.py`: `language = "es"`).

## Widgets

| Widget | Fichero / clase | Qué hace |
|---|---|---|
| Filtro Univariante | `owunivariateselection.py` / `OWUnivariateSelection` | `SelectKBest`, `SelectPercentile`, `SelectFpr`, `SelectFdr`, `SelectFwe` con `chi2`, `f_classif`, `f_regression`, `r_regression` (solo las compatibles con el tipo de objetivo). `auto_apply=True`. |
| Selección Wrapper | `owwrapperselection.py` / `OWWrapperSelection` | `RFE`, `RFECV`, `SequentialFeatureSelector` con estimador base (logística/lineal o bosque aleatorio) y parámetros por método. `auto_apply=False` a propósito (lento): datos nuevos → `commit.now()`, parámetros → «Apply». |
| Selección Embebida | `owembeddedselection.py` / `OWEmbeddedSelection` | `SelectFromModel` con 8 estimadores de clasificación y 10 de regresión, umbral media/mediana/personalizado y máximo de atributos opcional (`gui.spin(..., checked=...)`). `auto_apply=True`. |

Lógica común en `widgets/utils.py`: `problem_type(data)`, `reduce_domain(data,
mask)`, `rebuild_combo(combo, widget, attr_name, items)`. Todo widget nuevo las
reutiliza (`from orangecontrib.orange_gualbe_fs.widgets.utils import ...`).

## Estructura

- `orangecontrib/orange_gualbe_fs/widgets/`: widgets, `utils.py`, `icons/`.
- `doc/`: fuentes Sphinx de la ayuda (`index.rst` + `widgets/*.rst`). El HTML se
  genera en `orangecontrib/orange_gualbe_fs/_help/html` (ignorado en git).
- `assets/`: imágenes del README (banner, `familias`, `flujo`, esquemas por widget
  y `captura_*.png`), regenerables con `python assets/generar_imagenes.py
  [--capturas]`. Paleta: filtro azul, wrapper violeta, embebida verde; nodos
  propios en `#FFA85C` con anillo discontinuo.
- `tests/`: todavía no hay tests propios; `../orange-hub/scripts/probar.sh` hace al
  menos la prueba de humo (descubrimiento e instanciación de cada widget).

## Pruebas

```bash
../orange-hub/scripts/probar.sh .            # humo + tests/test_*.py + ayuda + paquete
../orange-hub/scripts/probar.sh . --rapido   # solo humo y tests, en Orange.app
```

Cada `tests/test_*.py` es un script ejecutable con el Python de Orange que sale con
código distinto de 0 si algo falla. Prueba la matriz completa de combinaciones de
cada widget (método × puntuación × tipo de objetivo), no solo las habituales.

## Ficheros comunes con los otros add-ons

Iguales en todos salvo el nombre del paquete: `.github/workflows/publish.yml`,
`.gitignore`, `LICENSE`, `doc/conf.py` (salvo idioma y estáticos), la estructura de
`pyproject.toml` y la cabecera de `widgets/__init__.py` (`WIDGET_HELP_PATH`). Si un
cambio toca uno de ellos, dilo en el informe a la coordinadora: probablemente haya
que propagarlo (skill `orange-propagar`) y actualizar `../orange-hub/plantilla/`.
`../orange-hub/scripts/comparar.sh <ruta>` muestra cuánto difiere.

## Cierre obligatorio de cada mantenimiento

Skill `orange-release`. En resumen: pruebas en verde → `version` en
`pyproject.toml` (parche para correcciones, menor para funciones nuevas) →
sección `## X.Y.Z (AAAA-MM-DD)` en `CHANGELOG.md` → si cambia un widget, su ayuda y
el README (y las imágenes) → commit en `main` («Descripción (X.Y.Z)») →
`../orange-hub/scripts/publicar.sh .` (push, release `vX.Y.Z`, CI a PyPI e
instalación en Orange.app y Orange-Gualbe.app). Los cambios que solo afectan al
repo (README de GitHub, CLAUDE.md, CHANGELOG) no necesitan versión nueva.

## Pendientes conocidos

- `r_regression` con «K mejores» o «Percentil» ordena con signo (en `housing` deja
  fuera `LSTAT`, r = −0,74). Está documentado; falta que el usuario decida si se
  ordena por valor absoluto.
- La descripción corta de `pyproject.toml` dice «seleccion» sin tilde (se ve en
  PyPI); arreglarlo exige publicar versión.
- Falta la comprobación visual del usuario en el lienzo de Orange.
