# Karaoke — Clases de Canto

Página estática con pistas instrumentales (separadas con Demucs) y letra sincronizada,
para usar en el salón de clases de canto sin depender de WhatsApp Web ni de una laptop
propia.

- Audio: mp3 servidos directo desde este repo (vía GitHub Pages).
- Letra: por ahora sincronizada línea por línea, obtenida gratis de [LRCLIB](https://lrclib.net)
  cuando existe una versión conocida del tema. Cuando no hay cobertura en LRCLIB, la
  canción se lista igual pero sin letra sincronizada (`"sync": "none"` en `data/<slug>.json`).
- El formato de datos ya soporta un futuro nivel `"sync": "word"` (resaltado palabra por
  palabra) agregando un array `words` a cada línea — pendiente de generar con una
  herramienta de alineación forzada (ver conversación / skill `karaoke-stem-separation`).

Este repo es un espejo liviano — el archivo maestro completo (fuente + variantes) vive en
`/home/sebas/Music/karaoke/` en el Pi, documentado en su propio `README.md`.

## Agregar una canción nueva

1. Conseguir el `karaoke.mp3` (ver skill `karaoke-stem-separation`).
2. Copiarlo a `audio/<slug>.mp3`.
3. Buscar en LRCLIB: `curl -s "https://lrclib.net/api/search?track_name=<title>&artist_name=<artist>"`.
4. Si hay resultado con `syncedLyrics`, parsear a `data/<slug>.json` (ver `_parse_lrc.py`
   como referencia de formato).
5. Agregar la entrada en `data/songs.json`.
