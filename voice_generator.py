
import os
import requests
import uuid

# Get the ElevenLabs Proxy URL from environment variables
ELEVENLABS_PROXY_URL = os.environ.get("ELEVENLABS_PROXY_URL")

def generate_voice_over(script_text):
    """
    Generates a voice-over MP3 from the given script using the ElevenLabs proxy.

    Args:
        script_text (str): The text to be converted to speech.

    Returns:
        str: The local file path of the saved MP3 audio file.
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
        
        # Ensure the /tmp directory exists if you are running in a standard Linux environment
        # On Render, the filesystem is ephemeral, so saving to the root or a temp folder is fine.
        temp_filepath = os.path.join("/tmp", temp_filename)
        if not os.path.exists("/tmp"):
             os.makedirs("/tmp") # For local testing if /tmp doesn't exist


        # Save the audio content to the file
        with open(temp_filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"[*] Audio file successfully saved to {temp_filepath}")
        return temp_filepath

    except requests.exceptions.RequestException as e:
        print(f"[!] Error calling ElevenLabs Proxy: {e}")
        # Log the response content if available for more details
        if e.response is not None:
            print(f"[!] Response status: {e.response.status_code}")
            print(f"[!] Response body: {e.response.text}")
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
