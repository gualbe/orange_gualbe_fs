.. _selección wrapper:

Selección Wrapper
===================

Selecciona los atributos más relevantes de una tabla de datos mediante
métodos wrapper, que evalúan subconjuntos de atributos entrenando
repetidamente un modelo predictivo (a diferencia del :ref:`filtro
univariante <filtro univariante>`, que no entrena ningún modelo).

Descripción
-----------

Los métodos wrapper suelen ser más lentos que los de filtro, pero tienen
en cuenta las **interacciones entre atributos**, ya que evalúan
conjuntos de atributos con un modelo real en lugar de puntuar cada
atributo por separado.

Entradas
--------

- **Data**: una tabla de datos de Orange con una variable objetivo definida.

Salidas
-------

- **Data**: la misma tabla, con solo los atributos seleccionados. La
  variable objetivo y los metadatos se conservan siempre.

1. Elige un método wrapper
----------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Método
     - Qué hace
   * - **RFE** (Eliminación Recursiva)
     - Entrena el modelo, elimina el atributo menos importante, y repite
       hasta llegar al número de atributos indicado.
   * - **RFECV**
     - Igual que RFE, pero usa validación cruzada para elegir
       automáticamente el número óptimo de atributos (no hace falta
       indicarlo).
   * - **SFS** (Selección Secuencial)
     - Añade (o quita) atributos uno a uno, evaluando cada paso con
       validación cruzada, hasta llegar al número de atributos indicado.

2. Elige un modelo base (estimador)
--------------------------------------

Los tres métodos necesitan un modelo predictivo con el que evaluar los
atributos. El widget ofrece un modelo lineal y un modelo de árboles,
adaptados automáticamente al tipo de variable objetivo (categórica o
numérica):

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Estimador
     - Notas
   * - **Regresión Logística / Lineal**
     - Rápido. Funciona mejor cuando la relación entre atributos y
       target es aproximadamente lineal.
   * - **Bosque Aleatorio**
     - Más lento, pero capta relaciones no lineales entre atributos.

3. Parámetros de cada método
-------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Parámetro
     - Métodos que lo usan
     - Qué significa
   * - Número de atributos a seleccionar
     - RFE, SFS
     - Cuántos atributos debe conservar el resultado final.
   * - Paso
     - RFE, RFECV
     - Cuántos atributos se eliminan en cada iteración.
   * - Mínimo de atributos a conservar
     - RFECV
     - Límite inferior de la búsqueda automática por validación cruzada.
   * - Pliegues de validación cruzada (cv)
     - RFECV, SFS
     - En cuántos grupos se divide a los datos para evaluar cada paso.
   * - Dirección
     - SFS
     - *Hacia adelante*: empieza sin atributos y va añadiendo. *Hacia
       atrás*: empieza con todos y va quitando.
   * - Métrica (scoring)
     - RFECV, SFS
     - Con qué métrica se compara cada subconjunto de atributos durante
       la validación cruzada (por defecto, la del propio modelo).

4. Resultado
------------

El widget envía a su salida la misma tabla de datos, pero con solo los
atributos seleccionados.

Notas importantes
------------------

- Los métodos wrapper pueden tardar **varios segundos o minutos** con
  muchos atributos o datasets grandes, especialmente RFECV y SFS con
  dirección "hacia atrás" (evalúan muchas combinaciones con validación
  cruzada). Por eso este widget no aplica los cambios automáticamente:
  hay que pulsar **Apply** después de ajustar los parámetros.
- Si hay valores ausentes, imputa antes con el widget "Impute" de Orange.
