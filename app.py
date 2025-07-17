from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    print("[*] DEBUG: Minimal App - Homepage accessed. This 
should definitely show up!")
    return "Gemini CLI: Minimal App Test - If you see this, 
the deployment is working!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
