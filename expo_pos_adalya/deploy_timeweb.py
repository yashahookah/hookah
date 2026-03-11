#!/usr/bin/env python3
"""
Скрипт деплоя Expo POS на Timeweb Cloud App Platform через API.
Запуск: TIMEWEB_TOKEN="ваш_токен" python3 deploy_timeweb.py
"""
import json
import os
import sys
import urllib.request
import urllib.error

BASE = "https://api.timeweb.cloud"
# Токен из env или fallback (если не задан)
_DEFAULT_TOKEN = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6IjFrYnhacFJNQGJSI0tSbE1xS1lqIn0.eyJ1c2VyIjoieGIxMzA4NzkiLCJ0eXBlIjoiYXBpX2tleSIsImFwaV9rZXlfaWQiOiI4ZDBmMjQzNi04YjhiLTRlZDAtOTk4ZC01OWFmOTY5YTU2ODMiLCJpYXQiOjE3NzI4MTAyODEsImV4cCI6MTc3Nzk5NDI3OX0.nJimzy6I9RRXhW8nJI924o6ePfpVtV3-M7eN0Uul05rrwtAGxbj06_7F4IJtd1vZBCycd5j55VWlaa2mE0qikaBiYNL-2FJku4wBfc1tdfna9HNP65oOScVVI0GKPH_HNa2Ot-QTtMEf92OY1Oix-36HhlI4c-esHG1Q2Ma2cdsfULL-NY-LwqKhuczFNGm_Izh0hAjct3Vi5fqDqZd6cQ_6aTAQQZAQrXwL823qUKb67ylKqdlmg4daKWTp3FlnQqwqfqOb5Aq1Nck4r3rp57SwFsf06o-VeKPdWWhxpZNKQnM8dR1nn-hOdjcNQFuMRXcLnxBvbm-eLRfIRDOCjEyAlrXkLAkx-5Wb-gX8ABFvGWSx_2PulGc5rrHnimWrAg-9MhDMpzSmnspIM1yWKZkXOVd_UZ9K-xNLBMDUV7FJtJfYzjSWEn5Ta7Rce5odlRay7VDerxJtTG-j9SX8v8HcxlEYtCzedKD5tGv8hWozKbwvtG-APFhNVH4zQBdN"
TOKEN = os.environ.get("TIMEWEB_TOKEN", "").strip() or _DEFAULT_TOKEN

if not TOKEN:
    print("Задайте токен: export TIMEWEB_TOKEN='ваш_jwt_токен'")
    sys.exit(1)

# DISCOVER=1 — поиск допустимых type/framework через API
if os.environ.get("DISCOVER"):
    print("=== Режим DISCOVER: ищем допустимые type/framework ===\n")
    for path in [
        "/api/v1/apps/templates", "/api/v1/app-templates", "/api/v1/frameworks",
        "/api/v1/stacks", "/api/v1/app-types", "/api/v1/apps/schemas",
    ]:
        r = req("GET", path)
        if isinstance(r, dict) and "raw" not in r and r:
            print(f"  Ответ {path}:")
            print("  ", json.dumps(r, indent=2, ensure_ascii=False)[:600])
            print()
    sys.exit(0)

# JWT обычно 300+ символов. Если короче или есть "..." — токен обрезан
if len(TOKEN) < 200 or "..." in TOKEN:
    print("ВНИМАНИЕ: Токен похож на обрезанный (должен быть полный JWT без ...)")
    print("Скопируй токен целиком из Timeweb → Настройки → API и Terraform")


def req(method, path, data=None):
    url = f"{BASE}{path}"
    req_obj = urllib.request.Request(
        url,
        data=json.dumps(data).encode() if data else None,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req_obj, timeout=30) as r:
            body = r.read().decode()
            print(f"  {method} {path} -> {r.status}")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        print(f"  {method} {path} -> {e.code}")
        body = e.read().decode() if e.fp else ""
        try:
            out = json.loads(body) if body else {"raw": str(e)}
            if e.code == 401 and body:
                print(f"  Ответ API: {body[:300]}")
            return out
        except json.JSONDecodeError:
            if e.code == 401 and body:
                print(f"  Ответ API: {body[:300]}")
            return {"raw": body[:500] if body else str(e)}
    except Exception as e:
        print(f"  {method} {path} -> ошибка: {e}")
        return {"raw": str(e)}


