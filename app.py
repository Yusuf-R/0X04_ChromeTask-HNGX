from flask import Flask, request, jsonify, send_from_directory
import os
import whisper
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 Mb


VIDEO_ID_FILE = "current_video_id.txt"

# Model for Video
class Video:
  """Template for the video class."""
  def __init__(self, video_id):
    """constructor"""
    self.id = video_id
    self.completed = False


# Store information about ongoing recordings
ongoing_recordings = {}

# setup whisper for video transcription
model = whisper.load_model("tiny.en")


# Load the current video ID from the file
# Load the current video ID from the file or generate a new one
def load_or_generate_video_id():
    """load the current video ID from the file or generate a new one"""
    try:
        with open(VIDEO_ID_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return str(uuid.uuid4())

# Save the current video ID to the file
def save_current_video_id(video_id):
    """Save the current video ID to the file"""
    with open(VIDEO_ID_FILE, "w") as f:
        f.write(video_id)

@app.route('/create', methods=['POST'])
def create_video_instance():
    """API endpoint to create a new video instance"""
    # Load or generate the current video ID
    video_id = load_or_generate_video_id()

    # If the video ID is not in ongoing_recordings, initialize it
    if video_id not in ongoing_recordings:
        ongoing_recordings[video_id] = {'chunks': [], 'completed': False}

    # Save the video ID to the file
    save_current_video_id(video_id)

    return jsonify({"id": video_id}), 201
  
  

@app.route('/update/<video_id>/<int:chunk_index>', methods=['POST'])
def update_video_chunk(video_id, chunk_index):
    """Update a video chunk"""
    if video_id not in ongoing_recordings:
        return jsonify({"error": "Invalid video ID"}), 400

    video_data = request.data  # Access raw data from the request body
    print(f"Received chunk {chunk_index}: {len(video_data)} bytes")

    if not video_data and request.headers.get('X-Last-Chunk') != 'true':
        return jsonify({"error": "No video data provided"}), 400

    # Append the received chunk to the ongoing recording
    ongoing_recordings[video_id]['chunks'].append({'index': chunk_index, 'data': video_data})

    # Check if this is the last chunk
    if request.headers.get('X-Last-Chunk') == 'true':
        return jsonify({"message": "Last chunk received. Recording ongoing"}), 200

    return jsonify({"message": "Chunk received successfully"}), 200

@app.route('/complete/<video_id>', methods=['PUT'])
def complete_video_recording(video_id):
    if video_id not in ongoing_recordings:
        return jsonify({"error": "Invalid video ID"}), 400

    # Set the 'completed' flag to True to indicate that recording is complete
    ongoing_recordings[video_id]['completed'] = True

    # Transcribe audio content after the recording is complete
    sorted_chunks = sorted(ongoing_recordings[video_id]['chunks'], key=lambda x: x['index'])
    video_content = b''.join(chunk['data'] for chunk in sorted_chunks)

    # Save the complete video to disk
    video_filename = f"{video_id}.mp4"
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
    with open(video_path, 'wb') as f:
        f.write(video_content)

    return jsonify({
        "message": "Recording completed",
        "video_url": f"/videos/{video_filename}"
    }), 200



# @app.route('/update/<video_id>/<int:chunk_index>', methods=['POST'])
# def update_video_chunk(video_id, chunk_index):
#     if video_id not in ongoing_recordings:
#         return jsonify({"error": "Invalid video ID"}), 400

#     video_data = request.data  # Access raw data from the request body
#     print(f"Received chunk {chunk_index}: {len(video_data)} bytes")

#     if not video_data and request.headers.get('X-Last-Chunk') != 'true':
#         return jsonify({"error": "No video data provided"}), 400

#     # Append the received chunk to the ongoing recording
#     ongoing_recordings[video_id]['chunks'].append({'index': chunk_index, 'data': video_data})

#     # Check if this is the last chunk
#     if request.headers.get('X-Last-Chunk') == 'true':
#         # Sort the chunks based on index
#         sorted_chunks = sorted(ongoing_recordings[video_id]['chunks'], key=lambda x: x['index'])
        
#         # Concatenate chunks to reconstruct the complete video
#         video_content = b''.join(chunk['data'] for chunk in sorted_chunks)
#         print(f"Video content after join {len(video_content)} bytes")

#         # Save the complete video to disk
#         video_filename = f"{video_id}.mp4"
#         # Replace this with your logic to save the file
#         with open(video_filename, 'wb') as f:
#             f.write(video_content)

#         return jsonify({"message": "Last chunk received. Processing complete"}), 200

#     return jsonify({"message": "Chunk received successfully"}), 200


# @app.route('/complete/<video_id>', methods=['PUT'])
# def complete_video_recording(video_id):
#     if video_id not in ongoing_recordings:
#         return jsonify({"error": "Invalid video ID"}), 400

#     # Set the 'completed' flag to True to indicate that recording is complete
#     ongoing_recordings[video_id]['completed'] = True
    
#     # Transcribe audio content after the recording is complete
#     audio_content = b''.join(ongoing_recordings[video_id]['chunks'])
#     result = model.transcribe(audio_content)
#     transcription = result['segment']  

#     # Save the complete video to disk
#     video_filename = f"{video_id}.mp4"
#     video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
#     with open(video_path, 'wb') as f:
#         f.write(audio_content)

#     return jsonify({
#         "message": "Recording completed",
#         "transcription": transcription,
#         "video_url": f"/videos/{video_filename}"
#     }), 200


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