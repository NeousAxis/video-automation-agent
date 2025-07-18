import os
import threading
from flask import Flask, request, jsonify, send_from_directory # Added send_from_directory
from dotenv import load_dotenv
import sys # Import sys for stdout.flush()

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
    print("[*] DEBUG: create_video_task function entered.")
    sys.stdout.flush() # Force flush

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
        sys.stdout.flush() # Force flush

        # 1. Generate script and image
        print("[*] DEBUG: Calling generate_script_and_image...")
        sys.stdout.flush() # Force flush
        script, image_url = generate_script_and_image(
            project_name, video_goal, central_message, tone, target_audience, call_to_action
        )
        print(f"[*] Script and image generated successfully.")
        print(f" - Script: {script[:80]}...")
        print(f" - Image URL: {image_url}")
        sys.stdout.flush() # Force flush


        # 2. Generate voice-over
        print("[*] DEBUG: Calling generate_voice_over...")
        sys.stdout.flush() # Force flush
        audio_file_url = generate_voice_over(script) # Changed to audio_file_url
        print(f"[*] Voice-over generated and saved to: {audio_file_url}") # Changed to audio_file_url
        sys.stdout.flush() # Force flush

        # 3. Merge image and audio into a video
        print("[*] DEBUG: Calling merge_audio_and_image...")
        sys.stdout.flush() # Force flush
        video_url = merge_audio_and_image(image_url, audio_file_url) # Changed to audio_file_url
        print(f"[*] Video merged successfully. URL: {video_url}")
        sys.stdout.flush() # Force flush

        # 4. Send the final video to the client
        print("[*] DEBUG: Calling send_video_to_client...")
        sys.stdout.flush() # Force flush
        send_video_to_client(client_email, video_url, project_name)
        print(f"[*] Video sent to {client_email}.")
        sys.stdout.flush() # Force flush

        # 5. Clean up local temporary files (optional but recommended)
        # Note: The audio file is now served from /tmp and will be cleaned up by the OS or on restart
        # if os.path.exists(audio_file_path): # This line is removed as audio_file_path is no longer returned
        #     os.remove(audio_file_path)
        #     print(f"[*] Cleaned up temporary file: {audio_file_path}")
        #     sys.stdout.flush() # Force flush

        print(f"[+] Video creation process for {project_name} completed successfully.")
        sys.stdout.flush() # Force flush

    except Exception as e:
        print(f"[!] An error occurred during the video creation process: {e}")
        sys.stdout.flush() # Force flush
        # Optional: Send an error notification to yourself
        # send_error_notification(str(e), form_data)


@app.route('/webhook/tally', methods=['POST'])
def tally_webhook():
    print("[*] DEBUG: Webhook function entered.")
    sys.stdout.flush() # Force flush
    """
    Receives the webhook from Tally.so, starts the video creation
    in a background thread, and returns an immediate response.
    """
    if request.json:
        print(f"[*] Received raw JSON from Tally: {request.json}")
        sys.stdout.flush() # Force flush
        data = request.json.get('data', {})
        fields = data.get('fields', [])

        # Transform the Tally fields array into a simple key-value dictionary
        form_data = {}
        field_mapping = {
            "What’s the name of your project or brand?": "projectName",
            "What’s the goal of your video?": "videoGoal",
            "What is the core message you want to convey?": "centralMessage",
            "What tone do you want for the video?": "tone",
            "Who is your target audience?": "targetAudience",
            "What should the final call-to-action be?": "callToAction",
            "What’s your email address to receive the final video?": "email"
        }

        for field in fields:
            label = field.get('label')
            key = field_mapping.get(label)
            if key:
                if field.get('type') == 'MULTIPLE_CHOICE':
                    selected_option_id = field.get('value')[0] if field.get('value') else None
                    if selected_option_id:
                        for option in field.get('options', []):
                            if option.get('id') == selected_option_id:
                                form_data[key] = option.get('text')
                                break
                else:
                    form_data[key] = field.get('value')
        print(f"[*] Debug: Parsed form_data: {form_data}")
        print(f"[*] Received form data: {form_data}")
        sys.stdout.flush() # Force flush

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
    print("[*] DEBUG: Homepage accessed. Original code is running!")
    sys.stdout.flush() # Force flush
    return "Video Automation Agent is running."

# New route to serve temporary files
@app.route('/temp_files/<path:filename>')
def serve_temp_file(filename):
    print(f"[*] Serving temporary file: {filename}")
    sys.stdout.flush()
    return send_from_directory('/tmp', filename)

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)