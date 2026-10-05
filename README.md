# WSS Framework: evaluación de configuraciones Wi-Fi observables

Aplicación de escritorio en Python para Windows desarrollada como parte de la tesis **«Sistema automatizado de evaluación de seguridad Wi-Fi con validación experimental controlada en una organización de Asunción, Paraguay, 2026»**, de José Luis Cabrera Oviedo y Arturo Rafael Ferreira Cardozo, Facultad de Ingeniería de la Universidad del Norte.

El proyecto integra captura o importación de parámetros Wi-Fi, normalización, puntuación, recomendaciones y reportes. El modelo final de la investigación se denomina **Wireless Severity Score (WSS) 2.0** y estima **severidad técnica relativa** mediante autenticación y cifrado. Un puntaje menor indica menor severidad dentro del modelo; no garantiza que una red sea segura.

## Estado del repositorio y correspondencia con la tesis

**La implementación publicada en `main` todavía utiliza la formulación preliminar de cinco componentes. Este README documenta el modelo final de la tesis y la diferencia con el código publicado; su actualización no migra la aplicación a WSS 2.0.**

La revisión del 5 de octubre de 2026 tomó como base el commit [`0d1bc90`](https://github.com/atreus-oss/test-app-wss_framework/commit/0d1bc90e0c9cabbc709baeca26d2a3187e56b786). La tesis identifica la rama `sprint-05-wss-v2-au-en` como su versión sincronizada; esa rama no aparecía entre las ramas remotas publicadas durante la revisión.

| Aspecto | Modelo final de la tesis | Implementación revisada en `main` |
|---|---|---|
| Fórmula | `10 × (0.50 × AU + 0.50 × EN)` | `10 × (0.30 × AU + 0.25 × EN + 0.15 × EX + 0.20 × AN + 0.10 × BM)` |
| Señal y alineación técnica | Contexto descriptivo, sin modificar el puntaje | EX y BM participan en el cálculo |
| Vector | `WSS:2.0/AU:<valor>/EN:<valor>` | `WSS:1.0/AU:.../EN:.../EX:.../AN:.../BM:...` |
| Infraestructura | Observaciones para revisión, sin detección de ataques | Se conservan observaciones; AN permanece en el modelo y recibe 0 en la evaluación de redes |
| Calculadora de demostración | Debe representar la fórmula final AU/EN | `index.html` conserva la fórmula preliminar de cinco componentes |
| Pruebas | La tesis informa 99 pruebas aprobadas para su versión sincronizada | Deben distinguirse de las pruebas del código actualmente publicado |

`ENGINE_VERSION = "2.0"` y `REPORT_VERSION = "2.0"` identifican el motor y el formato de reporte. Esas etiquetas **no acreditan que el código implemente el modelo WSS 2.0**: debe verificarse la fórmula y el vector efectivo.

Para completar la coherencia entre tesis y software es necesario incorporar o revisar la versión AU/EN, sincronizar la calculadora y los reportes, y verificar sus pruebas. Los valores WSS 2.0 de este documento son la especificación académica y no deben atribuirse a los resultados actuales de `main`.

## Propósito y alcance

La investigación busca diseñar e implementar un sistema que evalúe configuraciones inalámbricas observables, presente resultados comprensibles y trazables, permita estudiar su comportamiento en escenarios controlados y valore su comprensión y utilidad en una organización de Asunción.

La tesis denomina al enfoque **observación pasiva**: la aplicación consulta información disponible mediante Windows, sin conectarse a las redes evaluadas, capturar contraseñas, interceptar tráfico privado ni ejecutar pruebas de penetración. La fuente principal es:

```powershell
netsh wlan show networks mode=bssid
```

Este alcance describe las acciones de la aplicación; no verifica que el adaptador opere exclusivamente en escucha a nivel de radio.

El sistema no mide riesgo organizacional integral, no detecta Evil Twin, intrusiones ni anomalías de ataque y no sustituye una auditoría profesional. No evalúa contraseñas, firmware, segmentación, dispositivos conectados ni políticas internas.

## Modelo WSS 2.0 definido en la tesis

### Fórmula y normalización

```text
WSS = 10 × (0.50 × AU + 0.50 × EN)
```

| Autenticación normalizada | AU |
|---|---:|
| SAE / WPA3-Personal | 0.1 |
| WPA2-PSK | 0.3 |
| WPA-PSK | 0.7 |
| OPEN | 1.0 |

| Cifrado normalizado | EN |
|---|---:|
| CCMP | 0.1 |
| TKIP | 0.8 |
| WEP | 0.9 |
| NONE | 1.0 |

Con estas tablas, las configuraciones evaluables producen puntajes entre **1.0 y 10.0**. Los coeficientes son heurísticos, definidos por los autores para ordenar la severidad relativa; no son probabilidades de ataque ni porcentajes de vulnerabilidad.

La ponderación 50/50 es una decisión metodológica ante la falta de evidencia empírica suficiente para asignar mayor peso a uno de los componentes. La tesis prevé un análisis de sensibilidad con pesos AU/EN de 40/60, 50/50 y 60/40; sus resultados no están presentados en el documento revisado.

### Clasificación

| Intervalo del puntaje | Clasificación |
|---|---|
| WSS ≤ 2.5 | Bajo |
| 2.5 < WSS ≤ 5.0 | Medio |
| 5.0 < WSS ≤ 7.5 | Alto |
| WSS > 7.5 | Crítico |

Los umbrales y coeficientes pertenecen a esta investigación. CVSS es una referencia conceptual para estructurar y comunicar severidad; WSS no implementa su fórmula ni adopta sus rangos. La denominación «2.0» distingue la formulación final de la versión exploratoria interna, no una versión de un estándar externo.

### Criterios de aceptación

| Escenario | AU | EN | WSS esperado | Clasificación |
|---|---:|---:|---:|---|
| WPA3/CCMP | 0.1 | 0.1 | 1.0 | Bajo |
| WPA2/CCMP | 0.3 | 0.1 | 2.0 | Bajo |
| WPA versión 1/TKIP | 0.7 | 0.8 | 7.5 | Alto |
| Red abierta, OPEN/NONE | 1.0 | 1.0 | 10.0 | Crítico |
| WEP teórico, OPEN/WEP | 1.0 | 0.9 | 9.5 | Crítico |

Son resultados determinísticos derivados de la fórmula 50/50, utilizados como criterios de aceptación. **No son mediciones experimentales obtenidas en la organización.** WEP se mantiene como caso teórico por falta de infraestructura para reproducirlo físicamente.

### Información contextual

En WSS 2.0, los siguientes datos explican el entorno y preservan trazabilidad sin modificar el puntaje:

- **Exposición observable:** señal porcentual y aproximación `RSSI ≈ -100 + Q/2 dBm`, donde Q es el porcentaje informado por Windows. No representa distancia exacta ni una vulnerabilidad por sí misma.
- **Alineación con la referencia técnica:** alineada para WPA3-Personal o WPA2-Personal con CCMP; parcialmente alineada para CCMP con autenticación fuera de esa referencia; desviada para cifrado obsoleto o ausente. No equivale a certificación de cumplimiento.
- **Infraestructura:** SSID, BSSID, banda, canal, tipo de radio y MFP cuando esté disponible. Varios BSSID bajo el mismo SSID pueden corresponder a doble banda, mesh, repetidores o varios puntos de acceso.

El vector final contiene exclusivamente AU y EN. No incluye AN, E-AN, EX ponderado ni BM ponderado. Esta separación aún debe trasladarse a la implementación publicada indicada al inicio.

## Funcionalidades de la aplicación publicada

- Captura desde `netsh` en Windows e importación de archivos `.txt` previamente guardados.
- Normalización de autenticación y cifrado, preservando los textos de origen.
- Vista sencilla con recomendaciones y vista técnica con parámetros, radios y trazabilidad.
- Agrupamiento por SSID visible, conservando los BSSID individuales. El agrupamiento Python selecciona como representante el resultado de mayor severidad; los SSID ocultos se separan por BSSID cuando está disponible.
- Observación de perfiles de seguridad diferentes bajo el mismo SSID, presentada como necesidad de revisión técnica y sin confirmar ataques.
- Recomendaciones para `NETWORK_OWNER`, `NETWORK_USER` o `GENERAL`. Cambiar el perfil modifica las recomendaciones, no el puntaje calculado.
- Exportación JSON y PDF desde los últimos resultados almacenados por Python, con diálogo nativo de guardado.
- Anonimización opcional de SSID y BSSID en los reportes.
- Datos sintéticos de demostración identificados con `synthetic_data: true`.

### Resultados incompletos

| Estado | Comportamiento |
|---|---|
| `COMPLETE` | Autenticación y cifrado reconocidos por el normalizador; se calcula un puntaje. |
| `INCOMPLETE` | Alguno de los parámetros no se reconoce; `wss_score = null` y `classification = "NO_EVALUABLE"`. |

Un resultado no evaluable no equivale a puntaje cero ni a configuración segura. El reconocimiento depende de los textos reportados por Windows y no valida la configuración interna del punto de acceso.

### Recomendaciones y reportes

`recommendation_engine.py` consume los resultados calculados y aplica reglas trazables: `REC-01` para WPA3/CCMP, `REC-02` para WPA2/CCMP, `REC-03` para TKIP, `REC-04` para WEP, `REC-05` para red abierta o sin cifrado, `REC-06` para parámetros no interpretados y `REC-07` para perfiles diferentes bajo el mismo SSID. La priorización es cualitativa y depende del rol del usuario.

Los reportes conservan fuente, parámetros originales y normalizados, clasificación, vector, observaciones y recomendaciones. El PDF agrupa redes lógicas y la exportación permite sustituir identificadores por etiquetas como `SSID-001` y `BSSID-001`. Antes de publicar evidencia, corresponde revisar también los nombres de archivos y cualquier otro dato institucional.

El estado del modelo se conserva como `PROVISIONAL`. Los reportes incorporan el siguiente alcance:

> Este reporte corresponde a una evaluación de parámetros Wi-Fi observables y no constituye una auditoría integral de ciberseguridad.

## Instalación y uso

La captura directa requiere Windows, un adaptador Wi-Fi disponible y el servicio WLAN habilitado. Se requiere Python 3.9 o superior. Las dependencias declaradas son `pywebview>=4.4` y `fpdf2>=2.7`.

Desde PowerShell, en la carpeta donde se desea clonar el proyecto:

```powershell
git clone https://github.com/atreus-oss/test-app-wss_framework.git
cd test-app-wss_framework
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

1. Abrir **Mis Redes** y ejecutar **Escanear**, o importar una salida `.txt` de `netsh`.
2. Consultar la clasificación, las recomendaciones y los detalles técnicos.
3. Seleccionar el perfil de usuario para ajustar las acciones sugeridas.
4. Exportar JSON o PDF y activar la anonimización cuando corresponda.

La **Calculadora Demo** permite explorar ejemplos, pero la versión publicada utiliza la fórmula preliminar. Los datos de demostración no constituyen evidencia de redes reales. La captura con `netsh` solo está disponible en Windows.

## Arquitectura

```text
netsh o archivo .txt
    -> wss_engine.py: lectura, normalización y cálculo
    -> recommendation_engine.py: interpretación y recomendaciones
    -> app.py / WssApi: coordinación, agrupamiento y reportes
    -> index.html / pywebview: presentación e interacción
```

La calculadora de demostración también contiene un cálculo propio en JavaScript dentro de `index.html`; su fórmula debe mantenerse sincronizada con el motor Python.

| Archivo o carpeta | Responsabilidad |
|---|---|
| [`wss_engine.py`](wss_engine.py) | Parser de `netsh`, normalización, observaciones y puntuación |
| [`recommendation_engine.py`](recommendation_engine.py) | Reglas y acciones priorizadas por perfil |
| [`app.py`](app.py) | Ventana nativa, API Python/JavaScript, agrupamiento y exportaciones |
| [`index.html`](index.html) | Interfaz de demostración y evaluación de redes |
| [`requirements.txt`](requirements.txt) | Dependencias de ejecución |
| [`requirements-dev.txt`](requirements-dev.txt) | Dependencias de pruebas |
| [`tests/`](tests/) | Pruebas automatizadas y archivos de entrada de referencia |
| `SPRINT_01_RESULTADOS.md` a `SPRINT_04_RESULTADOS.md` | Bitácoras de etapas previas; documentación histórica |

`WssApi` expone, entre otros, `scan_networks()`, `scan_networks_demo()`, `import_txt_file()`, `get_platform_info()`, `update_recommendation_profile()`, `export_json()` y `export_pdf()` mediante `window.pywebview.api`.

## Verificación y estado de la validación académica

Para ejecutar las pruebas sin abrir la interfaz ni escanear redes:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

La suite cubre parser, normalización, valores desconocidos, infraestructura, agrupamiento, recomendaciones, exportaciones JSON/PDF, anonimización y codificación de texto. Superarla verifica el comportamiento codificado; no demuestra por sí solo correspondencia con la fórmula final de la tesis.

En la revisión del 5 de octubre de 2026, la suite de `0d1bc90` ejecutada en Windows con Python 3.12.14, pytest 9.1.1 y fpdf2 2.8.9 produjo **76 pruebas aprobadas y 13 fallidas, de 89 en total**. Los fallos se produjeron en generación de PDF con `FPDFException: Not enough horizontal space to render a single character`. La interfaz gráfica y el ejecutable no se verificaron. Este resultado no reproduce las 99 pruebas aprobadas de la versión citada en la tesis y requiere revisión de compatibilidad y maquetación del reporte.

| Evidencia | Estado según el documento de tesis revisado |
|---|---|
| Pruebas de `sprint-05-wss-v2-au-en` | Se informan 99 pruebas aprobadas; requieren vinculación con el código y registro de ejecución de esa versión |
| Escenarios físicos WPA3/CCMP, WPA2/CCMP, WPA/TKIP y red abierta | Evidencias finales de configuración, capturas y reportes pendientes de incorporación documental |
| WEP | Caso teórico; no se afirma prueba física |
| Doble banda | Prueba funcional de agrupamiento; evidencia final prevista en anexos |
| Sensibilidad de ponderaciones | Procedimiento 40/60, 50/50 y 60/40 definido; resultados no presentados |
| Aplicación organizacional | Pendiente de incorporación documental final con autorización y evidencia |
| Comprensión y utilidad PRE/POST | Aplicación, procesamiento y resultados pendientes |

El componente con usuarios prevé invitar a **10 colaboradores**, con participación voluntaria y respuestas vinculadas mediante códigos **P01-P10**, sin solicitar nombres ni correos. Se trata de datos codificados o seudonimizados, no de anonimato absoluto.

El análisis previsto utiliza frecuencias, porcentajes, distribución de respuestas y, para escalas ordinales, mediana cuando corresponda. La comparación PRE/POST describe mejora, estabilidad o disminución por participante y compara respuestas correctas en una pregunta objetiva. No se construye un puntaje global de comprensión como escala validada. El diseño no tiene grupo control y no permite afirmar causalidad ni generalizar estadísticamente a otras organizaciones.

Las pruebas del software, los valores matemáticos esperados y las mediciones con participantes son evidencias diferentes. No deben publicarse porcentajes de mejora ni conclusiones de utilidad hasta disponer de datos reales.

## Empaquetado para Windows

Para generar un ejecutable con PyInstaller desde PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install pyinstaller
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --onefile --windowed --add-data "index.html;." --name "WSS-Framework" app.py
```

El resultado se genera en `dist/WSS-Framework.exe`. Debe comprobarse su arranque, carga de `index.html` y exportaciones en el equipo de destino; este procedimiento no implica que exista una distribución binaria publicada o validada.

## Referencia académica

Este README toma como referencia el documento de tesis de Cabrera Oviedo y Ferreira Cardozo, con fecha de portada febrero de 2026: objetivos y alcance en el capítulo I; definición del modelo en el capítulo II; normalización, evolución, fórmula, sensibilidad y validación en las secciones 4.5 a 4.15; estado de los resultados en las secciones 5.1 a 5.10; conclusiones y evidencias pendientes en los capítulos finales y anexos.

La coherencia documental exige distinguir severidad técnica de riesgo organizacional, modelo final de implementación publicada y resultados verificados de validaciones pendientes.
