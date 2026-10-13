import requests
import sys, getopt, os 
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from pathlib import Path

directory_path = "./data/"

directory = Path(directory_path)

try:
    directory.mkdir()
    print("Directory created successfully.\n")
except FileExistsError:
    print("Directory " + directory_path + " already exist\n")

# print(sys.argv[1])
r = requests.get(
    sys.argv[1],
    headers={"User-Agent": "Spider42/1.0 (projet pédagogique)"}
    )
# r = requests.get(sys.argv[1])
print(r.status_code)
soup = BeautifulSoup(r.content, 'html.parser')

images = soup.find_all('img')
print(len(images))
for image in images:
    url = image.get('src')
    img_data = requests.get(url).content
    parsed_url = urlparse(url)
    path = parsed_url.path
    if os.path.basename(path).endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        with open(directory_path + os.path.basename(path), 'wb') as file:
            file.write(img_data)

