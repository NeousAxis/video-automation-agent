import os
import requests
import base64
from mailjet_rest import Client

# Get Mailjet credentials from environment variables
MAILJET_API_KEY = os.environ.get('MAILJET_API_KEY')
MAILJET_API_SECRET = os.environ.get('MAILJET_API_SECRET')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL') # The email you verified with Mailjet

def send_video_to_client(recipient_email, video_url, project_name):
    """
    Sends the generated video to the client via email using Mailjet.
    The video is downloaded and attached directly to the email.
    """
    if not all([MAILJET_API_KEY, MAILJET_API_SECRET, SENDER_EMAIL]):
        raise ValueError("Mailjet API credentials and sender email must be set in environment variables.")

    # 1. Download the video content
    try:
        print(f"[*] Downloading video from {video_url} to attach to email...")
        response = requests.get(video_url)
        response.raise_for_status()
        video_content = response.content
        print("[*] Video downloaded successfully.")
    except requests.exceptions.RequestException as e:
        print(f"[!] Failed to download video for emailing: {e}. Sending link only.")
        send_video_link_to_client(recipient_email, video_url, project_name)
        return

    # 2. Initialize Mailjet client
    mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3.1')

    # 3. Encode attachment
    encoded_content = base64.b64encode(video_content).decode('utf-8')

    # 4. Prepare email data
    data = {
        'Messages': [
            {
                "From": {
                    "Email": SENDER_EMAIL,
                    "Name": "Automated Video Team"
                },
                "To": [
                    {
                        "Email": recipient_email,
                        "Name": "Valued Client"
                    }
                ],
                "Subject": f"Your Video for '{project_name}' is Ready!",
                "HTMLPart": f"""
                    <h3>Hello,</h3>
                    <p>Thank you for your order! Your custom video for the project '<strong>{project_name}</strong>' is complete and attached to this email.</p>
                    <p>You can also download it directly from this link: <a href='{video_url}'>Download Video</a></p>
                    <p>We hope you love it!</p>
                """,
                "Attachments": [
                    {
                        "ContentType": "video/mp4",
                        "Filename": f"{project_name.replace(' ', '_')}_video.mp4",
                        "Base64Content": encoded_content
                    }
                ]
            }
        ]
    }

    # 5. Send the email
    try:
        result = mailjet.send.create(data=data)
        print(f"[*] Email sent to {recipient_email}. Status: {result.status_code}")
        if result.status_code != 200:
            print(f"[!] Mailjet Error: {result.json()}")
    except Exception as e:
        print(f"[!] An error occurred while sending email with Mailjet: {e}")
        raise

def send_video_link_to_client(recipient_email, video_url, project_name):
    """ A fallback method to send only the video link if the attachment fails. """
    mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3.1')
    data = {
        'Messages': [{
            "From": {"Email": SENDER_EMAIL, "Name": "Automated Video Team"},
            "To": [{"Email": recipient_email}],
            "Subject": f"Your Video for '{project_name}' is Ready!",
            "HTMLPart": f"""
                <h3>Hello,</h3>
                <p>Thank you for your order! Your custom video for '<strong>{project_name}</strong>' is ready.</p>
                <p>Please download it here: <a href='{video_url}'>Download Video</a></p>
            """
        }]
    }
    result = mailjet.send.create(data=data)
    print(f"[*] Fallback email (link only) sent. Status: {result.status_code}")