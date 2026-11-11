# Cambios

Cada versión se publica a la vez en GitHub (release `vX.Y.Z`) y en
[PyPI](https://pypi.org/project/orange-gualbe-fs/).

## 0.1.4 (2026-11-11)

- Autoría y licencia reforzadas, sin cambiar de licencia (sigue siendo
  GPL-3.0-or-later):
  - Cabecera SPDX con el copyright de Gualberto Asencio Cortés en todos los
    ficheros `.py`.
  - Nuevo fichero `NOTICE` con la autoría, la licencia y los términos adicionales
    del artículo 7 de la GPL-3 (atribución, marcado de las versiones modificadas
    y nombres «orange_gualbe», «Orange Gualbe» y «Gualbe» reservados), y los
    componentes de terceros.
  - Nuevo fichero `CITATION.cff` para citar el add-on.
  - El paquete declara la licencia con la sintaxis SPDX (PEP 639) e incluye
    `LICENSE` y `NOTICE` en el wheel y en el sdist; el autor figura con su
    nombre completo.
  - README: la sección «Licencia» pasa a «Licencia y autoría», con la política
    de nombres para forks y cómo citar.
  - Ayuda (F1): página «Licencia y autoría» y copyright del autor en el pie.
- Sin cambios funcionales en los widgets.

## 0.1.3 (2026-11-06)

- Página inicial renovada (GitHub y PyPI): banner, insignias, comparación visual
  de las tres familias de selección, flujo típico en el lienzo de Orange, un
  esquema y una captura real por widget, y tablas de parámetros.
- Corregido: en el **Filtro Univariante**, `r_regression` combinada con
  SelectFpr, SelectFdr o SelectFwe (que necesitan p-valores) lanzaba una
  excepción sin tratar. Ahora el widget muestra un error claro y no envía salida.
  La ayuda (F1) documenta esta limitación y que `r_regression` puntúa con signo.

## 0.1.2 (2026-11-06)

- La publicación en PyPI pasa a ser automática con Trusted Publishing: cada
  release de GitHub construye el paquete, lo sube a PyPI y adjunta los ficheros a
  la release.
- Sin cambios funcionales en los widgets.

## 0.1.1 (2026-11-06)

- Los metadatos del paquete enlazan a este repositorio (`Homepage`, `Repository`
  e `Issues`) y se añade el fichero `LICENSE` (GPL-3.0-or-later).
- Sin cambios funcionales respecto a la 0.1.0.

## 0.1.0 (2026-11-06)

Primera versión, con tres widgets de selección de atributos y ayuda nativa de
Orange en castellano (tecla F1):

- **Filtro Univariante** (SelectKBest, SelectPercentile, SelectFpr, SelectFdr y
  SelectFwe).
- **Selección Wrapper** (RFE, RFECV y SequentialFeatureSelector).
- **Selección Embebida** (SelectFromModel con 18 estimadores de clasificación y
  regresión).
