import requests
import sys, getopt, os 
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag

directory_path = "./data/"

def create_save_directory() -> None:
    directory = Path(directory_path)
    try:
        directory.mkdir()
        print("Directory created successfully.\n")
    except FileExistsError:
        print("Directory " + directory_path + " already exist\n")


def fetch_page(page_url) -> bytes:
    try:
        r = requests.get(page_url, headers={"User-Agent": "USER_AGENT"})
        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error\n" + page_url)
        raise
    print(r.status_code)
    return r.content

def extract_images(content, page_url) -> set[str]:
    
    set_imgs = set()
    soup = BeautifulSoup(content, 'html.parser')

    images = soup.find_all('img')
    print(len(images))
    for image in images:
        img_url = urljoin(page_url, image.get('src'))
        parsed_url = urlparse(img_url)
        path = parsed_url.path
        if os.path.basename(path).endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            set_imgs.add(img_url)
    return set_imgs

def extract_links(content, page_url) -> set[str]:
    
    set_links = set()
    set_links.add(page_url)

    soup = BeautifulSoup(content, 'html.parser')
    links = soup.find_all('a')

    for link in links:
        link_url = link.get('href')

        if not link_url or link_url.startswith('#'):
            continue

        full_url = urljoin(page_url, link_url)
        full_url = urldefrag(full_url).url

        if urlparse(full_url).netloc != urlparse(page_url).netloc:
            continue

        if full_url in set_links:
            continue

        set_links.add(full_url)
        print(full_url)
    return set_links

def download_img(img_url) -> None:
    try:
        r = requests.get(img_url, headers={"User-Agent": "USER_AGENT"})
        r.raise_for_status()
        img_data = r.content
        parsed_url = urlparse(img_url)
        img_path = parsed_url.path
        with open(directory_path + os.path.basename(img_path), 'wb') as file:
            file.write(img_data)
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error\n" + img_url)
        raise
    print(img_url + ":" + str(r.status_code))


def scrape(page_url) -> None:
    try:
        print(page_url)
        content = fetch_page(page_url)
        set_imgs = extract_images(content, page_url)
        for img_url in set_imgs:
            download_img(img_url)
        set_links = extract_links(content, page_url)
    except Exception as e:
        print("Error:", e)

def main() -> None:
    create_save_directory()
    scrape(sys.argv[1])
    

if __name__ == '__main__':
    main()