def get_github_commit_sha(owner, repo, branch="main"):
    """Получить SHA последнего коммита из GitHub (публичный API)."""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}"
    try:
        req_obj = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json"})
        with urllib.request.urlopen(req_obj, timeout=10) as r:
            data = json.loads(r.read().decode())
            return data.get("sha", "")[:40]
    except Exception as e:
        print(f"  Ошибка получения commit SHA: {e}")
        return ""


def main():
    # Режим поиска: ищем эндпоинты с допустимыми type/framework
    if os.environ.get("DISCOVER"):
        print("=== DISCOVER: поиск допустимых type/framework ===")
        for path in [
            "/api/v1/apps/templates", "/api/v1/app-templates", "/api/v1/frameworks",
            "/api/v1/stacks", "/api/v1/app-types", "/api/v1/apps/schemas",
        ]:
            r = req("GET", path)
            if isinstance(r, dict) and "raw" not in r and r:
                print(f"  {path}:")
                print("   ", json.dumps(r, indent=2, ensure_ascii=False)[:600])
        print()
        return

    print("=== Проверка токена ===")
    apps_data = None
    for path in ["/api/v1/apps", "/v1/apps"]:
        r = req("GET", path)
        if isinstance(r, dict) and "apps" in r:
            apps_data = r
            print("  Токен OK, приложения:", r.get("apps", [])[:3])
            break
        if isinstance(r, dict) and ("id" in r or "user" in r):
            print("  Токен OK")
            break
        if isinstance(r, dict) and ("message" in r or "raw" in r):
            err = str(r.get("message", r.get("raw", "")))
            if "401" in err or "Unauthorized" in err:
                print("  Ошибка: неверный токен")
                sys.exit(1)
    print()

    # Если приложение уже создано вручную — пробуем запустить деплой
    if apps_data and apps_data.get("apps"):
        for app in apps_data["apps"]:
            if "expo" in app.get("name", "").lower() or "hookah" in app.get("name", "").lower():
                app_id = app.get("id")
                print(f"=== Найдено приложение: {app.get('name')} (id={app_id}) ===")
                print("  Запуск деплоя...")
                for path in [f"/api/v1/apps/{app_id}/deploy", f"/api/v1/apps/{app_id}/deployments"]:
                    r = req("POST", path, {})
                    if isinstance(r, dict) and ("id" in r or "deployment" in r or "status" in r):
                        print("  Деплой запущен!")
                        return
                print("  Деплой через API не найден. Обновите приложение вручную в Timeweb.")
                return
    print()

    print("=== Получение provider_id и repository_id ===")
    provider_id = None
    repository_id = None
    vcs_response = None
    for path in ["/api/v1/vcs-providers", "/api/v1/providers", "/api/v1/vcs-provider"]:
        r = req("GET", path)
        if isinstance(r, dict) and "raw" not in r:
            vcs_response = r
            providers = r.get("providers") or r.get("vcs_providers") or r.get("data") or []
            if not isinstance(providers, list):
                providers = [r] if "id" in r else []
            for p in (providers if isinstance(providers, list) else []):
                pid = p.get("id") or p.get("provider_id")
                if pid:
                    provider_id = str(pid)
                    print(f"  provider_id: {provider_id}")
                    # Репозитории могут быть внутри провайдера
                    repos = p.get("repositories") or p.get("repos") or []
                    for repo in repos:
                        name = repo.get("name") or repo.get("full_name") or repo.get("slug", "")
                        if "hookah" in str(name).lower():
                            repository_id = str(repo.get("id") or repo.get("repository_id", ""))
                            print(f"  repository_id (из провайдера): {repository_id} ({name})")
                            break
                    break
            if provider_id:
                break
    if not provider_id:
        print("  provider_id не найден. Подключи GitHub в Timeweb: Apps → Настройки → Репозитории")
        sys.exit(1)

    # Пробуем разные эндпоинты для репозиториев
    repo_paths = [
        f"/api/v1/vcs-provider/{provider_id}/repositories",
        f"/api/v1/vcs-provider/repositories?provider_id={provider_id}",
        f"/api/v1/repositories?provider_id={provider_id}",
        f"/api/v1/providers/{provider_id}/repositories",
    ]
    for path in repo_paths:
        if repository_id:
            break
        r = req("GET", path)
        if isinstance(r, dict) and "raw" not in r:
            repos = r.get("repositories") or r.get("data") or r.get("repos") or r.get("items") or []
            if isinstance(r, list):
                repos = r
            for repo in repos:
                name = repo.get("name") or repo.get("full_name") or repo.get("slug") or ""
                if "hookah" in str(name).lower():
                    repository_id = str(repo.get("id") or repo.get("repository_id", ""))
                    print(f"  repository_id: {repository_id} ({name})")
                    break
            if repository_id:
                break

    if not repository_id and vcs_response:
        print("  Структура ответа vcs-provider:", json.dumps(vcs_response, indent=2, ensure_ascii=False)[:1200])
    if not repository_id:
        # Fallback 1: GitHub repo ID (числовой)
        print("  Пробуем получить ID репо из GitHub...")
        try:
            gh_req = urllib.request.Request(
                "https://api.github.com/repos/yashahookah/hookah",
                headers={"Accept": "application/vnd.github.v3+json"},
            )
            with urllib.request.urlopen(gh_req, timeout=10) as gh_r:
                gh_data = json.loads(gh_r.read().decode())
                repository_id = str(gh_data.get("id", ""))
                if repository_id:
                    print(f"  repository_id (GitHub id): {repository_id}")
        except Exception as e:
            print(f"  GitHub API: {e}")
    if not repository_id:
        # Fallback 2: формат owner/repo
        repository_id = "yashahookah/hookah"
        print(f"  repository_id (fallback owner/repo): {repository_id}")
    if not repository_id:
        # Последняя попытка: разные форматы
        for rid in ["yashahookah/hookah", "yashahookah_hookah"]:
            print(f"  Пробуем repository_id={rid}...")
            body_try = {
                "name": "expo-pos",
                "type": "docker",
                "provider_id": provider_id,
                "repository_id": rid,
                "build_cmd": "docker build -t app .",
                "branch_name": "main",
                "is_auto_deploy": True,
                "commit_sha": get_github_commit_sha("yashahookah", "hookah") or "main",
                "comment": "Expo POS deploy",
            }
            r = req("POST", "/api/v1/apps", body_try)
            if isinstance(r, dict) and ("id" in r or "app" in r):
                print("  Приложение создано!")
                return
        print("  repository_id не найден. Запусти с DEBUG=1 чтобы увидеть ответ vcs-provider:")
        print("  DEBUG=1 TIMEWEB_TOKEN='...' python3 deploy_timeweb.py")
        sys.exit(1)
    print()

    print("=== Получение commit SHA ===")
    commit_sha = get_github_commit_sha("yashahookah", "hookah", "main")
    if not commit_sha:
        commit_sha = "main"  # fallback
    print(f"  commit_sha: {commit_sha[:12]}...")
    print()

    print("=== Создание приложения ===")
    base_body = {
        "name": "expo-pos",
        "provider_id": provider_id,
        "repository_id": repository_id,
        "build_cmd": "docker build -t app .",
        "branch_name": "main",
        "is_auto_deploy": True,
        "commit_sha": commit_sha,
        "comment": "Expo POS deploy",
    }
    # Пробуем разные type/framework — API требует валидный enum
    for app_type, framework in [
        ("fastapi", "fastapi"),
        ("dockerfile", None),
        ("docker", None),
        ("python", "fastapi"),
        ("custom", "dockerfile"),
    ]:
        body = {**base_body, "type": app_type}
        if framework:
            body["framework"] = framework
        print(f"  Пробуем type={app_type}, framework={framework}...")
        r = req("POST", "/api/v1/apps", body)
        if isinstance(r, dict) and ("id" in r or "app" in r):
            print("  Приложение создано!")
            app_id = r.get("id") or r.get("app", {}).get("id")
            if app_id:
                print(f"  ID: {app_id}")
                print("  Деплой запущен. Подождите 5–10 минут.")
            return
        if isinstance(r, dict) and "message" in r:
            msg = r.get("message", "")
            if isinstance(msg, list):
                msg = " | ".join(str(m) for m in msg[:2])
            print(f"    -> {msg[:150]}")
    print()
    print("Не удалось создать приложение. Создайте вручную: https://timeweb.cloud/my/apps/create")


if __name__ == "__main__":
    main()
