
import os
import sendgrid
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64
import requests

# Get the SendGrid API Key from environment variables
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL') # The email you verified with SendGrid

def send_video_to_client(recipient_email, video_url, project_name):
    """
    Sends the generated video to the client via email using SendGrid.
    The video is downloaded and attached directly to the email.
    """
    if not SENDGRID_API_KEY or not SENDER_EMAIL:
        raise ValueError("SENDGRID_API_KEY and SENDER_EMAIL environment variables must be set.")

    # 1. Download the video content from the URL
    try:
        print(f"[*] Downloading video from {video_url} to attach to email...")
        response = requests.get(video_url)
        response.raise_for_status()
        video_content = response.content
        print("[*] Video downloaded successfully.")
    except requests.exceptions.RequestException as e:
        print(f"[!] Failed to download the video for emailing: {e}")
        # Fallback: just send the link
        send_video_link_to_client(recipient_email, video_url, project_name)
        return

    # 2. Prepare the email
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=recipient_email,
        subject=f"Your Video for '{project_name}' is Ready!",
        html_content=f"""
        <p>Hello,</p>
        <p>Thank you for your order! Your custom video for the project '<strong>{project_name}</strong>' is complete and attached to this email.</p>
        <p>You can also download it directly from this link:</p>
        <p><a href='{video_url}'>Download Video</a></p>
        <p>We hope you love it!</p>
        <p>Best regards,<br>The Automated Video Team</p>
        """
    )

    # 3. Encode the video content and create the attachment
    encoded_file = base64.b64encode(video_content).decode()
    attachedFile = Attachment(
        FileContent(encoded_file),
        FileName(f'{project_name.replace(" ", "_")}_video.mp4'),
        FileType('video/mp4'),
        Disposition('attachment')
    )
    message.attachment = attachedFile

    # 4. Send the email
    try:
        sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"[*] Email sent to {recipient_email}. Status code: {response.status_code}")
    except Exception as e:
        print(f"[!] An error occurred while sending the email: {e}")
        raise

def send_video_link_to_client(recipient_email, video_url, project_name):
    """ A fallback method to send only the video link if the attachment fails. """
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=recipient_email,
        subject=f"Your Video for '{project_name}' is Ready!",
        html_content=f"""
        <p>Hello,</p>
        <p>Thank you for your order! Your custom video for the project '<strong>{project_name}</strong>' is ready.</p>
        <p>You can download it directly from this link:</p>
        <p><a href='{video_url}'>Download Video</a></p>
        <p>We hope you love it!</p>
        <p>Best regards,<br>The Automated Video Team</p>
        """
    )
    try:
        sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"[*] Fallback email (link only) sent to {recipient_email}. Status code: {response.status_code}")
    except Exception as e:
        print(f"[!] An error occurred while sending the fallback email: {e}")
        raise

# Example usage (for testing)
if __name__ == '__main__':
    # You need to set SENDGRID_API_KEY and SENDER_EMAIL in your environment.
    from dotenv import load_dotenv
    load_dotenv()

    if not os.environ.get("SENDGRID_API_KEY") or not os.environ.get("SENDER_EMAIL"):
        print("[!] Please set SENDGRID_API_KEY and SENDER_EMAIL in your .env file to run this test.")
    else:
        # This is a real video URL, you can use it for testing.
        test_video_url = "https://res.cloudinary.com/dk9n3er7g/video/upload/v1703348279/merged_video.mp4"
        test_recipient = "test@example.com" # Change to your email to receive the test
        test_project = "My Awesome Test Project"
        
        print(f"[*] Running notification test for {test_project}...")
        try:
            send_video_to_client(test_recipient, test_video_url, test_project)
            print(f"\n[+] Test complete. Email sent to {test_recipient}.")
        except Exception as e:
            print(f"\n[!] Test failed: {e}")
