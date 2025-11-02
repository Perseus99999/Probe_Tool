# filter_urls.py

import sys
import argparse
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def ensure_scheme(u: str) -> str | None:
    if not u:
        return None
    u = u.strip()
    if not u:
        return None
    if not u.startswith(("http://", "https://")):
        u = "http://" + u
    return u

def build_session(ua: str, retries: int, backoff: float) -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": ua})
    retry = Retry(
        total=retries,
        backoff_factor=backoff,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods={"HEAD", "GET"},
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=100, pool_maxsize=100)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s

def probe(url: str, session: requests.Session, timeout: float, method: str):
    try:
        if method in ("HEAD", "AUTO"):
            r = session.head(url, timeout=timeout, allow_redirects=True)
            if method == "AUTO" and r.status_code in (405, 403):  # HEAD blocked
                r = session.get(url, timeout=timeout, stream=True, allow_redirects=True)
        else:  # GET
            r = session.get(url, timeout=timeout, stream=True, allow_redirects=True)
        ok = 200 <= r.status_code < 400
        return url, ok, r.status_code
    except requests.RequestException:
        return url, False, None

def main():
    p = argparse.ArgumentParser(description="Filter a stream of URLs into good/bad lists.")
    p.add_argument("-o", "--out", default="filtered_urls.txt", help="Output file for good URLs.")
    p.add_argument("--bad-out", default=None, help="Optional file for bad URLs.")
    p.add_argument("-w", "--workers", type=int, default=24, help="Concurrency (threads).")
    p.add_argument("--timeout", type=float, default=8.0, help="Request timeout (seconds).")
    p.add_argument("--method", choices=["AUTO", "HEAD", "GET"], default="AUTO",
                   help="Probe method. AUTO = HEAD with GET fallback.")
    p.add_argument("--ua", default="URLFilter/1.0 (+https://github.com/yourname/keyword-spider)",
                   help="User-Agent header.")
    p.add_argument("--retries", type=int, default=2, help="Retry count for 429/5xx.")
    p.add_argument("--backoff", type=float, default=0.3, help="Backoff factor for retries.")
    args = p.parse_args()

    raw = sys.stdin.read().splitlines()

    # normalize + dedupe
    urls = []
    seen = set()
    for line in raw:
        u = ensure_scheme(line)
        if u and u not in seen:
            seen.add(u)
            urls.append(u)

    session = build_session(args.ua, args.retries, args.backoff)

    good, bad = [], []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(probe, u, session, args.timeout, args.method) for u in urls]
        for fut in as_completed(futs):
            url, ok, status = fut.result()
            (good if ok else bad).append(url)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(good))
    if args.bad_out:
        with open(args.bad_out, "w", encoding="utf-8") as f:
            f.write("\n".join(bad))

    print(f"Checked {len(urls)} URLs → {len(good)} good, {len(bad)} bad")
    print(f"Saved good URLs to {args.out}" + (f"; bad URLs to {args.bad_out}" if args.bad_out else ""))

if __name__ == "__main__":
    main()
