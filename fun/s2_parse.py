import os
from bs4 import BeautifulSoup
import time

from . import fun


#region - PUBLIC -------------------------------------------------------------------------------------------------------

def parse_catalogue_pages(root_urls: list[str], catalogue_page_paths: list[str]) -> dict:
    """ For a list of catalogue pages and media pages, constructs a map between page_id -> page_obj, where the object 
    can be used fully to create the html page """

    # prepare required data
    paths_queue = [] # tuple ( path, depth, parent_id )
    for url in root_urls:
        id_, title = fun.get_page_id_and_title(url)
        paths_queue.append( (f'src/catalogue/[{id_}] {title}.html', 0, 'home') )
    
    catalogue_pages = { fun.get_page_id_from_filename(pth): pth for pth in catalogue_page_paths }
    
    data = {}
    
    # - PARSE CATALOGUE PAGES --------------------------------------------------

    touched = []
    handled = 0
    while paths_queue != []:
        curr_filename, depth, parent_id = paths_queue.pop(0)
        curr_id, curr_title = fun.get_page_id_and_title_from_filename(curr_filename)
        print('  {:>4}  |  queue: {:<4}  |  HANDLING NODE  {}  [{}] "{}"'.format( handled, len(paths_queue), '|___'*depth, curr_id, curr_title ))

        soup = _get_page_as_soup(curr_filename)
        content_links, media_links = _parse_links(soup)

        # parse page data
        obj = {
            'id': curr_id,
            # 'title': curr_title,
            'depth': depth,
            'parent': parent_id,
            'media_links': media_links,
        }
        parsed_data = _parse_data_from_soup(soup)
        obj = obj | parsed_data
        content_html = _get_content_html(soup)
        if content_html is None:
            print('ERROR: Unable to get post content for file:', curr_filename)
            continue
        obj['content_html'] = content_html
        data[curr_id] = obj

        # add content links to queue
        content_links = sorted(set(content_links))
        links_added = 0
        for link in content_links:
            link_id, link_title = fun.get_page_id_and_title(link)
            if link_id and link_id not in touched and link_id != curr_id:
                link_path = catalogue_pages[link_id]
                paths_queue.append( (link_path, depth+1, curr_id) )
                touched.append(link_id)
                links_added += 1
                print('{:>4}   {}   adding content link ({}): [{}] -> [{}] "{}" '.format(len(touched), '|___'*depth, links_added, curr_id, link_id, link_title))
                time.sleep(0.003)
    
        handled += 1
        # if handled > 10:
        #     break
    
    return data


def parse_media_pages(media_page_paths: list[str]) -> dict:

    # - PARSE MEDIA PAGES ------------------------------------------------------
    
    data = {}
    
    for idx, med_pth in enumerate(media_page_paths):
        print('  ({:_}/{:_})  PARSING MEDIA PAGE  |  {}'.format(idx+1, len(media_page_paths), med_pth))

        page_id = fun.get_page_id_from_filename(med_pth)
        obj = {
            'id': page_id,
        }
        data[page_id] = obj

    return data



#region - PRIVATE ------------------------------------------------------------------------------------------------------


# Parse Reddit Post Html
def _parse_data_from_soup(soup, show_data=False):
    # print("[HTML] Parsing Reddit post ...")
    
    data = {}

    topMatter = soup.find('div', {'class' : 'top-matter'})

    data['date_created'] = topMatter.find('time')['datetime'][:10]
    
    titleEl = topMatter.find('a', {'class' : 'title'})
    data['title'] = titleEl.text.strip()
    data['url'] = titleEl['href']

    authorEl = topMatter.find('a', {'class' : 'author'})
    data['author'] = authorEl.text.strip()
    data['author_href'] = authorEl['href']

    if show_data:
        print("  DATA FOUND:")
        print("   title: '{}'".format(data['title']))
        print("   url: '{}'".format(data['url']))
        print("   author: '{}'".format(data['author']))
        print("   author_href: '{}'".format(data['author_href']))
        print("   date_created: '{}'".format(data['date_created']))

    return data



def _get_content_html(soup):
    siteTable = soup.find('div', id='siteTable')
    post_content = siteTable.find('div', {'class' : 'md'})
    if post_content is None:
        return None
    return post_content.prettify()

def _parse_links(soup):
    postContent = soup.find('div', {'id': 'siteTable'})
    if postContent is None:
        raise Exception('Unable to find post content (id="siteTable")')
    links = postContent.findAll('a', href=True)
    content_links = [ x['href'] for x in links if fun.is_user_post(x['href']) ] # link to post under /user/ or /r/u_*
    media_links = [ x['href'] for x in links if fun.is_subreddit_post(x['href']) ] # link to post under subereddit (assumed r/SoGoodToBeBad)
    return content_links, media_links

def _get_page_as_soup(pth: str):
    with open(pth, 'r') as f:
        src = f.read()
    return BeautifulSoup(src, 'html.parser')

