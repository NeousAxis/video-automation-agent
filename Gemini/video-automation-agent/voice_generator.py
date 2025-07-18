import os
import requests
import uuid

# Get the ElevenLabs Proxy URL from environment variables
ELEVENLABS_PROXY_URL = os.environ.get("ELEVENLABS_PROXY_URL")

def generate_voice_over(script_text):
    """
    Generates a voice-over MP3 from the given script using the ElevenLabs proxy,
    saves it locally, and returns the public URL from the current application.
    """
    if not ELEVENLABS_PROXY_URL:
        raise ValueError("ELEVENLABS_PROXY_URL environment variable not set.")

    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "text": script_text
    }

    try:
        print(f"[*] Sending request to ElevenLabs Proxy at {ELEVENLABS_PROXY_URL}...")
        response = requests.post(ELEVENLABS_PROXY_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Generate a unique filename for the audio file
        temp_filename = f"temp_audio_{uuid.uuid4()}.mp3"
        temp_filepath = os.path.join("/tmp", temp_filename)
        if not os.path.exists("/tmp"):
             os.makedirs("/tmp") # For local testing if /tmp doesn't exist

        # Save the audio content to the file locally
        with open(temp_filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"[*] Audio file successfully saved locally to {temp_filepath}")

        # Construct the public URL for the audio file
        # This assumes your app is accessible via its Render URL
        # You might need to get the base URL from an environment variable if it's not fixed
        # For Render, it's usually https://YOUR_APP_NAME.onrender.com
        # Let's assume the base URL is available as an environment variable for robustness
        APP_BASE_URL = os.environ.get("RENDER_EXTERNAL_HOSTNAME") # Render provides this
        if not APP_BASE_URL:
            # Fallback for local testing or if variable is not set
            APP_BASE_URL = "http://localhost:5000" # Or your local development URL

        public_audio_url = f"https://{APP_BASE_URL}/temp_files/{temp_filename}" # Construct the URL
        print(f"[*] Public audio URL: {public_audio_url}")

        return public_audio_url # Return the public URL

    except requests.exceptions.RequestException as e:
        print(f"[!] Error during ElevenLabs API call: {e}")
        if e.response is not None:
            print(f"[!] Response status: {e.response.status_code}")
            print(f"[!] Response body: {e.response.text}")
        raise
    except Exception as e:
        print(f"[!] An unexpected error occurred in voice_generator: {e}")
        raise

# Example usage (for testing)
if __name__ == '__main__':
    # You need to set ELEVENLABS_PROXY_URL in your environment for this test.
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.environ.get("ELEVENLABS_PROXY_URL"):
        print("[!] Please set the ELEVENLABS_PROXY_URL in your .env file to run this test.")
    else:
        test_script = "Hello, this is a test of the voice generation system. If you can hear this, it means the proxy is working correctly."
        print("[*] Running voice generation test...")
        try:
            audio_path = generate_voice_over(test_script)
            print(f"\n[+] Test complete. Audio file saved at: {audio_path}")
            # You can play this file to verify
        except Exception as e:
            print(f"\n[!] Test failed: {e}")
