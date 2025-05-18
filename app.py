import os
import re
import cv2
import easyocr
import requests
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# HandyAPI details (replace with your actual API key)
HANDYAPI_KEY = 'PUB-0YQwrTh5d98gp8407utCy'
HANDYAPI_URL = 'https://data.handyapi.com/bin/'

# Initialize OCR reader globally for efficiency
reader = easyocr.Reader(['en'])

def extract_card_number(image_path):
    img = cv2.imread(image_path)
    results = reader.readtext(img)
    all_text = " ".join([res[1] for res in results])

    matches = re.findall(r'(?:\d[\d\s\-OIl]{11,30}\d)', all_text)

    card_number = None
    for match in matches:
        cleaned = match.replace('O', '0').replace('I', '1').replace('l', '1').replace('?', '')
        digits_only = re.sub(r'\D', '', cleaned)
        length = len(digits_only)

        if 13 <= length <= 19:
            if length == 13:
                card_number = f"{digits_only[:4]} {digits_only[4:9]} {digits_only[9:]}"
            elif length == 14:
                card_number = f"{digits_only[:4]} {digits_only[4:10]} {digits_only[10:]}"
            elif length == 15:
                card_number = f"{digits_only[:4]} {digits_only[4:10]} {digits_only[10:]}"
            elif length == 16:
                card_number = " ".join([digits_only[i:i+4] for i in range(0, 16, 4)])
            elif length == 17:
                card_number = f"{digits_only[:4]} {digits_only[4:9]} {digits_only[9:13]} {digits_only[13:]}"
            elif length == 18:
                card_number = f"{digits_only[:4]} {digits_only[4:10]} {digits_only[10:14]} {digits_only[14:]}"
            elif length == 19:
                card_number = f"{digits_only[:4]} {digits_only[4:10]} {digits_only[10:15]} {digits_only[15:]}"
            break

    return card_number

def check_card_with_handyapi(card_number, api_key):
    digits_only = card_number.replace(" ", "")
    bin_number = digits_only[:8]
    url = f'{HANDYAPI_URL}{bin_number}'
    headers = {'x-api-key': api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': f'HandyAPI request failed with status {response.status_code}'}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'card_image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['card_image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filepath = os.path.join('uploads', file.filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(filepath)

            card_number = extract_card_number(filepath)
            if not card_number:
                flash('Could not detect card number in image.')
                return redirect(request.url)

            validation_result = check_card_with_handyapi(card_number, HANDYAPI_KEY)

            # Check if the card type is CREDIT, else flash error and redirect
            if 'Type' in validation_result:
                if validation_result['Type'].upper() != 'CREDIT':
                    flash('The detected card is NOT a Credit card. Only Credit cards are allowed.')
                    return redirect(request.url)
            else:
                # Handle cases where 'Type' field is missing or error in response
                if 'error' in validation_result:
                    flash(validation_result['error'])
                else:
                    flash('Could not verify card type from API.')
                return redirect(request.url)

            return render_template('index.html',
                                   card_number=card_number,
                                   validation=validation_result)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
