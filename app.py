from flask import Flask, request, jsonify
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, AudioFileClip

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to your Flask App!"

@app.route('/test-access', methods=['GET'])
def test_access():
    try:
        # Try to access a sample file
        with open('path_to_your_file', 'r') as f:
            content = f.read()  # Attempt to read the file
        return jsonify({"message": "File accessed successfully!", "content": content}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/create-video', methods=['POST'])
def create_video():
    data = request.json
    image_paths = data.get('images')
    audio_path = data.get('audio')
    subtitles = data.get('subtitles')

    if not image_paths or (audio_path is None and not subtitles):
        return jsonify({"error": "Invalid input data. Please provide images and either audio or subtitles."}), 400

    try:
        clips = [VideoFileClip(image).set_duration(2) for image in image_paths]
        video = concatenate_videoclips(clips, method="compose")

        if subtitles:
            subtitle_clips = [
                TextClip(txt=sub["text"], fontsize=24, color='white')
                .set_position(('center', 'bottom'))
                .set_start(sub['start'])
                .set_duration(sub['duration'])
                for sub in subtitles
            ]
            video = CompositeVideoClip([video, *subtitle_clips])

        if audio_path:
            audio = AudioFileClip(audio_path)
            video = video.set_audio(audio)

        output_path = "final_video.mp4"
        video.write_videofile(output_path, codec="libx264")

        return jsonify({"message": "Video created successfully!", "output_path": output_path})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
