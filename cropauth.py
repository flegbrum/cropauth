"""Tiny client for the cropauth API: German (BVL) and French (Anses E-Phy) plant protection
product authorisations, with a row-level change feed. Standard library only, Python 3.8+.

    from cropauth import Client
    c = Client()
    c.search("glyphosate", type="substance", country="de")
    for ch in c.changes(country="fr", since="2026-11-18"):
        print(ch["first_seen"], ch["op"], ch["product"], ch["changed_columns"])

Not legal advice. The official registers and the product label are what count.
"""
import json
import time
import urllib.parse
import urllib.request

__version__ = "0.1.0"
BASE_URL = "https://cropauth-api.axolo6.workers.dev"


class CropauthError(Exception):
    def __init__(self, status, body):
        super().__init__(f"HTTP {status}: {body[:200]}")
        self.status, self.body = status, body


class Client:
    def __init__(self, base_url=BASE_URL, timeout=30, user_agent=f"cropauth-py/{__version__}", retries=3):
        self.base_url, self.timeout, self.user_agent, self.retries = base_url.rstrip("/"), timeout, user_agent, retries

    def get(self, path, **params):
        """GET a path (or a 'next' link) and return parsed JSON. Waits and retries on 429 (60 requests/min/IP)."""
        q = {k: v for k, v in params.items() if v is not None}
        url = self.base_url + path + ("&" if "?" in path else "?") * bool(q) + urllib.parse.urlencode(q)
        for attempt in range(self.retries + 1):
            req = urllib.request.Request(url, headers={"user-agent": self.user_agent, "accept": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    return json.load(r)
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", "replace")
                if e.code == 429 and attempt < self.retries:
                    time.sleep(int(e.headers.get("retry-after") or 60))
                    continue
                raise CropauthError(e.code, body) from None

    def search(self, q, type=None, country=None, limit=None):
        """type: product | substance | crop; country: de | fr."""
        return self.get("/v1/search", q=q, type=type, country=country, limit=limit)

    def product(self, country, id):
        return self.get(f"/v1/products/{country}/{urllib.parse.quote(str(id), safe='')}")

    def substance(self, country, id):
        return self.get(f"/v1/substances/{country}/{urllib.parse.quote(str(id), safe='')}")

    def crop(self, country, id):
        return self.get(f"/v1/crops/{country}/{urllib.parse.quote(str(id), safe='')}")

    def changes(self, country=None, since=None, product=None, entity=None, table=None, op=None, limit=200):
        """Yield every change item, following 'next' links. since: YYYY-MM-DD (first_seen date)."""
        page = self.get("/v1/changes", country=country, since=since, product=product, entity=entity,
                        table=table, op=op, limit=limit)
        while True:
            yield from page.get("items", [])
            if not page.get("next"):
                return
            page = self.get(page["next"])

    def snapshots(self):
        return self.get("/v1/snapshots")["snapshots"]

    def status(self):
        return self.get("/v1/status")


if __name__ == "__main__":
    import sys
    c = Client()
    print(json.dumps(c.search(" ".join(sys.argv[1:]) or "glyphosate"), indent=2, ensure_ascii=False))
