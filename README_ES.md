<h1 align="center">Limsy</h1>
<p align="center">
  🇺🇸 <a href="README.md">English</a> |
  🇪🇸 <a href="README_ES.md"><b>Español</b></a>
</p>
<p align="center">
  <img width="460" height="94" alt="image" src="https://github.com/user-attachments/assets/46959962-be02-426c-bd5f-9ae972fcf29f" />
</p>
<p align="center">
  <b>Analizador ligero de rate-limit HTTP</b><br>
  Herramienta de prueba simple, asíncrona y no intrusiva
</p>

---

## ✨ ¿Qué es Limsy?

**Limsy** es una pequeña herramienta de línea de comandos diseñada para **analizar el comportamiento de rate-limiting HTTP** de servicios web y APIs.

Envía solicitudes a ritmos controlados y observa cómo responde el servidor, ayudando a desarrolladores y administradores a entender:

* Cuándo se activan los límites de tasa
* Cómo reaccionan los servidores ante un aumento progresivo de solicitudes
* Si ocurre bloqueo, throttling o redirección

Limsy **no** es una herramienta de stress-testing ni de DoS.
Su enfoque es el análisis, el diagnóstico y la comprensión de la infraestructura.

---

## 🧠 Características clave

* Solicitudes asíncronas usando `asyncio` y `aiohttp`
* Etapas graduales de solicitudes con control de tasa (sin ráfagas)
* Detección inteligente de:

  * HTTP 429 (Too Many Requests)
  * Respuestas de bloqueo (403, 5xx)
  * Redirecciones fuera del objetivo
* Detención automática cuando se detecta un bloqueo fuerte
* Salida por consola legible para humanos
* Cierre seguro con `Ctrl+C`

---

## ⚠️ Descargo de responsabilidad

Limsy está destinado **únicamente** a:

* Probar servicios que te pertenecen
* Sistemas que estás autorizado a analizar
* Fines educativos y de diagnóstico

**No** utilices esta herramienta contra sistemas sin permiso explícito.

Eres responsable del uso que le des.

---

## 📦 Instalación

Clona el repositorio:

```bash
git clone https://github.com/urdev4ever/limsy.git
cd limsy
```

Instala las dependencias:

```bash
pip install aiohttp colorama
```

---

## 🚀 Uso

Uso básico:

```bash
python limsy.py -u https://example.com
```

Con concurrencia personalizada:

```bash
python limsy.py -u https://example.com -c 30
```

Modo silencioso (sin prompts interactivos):

```bash
python limsy.py -u https://example.com -q
```

---

## 🧪 Cómo funciona

Limsy ejecuta múltiples etapas de solicitudes con un aumento progresivo de requests-per-second (RPS).

En cada etapa:

1. Envía solicitudes HTTP controladas

.<img width="493" height="439" alt="image" src="https://github.com/user-attachments/assets/5718df70-4cbd-4385-a307-ee9d5faf8ffa" />

.<img width="490" height="314" alt="image" src="https://github.com/user-attachments/assets/26710a91-e6b1-4b6c-b14c-00889de0498c" />

3. Recopila códigos de estado
4. Detecta señales de throttling o bloqueo
5. Se detiene automáticamente si se detectan límites fuertes
6. Genera un **resumen de análisis**

<img width="493" height="500" alt="image" src="https://github.com/user-attachments/assets/d35f864d-71e6-4d7c-b0d1-8164f5e5c833" />

> Por defecto, Limsy utiliza solicitudes **HEAD** para minimizar el uso de ancho de banda.

---

## 🛠️ Opciones de línea de comandos

* `-u, --url` — URL objetivo (requerida)
* `-c, --concurrency` — Máximo de solicitudes concurrentes (por defecto: 20)
* `-q, --quiet` — Desactiva los prompts interactivos

---

## 🧩 Casos de uso

* Descubrimiento de rate-limits en APIs
* Diagnóstico de infraestructura
* Análisis del comportamiento de balanceadores de carga
* Experimentos educativos con límites HTTP
* Pruebas en entornos de CI / staging

---

## ⭐ Nota final

Limsy es intencionalmente simple, legible y ética.
Si necesitas pruebas de carga agresivas, utiliza herramientas dedicadas.
Si buscas **claridad**, **control** y **comprensión** — Limsy es para vos.

---

Hecho con <3 por URDev.
