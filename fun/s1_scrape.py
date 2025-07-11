import requests
from bs4 import BeautifulSoup as BS
from http.cookiejar import MozillaCookieJar
import time
from fun.fun import *

# Create graph
def fetch_post_network(root_urls, quiet=False, pause_between=1, pause_timeout=60):

    data = {}
    queue = [ (url, 0) for url in root_urls ]
    touched = set([ get_page_id_and_title(x[0])[0] for x in queue ])

    while queue != []:
        url, depth = queue.pop(0) # breadth first
        if pause_between:
            time.sleep(pause_between)
        res = None
        while res == None:
            res = fetch_reddit_post(url)
            if not res: 
                print(f'Failed to fetch "{url}"\nsleeping for {pause_timeout} seconds ...')
                time.sleep(pause_timeout)
        
        post_id, post_title = res['id'], res['title']
        print('{:>4} : {} SCRAPING NODE: [{}] "{}"'.format(len(data), '|___'*depth, post_id, post_title))

        res['has_media_links'] = res.get('media_links', []) != []
        res['depth'] = depth
        data[post_id] = res
        
        added = 0
        content_links = list(set(res['content_links']))
        for link in content_links:
            link_post_id, link_post_title = get_page_id_and_title(link)
            if link_post_id not in touched and link_post_id != post_id:
                added += 1
                print('{:>4}   {}   adding content link ({}): [{}] -> [{}] "{}" '.format(len(touched), '|___'*depth, added, post_id, link_post_id, link_post_title))
                queue.append((link, depth+1))
                touched.add(link_post_id)
                time.sleep(0.01)
        # print('     {} Added {} nodes'.format('  | '*depth, added))
        # print()
        
    return data


def fetch_reddit_post(url):
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
    else:
        post_id, post_title = get_page_id_and_title(url)
        soup = BS(res.content, 'html.parser')
        postContent = soup.find('div', {'id': 'siteTable'})
        if postContent == None:
            print('Unable to find post content (id="siteTable")')
            return None
        links = postContent.findAll('a', href=True)
        content_links = [ x['href'] for x in links if is_user_post(x['href']) ] # link to post under /user/ or /r/u_*
        media_links = [ x['href'] for x in links if is_subreddit_post(x['href']) ] # link to post under subereddit (assumed r/SoGoodToBeBad)
        comments = []
    return {
        'url': url,
        'id': post_id,
        'title': post_title,
        'content_links': content_links,
        'media_links': media_links,
        'soup': soup,
        'comments': comments
    }

