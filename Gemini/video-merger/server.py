from flask import Flask, request, jsonify, send_file
import requests
import uuid
import os
import subprocess
import sys # Added for sys.stdout.flush()

app = Flask(__name__)

@app.route("/merge", methods=["POST"])
def merge_video():
    try:
        data = request.get_json()
        audio_url = data.get("audio_url")
        image_url = data.get("image_url")

        if not audio_url or not image_url:
            return jsonify({"error": "Missing audio_url or image_url"}), 400

        uid = uuid.uuid4().hex
        audio_path = f"/tmp/audio_{uid}.mp3"
        image_path = f"/tmp/image_{uid}.jpg"
        output_path = f"/tmp/output_{uid}.mp4"

        print(f"[*] Downloading audio from: {audio_url}")
        sys.stdout.flush()
        with requests.get(audio_url, stream=True) as r:
            r.raise_for_status()
            with open(audio_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"[*] Audio downloaded to: {audio_path}")
        sys.stdout.flush()

        print(f"[*] Downloading image from: {image_url}")
        sys.stdout.flush()
        with requests.get(image_url, stream=True) as r:
            r.raise_for_status()
            with open(image_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"[*] Image downloaded to: {image_path}")
        sys.stdout.flush()

        command = [
            "ffmpeg",
            "-y", # Overwrite output files without asking
            "-loop", "1",
            "-i", image_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            "-vf", "scale=1280:720",
            "-pix_fmt", "yuv420p",
            output_path
        ]
        
        print(f"[*] Executing FFmpeg command: {' '.join(command)}")
        sys.stdout.flush()

        # Execute FFmpeg and capture its output
        process = subprocess.run(command, capture_output=True, text=True, check=False)
        
        print(f"[*] FFmpeg stdout:\n{process.stdout}")
        print(f"[*] FFmpeg stderr:\n{process.stderr}")
        print(f"[*] FFmpeg exit code: {process.returncode}")
        sys.stdout.flush()

        if process.returncode != 0:
            raise Exception(f"FFmpeg failed with exit code {process.returncode}. Stderr: {process.stderr}")

        # Check if the output file was actually created and is not empty
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise Exception(f"FFmpeg did not create a valid output file. Path: {output_path}, Size: {os.path.getsize(output_path)}. FFmpeg Stderr: {process.stderr}")

        print(f"[*] Video merged successfully to: {output_path}")
        sys.stdout.flush()

        # Clean up temporary files
        if os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"[*] Cleaned up temporary audio file: {audio_path}")
            sys.stdout.flush()
        if os.path.exists(image_path):
            os.remove(image_path)
            print(f"[*] Cleaned up temporary image file: {image_path}")
            sys.stdout.flush()
        
        # Send the file and then clean it up
        response = send_file(output_path, mimetype="video/mp4")
        
        # Schedule cleanup of the output video file after sending
        @response.call_on_close
        def cleanup_output_file():
            if os.path.exists(output_path):
                os.remove(output_path)
                print(f"[*] Cleaned up temporary output video file: {output_path}")
                sys.stdout.flush()

        return response

    except requests.exceptions.RequestException as e:
        print(f"[!] Error downloading audio or image: {e}")
        if e.response is not None:
            print(f"[!] Response status: {e.response.status_code}")
            print(f"[!] Response body: {e.response.text}")
        return jsonify({"error": f"Failed to download input files: {e}"}), 500
    except Exception as e:
        print(f"[!] An error occurred during video merging: {e}")
        sys.stdout.flush()
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return "FFmpeg Video Merger is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
