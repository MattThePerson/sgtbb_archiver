import requests
from bs4 import BeautifulSoup
from http.cookiejar import MozillaCookieJar
import time
import os

from fun import fun



def download_post_network_catalogue_pages(root_urls, download_dir, redo_scraping=False, quiet=False, pause_between=1, pause_timeout=60):
    
    queue = [ (url, 0) for url in root_urls ]
    touched = set([ fun.get_page_id_and_title(x[0])[0] for x in queue ])
    handled = 0
    media_links_array = []
    
    print('DOWNLOADING CATALOGUE PAGES')
    catalogue_dir = download_dir + '/catalogue/'
    os.makedirs(catalogue_dir, exist_ok=True)
    while queue != []:
        url, depth = queue.pop(0)
        post_id, post_title = fun.get_page_id_and_title(url)
        savename = catalogue_dir + f'[{post_id}] {post_title}.html'
        print('  {:>4}  |  queue: {:<4}  |  HANDLING NODE  {}  [{}] "{}"'.format( handled, len(queue), '|___'*depth, post_id, post_title ))

        src = None
        read_from_file = False
        if os.path.exists(savename) and not redo_scraping:
            print('reading src from:', savename)
            with open(savename, 'r') as f:
                src = f.read()
            read_from_file = True
        
        else:
            src = None
            while src is None:
                src = _fetch_reddit_post_src(url)
                if not src: 
                    print(f'Failed to fetch "{url}"\nsleeping for {pause_timeout} seconds ...')
                    time.sleep(pause_timeout)
            with open (savename, 'w') as f:
                f.write(src)
        
        # parse links
        content_links, media_links = _parse_links(src)
        
        media_links_array.extend(media_links)
        
        links_added = 0
        content_links = sorted(set(content_links))
        for link in content_links:
            link_post_id, link_post_title = fun.get_page_id_and_title(link)
            if link_post_id not in touched and link_post_id != post_id:
                links_added += 1
                print('{:>4}   {}   adding content link ({}): [{}] -> [{}] "{}" '.format(len(touched), '|___'*depth, links_added, post_id, link_post_id, link_post_title))
                queue.append((link, depth+1))
                touched.add(link_post_id)
                time.sleep(0.003)
        

        handled += 1
        if pause_between and not read_from_file:
            time.sleep(pause_between)
        # if handled >= 5:
        #     break

    print('DOWNLOADING MEDIA PAGES')
    media_page_dir = download_dir + '/media_page/'
    os.makedirs(media_page_dir, exist_ok=True)
    media_links_array = sorted(set(media_links_array))
    for idx, link in enumerate(media_links_array):
        post_id = fun.get_post_id(link)
        if post_id is not None:
            savename = media_page_dir + f'{post_id}.html'
            print('  {:_}/{:_} : DOWNLOADING MEDIA PAGE:  {:<35}  |  {:<70}  |  '.format(idx+1, len(media_links_array), savename[:32], link.split('reddit.com')[-1][:68]), end='')

            if not os.path.exists(savename) or redo_scraping:
                src = None
                while src is None:
                    src = _fetch_reddit_post_src(link)
                    if not src: 
                        print(f'Failed to fetch "{link}"\nsleeping for {pause_timeout} seconds ...')
                        time.sleep(pause_timeout)
                with open (savename, 'w') as f:
                    f.write(src)
                print('done.')
                if pause_between:
                    time.sleep(pause_between)
            else:
                print('already exists!')


# OLD
def fetch_post_network(root_urls, quiet=False, pause_between=1, pause_timeout=60):

    data = {}
    queue = [ (url, 0) for url in root_urls ]
    touched = set([ fun.get_page_id_and_title(x[0])[0] for x in queue ])

    while queue != []:
        url, depth = queue.pop(0) # breadth first
        if pause_between:
            time.sleep(pause_between)
        res = None
        while res is None:
            res = _fetch_reddit_post(url)
            if not res: 
                print(f'Failed to fetch "{url}"\nsleeping for {pause_timeout} seconds ...')
                time.sleep(pause_timeout)
        
        post_id, post_title = res['id'], res['title']
        print('  {:>4}  |  queue: {:<4}  |  HANDLING NODE  {}  [{}] "{}"'.format( len(data), len(queue), '|___'*depth, post_id, post_title ))

        res['has_media_links'] = res.get('media_links', []) != []
        res['depth'] = depth
        data[post_id] = res
        
        added = 0
        content_links = list(set(res['content_links']))
        for link in content_links:
            link_post_id, link_post_title = fun.get_page_id_and_title(link)
            if link_post_id not in touched and link_post_id != post_id:
                added += 1
                print('{:>4}   {}   adding content link ({}): [{}] -> [{}] "{}" '.format(len(touched), '|___'*depth, added, post_id, link_post_id, link_post_title))
                queue.append((link, depth+1))
                touched.add(link_post_id)
                time.sleep(0.01)
        # print('     {} Added {} nodes'.format('  | '*depth, added))
        # print()
        
    return data



def _fetch_reddit_post_src(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    jar = MozillaCookieJar('cookies/cookies.txt')
    jar.load()
    
    url = url.replace('www.', 'old.')
    res = requests.get(url, cookies=jar, headers=headers)
    if res.status_code != 200:
        print('status_code:', res.status_code)
        return None
    soup = BeautifulSoup(res.content, 'html.parser')
    return soup.prettify()
    

def _parse_links(src):
    soup = BeautifulSoup(src, 'html.parser')
    postContent = soup.find('div', {'id': 'siteTable'})
    if postContent is None:
        raise Exception('Unable to find post content (id="siteTable")')
    links = postContent.findAll('a', href=True)
    content_links = [ x['href'] for x in links if fun.is_user_post(x['href']) ] # link to post under /user/ or /r/u_*
    media_links = [ x['href'] for x in links if fun.is_subreddit_post(x['href']) ] # link to post under subereddit (assumed r/SoGoodToBeBad)
    return content_links, media_links

