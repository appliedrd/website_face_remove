import os
import requests
from bs4 import BeautifulSoup
import face_recognition
from io import BytesIO
from PIL import Image
from requests.exceptions import ReadTimeout, RequestException, HTTPError
import time
import webbrowser
import tempfile

# Load the image of the person you want to recognize
known_image = face_recognition.load_image_file('match_img//trump.jpg')
known_face_encoding = face_recognition.face_encodings(known_image)[0]

# URL of the web page to parse
url = 'https://www.cbc.ca/news'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Function to fetch the web page with retry mechanism
def fetch_url_with_retries(url, retries=3, backoff_factor=1):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except ReadTimeout:
            print(f"Request to {url} timed out. Retrying in {backoff_factor * (2 ** attempt)} seconds...")
            time.sleep(backoff_factor * (2 ** attempt))
        except RequestException as e:
            print(f"Request to {url} failed: {e}")
            break
    return None

# Fetch the web page
response = fetch_url_with_retries(url)
if not response:
    print(f"Failed to fetch {url} after multiple attempts.")
    exit(1)

soup = BeautifulSoup(response.content, 'html.parser')

# Find all image tags
img_tags = soup.find_all('img')

# Extract and test only the first URL from srcset attribute
for img_tag in img_tags:
    srcset = img_tag.get('srcset')
    if srcset:
        # Extract the first URL from the srcset
        first_src = srcset.split(',')[0].split()[0]
    else:
        # Use the src attribute if srcset is not present
        first_src = img_tag.get('src')

    if first_src:
        if not first_src.startswith('https://'):
            print(f"Skipping non-https URL: {first_src}")
            continue

        try:
            # Fetch the image
            img_response = requests.get(first_src, headers=headers, timeout=10)
            img_response.raise_for_status()
        except ReadTimeout:
            print(f"Request to {first_src} timed out.")
            continue
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            continue

        img = Image.open(BytesIO(img_response.content))
        img_array = face_recognition.load_image_file(BytesIO(img_response.content))

        # Get face encodings for the image
        unknown_face_encodings = face_recognition.face_encodings(img_array)

        # Compare the known face encoding with the unknown face encodings
        results = face_recognition.compare_faces(unknown_face_encodings, known_face_encoding)

        # If the face is found in the image, remove the image tag from the soup
        if any(results):
            print(f"Trump's face is in the image: {first_src}")
            img_tag.decompose()
        else:
            print(f"Trump's face is not in the image: {first_src}")

# Save the modified HTML to a temporary file and open it in the default web browser
with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as temp_file:
    temp_file.write(soup.prettify().encode('utf-8'))
    webbrowser.open(f'file://{temp_file.name}')