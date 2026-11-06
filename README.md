# orange_gualbe_fs

Add-on de **selección de atributos (feature selection)** para
[Orange Data Mining](https://orangedatamining.com/).

Añade una nueva categoría "Selección de Atributos" al lienzo de Orange, con
widgets que reciben una tabla de datos, permiten configurar un algoritmo de
selección de atributos desde su interfaz gráfica, y devuelven la tabla
reducida solo con los atributos elegidos.

## Widgets incluidos

### Filtro Univariante

Selecciona atributos evaluando cada uno por separado frente a la variable
objetivo (target), sin entrenar ningún modelo. Permite elegir:

- **Método de selección**: `SelectKBest`, `SelectPercentile`, `SelectFpr`,
  `SelectFdr`, `SelectFwe` (de `scikit-learn`).
- **Función de puntuación (scoring)**: `chi2`, `f_classif`, `f_regression`,
  `r_regression`.

El widget detecta automáticamente si el target de los datos de entrada es
**categórico** (clasificación) o **numérico** (regresión), y solo deja
activas las funciones de puntuación compatibles con ese tipo de problema.

### Selección Wrapper

Selecciona atributos mediante métodos wrapper, que evalúan subconjuntos de
atributos entrenando repetidamente un modelo predictivo:

- **Método**: `RFE`, `RFECV`, `SequentialFeatureSelector` (de `scikit-learn`).
- **Estimador base**: Regresión Logística/Lineal o Bosque Aleatorio, según
  el tipo de target detectado.
- Parámetros configurables por método: número de atributos, paso,
  mínimo de atributos (RFECV), pliegues de validación cruzada, dirección
  (SFS) y métrica de evaluación (scoring).

A diferencia del Filtro Univariante, este widget **no aplica los cambios
automáticamente** (`auto_apply` desactivado por defecto): al ser más lento,
hay que pulsar **Apply** tras ajustar los parámetros. Sí procesa los datos
automáticamente en cuanto llegan por la entrada.

### Selección Embebida

Selecciona atributos según la importancia o los coeficientes que les
asigna un modelo predictivo ya entrenado (`SelectFromModel` de
`scikit-learn`) — entrena el modelo una sola vez, a diferencia de los
métodos wrapper:

- **Estimador base**: una selección amplia de algoritmos de `scikit-learn`
  según el tipo de target — 8 de clasificación (Regresión Logística, SVM
  Lineal, SGD, Árbol de Decisión, Bosque Aleatorio, Extra Trees, Gradient
  Boosting, AdaBoost) y 10 de regresión (los mismos más Ridge, Lasso y
  ElasticNet).
- **Umbral de selección**: media, mediana o un valor personalizado.
- **Límite de atributos** opcional (número máximo, independiente del umbral).

`auto_apply` activado por defecto (un único ajuste del modelo, más rápido
que los métodos wrapper).

Los tres widgets integran su ayuda con el **sistema de ayuda nativo de
Orange**: selecciona el widget en el lienzo y pulsa **F1**, o haz clic en
el icono **"?"** de la barra de estado del widget.

## Instalación para desarrollo

```bash
python -m venv .venv
source .venv/bin/activate
pip install Orange3 PyQt5
pip install -e .
```

Abrir Orange Canvas con el add-on instalado:

```bash
python -m Orange.canvas
```

El widget aparecerá en el lienzo bajo la categoría "Selección de Atributos".

## Ayuda de los widgets (documentación)

La ayuda que se abre con F1/"?" se genera con [Sphinx](https://www.sphinx-doc.org/)
a partir de los archivos en `doc/`. Cada widget tiene una página en
`doc/widgets/<nombre>.rst`, con una etiqueta al inicio que debe coincidir
**exactamente** con el nombre del widget en minúsculas (por ejemplo,
`.. _filtro univariante:` para el widget `name = "Filtro Univariante"`) —
así es como Orange encuentra la página correcta.

Para (re)generar la documentación tras editar o añadir un widget:

```bash
pip install sphinx
python -m sphinx -b html doc doc/build/html
```

`doc/build/html/` no se versiona en el control de código fuente: es un
artefacto generado, igual que `dist/`. Debe reconstruirse cada vez que se
edite un archivo `.rst` en `doc/widgets/`.

## Requisitos de los datos de entrada

- La tabla debe tener una variable objetivo (target) definida.
- Si vas a usar `chi2`, todos los atributos deben ser no negativos (aplica
  antes una normalización si es necesario).
- Si los datos tienen valores ausentes, imputa antes con el widget
  "Impute" de Orange: las funciones de puntuación de `scikit-learn` no
  admiten valores faltantes.
