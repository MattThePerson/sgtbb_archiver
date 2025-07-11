""" 
r/SoGoodToBeBad downloader

This script does the following:
- scrapes the network of u/katiethebandit2 posts on r/SoGoodToBeBad starting from the 3 root posts (can take several minutes) & saves scraped data to pickle format
- generates html site from data
- alters html site to open links in CandyPopGallery app
- checks if media exists for each media link and attempts to download
- exports site to CPop-Gall app

"""
import argparse
import json
import pickle
import os

from pprint import pprint

from fun.s1_scrape import fetch_post_network
from fun.s2_generate import generate_html_pages


# Primary URLS
root_urls = [
    # Full Gif Archive:
    # - Alphabetical archive of performers pages
    # - Links to performers pages
    'https://www.reddit.com/user/katiethebandit2/comments/k6bngd/full_gif_archive_rsogoodtobebad/',

    # Full Category Gif Archive:
    # - Links to category pages
    # - category pages organized by date
    # - 25 links (+ lesbian archive, which links to 7 category pages)
    'https://www.reddit.com/user/katiethebandit2/comments/ktb6g5/full_category_gif_archive_rsogoodtobebad/',

    # Gif Series:
    # - Links to around 15 gif series pages
    # - *is also a category page (linked to by gif archive)
    'https://www.reddit.com/user/katiethebandit2/comments/v7xxiz/list_of_sogoodtobebad_gif_series/',
]


def main(args, download_dir, export_dir):
    
    if args.scrape_post_network:
        print('Scraping post network ...')
        global root_urls
        posts_dict = fetch_post_network(root_urls, quiet=args.quiet, pause_between=args.pause_between, pause_timeout=args.pause_timeout)
        save_post_network(posts_dict)
    
    
    saved_data_filenames = sorted([f for f in os.listdir('data/') if f.endswith('.pkl')], reverse=True)
    if args.list_saved:
        print('SAVED POST OBJECTS:')
        for idx, fn in enumerate(saved_data_filenames):
            print('{:>3} : "{}"'.format(idx+1, fn))
    
    
    
    if args.generate_html: # -select
        posts_dict = load_post_network(saved_data_filenames[args.select-1])
        if posts_dict:
            generate_html_pages(posts_dict)
        
        
    
    if args.integrate: # -download
        ...
    
    if args.export:
        ...










#### MISC. HELPER FUNCTIONS ####


def load_post_network(fn):
    fp = os.path.join('data', fn)
    print('Loading data from: "{}"'.format(fp))
    try:
        with open(fp, 'rb') as f:
            data = pickle.load(f)
        return data
    except Exception as e:
        print('ERROR: Unable to read data')
        print(e)
        return None

def save_post_network(dict):
    from datetime import datetime
    dt = datetime.now().strftime(r'%Y-%m-%dT%H-%M-%S')
    fn = f'post_objects_{dt}.pkl'
    print(fn)
    fp = os.path.join( 'data', fn )
    with open(fp, 'wb') as f:
        pickle.dump(dict, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scraper and Downloader for the network of curated posts on r/SoGoodToBeBad")
    
    # parser.add_argument('-wtf', action='store_true', help='wtf')
    parser.add_argument('--scrape-post-network', '-s1', action='store_true',    help='[STEP 1] Scrapes network of posts starting from the 3 root nodes')
    parser.add_argument('--generate-html', '-s2', action='store_true',          help='[STEP 2] Generates hyperlinked HTML pages from scraped network (deletes old HTML pages)')
    parser.add_argument('--integrate', '-s3', action='store_true',              help='[STEP 3] Changes HTML pages a-tags to point to local media')
    parser.add_argument('--download', '-d', action='store_true',                help='[STEP 3] Attempts to download media for media links without local media into "media_directory" from settings.json')
    parser.add_argument('--export', '-s4', action='store_true',                 help='[STEP 4] Copies HTML pages to "export_location" from settings.json')

    parser.add_argument('--list-saved', action='store_true',                    help='List saved post networks')
    parser.add_argument('--select', '-s',                                       help='Select which post objects to use (listed from newest to oldest) for STEP 2', type=int, default=1)
    parser.add_argument('--quiet', '-q', action='store_true',                   help='Suppresses normal printout from processes')
    parser.add_argument('--pause-between',                                      help='Number of seconds to pause between url requests', type=float, default=2)
    parser.add_argument('--pause-timeout',                                      help='Number of seconds to pause when recieved 429 status_code', type=float, default=60)
    
    args = parser.parse_args()
    
    with open('settings.json', 'r') as f:
        settings = json.load(f)
    
    print()
    try:
        main(args, settings.get('media_directory'), settings.get('export_location'))
    except KeyboardInterrupt:
        print('\n... Interrupted by KeyboardInterrupt')
    print()


