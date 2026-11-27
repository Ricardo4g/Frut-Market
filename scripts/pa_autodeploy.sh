#!/bin/bash
# Despliegue continuo desde PythonAnywhere (modelo "pull").
# Se ejecuta como tarea programada en PythonAnywhere: si hay commits nuevos en
# la rama main de GitHub, copia los archivos de la aplicación a la carpeta de la
# web app y la recarga. La base de datos no se toca.
#
# Uso:  bash pa_autodeploy.sh            (solo despliega si hay cambios)
#       bash pa_autodeploy.sh --forzar   (despliega aunque no haya cambios)
set -e

REPO="$HOME/Frut-Market-repo"
WSGI="/var/www/frutmarket_pythonanywhere_com_wsgi.py"
URL="https://frutmarket.pythonanywhere.com/health"

# Carpeta del proyecto: la que aparece en el archivo WSGI de la web app
DEST=$(grep -o "/home/$USER/[^'\"]*" "$WSGI" | head -1)
DEST="${DEST%/}"
if [ -z "$DEST" ] || [ ! -d "$DEST" ]; then
    echo "$(date '+%F %T') ERROR: no encontré la carpeta del proyecto en $WSGI"
    exit 1
fi

if [ ! -d "$REPO/.git" ]; then
    git clone -q https://github.com/Ricardo4g/Frut-Market.git "$REPO"
fi

cd "$REPO"
git fetch -q origin main
ANTES=$(git rev-parse HEAD)
NUEVO=$(git rev-parse origin/main)

if [ "$ANTES" = "$NUEVO" ] && [ "$1" != "--forzar" ]; then
    echo "$(date '+%F %T') sin cambios (${NUEVO:0:7}, versión $(cat VERSION))"
    exit 0
fi

git reset -q --hard origin/main
echo "$(date '+%F %T') publicando versión $(cat VERSION) (${NUEVO:0:7}) en $DEST"
git log --oneline "${ANTES}..${NUEVO}" 2>/dev/null | sed 's/^/  commit /' || true

# Solo los archivos que necesita la aplicación (sin pruebas, CI ni base de datos)
cp -r app.py database.py demo_data.py VERSION requirements.txt templates static "$DEST"/

# Tocar el archivo WSGI recarga la web app en PythonAnywhere
touch "$WSGI"

# La recarga tarda alrededor de un minuto: se espera hasta que /health reporte la versión nueva
VERSION_NUEVA=$(cat VERSION)
for i in $(seq 1 24); do
    sleep 5
    RESP=$(curl -s -m 20 "$URL" || true)
    if echo "$RESP" | grep -q "\"version\":\"$VERSION_NUEVA\""; then
        echo "$(date '+%F %T') OK /health -> $RESP"
        exit 0
    fi
done
echo "$(date '+%F %T') ERROR: después de 2 minutos /health no reporta la versión $VERSION_NUEVA"
echo "  última respuesta: $RESP"
exit 1
