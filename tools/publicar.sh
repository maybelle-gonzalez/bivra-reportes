#!/usr/bin/env bash
# Arma y cifra el reporte de un cliente y lo deja en <carpeta>/index.html.
#
# Uso: REPORTE_CLAVE='...' tools/publicar.sh <carpeta> <trabajo> "<título>"
#   <carpeta>  carpeta del cliente en el repo (ej. spine-center)
#   <trabajo>  carpeta con page.html, brand.css y data/<id>.json (fuera del repo)
#   <título>   título de la pestaña y de la pantalla de acceso
#
# La contraseña viene de REPORTE_CLAVE, nunca se escribe en el repo.
# La data nunca se sube sin cifrar: el HTML plano queda en <trabajo>.
set -euo pipefail

CARPETA="$1"; TRABAJO="$2"; TITULO="$3"
: "${REPORTE_CLAVE:?Falta la variable REPORTE_CLAVE}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
TOOLS="$TRABAJO/node"

mkdir -p "$TOOLS" "$TRABAJO/build"
if [ ! -x "$TOOLS/node_modules/.bin/staticrypt" ]; then
  (cd "$TOOLS" && npm init -y >/dev/null && npm i --silent staticrypt@3 d3@7)
fi

python3 "$REPO/tools/build.py" \
  --page "$TRABAJO/page.html" --css "$TRABAJO/brand.css" --data "$TRABAJO/data" \
  --d3 "$TOOLS/node_modules/d3/dist/d3.min.js" --title "$TITULO" \
  --out "$TRABAJO/build/index.html"

mkdir -p "$REPO/$CARPETA"
cd "$REPO"
"$TOOLS/node_modules/.bin/staticrypt" "$TRABAJO/build/index.html" \
  -p "$REPORTE_CLAVE" -d "$CARPETA" --short --config .staticrypt.json \
  --template-title "$TITULO" \
  --template-instructions "Reporte preparado por BIVRA. Ingresa la contraseña para verlo." \
  --template-button "Entrar" --template-placeholder "Contraseña" \
  --template-error "Contraseña incorrecta" --template-remember "Recordarme en este equipo" \
  --template-color-primary "#00ff88" --template-color-secondary "#000000"

# Control: el archivo publicado no debe tener números ni nombres de campaña en claro.
if grep -q 'report-data\|LANZAMIENTO' "$CARPETA/index.html"; then
  echo "ERROR: el archivo cifrado contiene texto plano; no publicar." >&2
  exit 1
fi
echo "Listo: $CARPETA/index.html"
