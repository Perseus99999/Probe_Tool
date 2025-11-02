# 🚦 URL Filter (Probe)

<div align="center">

**A speedy URL probe** — read URLs from **STDIN**, check them concurrently with retry/backoff, and write **good** and **bad** lists to files.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python\&logoColor=white)](#-requirements)
[![Requests](https://img.shields.io/badge/HTTP-requests-000000.svg)](https://docs.python-requests.org/)
[![urllib3 Retry](https://img.shields.io/badge/Retry-urllib3-success.svg)](https://urllib3.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](#-license)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#-contributing)

</div>

> Zero-fuss link checker for lists of URLs. Pipes in, probes fast, files out. Designed for CI and quick audits.

---

## ✨ Features

* **Concurrency** — multithreaded probing for speed.
* **Retries & backoff** — resilient against 429/5xx blips.
* **HEAD→GET fallback** — if servers block HEAD, it auto-tries GET (streamed).
* **Redirects handled** — follows redirects to determine health.
* **Timeouts & UA** — avoids hangs and sets a browser-like User-Agent.
* **Normalize & de-dupe** — adds `http://` to bare domains and removes duplicates.
* **Clean outputs** — writes `good` and `bad` URL lists.

---

## 📚 Table of Contents

* [Requirements](#-requirements)
* [Installation](#-installation)
* [Quickstart](#-quickstart)
* [Usage](#-usage)
* [CLI Options](#-cli-options)
* [Examples](#-examples)
* [Troubleshooting](#-troubleshooting)
* [Limitations](#-limitations)
* [Contributing](#-contributing)
* [License](#-license)

---

## 🔧 Requirements

* **Python**: 3.10+
* **Packages**: `requests`, `urllib3`

Install deps:

```bash
pip install -U requests urllib3
```

---

## 📦 Installation

Save the script as **`filter_urls.py`** in your repo (or `scripts/`).

---

## 🚀 Quickstart

### Create a small test set

**PowerShell:**

```powershell
@'
example.com
https://example.com/nosuchpage
https://httpbin.org/status/200
https://httpbin.org/redirect/1
https://httpbin.org/status/404
https://httpbin.org/status/500
neverssl.com
http://127.0.0.1:1
'@ | Set-Content test_urls.txt
```

**bash:**

```bash
cat > test_urls.txt <<'EOF'
example.com
https://example.com/nosuchpage
https://httpbin.org/status/200
https://httpbin.org/redirect/1
https://httpbin.org/status/404
https://httpbin.org/status/500
neverssl.com
http://127.0.0.1:1
EOF
```

### Run the probe

```powershell
Get-Content .\test_urls.txt | python .\filter_urls.py -o good.txt --bad-out bad.txt -w 16 --method AUTO --timeout 8
```

```bash
cat test_urls.txt | python filter_urls.py -o good.txt --bad-out bad.txt -w 16 --method AUTO --timeout 8
```

Expected output (counts may vary slightly by region/network):

```
Checked 8 URLs → 4 good, 4 bad
Saved good URLs to good.txt; bad URLs to bad.txt
```

---

## 🧰 Usage

The tool reads **one URL per line from STDIN** and writes:

* `--out` (default `filtered_urls.txt`) → **good URLs** (HTTP 2xx/3xx)
* `--bad-out` (optional) → **bad URLs** (HTTP 4xx/5xx, connection errors)

Basic pipeline:

```bash
cat urls.txt | python filter_urls.py -o good.txt --bad-out bad.txt
```

---

## ⚙️ CLI Options

| Flag              |                 Default | Description                                            |
| ----------------- | ----------------------: | ------------------------------------------------------ |
| `-o`, `--out`     |     `filtered_urls.txt` | Output file for **good** URLs                          |
| `--bad-out`       |                *(none)* | Optional file for **bad** URLs                         |
| `-w`, `--workers` |                    `24` | Number of threads                                      |
| `--timeout`       |                   `8.0` | Per-request timeout (seconds)                          |
| `--method`        |                  `AUTO` | `AUTO` = HEAD with GET fallback; or force `HEAD`/`GET` |
| `--ua`            | `"URLFilter/1.0 (...)"` | User-Agent header                                      |
| `--retries`       |                     `2` | Retry count for 429/5xx                                |
| `--backoff`       |                   `0.3` | Backoff factor between retries                         |

---

## 🧪 Examples

**Force GET only** (sometimes friendlier than HEAD):

```bash
cat urls.txt | python filter_urls.py --method GET -o good.txt --bad-out bad.txt
```

**Bigger lists with more threads:**

```bash
cat big_urls.txt | python filter_urls.py -w 64 -o good.txt --bad-out bad.txt
```

**CI usage** (fail build if any bad links):

```bash
cat urls.txt | python filter_urls.py --bad-out bad.txt \
&& test ! -s bad.txt
```

> [!TIP]
> Use `sort`/`uniq` before piping to reduce duplicates:
> `sort urls.txt | uniq | python filter_urls.py ...`

---

## 🩺 Troubleshooting

> [!NOTE]
> **“Nothing happens / hangs”** — bump `--timeout`, confirm internet proxy rules, or try `--method GET`.

> [!TIP]
> **Many `bad` results** — some sites block HEAD or bots. Use `--method GET` and customize `--ua`.

> [!WARNING]
> **Windows PowerShell pipeline quirks** — prefer `Get-Content urls.txt | python filter_urls.py ...` over `type`.

---

## 📌 Limitations

* Only reports **URL reachability** (2xx/3xx vs everything else). It does **not** validate page content.
* No `robots.txt` checks (this tool is a checker, not a crawler).
* No rate limit flag; use OS-level throttling if needed or reduce `-w`.

---

## 🤝 Contributing

Batteries welcome: CSV/JSON stats output, rate limiting, domain scoping, richer status reporting. Please keep the CLI stable and add tests for new behaviors.

---

## 📄 License

Released under the **MIT License**. See `LICENSE` for details.
