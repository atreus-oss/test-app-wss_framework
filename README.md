# WSS Framework — App de Escritorio

Aplicación de escritorio para Windows que evalúa, de forma **pasiva** (sin ataques, sin interceptar tráfico), qué tan expuesta está una red Wi-Fi según los parámetros que su propio punto de acceso ya transmite públicamente. Es la implementación práctica del modelo **WSS (Wireless Security Score)** desarrollado en la tesis *"Sistema automatizado de evaluación de seguridad Wi-Fi con validación experimental controlada"*.

---

## 🟢 Para perfiles no técnicos: ¿Qué hace esta app?

Pensala como un **chequeo de salud para tu red Wi-Fi**, parecido al de un mecánico que revisa el auto sin desarmarlo: la app "escucha" lo que tu punto de acceso ya está anunciando al aire (nombre de la red, tipo de protección, señal) y te dice, en palabras simples, qué tan bien o mal protegida está.

**Lo que la app hace:**
-  Revisa las redes Wi-Fi visibles desde tu computadora.
-  Te dice, con un semáforo de colores, si cada red está bien protegida o necesita atención.
-  Te explica **por qué** con una frase entendible, no con jerga técnica.
-  Te sugiere una acción concreta ("qué hacer"), ajustada a si sos quien administra la red o solo querés conectarte.
-  Te arma un reporte en PDF que podés guardar y compartir con quien resuelva temas técnicos en tu organización.

**Lo que la app NO hace (y es importante saberlo):**
-  No "hackea" ni ataca ninguna red — solo mira información pública que cualquier dispositivo cercano ya puede ver.
-  No confirma que exista un ataque en curso — si algo se ve raro, te avisa que conviene revisarlo, no te dice "te están atacando".
-  No es un reemplazo de una auditoría de seguridad completa hecha por un profesional.

### Cómo usarla en 3 pasos

1. Abrí la aplicación (doble clic en `WSS-Framework.exe`, o ver instalación más abajo si tenés Python).
2. Andá a la pestaña **"Mis Redes"** y presioná **Escanear**.
3. Mirá el color de cada tarjeta: 🟢 verde está bien, 🟡 amarillo puede mejorar, 🟠 naranja necesita atención, 🔴 rojo requiere acción inmediata. Tocá **"Ver detalles técnicos"** solo si querés profundizar.

Si querés guardar el resultado, el botón **"Exportar PDF"** te deja elegir dónde guardarlo, con un nombre y fecha automáticos.

---

## 🔧 Para perfiles técnicos: ¿Qué es y cómo está construido?

### Componentes

La app combina dos experiencias en una sola ventana nativa (`pywebview`):

- **Calculadora Demo**: la misma calculadora interactiva de la landing comercial del proyecto, con escenarios de ejemplo (E1–E5, E-AN) para explicar el modelo WSS sin necesidad de hardware real.
- **Mis Redes**: escaneo real de las redes Wi-Fi visibles desde el equipo (`netsh wlan show networks` en Windows), con el modelo WSS aplicado a cada red detectada, más un motor de recomendaciones que traduce cada resultado a una vista sencilla y a acciones priorizadas.

### Arquitectura y flujo de datos

El proyecto separa estrictamente el cálculo técnico de la interpretación para el usuario:

```
netsh (Windows)  o  archivo .txt importado
        │
        ▼
┌──────────────────────┐
│   wss_engine.py      │  Parsea, normaliza y calcula el modelo WSS
│                      │  (AU, EN, EX, AN, BM → score → clasificación)
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ recommendation_      │  Traduce cada resultado normalizado a
│ engine.py            │  estado sencillo, hallazgo, acción priorizada
│                      │  y buenas prácticas (según perfil de usuario)
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│   app.py             │  Orquesta: agrupa redes lógicas (por SSID),
│   (clase WssApi)     │  anonimiza si se pide, genera JSON/PDF,
│                      │  expone todo a JavaScript vía pywebview
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│   index.html         │  Renderiza vista sencilla + drawer técnico
│                      │  con pestañas (Resumen / Parámetros / Radios /
│                      │  Trazabilidad avanzada)
└──────────────────────┘
```

`recommendation_engine.py` **nunca modifica** la fórmula WSS, los pesos ni los umbrales de clasificación definidos en la tesis — solo consume el resultado ya calculado y lo traduce.

### Estados de evaluación (por qué un resultado puede no tener score)

No todo lo que observa `netsh` es interpretable con certeza. El motor distingue:

| Estado | Significado |
|---|---|
| `COMPLETE` | Autenticación y cifrado se reconocieron sin ambigüedad; hay `wss_score` numérico. |
| `INCOMPLETE` | Se observó un valor no reconocido (`UNKNOWN`); `wss_score = null` y `classification = "NO_EVALUABLE"`. No se inventa un puntaje. |

### Estados de observación de infraestructura (por qué el AN no salta con cualquier BSSID extra)

Un mismo SSID con varios BSSID **no es automáticamente una anomalía** — es el comportamiento normal de routers dual-band, redes mesh o repetidores. El motor distingue explícitamente:

