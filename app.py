from flask import Flask, request, jsonify
from moviepy.editor import VideoFileClip, concatenate_videoclips
import os

app = Flask(__name__)

# Endpoint to upload images and audio to create a video
@app.route('/create-video', methods=['POST'])
def create_video():
    if 'audio' not in request.files or 'images' not in request.files:
        return jsonify({"error": "Audio and images are required"}), 400

    audio = request.files['audio']
    images = request.files.getlist('images')

    # Save audio and images locally
    audio.save('uploaded_audio.mp3')
    image_paths = []
    for index, image in enumerate(images):
        image_path = f'image_{index}.jpg'
        image.save(image_path)
        image_paths.append(image_path)

    # Create a video (this is just an example, you can modify it)
    clips = [VideoFileClip(image_path).set_duration(2) for image_path in image_paths]
    final_video = concatenate_videoclips(clips)
    final_video.write_videofile('output_video.mp4')

    return jsonify({"message": "Video created successfully!", "video_path": "output_video.mp4"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
