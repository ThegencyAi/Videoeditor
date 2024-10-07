import os
import requests
from flask import Flask, request, jsonify
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, AudioFileClip

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to your Flask App!"

@app.route('/create-video', methods=['POST'])
def create_video():
    data = request.json
    image_urls = data.get('images')  # List of image URLs
    audio_url = data.get('audio')     # Audio file URL
    subtitles = data.get('subtitles')  # List of subtitles with timestamps

    # Validate input
    if not image_urls or (audio_url is None and not subtitles):
        return jsonify({"error": "Invalid input data. Please provide images and either audio or subtitles."}), 400

    try:
        # Create a directory to store downloaded files
        os.makedirs("downloads", exist_ok=True)

        # Download images from URLs
        local_image_paths = []
        for url in image_urls:
            response = requests.get(url)
            if response.status_code == 200:
                local_image_path = os.path.join("downloads", os.path.basename(url))
                with open(local_image_path, 'wb') as f:
                    f.write(response.content)
                local_image_paths.append(local_image_path)
            else:
                return jsonify({"error": f"Failed to download image from {url}"}), 400

        # Download audio from URL if provided
        local_audio_path = None
        if audio_url:
            response = requests.get(audio_url)
            if response.status_code == 200:
                local_audio_path = os.path.join("downloads", os.path.basename(audio_url))
                with open(local_audio_path, 'wb') as f:
                    f.write(response.content)
            else:
                return jsonify({"error": f"Failed to download audio from {audio_url}"}), 400

        # Create video from downloaded images
        clips = [VideoFileClip(img).set_duration(2) for img in local_image_paths]
        video = concatenate_videoclips(clips, method="compose")

        # Add subtitles if provided
        if subtitles:
            subtitle_clips = [
                TextClip(txt=sub["text"], fontsize=24, color='white')
                .set_position(('center', 'bottom'))
                .set_start(sub['start'])
                .set_duration(sub['duration'])
                for sub in subtitles
            ]
            video = CompositeVideoClip([video, *subtitle_clips])

        # Add audio to video if provided
        if local_audio_path:
            audio = AudioFileClip(local_audio_path)
            video = video.set_audio(audio)

        # Save the final video
        output_path = "final_video.mp4"
        video.write_videofile(output_path, codec="libx264")

        # Clean up downloaded files
        for img in local_image_paths:
            os.remove(img)
        if local_audio_path:
            os.remove(local_audio_path)

        return jsonify({"message": "Video created successfully!", "output_path": output_path})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
