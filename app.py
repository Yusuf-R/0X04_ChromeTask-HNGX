from flask import Flask, request, jsonify, send_from_directory
import os
# import whisper
import uuid
from flask_cors import CORS

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 Mb
CORS(app, resources={r"/*": {"origins": "*"}})

# Store information about ongoing recordings
ongoing_recordings = {}

# setup whisper for video transcription
# model = whisper.load_model("tiny.en")

@app.route('/create', methods=['POST'])
def create_video_instance():
    # Generate a new video ID using uuid.uuid4()
    video_id = str(uuid.uuid4())
    ongoing_recordings[video_id] = {'chunks': [], 'completed': False}

    return jsonify({"id": video_id}), 201

@app.route('/update/<video_id>/<int:chunk_index>', methods=['PUT'])
def update_video_chunk(video_id, chunk_index):
    if video_id not in ongoing_recordings:
        return jsonify({"error": "Invalid video ID"}), 400

    video_file = request.files.get('video')
    if not video_file:
        return jsonify({"error": "No video file provided"}), 400

    # Append the received chunk to the ongoing recording
    chunk = video_file.read()
    print(f"Received chunk {chunk_index} for video {video_id}: {len(chunk)} bytes")
    ongoing_recordings[video_id]['chunks'].append({'index': chunk_index, 'data': chunk})

    # Check if this is the last chunk
    if request.headers.get('X-Last-Chunk') == 'true':
        # Sort the chunks based on index
        sorted_chunks = sorted(ongoing_recordings[video_id]['chunks'], key=lambda x: x['index'])
        
        # Concatenate chunks to reconstruct the complete video
        video_content = b''.join(chunk['data'] for chunk in sorted_chunks)

        # Continue with the rest of your logic (e.g., transcription, saving to disk)
        
        # Save the complete video to disk
        video_filename = f"{video_id}.mp4"
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
        with open(video_path, 'wb') as f:
            f.write(video_content)

        return jsonify({"message": "Last chunk received. Processing complete"}), 200

    return jsonify({"message": "Chunk received successfully"}), 200

@app.route('/complete/<video_id>', methods=['PUT'])
def complete_video_recording(video_id):
    if video_id not in ongoing_recordings:
        return jsonify({"error": "Invalid video ID"}), 400

    # Set the 'completed' flag to True to indicate that recording is complete
    ongoing_recordings[video_id]['completed'] = True
    
    # Transcribe audio content after the recording is complete
    audio_content = b''.join(ongoing_recordings[video_id]['chunks'])
    # result = model.transcribe(audio_content)
    transcription = " Hi " # result['segment']  

    # Save the complete video to disk
    video_filename = f"{video_id}.mp4"
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
    with open(video_path, 'wb') as f:
        f.write(audio_content)

    return jsonify({
        "message": "Recording completed",
        "transcription": transcription,
        "video_url": f"/videos/{video_filename}"
    }), 200

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

@app.route('/all_ids', methods=['GET'])
def get_all_video_ids():
    all_ids = [{'id': video_id, 'completed': ongoing_recordings[video_id]['completed']} for video_id in ongoing_recordings]
    return jsonify(all_ids), 200

if __name__ == '__main__':
    app.run(debug=True)
