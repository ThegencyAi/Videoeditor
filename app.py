from flask import Flask, request, jsonify
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, AudioFileClip
import os

app = Flask(__name__)

# Define your API key (for demonstration; in a real application, use environment variables)
API_KEY = 'bravo1122'  # Replace with your actual API key

# Define the home route
@app.route('/')
def home():
    return "Welcome to your Flask App!"

# Define an API route to create a video
@app.route('/create-video', methods=['POST'])
def create_video():
    # Check for API key in the request headers
    api_key = request.headers.get('x-api-key')
    if api_key != API_KEY:
        return jsonify({"error": "Unauthorized: Invalid API Key"}), 401

    # Extract data from the POST request (images, audio, and subtitles)
    data = request.json
    image_paths = data.get('images')  # List of image paths
    audio_path = data.get('audio')     # Path to audio file
    subtitles = data.get('subtitles')  # List of subtitles with timestamps

    if not image_paths or (audio_path is None and not subtitles):
        return jsonify({"error": "Invalid input data. Please provide images and either audio or subtitles."}), 400

    try:
        # Create video from images
        clips = [VideoFileClip(image).set_duration(2) for image in image_paths]
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
        if audio_path:
            audio = AudioFileClip(audio_path)
            video = video.set_audio(audio)

        # Save the final video
        output_path = "final_video.mp4"
        video.write_videofile(output_path, codec="libx264")

        return jsonify({"message": "Video created successfully!", "output_path": output_path})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
