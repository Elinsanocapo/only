import subprocess
from flask import Flask, request, Response

app = Flask(__name__)

def get_video_title(video_url):
    """Obtiene el título del video usando yt-dlp."""
    try:
        result = subprocess.run(
            ['yt-dlp', '--print', '%(title)s', video_url],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.stdout.strip()
    except Exception:
        return None

@app.route('/download')
def download():
    video_id = request.args.get('id')
    download_type = request.args.get('type', 'video')  # Default to 'video'
    
    if not video_id:
        return "Missing 'id' parameter", 400
    
    video_url = f'https://www.youtube.com/watch?v={video_id}'
    video_title = get_video_title(video_url)
    if not video_title:
        video_title = video_id  # Fallback to video ID if title can't be fetched

    # Comando de yt-dlp para descargar el video
    ytdlp_cmd = [
        'yt-dlp',
        video_url,
        '--quiet',
        '--no-warnings',
        '-o', '-',  # Salida directamente a stdout
    ]
    
    if download_type == 'audio':
        ytdlp_cmd.extend(['-f', 'bestaudio'])  # Mejor formato de audio
        file_extension = 'mp3'
        mime_type = 'audio/mpeg'
    else:
        ytdlp_cmd.extend(['-f', 'bestvideo+bestaudio/best'])  # Mejor formato de video
        file_extension = 'mp4'
        mime_type = 'video/mp4'

    # Generar la respuesta transmitiendo la salida de yt-dlp
    def generate():
        process = subprocess.Popen(ytdlp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            while True:
                chunk = process.stdout.read(1024 * 8)  # Leer en bloques de 8 KB
                if not chunk:
                    break
                yield chunk
        finally:
            process.terminate()

    # Enviar el video/audio al cliente
    response = Response(generate(), content_type=mime_type)
    response.headers['Content-Disposition'] = f'attachment; filename="{video_title}.{file_extension}"'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
