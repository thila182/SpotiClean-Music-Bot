# 🎧 SpotiClean Musical Bot

Bot de Telegram especializado en enriquecer enlaces de Spotify. Extrae metadatos, busca alternativas en otros servicios y genera una previsualización de audio automática.

### 🚀 Funcionalidades
- **Enriquecimiento de Enlaces:** Recibe un link de Spotify y extrae Artista, Álbum, Género y Portada.
- **Multi-Plataforma:** Genera automáticamente botones para buscar la canción en YouTube o abrirla en otros servicios mediante Songlink.
- **Audio Preview:** Integra la API de iTunes para enviar un clip de audio de 30 segundos como previsualización.
- **Lógica de Personalidad:** Incluye un "Juez Musical" que emite opiniones basadas en el género detectado.

### 🛠️ Tecnologías
- **Cloudscraper & BeautifulSoup4:** Scraping avanzado para obtener metadatos de Spotify.
- **iTunes Search API:** Para obtención de géneros y previews de audio.
- **Regex (Re):** Limpieza y formateo de URLs y títulos.
