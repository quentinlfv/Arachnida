import requests
import argparse
import sys, getopt, os 
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag

directory_path = "./data/"

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog='my scrapper', description='scrapper')
    parser.add_argument("url", help="url to scrape")
    parser.add_argument("-r", action="store_true", help="enable recursivity")
    parser.add_argument("-l", type=int, default=5, help="max depth")
    parser.add_argument("-p", default="./data/", help="path to download images to")
    parser.print_help()
    args = parser.parse_args()
    if args.r == False:
        args.l = 1
    return args


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
        # if img_url in visited_urls:
        #     return 
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

def scrape(args, url, visited_urls, depth = 0) -> None:
    if depth >= args.l:
        return
    if url in visited_urls:
        return
    try:
        visited_urls.add(url)
        content = fetch_page(url)
        set_imgs = extract_images(content, url)
        print("number of imgs found:" + str(len(set_imgs)))
        for img_url in set_imgs:
            download_img(img_url)
            # visited_urls.add(img_url)
        set_links = extract_links(content, url)
        print("number of url found:" + str(len(set_links)))
        for link in set_links:
            scrape(args, link, visited_urls, depth + 1)
    except Exception as e:
        print("Error with url:" + url)


# def scrape(args) -> None:
#     try:
#         print(args.url)
#         content = fetch_page(args.url)
#         set_imgs = extract_images(content, args.url)
#         print("number img:" + str(len(set_imgs)))
#         for img_url in set_imgs:
#             download_img(img_url)
#         set_links = extract_links(content, args.url)
#         # if args.r == True:
#             # for link in links:
#                 # download_images_recusively(args, link)
#     except Exception as e:
#         print("Error:", e)

def main() -> None:
    args = parse_args()
    create_save_directory()
    visited_urls = set()
    # scrape(args)
    scrape(args, args.url, visited_urls)
    print(args.url)
    print(args.r)
    print(args.l)
    print(args.p)

if __name__ == '__main__':
    main()