<h1 align="center">Limsy</h1>
<p align="center">
  🇺🇸 <b>English</b> |
  🇪🇸 <a href="README_ES.md">Español</a>
</p>
<p align="center">
  <img width="460" height="94" alt="image" src="https://github.com/user-attachments/assets/46959962-be02-426c-bd5f-9ae972fcf29f" />
</p>
<p align="center">
  <b>Lightweight HTTP rate-limit analyzer</b><br>
  Simple, async, and non-intrusive testing tool
</p>

---

## ✨ What is Limsy?

**Limsy** is a small command-line tool designed to **analyze HTTP rate-limiting behavior** of web services and APIs.

It sends requests at controlled rates and observes how the server responds, helping developers and administrators understand:

* When rate limits are triggered
* How servers react under increasing request pressure
* Whether blocking, throttling, or redirection occurs

Limsy is **not** a stress-testing or DoS tool.
Its focus is analysis, diagnostics, and infrastructure understanding.

---

## 🧠 Key Features

* Asynchronous requests using `asyncio` and `aiohttp`
* Gradual, rate-controlled request stages (no bursts)
* Intelligent detection of:

  * HTTP 429 (Too Many Requests)
  * Blocking responses (403, 5xx)
  * Redirection away from the target
* Automatic stop when strong blocking is detected
* Human-readable console output
* Graceful shutdown on `Ctrl+C`

---

## ⚠️ Disclaimer

Limsy is intended **only** for:

* Testing services you own
* Systems you are authorized to analyze
* Educational and diagnostic purposes

Do **not** use this tool against systems without explicit permission.

You are responsible for how you use it.

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/urdev4ever/limsy.git
cd limsy
```

Install dependencies:

```bash
pip install aiohttp colorama
```

---

## 🚀 Usage

Basic usage:

```bash
python limsy.py -u https://example.com
```

With custom concurrency:

```bash
python limsy.py -u https://example.com -c 30
```

Quiet mode (no interactive prompts):

```bash
python limsy.py -u https://example.com -q
```
---

## 🧪 How It Works

Limsy runs multiple request stages with increasing requests-per-second (RPS).

At each stage, it:

1. Sends controlled HTTP requests

.<img width="493" height="439" alt="image" src="https://github.com/user-attachments/assets/5718df70-4cbd-4385-a307-ee9d5faf8ffa" />

.<img width="490" height="314" alt="image" src="https://github.com/user-attachments/assets/26710a91-e6b1-4b6c-b14c-00889de0498c" />

   
3. Collects status codes
4. Detects signs of throttling or blocking
5. Stops automatically if strong limits are detected
6. Generates **analysis summary**

<img width="493" height="500" alt="image" src="https://github.com/user-attachments/assets/d35f864d-71e6-4d7c-b0d1-8164f5e5c833" />


> By default, Limsy uses **HEAD requests** to minimize bandwidth usage.

---

## 🛠️ Command-line Options

* `-u, --url` — Target URL (required)
* `-c, --concurrency` — Max concurrent requests (default: 20)
* `-q, --quiet` — Disable interactive prompts

---

## 🧩 Use Cases

* API rate-limit discovery
* Infrastructure diagnostics
* Load-balancer behavior analysis
* Educational experiments with HTTP limits
* CI / staging environment testing

---

## ⭐ Contributing

Pull requests are welcome if they:

* Improve rate-detection logic, response classification accuracy, or stage analysis clarity
* Enhance async performance, concurrency stability, or graceful shutdown behavior without increasing aggressiveness
* Preserve the controlled, non-intrusive philosophy (no traffic bursts, no stress-testing patterns, no DoS-style behavior)

---

## 📝 Final Note

Limsy is intentionally simple, readable, and ethical.
If you need aggressive load testing, use dedicated tools.
If you want **clarity**, **control**, and **understanding** — Limsy is for you.

---
Made with <3 by URDev.
