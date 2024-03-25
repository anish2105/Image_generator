#Importing libraries
import base64
import time
from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import io
from PIL import Image , UnidentifiedImageError
import secrets
from flask import send_file
import os

#Generating a secret key to prevent CRSF attacks
secret_key = secrets.token_hex(16)

#Initialising Flask app
app = Flask(__name__)
app.secret_key = secret_key
UPLOAD_FOLDER = 'Images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Global Hugging face token
HF_TOKEN = None

#Home page route
@app.route('/')
def index():
    return render_template('index.html')

#Route to get HF API key page
@app.route('/enter_api_key', methods=['GET'])
def enter_api_key():
    return render_template('enter_api.html')

#Route after getting HF token
@app.route('/enter_details', methods=['POST'])
def enter_details():
    api_key = request.form['api_key']
    n = len(api_key)
    # if not api_key.startswith("hf_") and not n <=10:
    #     return "Invalid API key! Please provide a valid Hugging Face token."
    
    #Instiatising HF token to input by user, it's validity is done in the HTML page through JS
    global HF_TOKEN
    HF_TOKEN = api_key
    return redirect(url_for('enter_details_page'))

#Route to page which takes prompt from user
@app.route('/enter_details_page', methods=['GET'])
def enter_details_page():
    return render_template('Txt_to_image.html')

#Once prompt to generate text is provided, our model generates the prompt
@app.route('/submit_details', methods=['POST'])
def submit_details():
    prompt = request.form['name']

    # Header for Hugging Face API authorization
    header_token = "Bearer " + HF_TOKEN
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": header_token}

    try:
        # API call
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        image_bytes = response.content
        image = Image.open(io.BytesIO(image_bytes))
        image.show()
        # return "Image generated successfully!"
        timestamp = int(time.time())
        image_path = os.path.join(UPLOAD_FOLDER, f"generated_image_{timestamp}.jpg")
        image.save(image_path)

        return redirect(url_for('display_image', filename=image_path))

    except UnidentifiedImageError:
        flash("Please enter a correct API key.")
        return redirect(url_for('enter_api_key'))

@app.route('/display_image/<filename>')
def display_image(filename):
    return render_template('display_image.html', image_path=filename)

@app.route('/download_image/<image_path>')
def download_image(image_path):
    return send_file(image_path, as_attachment=True)


# if __name__ == '__main__':
#     app.run(debug=True)
