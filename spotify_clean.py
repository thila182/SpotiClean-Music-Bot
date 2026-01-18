import telebot
from telebot import types
import cloudscraper
import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
import re
from datetime import datetime

# ==========================================
# 🔐 CONFIGURACIÓN
# ==========================================
TOKEN_TELEGRAM = "TU_TELEGRAM_TOKEN"

print("✅ Bot iniciado...")

bot = telebot.TeleBot(TOKEN_TELEGRAM)

# ==========================================
# ⚖️ EL JUEZ MUSICAL
# ==========================================
def obtener_opinion_bot(genero):
    if not genero or genero == "No disponible": return "🤔 Inclasificable."
    g = genero.lower()
    
    if "metal" in g or "hardcore" in g or "punk" in g: return "💀 Uff, qué tralla. Aprobado."
    if "rock" in g or "alternative" in g: return "🤘 Un clásico. Buena elección."
    if "pop" in g: return "🍬 Algo comercial, pero se te pega."
    if "hip hop" in g or "rap" in g or "urban" in g: return "🎤 Tira unas barras ahí."
    if "jazz" in g or "blues" in g or "soul" in g: return "🎷 Fino señores, muy fino."
    if "electronic" in g or "dance" in g or "house" in g or "techno" in g: return "💊 ¿Dónde es la rave?"
    if "latino" in g or "reggaeton" in g: return "🔥 Perreo hasta el suelo."
    if "classical" in g or "soundtrack" in g: return "🎻 Qué culto eres, madre mía."
    
    return "🎧 Interesante sonido."

# ==========================================
# 🎵 LÓGICA DE MÚSICA (Spotify + iTunes)
# ==========================================
def consultar_info_itunes(artista, titulo_album):
    """Busca en iTunes para obtener género y preview de audio"""
    try:
        if "," in artista: artista = artista.split(",")[0].strip()
        encoded = urllib.parse.quote(f"{artista} {titulo_album}")
        
        # 1. Buscar canción
        r = requests.get(f"https://itunes.apple.com/search?term={encoded}&entity=song&limit=1", timeout=5)
        if r.status_code == 200 and r.json()["resultCount"] > 0:
            res = r.json()["results"][0]
            return {"genero": res.get("primaryGenreName", "No disponible"), "audio": res.get("previewUrl", None)}
        
        # 2. Buscar artista (Fallback si no encuentra la canción exacta)
        r2 = requests.get(f"https://itunes.apple.com/search?term={urllib.parse.quote(artista)}&entity=musicArtist&limit=1", timeout=5)
        if r2.status_code == 200 and r2.json()["resultCount"] > 0:
             return {"genero": r2.json()["results"][0].get("primaryGenreName", "No disponible"), "audio": None}
    except: return None
    return None

def obtener_datos_spotify(url):
    """Scraping de Spotify usando Cloudscraper para saltar protección"""
    scraper = cloudscraper.create_scraper()
    try:
        r = scraper.get(url)
        if r.status_code != 200: return {"error": "❌ Error enlace."}
        soup = BeautifulSoup(r.text, 'html.parser')
        
        titulo, artista, fecha, imagen = "Desconocido", "Desconocido", "Desconocido", None
        
        # Extracción de metadatos básicos
        meta_title = soup.find('meta', property='og:title')
        if meta_title: 
            raw = meta_title['content']
            clean = re.split(r"\s-\s(Album|Single|EP)\sby", raw, flags=re.IGNORECASE)[0]
            titulo = clean.replace(" | Spotify", "").strip()
        
        meta_desc = soup.find('meta', property='og:description')
        if meta_desc:
            c = meta_desc['content']
            if " · " in c: artista = c.split(" · ")[0]
            elif " - " in c: artista = c.split(" - ")[0]
        
        meta_img = soup.find('meta', property='og:image')
        if meta_img: imagen = meta_img['content']
        
        # Enriquecer datos con iTunes (Audio + Género)
        extra = consultar_info_itunes(artista, titulo)
        genero = extra["genero"] if extra else "No disponible"
        audio = extra["audio"] if extra else None

        # Opinión del Juez Musical
        opinion = obtener_opinion_bot(genero)

        texto = f"🎸 *ARTISTA:* {artista}\n💿 *ÁLBUM:* {titulo}\n🏷️ *GÉNERO:* {genero}\n📅 *FECHA:* {fecha}\n💬 *BOT:* {opinion}"
        
        return {"error": None, "texto": texto, "imagen": imagen, "audio": audio, "artista": artista, "titulo": titulo}
    except Exception as e: return {"error": f"Error: {e}"}

# ==========================================
# 🎮 COMANDOS
# ==========================================

@bot.message_handler(commands=['start'])
def welcome(m): 
    bot.reply_to(m, "🎧 **SpotiBot Musical**\n\nEnvíame un enlace de Spotify (canción o álbum) y te daré toda la info, enlaces alternativos y una previsualización de audio.")

# ==========================================
# 📥 PROCESADOR DE ENLACES
# ==========================================

@bot.message_handler(func=lambda m: m.text and "http" in m.text and "spotify" in m.text)
def procesar_link(message):
    words = message.text.split()
    # Busca el enlace exacto dentro del mensaje
    url = next((p for p in words if "spotify" in p and "http" in p), None)
    
    if url:
        try:
            # Limpieza de tracking (?si=...)
            url_limpia = url.split('?')[0]
            
            bot.send_chat_action(message.chat.id, 'upload_photo')
            res = obtener_datos_spotify(url_limpia)
            
            if not res["error"]:
                # Creación de botones
                keyboard = types.InlineKeyboardMarkup()
                
                # Botón YouTube
                yt_query = urllib.parse.quote(f"{res['artista']} {res['titulo']}")
                keyboard.add(types.InlineKeyboardButton("📺 Buscar en YouTube", url=f"https://www.youtube.com/results?search_query={yt_query}"))
                
                # Botón Otros Servicios (Songlink)
                songlink_url = f"https://song.link/{url_limpia}"
                keyboard.add(types.InlineKeyboardButton("🌍 Abrir en otras Apps", url=songlink_url))
                
                # Enviar Portada + Texto
                if res["imagen"]: 
                    bot.send_photo(message.chat.id, res["imagen"], caption=res["texto"], parse_mode='Markdown', reply_markup=keyboard)
                else: 
                    bot.reply_to(message, res["texto"], reply_markup=keyboard)
                
                # Enviar Audio (Preview)
                if res["audio"]: 
                    bot.send_chat_action(message.chat.id, 'upload_voice')
                    bot.send_audio(message.chat.id, res["audio"], caption=f"🎧 Preview: {res['titulo']}")
                    
        except Exception as e:
            print(f"Error procesando link: {e}")

bot.infinity_polling()