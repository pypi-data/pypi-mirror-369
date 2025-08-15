import os
import sys
from flask import url_for, render_template, request
from markupsafe import Markup
import importlib.util
from pathlib import Path

_env_cache = None
CONFIG_CACHE = {}

def _find_project_root():
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / ".env").exists() or (parent / "config").exists():
            return str(parent)
    return str(current)

PROJECT_ROOT = _find_project_root()

def _load_env():
    global _env_cache
    if _env_cache is None:
        _env_cache = {}
        env_path = os.path.join(PROJECT_ROOT, ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        value = value.strip().strip('"').strip("'")
                        _env_cache[key.strip()] = value
    return _env_cache

def env(key, default=None):
    return _load_env().get(key, default)

def config(key, default=None):
    parts = key.split(".")
    if not parts:
        return default

    file_name = parts[0]

    if file_name not in CONFIG_CACHE:
        file_path = os.path.join(PROJECT_ROOT, "config", f"{file_name}.py")
        if not os.path.exists(file_path):
            return default

        spec = importlib.util.spec_from_file_location(file_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        CONFIG_CACHE[file_name] = getattr(module, file_name, {})

    value = CONFIG_CACHE[file_name]
    for part in parts[1:]:
        if isinstance(value, dict):
            value = value.get(part, default)
        else:
            return default

    return value

def view(template_name, data=None):
    if data is None:
        data = {}
    template_path = template_name.replace(".", "/")
    if not os.path.splitext(template_path)[1]:
        template_path += ".html"

    return render_template(template_path, **data)

def route(name, **kwargs):
    return url_for(name, **kwargs)

def url(path=""):
    base = request.url_root.rstrip("/")
    return f"{base}/{path.lstrip('/')}" if path else base

def asset(path):
    return url_for("static", filename=path)

def css(filename):
    file_path = os.path.join(PROJECT_ROOT, "resources", "css", filename)
    version = int(os.path.getmtime(file_path)) if os.path.exists(file_path) else 1
    url_path = f"resources/css/{filename}"
    return Markup(
        f'<link rel="stylesheet" href="{request.url_root.rstrip("/")}/{url_path}?v={version}">'
    )

def js(filename):
    file_path = os.path.join(PROJECT_ROOT, "resources", "js", filename)
    version = int(os.path.getmtime(file_path)) if os.path.exists(file_path) else 1
    url_path = f"resources/js/{filename}"
    return Markup(
        f'<script src="{request.url_root.rstrip("/")}/{url_path}?v={version}"></script>'
    )
