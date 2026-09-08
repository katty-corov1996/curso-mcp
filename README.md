## Clase 2 — APIs de IA Generativa y memoria conversacional

### Conversación de 8 turnos (Paso 7)

Ver evidencia en `entregas/s02/evidencia/memoria.png`.

La conversación se ejecutó durante 8 turnos. En el primer turno se indicó que el usuario se llamaba Alex y que su color favorito era el verde. En el turno 8, el modelo recordó correctamente ambos datos, demostrando que el historial de conversación fue reenviado en cada llamada.

Ejemplo de la salida final:

Turno 8:

[tokens] total_token_count=472

[finish] FinishReason.STOP

Te llamas **Alex** y tu color favorito es el **verde**.

### Por qué elegí ventana deslizante

Se utilizó una estrategia de ventana deslizante porque permite conservar los turnos más recientes de la conversación sin mantener un historial ilimitado.

Para esta práctica se configuró `MAX_TURNS = 10`, lo cual permite conservar completamente la conversación de 8 turnos. Esta estrategia es sencilla, controla el crecimiento del contexto y evita utilizar mecanismos más complejos como resumen progresivo, memoria selectiva o almacenamiento externo.

### Límite de solicitudes provocado (Paso 9)

Ver evidencia en `entregas/s02/evidencia/rate_limit.png`.

Durante la ejecución se alcanzó el límite de solicitudes del nivel gratuito de Gemini y se obtuvo un error `429`. El programa manejó el error mediante reintentos con backoff exponencial de 1, 2 y 4 segundos, evitando que la aplicación terminara inesperadamente.

También se presentaron errores temporales `503`, que fueron capturados como `ServerError` y manejados mediante reintentos.

### Nota de compatibilidad del modelo

La guía original utiliza `gemini-2.5-flash`. Durante la práctica, la API devolvió un error `404 NOT_FOUND` indicando que este modelo ya no estaba disponible para nuevos usuarios.

Por esta razón se utilizó `gemini-3.6-flash`, manteniendo la misma lógica de la práctica: parámetros explícitos, control de tokens, memoria conversacional y manejo de errores.