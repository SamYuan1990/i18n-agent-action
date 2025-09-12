## Por qué tenemos esto

Se discutió en KCD 2025 Beijing, Community Over Code 2025 China y finalmente decidimos crear un agente para manejar trabajos de i18n (internacionalización) para la comunidad.
En cuanto a mí, no puedo paralelizar en [https://github.com/sustainable-computing-io/kepler-doc/issues/175](https://github.com/sustainable-computing-io/kepler-doc/issues/175) y la sesión de Community Over Code 2025.

## En alcance y no en alcance, y cómo funciona

> No queremos reinventar la rueda.

- El disparador no está en alcance
  - dejar a manual para acción de actualización completa o diferencial
  - API del modelo y endpoint del modelo
  > ¿Las personas pueden seleccionar cualquier servicio LLM con API de OpenAI?
  - punto de entrada de configuración
  > Necesitamos saber el idioma predeterminado y qué idiomas son el objetivo, está en el archivo de configuración.

--- alcance ---

- Fase uno: desde el archivo de configuración

> Sam en julio de 2025: No quiero que LLM escanee el proyecto, por el costo de tokens o porque podría equivocarse. Simplemente pedir al mantenedor del documento que proporcione el archivo de configuración de i18n, el punto manual al archivo de configuración será 100% correcto para la configuración de i18n.

- alcance del idioma, ¿cómo obtener el alcance del idioma?
  - = consumir archivos de configuración para obtener la lista de idiomas.
  - = idioma predeterminado - idioma existente (una diferencia de archivo)

- guardar resultado en el archivo específico

> Sam en julio de 2025: después de tener el alcance de traducción, también necesitamos tener reglas de nomenclatura desde los archivos de configuración. (o quizás pedir a LLM que lo note)

-- fin aquí: obtener una lista para archivo fuente, traducir objetivo, idioma.
> Sam en julio de 2025: como resultado de esta fase, necesitamos tener un alcance claro para todas las tareas.

-- Fase dos, un bucle A aquí para traducir

- Traducir pedir ayuda a LLM
  - ¿cómo obtener un glosario para mapeo de contenido?
  - ¿Brechas? (o simplemente actualizar todo)

> Sam en julio de 2025: para ser específico.

--- no en alcance ---

- crear PR dejar a Acción PR

> No queremos reinventar la rueda. ya que ya hay acciones de PR para abrir PR para cambios.