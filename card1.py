import cv2
import easyocr
import re

# Load image directly (no grayscale to avoid reflection issue)
img = cv2.imread('Screenshot 2025-05-16 184810.png')

# Initialize OCR reader
reader = easyocr.Reader(['en'])

# Run OCR on the whole image
results = reader.readtext(img)

# Combine OCR text results
all_text = " ".join([res[1] for res in results])
print("OCR Raw Output:", all_text)

# Fix common OCR mistakes and extract numbers of length 13-19
matches = re.findall(r'(?:\d[\d\s\-OIl]{11,30}\d)', all_text)

card_number = None
for match in matches:
    match = match.replace('O', '0').replace('I', '1').replace('l', '1').replace('?', '')
    digits_only = re.sub(r'\D', '', match)
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
if card_number:
    print("Detected Card Number:", card_number)
else:
    print("Card number not detected.")
