
import os
import threading
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Import your custom modules
from content_generator import generate_script_and_image
from voice_generator import generate_voice_over
from video_processor import merge_audio_and_image
from notification import send_video_to_client

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

def create_video_task(form_data):
    """
    The main task to be run in a background thread.
    It orchestrates the entire video creation process.
    """
    try:
        # Extract data from the form
        project_name = form_data.get("projectName")
        video_goal = form_data.get("videoGoal")
        central_message = form_data.get("centralMessage")
        tone = form_data.get("tone")
        target_audience = form_data.get("targetAudience")
        call_to_action = form_data.get("callToAction")
        client_email = form_data.get("email")

        print(f"[*] Starting video creation for {project_name}...")

        # 1. Generate script and image
        script, image_url = generate_script_and_image(
            project_name, video_goal, central_message, tone, target_audience, call_to_action
        )
        print(f"[*] Script and image generated successfully.")
        print(f" - Script: {script[:80]}...")
        print(f" - Image URL: {image_url}")


        # 2. Generate voice-over
        audio_file_path = generate_voice_over(script)
        print(f"[*] Voice-over generated and saved to: {audio_file_path}")

        # 3. Merge image and audio into a video
        video_url = merge_audio_and_image(image_url, audio_file_path)
        print(f"[*] Video merged successfully. URL: {video_url}")

        # 4. Send the final video to the client
        send_video_to_client(client_email, video_url, project_name)
        print(f"[*] Video sent to {client_email}.")

        # 5. Clean up local temporary files (optional but recommended)
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)
            print(f"[*] Cleaned up temporary file: {audio_file_path}")

        print(f"[+] Video creation process for {project_name} completed successfully.")

    except Exception as e:
        print(f"[!] An error occurred during the video creation process: {e}")
        # Optional: Send an error notification to yourself
        # send_error_notification(str(e), form_data)


@app.route('/webhook/tally', methods=['POST'])
def tally_webhook():
    """
    Receives the webhook from Tally.so, starts the video creation
    in a background thread, and returns an immediate response.
    """
    if request.json:
        form_data = request.json.get('data', {})
        
        # Run the video creation process in a background thread
        # to avoid Tally webhook timeouts.
        thread = threading.Thread(target=create_video_task, args=(form_data,))
        thread.start()
        
        # Immediately confirm receipt to Tally
        return jsonify({'status': 'success', 'message': 'Video creation process started.'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid request format.'}), 400

@app.route('/', methods=['GET'])
def index():
    return "Video Automation Agent is running."

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
