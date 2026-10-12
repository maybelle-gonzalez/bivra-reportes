# bivra-reportes

Reportes de pauta de BIVRA para clientes, publicados en **reportes.bivradna.com** con GitHub Pages.

Cada cliente tiene su carpeta (ej. `spine-center/`) con un solo `index.html` **cifrado con contraseña** (AES, con [StaticCrypt](https://github.com/robinmoisson/staticrypt)). El repo es público, pero sin la contraseña no se puede leer ningún número: la data solo existe dentro del archivo cifrado.

| Cliente | Enlace | Se actualiza |
|---|---|---|
| Spine Center | reportes.bivradna.com/spine-center/ | Todos los días, 6:55 a. m. (hora RD) |

## Cómo se arma

1. El dashboard vive en Claude (Artifact tipo Dashboard), con data de Windsor.ai (Meta Ads, Google Ads, GA4).
2. Una tarea programada refresca esa data cada mañana, toma la página y los archivos de data, y corre:

   ```bash
   REPORTE_CLAVE='…' tools/publicar.sh spine-center /ruta/de/trabajo "Spine Center · Reporte de pauta"
   ```

   - `tools/build.py` junta página + estilos + d3 + data en un HTML autónomo (fuera del repo).
   - StaticCrypt lo cifra y lo deja en `spine-center/index.html`.
3. La tarea hace commit y push; GitHub Pages lo publica en uno o dos minutos.

## Reglas

- **Nunca** subir data o HTML sin cifrar (`*.json` de data, `plano.html`). La contraseña no va en el repo.
- `.staticrypt.json` guarda solo la *sal* del cifrado (no es secreta); mantenerla igual hace que "Recordarme" siga funcionando entre actualizaciones.
- `robots.txt` y `noindex` evitan que los reportes aparezcan en Google.
