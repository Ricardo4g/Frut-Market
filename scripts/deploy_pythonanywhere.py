"""Despliega Frut Market en PythonAnywhere usando su API.

1. Ubica la carpeta del proyecto leyendo el archivo WSGI de la aplicación web.
2. Sube los archivos de la aplicación (sin pruebas, base de datos ni archivos de CI).
3. Recarga la aplicación web.
4. Verifica en /health que la versión publicada sea la del archivo VERSION.

Variables de entorno: PA_API_TOKEN (secreto), PA_USERNAME y PA_DOMAIN.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid

TOKEN = os.environ["PA_API_TOKEN"]
USER = os.environ.get("PA_USERNAME", "FrutMarket")
DOMAIN = os.environ.get("PA_DOMAIN", "frutmarket.pythonanywhere.com")
API = f"https://www.pythonanywhere.com/api/v0/user/{USER}"

# Solo se publican los archivos que necesita la aplicación en producción
INCLUIR = ("app.py", "database.py", "demo_data.py", "VERSION", "requirements.txt",
           "templates/", "static/")


def api(method, path, data=None, headers=None):
    req = urllib.request.Request(API + path, data=data, method=method,
                                 headers={"Authorization": f"Token {TOKEN}", **(headers or {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.read()


def carpeta_proyecto():
    _, body = api("GET", f"/webapps/{DOMAIN}/")
    info = json.loads(body)
    wsgi = info.get("wsgi_file") or f"/var/www/{DOMAIN.replace('.', '_')}_wsgi.py"
    _, contenido = api("GET", f"/files/path{wsgi}")
    rutas = re.findall(r"['\"](/home/%s/[^'\"]+)['\"]" % re.escape(USER), contenido.decode("utf-8"))
    if not rutas and info.get("source_directory"):
        rutas = [info["source_directory"]]
    if not rutas:
        sys.exit(f"No encontré la carpeta del proyecto en {wsgi}")
    return rutas[0].rstrip("/")


def subir(local, remoto):
    limite = uuid.uuid4().hex
    with open(local, "rb") as f:
        contenido = f.read()
    cuerpo = (f"--{limite}\r\nContent-Disposition: form-data; name=\"content\"; "
              f"filename=\"{os.path.basename(local)}\"\r\n"
              "Content-Type: application/octet-stream\r\n\r\n").encode() + contenido + \
        f"\r\n--{limite}--\r\n".encode()
    estado, _ = api("POST", f"/files/path{remoto}", cuerpo,
                    {"Content-Type": f"multipart/form-data; boundary={limite}"})
    print(f"  {estado}  {local}")


def verificar(version):
    url = f"https://{DOMAIN}/health"
    for intento in range(1, 11):
        try:
            inicio = time.time()
            with urllib.request.urlopen(url, timeout=30) as r:
                datos = json.loads(r.read())
            ms = (time.time() - inicio) * 1000
            print(f"  intento {intento}: {datos} ({ms:.0f} ms)")
            if datos.get("status") == "ok" and datos.get("version") == version:
                return
        except (urllib.error.URLError, ValueError) as e:
            print(f"  intento {intento}: {e}")
        time.sleep(6)
    sys.exit(f"La versión publicada no respondió como {version} en {url}")


def main():
    version = open("VERSION", encoding="utf-8").read().strip()
    destino = carpeta_proyecto()
    print(f"Carpeta del proyecto en PythonAnywhere: {destino}")
    archivos = subprocess.run(["git", "ls-files"], capture_output=True, text=True,
                              check=True).stdout.split()
    archivos = [a for a in archivos if a.startswith(INCLUIR) or a in INCLUIR]
    print(f"Subiendo {len(archivos)} archivos de la versión {version}:")
    for a in archivos:
        subir(a, f"{destino}/{a}")
    estado, _ = api("POST", f"/webapps/{DOMAIN}/reload/")
    print(f"Recarga de la aplicación web: {estado}")
    print("Verificando /health:")
    verificar(version)
    print(f"Versión {version} publicada en https://{DOMAIN}")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        detalle = " ".join(e.read().decode("utf-8", "replace")[:300].split())
        print(f"::error::PythonAnywhere respondió {e.code} en {e.url}: {detalle}")
        sys.exit(1)
    except SystemExit as e:
        if e.code not in (0, None):
            print(f"::error::{e.code}")
        raise
