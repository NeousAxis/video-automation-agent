import os
import requests

# Get the Video Merger service URL from environment variables
VIDEO_MERGER_URL = os.environ.get("VIDEO_MERGER_URL")

def merge_audio_and_image(image_url, audio_url): # Changed audio_file_path to audio_url
    """
    Merges an image and an audio URL into a video using the video-merger service.

    Args:
        image_url (str): The public URL of the background image.
        audio_url (str): The public URL of the MP3 audio file (e.g., from your app's /temp_files endpoint).

    Returns:
        str: The URL of the generated MP4 video.
    """
    if not VIDEO_MERGER_URL:
        raise ValueError("VIDEO_MERGER_URL environment variable not set.")

    # The video-merger service now expects a JSON payload with URLs
    payload = {
        'audio_url': audio_url, # Changed to audio_url
        'image_url': image_url
    }
    headers = {
        "Content-Type": "application/json" # New: Specify JSON content type
    }

    try:
        print(f"[*] Sending request to Video Merger at {VIDEO_MERGER_URL} with JSON payload...")
        response = requests.post(VIDEO_MERGER_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        # The merger service returns a JSON payload with the video URL
        response_data = response.json()
        video_url = response_data.get('video_url')

        if not video_url:
            raise ValueError("Video URL not found in the response from the merger service.")

        return video_url

    except requests.exceptions.RequestException as e:
            print(f"[!] Error calling Video Merger service: {e}")
            if e.response is not None:
                print(f"[!] Response status: {e.response.status_code}")
                print(f" - Response body: {e.response.text}") # Added hyphen for clarity
            raise