| Estado | Cuándo aparece | ¿Afecta el score? |
|---|---|---|
| `SINGLE_BSSID` | Un solo punto de acceso observado para ese SSID. | — |
| `MULTI_RADIO_OBSERVED` | Mismo SSID en varias bandas (ej. 2,4 GHz y 5 GHz). | No, `AN=0`. |
| `MULTI_AP_OBSERVED` | Varios puntos de acceso con el mismo perfil de seguridad. | No, `AN=0`. |
| `SECURITY_PROFILE_MISMATCH` | Mismo SSID con perfiles de seguridad distintos entre BSSID. | No, `AN=0`; se marca como "requiere verificación técnica", sin afirmar ataque. |
| `HIDDEN_SSID` | SSID oculto observado individualmente; se numeran de forma estable (`SSID oculto 1`, `SSID oculto 2`...). | — |

`AN=1` (condición anómala confirmada) queda reservado para cuando exista una línea base autorizada de comparación — no se dispara solo por heurística de BSSID múltiple.

### Motor de recomendaciones

Siete reglas trazables, cada una con código y versión:

| Regla | Condición | Estado sencillo |
|---|---|---|
| `REC-01` | WPA3-Personal con CCMP | Configuración adecuada |
| `REC-02` | WPA2-Personal con CCMP/AES | Configuración adecuada |
| `REC-03` | WPA/WPA2 con TKIP | Requiere atención |
| `REC-04` | WEP | Protección insuficiente |
| `REC-05` | Red abierta / sin cifrado | Protección insuficiente |
| `REC-06` | Valores no reconocidos / evaluación incompleta | No se pudo completar la evaluación |
| `REC-07` | Perfiles de seguridad distintos bajo el mismo SSID | Requiere verificación técnica |

El estado sencillo, el color y la severidad usan un **único mapeo central** (`CLASSIFICATION_RANK` / `CLASSIFICATION_PRESENTATION`) para que clasificación técnica, texto y color nunca se contradigan entre sí.

Además, cada resultado genera **acciones priorizadas cualitativamente** (sin puntajes de costo-beneficio inventados) según el perfil de quien consulta:

- `NETWORK_OWNER` — propietario/responsable de la red: acción principal, alternativa inmediata, solución definitiva y buenas prácticas.
- `NETWORK_USER` — solo quiere conectarse: recomendaciones prudentes (evitar operaciones sensibles, preferir otra red, usar una VPN confiable solo si no hay alternativa).
- `GENERAL` — perfil por defecto cuando no se especifica relación con la red.

La app nunca afirma seguridad garantizada, ataque confirmado, "Evil Twin" confirmado, ni usa relaciones no verificadas tipo 80/20.

### Exportación de reportes (JSON y PDF)

Ambos formatos se generan desde `WssApi.last_results` / `last_metadata` — es decir, desde lo último efectivamente evaluado en Python, nunca desde datos que pudieran modificarse en el navegador embebido.

- **Guardado nativo**: usa el diálogo `Guardar como` de Windows (no escribe directamente en la carpeta del proyecto). Carpeta inicial: `Descargas` → `Documentos` → carpeta personal, en ese orden de preferencia.
- **Nombre sugerido automático**: `WSS_Reporte_<AAAA-MM-DD>_<HHMMSS>.pdf` (o `.json`), con sufijo `_anon` si se anonimiza.
- **Anonimización opcional**: reemplaza SSID por `SSID-001`, `SSID-002`... y BSSID por `BSSID-001`, `BSSID-002`..., de forma consistente dentro del mismo reporte. Los identificadores de SSID oculto (`SSID oculto N`) se preservan tal cual, ya que funcionan como etiqueta técnica, no como dato identificable.
- **Agrupación lógica en el PDF**: una red dual-band o con varios puntos de acceso aparece como **una sola ficha**, no una por cada BSSID — evita duplicar visualmente lo que es la misma red.
- **Texto de alcance obligatorio** en cada reporte: *"Este reporte corresponde a una evaluación de parámetros Wi-Fi observables y no constituye una auditoría integral de ciberseguridad."*

---

## Requisitos

- Windows 10/11 (el escaneo real solo funciona en Windows; en otros sistemas operativos la pestaña "Mis Redes" ofrece datos de ejemplo para poder probar la interfaz).
- Python 3.9 o superior.

## Instalación

```bash
pip install -r requirements.txt
```

Dependencias principales (`requirements.txt`): `pywebview>=4.4` (ventana nativa) y `fpdf2>=2.7` (generación de PDF).

## Ejecución

```bash
python app.py
```

Se abre una ventana nativa con la aplicación. La pestaña "Calculadora Demo" está disponible siempre; la pestaña "Mis Redes" detecta automáticamente si el escaneo real está disponible en este sistema (`get_platform_info()`).

## Estructura del repositorio

