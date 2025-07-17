
import os
from openai import OpenAI

# Initialize the OpenAI client
# It will automatically use the OPENAI_API_KEY from your .env file
client = OpenAI()

def generate_script_and_image(project_name, video_goal, central_message, tone, target_audience, call_to_action):
    """
    Generates a video script using GPT-4 and a background image using DALL·E 3.

    Returns:
        tuple: A tuple containing the generated script (str) and the image URL (str).
    """
    
    # 1. Generate the video script
    script_prompt = f"""
    You are a professional scriptwriter for short, impactful promotional videos.
    Create a script for a 30-60 second video based on the following details:

    - **Project/Brand Name:** {project_name}
    - **Video Goal:** {video_goal}
    - **Core Message:** {central_message}
    - **Desired Tone:** {tone}
    - **Target Audience:** {target_audience}
    - **Call to Action:** {call_to_action}

    The script should have three parts: a compelling hook, a body that develops the message, and a clear call to action at the end. The total length should be suitable for a voice-over of around 30-60 seconds (approx. 90-150 words).
    
    Output ONLY the script text, without any titles, headings, or formatting.
    """

    try:
        script_response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a professional scriptwriter for short, impactful promotional videos."},
                {"role": "user", "content": script_prompt}
            ],
            temperature=0.7,
            max_tokens=250
        )
        script = script_response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[!] OpenAI Script Generation Error: {e}")
        raise

    # 2. Generate the background image
    image_prompt = f"""
    Create a visually stunning, high-quality, professional background image for a promotional video. The image should be abstract and cinematic, subtly reflecting the following themes:

    - **Core Message:** {central_message}
    - **Tone:** {tone}
    - **Project/Brand:** {project_name}

    The image must be clean, aesthetically pleasing, and suitable for overlaying text or a logo. Avoid any text or complex subjects. Focus on textures, gradients, and mood.
    Style: 16:9 aspect ratio, cinematic, high resolution.
    """

    try:
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            n=1,
            size="1792x1024",  # 16:9 aspect ratio
            quality="standard"
        )
        image_url = image_response.data[0].url
    except Exception as e:
        print(f"[!] OpenAI Image Generation Error: {e}")
        raise

    return script, image_url

# Example usage (for testing)
if __name__ == '__main__':
    # You would need to set up your OPENAI_API_KEY in your environment
    # for this test to work.
    from dotenv import load_dotenv
    load_dotenv()
    
    test_project = "InnovateSphere"
    test_goal = "Promote our new AI-driven analytics platform."
    test_message = "Unlock the power of your data with seamless, intelligent insights."
    test_tone = "Inspiring, professional, and slightly futuristic."
    test_audience = "Tech startups and data analysts."
    test_cta = "Visit innovatesphere.com to request a demo."

    print(f"[*] Running content generation test for {test_project}...")
    generated_script, generated_image_url = generate_script_and_image(
        test_project, test_goal, test_message, test_tone, test_audience, test_cta
    )
    print("\n--- Generated Script ---")
    print(generated_script)
    print("\n--- Generated Image URL ---")
    print(generated_image_url)
    print("\n[+] Test complete.")
