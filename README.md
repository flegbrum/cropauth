# cropauth

A free, read-only JSON API for the German and French plant protection product registers, with a dated change history.

- **Germany:** BVL PSM-API (products, uses/Anwendungen, crops, target organisms, pre-harvest intervals, distributors, parallel imports)
- **France:** Anses E-Phy weekly open data (products, uses with end-of-sale / end-of-use dates, conditions of use, parallel-trade permits)
- **Change feed:** every row added, removed or changed between two consecutive source releases, with the date it first appeared. Tracking started on 2026-11-17.

Base URL: **https://cropauth-api.axolo6.workers.dev** · docs (EN/DE/FR): same URL · OpenAPI: `/openapi.json`

No key and no sign-up. 60 requests per minute per IP. It's free, and there is no paid tier.

> **Not legal advice / keine Rechtsberatung / ceci n'est pas un conseil juridique.** This is an unofficial copy of public register data. Before you buy or apply a product, check the official register (BVL / E-Phy) and the label.

## Why

Both registers publish open data, but neither offers a simple "what changed this week" view. The French data is a weekly zip of CSVs, and the German data is a paginated API made of normalised code tables. If you maintain a product database, a farm app, or compliance checks, you usually end up writing your own differ. This project runs one every day and publishes the result.

## curl

```sh
# search products, active substances or crops (type=product|substance|crop, country=de|fr)
curl 'https://cropauth-api.axolo6.workers.dev/v1/search?q=glyphosate&type=substance&country=de'

# one German product: uses, crops, target organisms, pre-harvest intervals, distributors
curl 'https://cropauth-api.axolo6.workers.dev/v1/products/de/00A579-00'

# products usable on a crop (DE uses EPPO/BVL crop codes; FR uses the E-Phy crop label)
curl 'https://cropauth-api.axolo6.workers.dev/v1/crops/de/TRZSS'
curl 'https://cropauth-api.axolo6.workers.dev/v1/crops/fr/Bl%C3%A9'

# what changed in the French register since a date (follow "next" to page)
curl 'https://cropauth-api.axolo6.workers.dev/v1/changes?country=fr&since=2026-11-18&limit=50'

# every stored source snapshot, and freshness
curl 'https://cropauth-api.axolo6.workers.dev/v1/snapshots'
curl 'https://cropauth-api.axolo6.workers.dev/v1/status'
```

Each change item has the old and new source row and the list of changed columns. `first_seen` is the time the daily fetch first saw the new release. It is **not** the authority's decision date.

## Python

`cropauth.py` is one file and uses only the standard library:

```python
from cropauth import Client

c = Client()
hits = c.search("Weizen", type="crop", country="de")
wheat = c.crop("de", hits["results"][0]["id"])

for ch in c.changes(country="fr", since="2026-11-18"):
    print(ch["first_seen"], ch["op"], ch["product"], ch["changed_columns"])
```

The client waits and retries when it gets HTTP 429. See `examples/` for a weekly "what changed for my products" script.

## Sources and licences

Every record carries `source.url`, `source.stand` (the release date) and `source.line`. If you republish the data, keep `source.line`:

- DE: attribution as required by §3 of the BVL PSM-API terms of use (exact line in each record)
- FR: *Données E-Phy - Anses, mise à jour du [date]*, Licence Ouverte / Open Licence 2.0

This project is independent and not affiliated with BVL, Anses or data.gouv.fr.

## Limits and caveats

- The data is refreshed once a day, early morning UTC. The BVL release date is in `/v1/status`.
- The German PSM-API has no sell-off date (Abverkaufsfrist) field.
- There's a shared daily request budget. When it runs out, the API answers `503` until 00:00 UTC.
- Privacy: IP addresses are not logged. A salted, truncated daily hash is used for rate limiting and for counting clients per day, and it is deleted the next day.

## Maintainer

Maintained by [@flegbrum](https://github.com/flegbrum). The API runs on Cloudflare Workers. Legal notice (Impressum): https://cropauth-api.axolo6.workers.dev/#impressum

## Feedback

Please report bugs, wrong data or missing fields in [Issues](../../issues). It helps if you include the product ID and the URL you called.

Code in this repository (the client and the examples) is MIT-licensed. Data licences are listed above.
