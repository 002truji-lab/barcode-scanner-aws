# Nuevo Modo: Verificación por Master Box (`app2.py`)

Se va a crear una segunda aplicación (`app2.py`) que funcione de forma muy parecida a la original, pero orientada a un flujo de trabajo específico: **Completar una Master Box**.

## Flujo de Trabajo Propuesto

1. **Pantalla de Inicio:** En lugar de escanear directamente los productos, la aplicación te pedirá primero que escanees o introduzcas el código de la **Master Box** que quieres trabajar.
2. **Validación:** El sistema comprobará en AWS RDS cuántos productos pertenecen a esa Master Box y cuántos ya han sido encontrados. 
3. **Modo Escáner (Contador):** Una vez validada la Master Box, aparecerá el escáner normal (con las 3 opciones de cámara, foto o teclado) y un **gran contador** (ej. `0/3`).
4. **Verificación de Códigos:** 
   - Al escanear un código, si pertenece a esa Master Box y es nuevo, sonará el **pitido de éxito**, la pantalla se pondrá verde y el contador subirá a `1/3`.
   - Si escaneas un código que **NO** pertenece a la Master Box activa (aunque exista en la base de datos), sonará el **pitido de error** y te avisará de que te has equivocado de caja.
   - Si el código no existe, dará error normal.
5. **Finalización:** Cuando el contador llegue a `3/3` (o el total que sea), te avisará de que la caja está completa y te dará un botón para cambiar a una nueva Master Box.

## Cambios Técnicos

### `db.py`
Se añadirá una nueva función `obtener_progreso_master_box(master_box: str)` que hará una consulta a PostgreSQL para contar el total de registros de esa caja y cuántos tienen la `fecha_encontrado` ya rellenada.

### `app2.py`
Será un archivo nuevo. Reutilizará todos los estilos visuales premium y las funciones de sonido de `app.py`. Incluirá una lógica de "estado" (`st.session_state`) para recordar en qué Master Box estás trabajando actualmente para no tener que pedirla en cada escaneo.

## Preguntas Abiertas
¿Estás de acuerdo con que la aplicación dé un **error** si escaneas un código correcto pero que pertenece a *otra* Master Box distinta a la que tienes seleccionada en ese momento? (Esto ayuda a evitar mezclar cajas).
