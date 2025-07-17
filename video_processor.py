
import os
import requests

# Get the Video Merger service URL from environment variables
VIDEO_MERGER_URL = os.environ.get("VIDEO_MERGER_URL")

def merge_audio_and_image(image_url, audio_file_path):
    """
    Merges an image and an audio file into a video using the video-merger service.

    Args:
        image_url (str): The public URL of the background image.
        audio_file_path (str): The local path to the MP3 audio file.

    Returns:
        str: The URL of the generated MP4 video.
    """
    if not VIDEO_MERGER_URL:
        raise ValueError("VIDEO_MERGER_URL environment variable not set.")

    # The video-merger service expects a multipart/form-data request
    with open(audio_file_path, 'rb') as audio_file:
        files = {
            'audio': (os.path.basename(audio_file_path), audio_file, 'audio/mpeg')
        }
        data = {
            'imageUrl': image_url
        }

        try:
            print(f"[*] Sending request to Video Merger at {VIDEO_MERGER_URL}...")
            response = requests.post(VIDEO_MERGER_URL, files=files, data=data)
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
                print(f"[!] Response body: {e.response.text}")
            raise

# Example usage (for testing)
if __name__ == '__main__':
    # This test requires a live image URL and a local audio file.
    # It also requires the VIDEO_MERGER_URL to be set in your environment.
    from dotenv import load_dotenv
    load_dotenv()

    if not os.environ.get("VIDEO_MERGER_URL"):
        print("[!] Please set the VIDEO_MERGER_URL in your .env file to run this test.")
    else:
        # Create a dummy audio file for testing purposes
        dummy_audio_path = "test_audio.mp3"
        with open(dummy_audio_path, 'w') as f:
            f.write("This is a dummy file.")

        # Use a placeholder image URL
        test_image_url = "https://fastly.picsum.photos/id/866/536/354.jpg?hmac=tGofDTV7tl2rpUxeA3MBNT_4LUrpN94M4epMBLC5vs4"
        
        print("[*] Running video processing test...")
        try:
            final_video_url = merge_audio_and_image(test_image_url, dummy_audio_path)
            print(f"\n[+] Test complete. Generated Video URL: {final_video_url}")
        except Exception as e:
            print(f"\n[!] Test failed: {e}")
        finally:
            # Clean up the dummy file
            if os.path.exists(dummy_audio_path):
                os.remove(dummy_audio_path)
