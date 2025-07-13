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
import pickle
import os
import json

from fun.s1_scrape import download_post_network_catalogue_pages
# from fun.s4_generate import generate_html_pages
from fun import s1_scrape, s2_parse, s4_generate


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


#reigon - MAIN ---------------------------------------------------------------------------------------------------------

def main(args):
    
    
    if args.scrape_post_network: # - [STEP 1] SCRAPE -----------------------------------------------
        print('Scraping post network ...')
        global root_urls
        posts_dict = s1_scrape.download_post_network_catalogue_pages(
            root_urls, 
            'src', 
            redo_scraping=args.redo_scraping, 
            quiet=args.quiet, 
            pause_between=args.pause_between, 
            pause_timeout=args.pause_timeout,
        )


    if args.parse_post_data: # - [STEP 2] PARSE ----------------------------------------------------
        catalogue_pages = os.listdir('site/catalogue')
        media_pages = os.listdir('site/meida_page')
        data = s2_parse.parse_data_from_html_pages(catalogue_pages, media_pages)
        _save_json_dated(data)



    if args.download_media: # - [STEP 3] DOWNLOAD --------------------------------------------------
        ...


    if args.generate_html_pages: # - [STEP 4] GENERATE ---------------------------------------------
        ...



    saved_data_filenames = sorted([f for f in os.listdir('data/') if f.endswith('.pkl')], reverse=True)

    if args.list_saved:
        print('SAVED POST OBJECTS:')
        for idx, fn in enumerate(saved_data_filenames):
            print('{:>3} : "{}"'.format(idx+1, fn))
    
    
    if args.integrate: # -download
        ...
    
    if args.export:
        ...




#reigon - HELPERS --------------------------------------------------------------------------------------------------------


def _save_json_dated(data):
    from datetime import datetime
    dt = datetime.now().strftime(r'%Y-%m-%dT%H-%M-%S')
    fn = f'data_{dt}.json'
    print(fn)
    fp = os.path.join( 'data', fn )
    with open(fp, 'w') as f:
        json.dump(data, f)


def _load_post_network(fn):
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


def _save_post_network(dict):
    from datetime import datetime
    dt = datetime.now().strftime(r'%Y-%m-%dT%H-%M-%S')
    fn = f'post_objects_{dt}.pkl'
    print(fn)
    fp = os.path.join( 'data', fn )
    with open(fp, 'wb') as f:
        pickle.dump(dict, f)
        


#reigon - START --------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scraper and Downloader for the network of curated posts on r/SoGoodToBeBad")
    
    # parser.add_argument('-wtf', action='store_true', help='wtf')
    parser.add_argument('-s1', '--scrape-post-network', action='store_true',    help='[STEP 1] Scrapes network of posts starting from the 3 root nodes, saves html files')
    parser.add_argument('-s2', '--parse-post-data', action='store_true',        help='[STEP 2] Parses local html files for data')
    parser.add_argument('-s3', '--download-media', action='store_true',         help='[STEP 3] Attempts to download media from media pages')
    parser.add_argument('-s4', '--generate-html-pages', action='store_true',    help='[STEP 4] Generates html pages from parsed data, finding local media')
    # parser.add_argument('-s5', '--', action='store_true',                 help='[STEP 4] Copies HTML pages to "export_location" from settings.json')

    parser.add_argument('--select-page',                                        help='post_id which to use for parsing data, download media or generating html pages')
    parser.add_argument('--list-saved', action='store_true',                    help='List saved post networks')
    parser.add_argument('--redo-scraping', action='store_true',                 help='Suppresses normal printout from processes')
    parser.add_argument('--quiet', '-q', action='store_true',                   help='Suppresses normal printout from processes')
    parser.add_argument('--pause-between',                                      help='Number of seconds to pause between url requests', type=float, default=2)
    parser.add_argument('--pause-timeout',                                      help='Number of seconds to pause when recieved 429 status_code', type=float, default=60)
    
    args = parser.parse_args()
    
    print()
    try:
        main(args)
    except KeyboardInterrupt:
        print('\n... Interrupted by KeyboardInterrupt')
    print()


