#!/usr/bin/env python3
"""Arma un reporte HTML autónomo a partir de la página del dashboard (Artifact
tipo Dashboard) y sus archivos de data, para publicarlo cifrado en GitHub Pages.

Uso:
  python3 tools/build.py --page index.html --css brand.css --data DIR \
      --d3 node_modules/d3/dist/d3.min.js --title "Spine Center · Pauta" --out plano.html

DIR tiene un <id>.json por fuente (meta_daily, meta_campaigns, meta_total,
google_daily, google_campaigns, ga4_sources, ga4_pages, ga4_events).
El HTML resultante lleva la data adentro: NUNCA se sube sin cifrar.
"""
import argparse, datetime, json, pathlib

SHIM = r"""
<script>
(function () {
  const DATA = JSON.parse(document.getElementById('report-data').textContent);
  const calcs = {}, cache = {}, listeners = [];
  function rows(id) {
    if (id in DATA) return DATA[id];
    if (id in cache) return cache[id];
    const c = calcs[id];
    if (!c) return null;
    try { cache[id] = c.fn(...c.inputs.map(rows)); } catch (e) { console.error(id, e); cache[id] = null; }
    return cache[id];
  }
  window.dash = {
    data(id) {
      const d = rows(id);
      if (d == null) return { status: 'missing', data: [], rows: [], columns: [], meta: [] };
      const arr = Array.isArray(d) ? d : [d];
      return { status: 'ok', data: d, rows: arr, columns: arr[0] ? Object.keys(arr[0]) : [], meta: [], refreshing: false };
    },
    calc(id, spec) { calcs[id] = { inputs: spec.inputs || [], fn: spec.fn }; },
    loader() {},
    onData(fn) { listeners.push(fn); fn(); },
    refresh() {}, setLink() {}, params() { return {}; }, setParams() {}, resetParams() {},
    colors: ['#00ff88', '#d9d9d9', '#00a651', '#ffd166', '#ff6b6b', '#7dd3fc', '#c084fc', '#a3a3a3'],
  };
  let w = window.innerWidth;
  window.addEventListener('resize', () => {
    if (window.innerWidth === w) return; w = window.innerWidth;
    clearTimeout(window.__rt); window.__rt = setTimeout(() => listeners.forEach((f) => f()), 150);
  });
})();
</script>
"""

TOKENS = """
:root{--cds-gap-xs:4px;--cds-gap-sm:8px;--cds-gap-md:16px;--cds-gap-lg:24px;--cds-gap-xl:40px;
--cds-pad-xs:4px;--cds-pad-sm:8px;--cds-pad-md:12px;--cds-pad-lg:20px;--cds-radius:12px;
--cds-font-size-caption:.8125rem;--cds-font-size-body:.9375rem;--cds-font-size-heading:1.0625rem;
--cds-dur-slow:.4s;--cds-shadow-popover:0 8px 24px rgba(0,0,0,.5);--font-anthropic-sans:system-ui,sans-serif;
color-scheme:dark}
html,body{margin:0;background:#000}
#dash-root{max-width:1280px;margin:0 auto}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--page', required=True)
    ap.add_argument('--css', required=True)
    ap.add_argument('--data', required=True)
    ap.add_argument('--title', default='Reporte de pauta · BIVRA')
    ap.add_argument('--d3', required=True, help='ruta a d3.min.js (v7)')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    page = pathlib.Path(a.page).read_text(encoding='utf-8')
    css = pathlib.Path(a.css).read_text(encoding='utf-8')
    d3js = pathlib.Path(a.d3).read_text(encoding='utf-8').replace('</script', '<\\/script')
    data = {p.stem: json.loads(p.read_text(encoding='utf-8')) for p in sorted(pathlib.Path(a.data).glob('*.json'))}
    if not data:
        raise SystemExit('No hay archivos de data en ' + a.data)

    page = page.replace('<link rel="stylesheet" href="brand.css">', '')
    blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y-%m-%d %H:%M')

    html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="generated" content="{stamp} (hora RD)">
<title>{a.title}</title>
<style>{TOKENS}</style>
<style>{css}</style>
<script>{d3js}</script>
</head>
<body>
<script type="application/json" id="report-data">{blob}</script>
{SHIM}
<div id="dash-root">
{page}
</div>
</body>
</html>
"""
    pathlib.Path(a.out).write_text(html, encoding='utf-8')
    print(f'OK {a.out}: {len(html):,} bytes, fuentes: {", ".join(data)}')


if __name__ == '__main__':
    main()
