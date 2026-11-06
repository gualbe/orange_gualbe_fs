.. _selección embebida:

Selección Embebida
=====================

Selecciona los atributos más relevantes de una tabla de datos según la
importancia o los coeficientes que les asigna un modelo predictivo ya
entrenado (``SelectFromModel`` de scikit-learn).

Descripción
-----------

A diferencia del :ref:`filtro univariante <filtro univariante>` (no
entrena ningún modelo) y de la :ref:`selección wrapper <selección
wrapper>` (entrena el modelo muchas veces, probando subconjuntos), la
selección embebida entrena el modelo **una sola vez** y usa directamente
lo que ese modelo ya sabe sobre la importancia de cada atributo
(``coef_`` en modelos lineales, ``feature_importances_`` en árboles y
ensambles). Es un buen punto intermedio entre velocidad y calidad.

Entradas
--------

- **Data**: una tabla de datos de Orange con una variable objetivo definida.

Salidas
-------

- **Data**: la misma tabla, con solo los atributos seleccionados. La
  variable objetivo y los metadatos se conservan siempre.

1. Elige un modelo base (estimador)
--------------------------------------

El widget ofrece una selección amplia de algoritmos de scikit-learn,
adaptada automáticamente al tipo de variable objetivo:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Estimadores de clasificación
     - Estimadores de regresión
   * - Regresión Logística, SVM Lineal, SGD, Árbol de Decisión, Bosque
       Aleatorio, Extra Trees, Gradient Boosting, AdaBoost
     - Regresión Lineal, Ridge, Lasso, ElasticNet, SGD, Árbol de
       Decisión, Bosque Aleatorio, Extra Trees, Gradient Boosting,
       AdaBoost

Los modelos lineales (Regresión Logística/Lineal, SVM, Ridge, Lasso,
ElasticNet, SGD) valoran los atributos por su coeficiente; los basados en
árboles (Árbol de Decisión, Bosque Aleatorio, Extra Trees, Gradient
Boosting, AdaBoost) por su importancia acumulada en las particiones del
árbol.

2. Umbral de selección
-------------------------

Se conservan los atributos cuya importancia supera un umbral:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Modo
     - Qué hace
   * - **Media (mean)**
     - Conserva los atributos por encima de la importancia media (por
       defecto).
   * - **Mediana (median)**
     - Conserva los atributos por encima de la importancia mediana
       (más permisivo que la media si hay unos pocos atributos muy
       dominantes).
   * - **Valor personalizado**
     - Fija manualmente el valor mínimo de importancia/coeficiente para
       conservar un atributo.

3. Límite de atributos (opcional)
------------------------------------

Además del umbral, se puede fijar un número máximo de atributos a
conservar (por ejemplo, "como mucho 10, aunque el umbral deje pasar
más"). Si no se activa esta casilla, solo manda el umbral.

4. Resultado
------------

El widget envía a su salida la misma tabla de datos, pero con solo los
atributos seleccionados.

Notas importantes
------------------

- Los datos de entrada deben tener una variable objetivo (target) definida.
- Si hay valores ausentes, imputa antes con el widget "Impute" de Orange.
- Con un umbral muy alto (o un valor personalizado grande) es posible que
  no quede ningún atributo seleccionado; el widget avisa de esta
  situación en lugar de fallar.
