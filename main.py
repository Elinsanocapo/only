from flask import Flask, request, Response
import subprocess
import json

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

    # yt-dlp command
    ytdlp_cmd = [
        'yt-dlp',
        video_url,
        '--quiet',
        '--no-warnings',
        '-o', '-',  # Output to stdout
    ]
    
    if download_type == 'audio':
        ytdlp_cmd.extend(['-f', 'bestaudio'])  # Best audio format
        file_extension = 'mp3'
    else:
        ytdlp_cmd.extend(['-f', 'bestvideo+bestaudio/best'])  # Best video format
        file_extension = 'mp4'

    def generate():
        process = subprocess.Popen(ytdlp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            while True:
                chunk = process.stdout.read(1024 * 8)  # Read in chunks of 8 KB
                if not chunk:
                    break
                yield chunk
        finally:
            process.terminate()

    mime_type = 'video/mp4' if download_type == 'video' else 'audio/mpeg'
    response = Response(generate(), content_type=mime_type)
    response.headers['Content-Disposition'] = f'attachment; filename="{video_title}.{file_extension}"'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
