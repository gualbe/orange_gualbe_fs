.. _filtro univariante:

Filtro Univariante
===================

Selecciona los atributos más relevantes de una tabla de datos mediante
métodos de filtro univariante.

Descripción
-----------

Este widget evalúa **cada atributo por separado** frente a la variable
objetivo (target) usando una función de puntuación estadística, sin
entrenar ningún modelo predictivo. Es el enfoque más rápido y sencillo de
selección de atributos.

Entradas
--------

- **Data**: una tabla de datos de Orange con una variable objetivo definida.

Salidas
-------

- **Data**: la misma tabla, con solo los atributos seleccionados. La
  variable objetivo y los metadatos se conservan siempre.

1. Método de selección
-----------------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Método
     - Qué hace
   * - **SelectKBest**
     - Se queda con los *k* atributos de mayor puntuación.
   * - **SelectPercentile**
     - Se queda con un porcentaje de los atributos con mayor puntuación.
   * - **SelectFpr**
     - Descarta atributos cuyo p-valor supera *alpha* (tasa de falsos
       positivos).
   * - **SelectFdr**
     - Igual que SelectFpr pero controlando la tasa de descubrimientos
       falsos (más estricto con muchos atributos).
   * - **SelectFwe**
     - Igual que SelectFpr pero controlando el error familiar (el más
       conservador de los tres).

2. Función de puntuación (scoring)
-----------------------------------

El widget detecta automáticamente si la variable objetivo es
**categórica** (clasificación) o **numérica** (regresión), y solo deja
activas las funciones compatibles con ese tipo de problema:

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - Función
     - Tipo de problema
     - Notas
   * - **chi2**
     - Clasificación
     - Requiere que todos los atributos sean no negativos.
   * - **f_classif**
     - Clasificación
     - ANOVA F entre cada atributo y las clases.
   * - **f_regression**
     - Regresión
     - Correlación lineal (F-test) entre cada atributo y el target.
   * - **r_regression**
     - Regresión
     - Coeficiente de correlación de Pearson.

3. Resultado
------------

El widget envía a su salida la misma tabla de datos, pero con solo los
atributos seleccionados.

Notas importantes
------------------

- Los datos de entrada deben tener una variable objetivo (target) definida.
- Si usas **chi2** y tienes valores negativos, normaliza antes los datos
  (por ejemplo con el widget "Normalize" de Orange).
- Si hay valores ausentes, imputa antes con el widget "Impute" de Orange:
  las funciones de puntuación de scikit-learn no admiten valores
  faltantes.
