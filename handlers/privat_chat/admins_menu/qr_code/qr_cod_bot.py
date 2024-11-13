import os

import qrcode
from dotenv import load_dotenv

load_dotenv()

# URL для QR-коду
url = os.getenv('URL_BOT')

# Створення об'єкта QR-коду
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)

# Створення зображення QR-коду
img = qr.make_image(fill='black', back_color='white')

file_path = 'bot_qr_code.png'
# Збереження зображення
img.save(file_path)
