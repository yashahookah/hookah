#!/usr/bin/env python3
"""
Поиск допустимых type/framework в Timeweb API.
Запуск: TIMEWEB_TOKEN='токен' python3 discover_timeweb_api.py
"""
import json
import os
import sys
import urllib.request
import urllib.error

BASE = "https://api.timeweb.cloud"
_DEFAULT = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6IjFrYnhacFJNQGJSI0tSbE1xS1lqIn0.eyJ1c2VyIjoieGIxMzA4NzkiLCJ0eXBlIjoiYXBpX2tleSIsImFwaV9rZXlfaWQiOiI4ZDBmMjQzNi04YjhiLTRlZDAtOTk4ZC01OWFmOTY5YTU2ODMiLCJpYXQiOjE3NzI4MTAyODEsImV4cCI6MTc3Nzk5NDI3OX0.nJimzy6I9RRXhW8nJI924o6ePfpVtV3-M7eN0Uul05rrwtAGxbj06_7F4IJtd1vZBCycd5j55VWlaa2mE0qikaBiYNL-2FJku4wBfc1tdfna9HNP65oOScVVI0GKPH_HNa2Ot-QTtMEf92OY1Oix-36HhlI4c-esHG1Q2Ma2cdsfULL-NY-LwqKhuczFNGm_Izh0hAjct3Vi5fqDqZd6cQ_6aTAQQZAQrXwL823qUKb67ylKqdlmg4daKWTp3FlnQqwqfqOb5Aq1Nck4r3rp57SwFsf06o-VeKPdWWhxpZNKQnM8dR1nn-hOdjcNQFuMRXcLnxBvbm-eLRfIRDOCjEyAlrXkLAkx-5Wb-gX8ABFvGWSx_2PulGc5rrHnimWrAg-9MhDMpzSmnspIM1yWKZkXOVd_UZ9K-xNLBMDUV7FJtJfYzjSWEn5Ta7Rce5odlRay7VDerxJtTG-j9SX8v8HcxlEYtCzedKD5tGv8hWozKbwvtG-APFhNVH4zQBdN"
TOKEN = os.environ.get("TIMEWEB_TOKEN", "").strip() or _DEFAULT

if not TOKEN:
    print("Задай TIMEWEB_TOKEN")
    sys.exit(1)


def req(method, path):
    url = f"{BASE}{path}"
    req_obj = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req_obj, timeout=15) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:1500]
        return {"_error": e.code, "_body": body}
    except Exception as e:
        return {"_error": str(e)}


# Эндпоинты, которые могут вернуть типы/фреймворки
paths = [
    "/api/v1/apps/templates",
    "/api/v1/apps/types",
    "/api/v1/app-templates",
    "/api/v1/frameworks",
    "/api/v1/stacks",
    "/api/v1/apps/schemas",
    "/api/v1/apps/create/schema",
]

print("=== Поиск допустимых type/framework ===\n")
for path in paths:
    r = req("GET", path)
    if "_error" in r:
        print(f"GET {path} -> {r['_error']}")
        if r.get("_body"):
            print("  Тело ответа:", r["_body"][:800])
        print()
    elif r and "_error" not in r:
        print(f"GET {path} -> 200")
        print(json.dumps(r, indent=2, ensure_ascii=False)[:2000])
        print()
print("\n=== Готово ===")
