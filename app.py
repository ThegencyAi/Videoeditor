from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from flask import Flask, request, send_file
import requests
import os

app = Flask(__name__)

def download_image(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

def create_video(images, subtitles, duration=5):
    clips = []
    for i, image_url in enumerate(images):
        filename = f"image_{i}.jpg"
        download_image(image_url, filename)
        clip = ImageClip(filename).set_duration(duration)
        txt_clip = TextClip(subtitles[i], fontsize=24, color='white', bg_color='black')
        txt_clip = txt_clip.set_pos('bottom').set_duration(duration)
        video = CompositeVideoClip([clip, txt_clip])
        clips.append(video)
    
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile("output.mp4", fps=24)

@app.route('/create-video', methods=['POST'])
def create_video_route():
    data = request.json
    images = data['images']
    subtitles = data['subtitles']
    
    create_video(images, subtitles)
    
    return send_file('output.mp4', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