```
test-app-wss_framework/
├── app.py                      ← punto de entrada: ventana pywebview, clase WssApi,
│                                   agrupación lógica, anonimización, exportación JSON/PDF
├── wss_engine.py                ← parser de netsh + cálculo del modelo WSS (AU/EN/EX/AN/BM)
├── recommendation_engine.py     ← motor de recomendaciones (reglas REC-01 a REC-07,
│                                   acciones priorizadas por perfil de usuario)
├── index.html                   ← interfaz completa (landing demo + vista "Mis Redes")
├── requirements.txt              ← dependencias de producción
├── requirements-dev.txt          ← dependencias de desarrollo (pytest)
├── tests/
│   ├── test_wss_engine.py
│   ├── test_app_io.py
│   ├── test_recommendation_engine.py
│   ├── test_encoding_guard.py            ← evita regresiones de codificación (mojibake)
│   ├── test_sprint_04_prioritization_pdf.py
│   └── fixtures/netsh/                    ← capturas anonimizadas reales + casos sintéticos
├── SPRINT_01_RESULTADOS.md      ← corrección del parser + pruebas automatizadas
├── SPRINT_02_RESULTADOS.md      ← trazabilidad de origen + corrección de falsos positivos AN
├── SPRINT_03_RESULTADOS.md      ← vista sencilla/técnica + motor de recomendaciones
└── SPRINT_04_RESULTADOS.md      ← priorización por perfil + exportación PDF profesional
```

Cada `SPRINT_0X_RESULTADOS.md` documenta, con evidencia real (comandos ejecutados, resultados de `pytest`, casos de prueba), qué cambió, por qué, y qué quedó explícitamente fuera de alcance en esa etapa — útil como bitácora de desarrollo trazable para el anexo metodológico de la tesis.

## Cómo se conecta Python con la interfaz

`app.py` crea una ventana con `pywebview` y expone una clase `WssApi` al JavaScript de `index.html` a través de `window.pywebview.api`. Métodos principales disponibles desde el frontend:

| Método | Qué hace |
|---|---|
| `scan_networks()` | Ejecuta el escaneo real (`netsh`) y devuelve resultados con WSS calculado y recomendaciones aplicadas. |
| `scan_networks_demo()` | Devuelve datos sintéticos de demostración (`synthetic_data: true`), útil en sistemas no-Windows. |
| `import_txt_file(selected_path=None)` | Abre el diálogo nativo de selección de archivo (o usa una ruta dada) y evalúa un `.txt` de `netsh` previamente exportado. |
| `get_platform_info()` | Informa si el escaneo real está disponible en este sistema. |
| `update_recommendation_profile(target_user)` | Recalcula las recomendaciones de los últimos resultados según el perfil elegido (`NETWORK_OWNER` / `NETWORK_USER` / `GENERAL`), sin volver a escanear. |
| `export_json(anonymize=False, selected_path=None)` | Genera el reporte JSON 2.0 desde los últimos resultados y lo guarda vía diálogo nativo. |
| `export_pdf(anonymize=False, organization=None, selected_path=None)` | Genera el reporte PDF profesional (redes agrupadas lógicamente) y lo guarda vía diálogo nativo. |
| `open_exported_file(saved_path)` | Abre el archivo exportado con la aplicación predeterminada de Windows. |
| `show_exported_file_in_folder(saved_path)` | Abre el Explorador de Windows y selecciona el archivo exportado. |

Toda la lógica de parseo de `netsh` y el cálculo del modelo WSS vive en `wss_engine.py`, independiente de la interfaz y probable por separado:

```bash
python wss_engine.py
```

## Pruebas automatizadas

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

La suite cubre parsing multilenguaje (español/inglés, con y sin tilde), estados incompletos, agrupación de redes lógicas, las 7 reglas de recomendación, priorización por perfil, generación de JSON/PDF (incluida su versión anonimizada) y una prueba preventiva de codificación (`test_encoding_guard.py`) que falla si se reintroduce texto corrupto en `index.html`, `app.py` o `wss_engine.py`.

## Empaquetado como ejecutable (.exe)

Para distribuir la app sin que el cliente necesite instalar Python, usar PyInstaller en una máquina Windows:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed ^
  --add-data "index.html;." ^
  --name "WSS-Framework" ^
  app.py
```

El ejecutable resultante queda en `dist/WSS-Framework.exe`.

## Alcance y limitaciones

- **El escaneo es pasivo**: solo lee parámetros que los puntos de acceso ya transmiten públicamente (SSID, BSSID, autenticación, cifrado, intensidad de señal, canal, banda). No ejecuta pruebas activas, no fuerza autenticaciones ni intercepta tráfico, en línea con el alcance definido en la tesis.
- **La detección de condición anómala es heurística y preliminar**: cuando el sistema encuentra algo que amerita revisión (por ejemplo, perfiles de seguridad distintos bajo el mismo SSID), lo señala como tal — nunca como un ataque confirmado o un "Evil Twin" detectado.
- **La intensidad de señal** que reporta `netsh` viene como porcentaje, no en dBm; se aplica una aproximación estándar para clasificar el factor de exposición, no una medición de precisión de laboratorio.
- **Este reporte no reemplaza una auditoría integral de ciberseguridad** — así lo indica explícitamente el texto de alcance incluido en cada JSON y PDF generado.
- El estado del modelo se marca como `PROVISIONAL` en cada exportación, reflejando que corresponde a un trabajo de tesis en curso, no a un producto certificado.