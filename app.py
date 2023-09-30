# app.py

from flask import Flask, request, jsonify, send_from_directory
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Store information about ongoing recordings
ongoing_recordings = {}

@app.route('/create', methods=['POST'])
def create_video_instance():
    # Generate a new video ID using uuid.uuid4()
    video_id = str(uuid.uuid4())
    ongoing_recordings[video_id] = {'chunks': [], 'completed': False}
    return jsonify({"id": video_id}), 201

@app.route('/update/<video_id>', methods=['PUT'])
def update_video_chunk(video_id):
    if video_id not in ongoing_recordings:
        return jsonify({"error": "Invalid video ID"}), 400

    video_file = request.files.get('video')
    if not video_file:
        return jsonify({"error": "No video file provided"}), 400

    # Append the received chunk to the ongoing recording
    chunk = video_file.read()
    ongoing_recordings[video_id]['chunks'].append(chunk)

    return jsonify({"message": "Chunk received successfully"}), 200

@app.route('/complete/<video_id>', methods=['PUT'])
def complete_video_recording(video_id):
    if video_id not in ongoing_recordings:
        return jsonify({"error": "Invalid video ID"}), 400

    # Set the 'completed' flag to True to indicate that recording is complete
    ongoing_recordings[video_id]['completed'] = True

    return jsonify({"message": "Recording completed"}), 200

@app.route('/render/<video_id>')
def render_video(video_id):
    if video_id not in ongoing_recordings or not ongoing_recordings[video_id]['completed']:
        return jsonify({"error": "Recording not found or not yet completed"}), 404

    # Concatenate chunks to reconstruct the complete video
    video_content = b''.join(ongoing_recordings[video_id]['chunks'])

    # Save the complete video to disk
    video_filename = f"{video_id}.mp4"
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
    with open(video_path, 'wb') as f:
        f.write(video_content)

    return jsonify({"message": "Video rendered successfully", "video_url": f"/videos/{video_filename}"}), 200

@app.route('/videos/<video_filename>')
def play_video(video_filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], video_filename)

if __name__ == '__main__':
    app.run(debug=True)
