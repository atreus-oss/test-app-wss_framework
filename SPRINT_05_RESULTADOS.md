# SPRINT_05_RESULTADOS

## Identificación

| Campo | Valor |
|---|---|
| Fecha | 5 de octubre de 2026 |
| Base local | `3e9af47`, con una edición previa del título en `index.html`, conservada |
| Objetivo | Alinear aplicación y reportes con WSS 2.0, corregir el cierre y depurar observaciones ocultas |
| Estado | Verificado localmente; sin commit ni publicación remota |

## Análisis y cambios

La versión inicial ponderaba AU/EN/EX/AN/BM tanto en Python como en JavaScript. Se adoptó la fórmula del libro:

```text
WSS = 10 × (0.50 × AU + 0.50 × EN)
WSS:2.0/AU:<valor>/EN:<valor>
```

Las tablas normalizadas y los umbrales se mantienen: Bajo hasta 2.5, Medio hasta 5.0, Alto hasta 7.5 y Crítico por encima de 7.5. Los desconocidos siguen siendo no evaluables, sin puntaje. Señal y alineación se conservan como contexto, sin intervenir en el cálculo. Se retiraron los factores numéricos EX/AN/BM y las afirmaciones de detección de anomalías de la calculadora y los resultados nuevos.

| Caso de aceptación | Puntaje | Clasificación |
|---|---:|---|
| WPA3/CCMP | 1.0 | Bajo |
| WPA2/CCMP | 2.0 | Bajo |
| WPA versión 1/TKIP | 7.5 | Alto |
| OPEN/NONE | 10.0 | Crítico |
| OPEN/WEP teórico | 9.5 | Crítico |

Estos resultados son criterios determinísticos comprobados con entradas sintéticas. No acreditan experimentos físicos ni participación organizacional.

### Cierre del informe técnico

El botón de cierre ya existía, pero el panel estaba dentro de un contexto de apilamiento inferior al de la barra de pestañas; la barra interceptaba los clics. Se trasladó el panel al nivel superior del documento, manteniendo su posición lateral. Se añadió la etiqueta explícita «Cerrar informe», se ajustó el cuerpo desplazable mediante flex y se verificaron Escape, recuperación del foco y pantalla estrecha. Cambiar de pestaña también cierra el panel.

### Redes ocultas y resultados vigentes

- La condición de SSID oculto proviene de un encabezado realmente vacío, no de comparar con un nombre de reemplazo.
- Se exige un BSSID con formato válido, distinto de cero y de broadcast; se descartan encabezados sin radio y valores inválidos.
- Se eliminan duplicados de SSID/BSSID/perfil dentro de la misma captura.
- Se prefiere el nombre visible cuando la misma captura contiene ese BSSID y perfil tanto oculto como identificado; perfiles distintos se conservan.
- Las observaciones ocultas válidas permanecen separadas por BSSID.
- Un escaneo nuevo elimina los resultados anteriores; si falla, no quedan resultados anteriores exportables ni tarjetas que parezcan actuales.

No se verificó una red física del usuario. Un BSSID válido en la salida de Windows constituye evidencia reportada por el sistema operativo, no prueba independiente de presencia física. No se elimina la caché del sistema operativo ni se inventan redes cuando la captura está vacía.

### Reportes y documentación

Se actualizaron JSON, PDF y README para WSS 2.0. Los párrafos del PDF vuelven al margen izquierdo y avanzan a la siguiente línea, resolviendo el error de espacio horizontal con fpdf2 2.8.9. Se reemplazaron parámetros obsoletos de posicionamiento y salida. Se revisaron visualmente páginas de un reporte sintético anonimizado.

Las bitácoras anteriores mantienen sus resultados históricos. Se retiraron referencias al asistente y rutas personales del entorno de ejecución, dejando comandos portables. La ejecución nueva se registra exclusivamente en esta bitácora.

## Entorno

Windows; Python 3.12.14; pytest 9.1.1; fpdf2 2.8.9. Prueba de interfaz con Playwright y Microsoft Edge en modo sin ventana. Los datos de interfaz proceden de la demostración Python; el puente de la ventana nativa se simula.

## Comandos utilizados

Ejecutados con el entorno de dependencias preparado, desde la raíz del proyecto. Las rutas del intérprete se expresan de forma portable:

```powershell
python -m py_compile app.py wss_engine.py recommendation_engine.py
python -m pytest -q --tb=short --basetemp=../pytest-stage
node tests/ui-smoke.cjs
```

Para reproducir la prueba de interfaz, instalar Playwright y configurar `PYTHON` con el intérprete que dispone de las dependencias de la aplicación. El navegador predeterminado del script es Edge; `WSS_BROWSER_CHANNEL` permite seleccionar otro canal instalado.

## Resultados

```text
Compilación Python: sin errores.
119 passed
Interfaz: cinco escenarios WSS 2.0, señal independiente, cierre, Escape, foco, pantalla estrecha y escaneos vacíos/fallidos: OK.
```

Las pruebas cubren los cinco escenarios completos desde entrada textual hasta JSON/PDF, límites de clasificación, señal y alineación independientes, parámetros desconocidos, ocultas válidas, BSSID inválidos, duplicados, nombre visible de una misma radio, perfiles diferentes y limpieza tras escaneos vacíos o fallidos. Se conservan las pruebas previas de recomendaciones, importación, exportación, anonimización y agrupamiento, actualizadas al contrato WSS 2.0 cuando corresponde.

## Límites de la verificación

No se ejecutaron ataques, conexión a redes evaluadas, capturas reales, encuestas PRE/POST ni pruebas físicas de WEP. La interfaz fue comprobada en navegador con puente simulado, no en la ventana nativa pywebview ni en un ejecutable empaquetado. Las 99 pruebas citadas en el libro corresponden a otra evidencia histórica y no se sustituyen silenciosamente por este resultado.
