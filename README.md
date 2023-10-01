# Video Transcription API

This API allows you to perform video transcription by uploading video files in chunks and obtaining the transcribed text once the upload is complete.

## Getting Started

These instructions will help you set up and run the API on your local machine for development and testing purposes.

### Prerequisites

Make sure you have the following installed on your machine:

- Python (version 3.6 or higher)
- pip (Python package installer)

### Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
### Running the API
1. Start the Flask application:
   ```bash
   python app.py
   ```
The API will be accessible at http://127.0.0.1:5000/ locally
or via render
https://tavish-chrome.onrender.com


## API Endpoints
1. Create Video Instance
- Endpoint:` /create`
- Method: POST
- Description: Generates a new video ID for a recording session.

Example:
```bash
curl -X POST http://127.0.0.1:5000/create
```
or 
```bash
curl -X POST https://tavish-chrome.onrender.com/create
```

Response:
```
{"id": "9b485351-cb75-45a1-919c-6fe369bd7c63"}
```

2. Update Video Chunk
- Endpoint:`/update/<video-id>`
- Method: `PUT`
- Description: Update the chunk of the video file base on its id.

Example:
```bash
curl -X PUT --data-binary "@video_chunk.mp4" http://127.0.0.1:5000/update/9b485351-cb75-45a1-919c-6fe369bd7c63 -H "Content-Type: multipart/form-data"
```
or 
```bash
curl -X PUT --data-binary "@video_chunk.mp4" http://tavish-chrome.onrender.com/update/9b485351-cb75-45a1-919c-6fe369bd7c63 -H "Content-Type: multipart/form-data"
```

Response:
```
{"message": "Chunk received successfully"}
```


3. Complete Video Recording
- Endpoint:`/complete/<video-id>`
- Method: `PUT`
- Description: Marks the video recording as complete and returns the transcription.


Example:
```bash
curl -X PUT http://127.0.0.1:5000/complete/9b485351-cb75-45a1-919c-6fe369bd7c63
```
or
```bash
curl -X PUT http://tavish-chrome.onrender.com/complete/9b485351-cb75-45a1-919c-6fe369bd7c63
```

Response:
```
{
  "message": "Recording completed",
  "transcription": "Transcribed text goes here.",
  "video_url": "/videos/9b485351-cb75-45a1-919c-6fe369bd7c63.mp4"
}

```

4. Render Video
- Endpoint:`/render/<video-id>`
- Method: `GET`
- Description: Retrieves the video for rendering alongside the transcribed text


Example:
```bash
curl http://0.0.1:5000/render/9b485351-cb75-45a1-919c-6fe369bd7c63
```
or
```bash
curl http://tavish-chrome.onrender.com/render/9b485351-cb75-45a1-919c-6fe369bd7c63
```

Response:
```
{"message": "Video rendered successfully", "video_url": "/videos/9b485351-cb75-45a1-919c-6fe369bd7c63.mp4"}

```
## License
This project is licensed under the MIT License - see the LICENSE file for details.
