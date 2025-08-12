from typing import Any
import os
from bs4 import BeautifulSoup as BS
from pathlib import Path
from python_src.fun import *



# DIRECTORIES
# root/
# - depth 0
# top/
# - pages with media links and fewer than 2 content links
# inter/
# - non root nodes that contain more than 2 content links
# inter3/
# - intermediate with depth 3
def generate_html_pages(post_objects: dict[str, Any]):
    """ Given a list of post objects, generate html page for each object """
    
    sitedir = 'site'
    
    # remove deleted posts and filter content links
    for post_id in list(post_objects.keys()):
        obj = post_objects[post_id]
        obj['content_links'] = list(set([ x for x in obj['content_links'] if get_post_id(x) != post_id ]))
        if obj['media_links'] == [] and obj['content_links'] == []:
            del post_objects[post_id]
        else:
            post_objects[post_id] = obj
    
    for idx, (post_id, obj) in enumerate(post_objects.items()):
        if obj['depth'] == 0 or True:
            dirname = get_post_dirname(obj)
            fp = os.path.join( dirname, '[{}] {}.html'.format(obj['id'], obj['title']) )
            content_links, media_links = obj['content_links'], obj['media_links']
            top_str = 'MEDIA' if media_links != [] else '     '
            inter_str = 'INTER' if len(content_links) > 2 and obj['depth'] > 0 else '     '
            print('{:<3}: {:<6} : c={:<3} : m={:<3} : {} : {} : <{:<6}> : "{}"'
                .format(idx+1, '|-'*(obj['depth']+1), len(content_links), len(media_links), top_str, inter_str, dirname, fp))
            fp = os.path.join(sitedir, fp)
            generate_post_page(fp, obj, post_objects)


def generate_post_page(fp, obj, posts):
    parent = Path(fp).parent
    os.makedirs(parent, exist_ok=True)
    # html = obj['soup'].prettify()
    html = generate_post_html(obj['soup'])
    html = change_a_tags(html, posts, obj['id'])
    with open(fp, 'w') as f:
        f.write(html.prettify())


def generate_post_html(soup):
    soup, data = parse_reddit_page(soup, show_data=False)
    html = create_html_page(soup, data)
    return html


# Parse Reddit Post Html
def parse_reddit_page(soup, show_data=True):
    # print("[HTML] Parsing Reddit post ...")
    siteTable = soup.find('div', id='siteTable')

    post_content = siteTable.find('div', {'class' : 'md'})
    topMatter = soup.find('div', {'class' : 'top-matter'})

    data = {}
    data['date'] = topMatter.find('time')['datetime'][:10]
    
    titleEl = topMatter.find('a', {'class' : 'title'})
    data['title'] = titleEl.text.strip()
    data['url'] = titleEl['href']

    authorEl = topMatter.find('a', {'class' : 'author'})
    data['author'] = authorEl.text.strip()
    data['authorUrl'] = authorEl['href']

    if show_data:
        print("  DATA FOUND:")
        print("   title: '{}'".format(data['title']))
        print("   url: '{}'".format(data['url']))
        print("   author: '{}'".format(data['author']))
        print("   authorUrl: '{}'".format(data['authorUrl']))
        print("   date: '{}'".format(data['date']))

    data['comments'] = get_comments_from_soup(soup)
    
    return post_content, data



def create_html_page(post, data):
    page = BS(features="html.parser")
    html = page.new_tag('html')
    page.append(html)

    # head
    head = page.new_tag('head')
    html.append(head)

    head.append( create_html_tag(page, 'title', text=data['title']) )

    style_tag = page.new_tag('link', rel='stylesheet', href='../styles.css')
    head.append(style_tag)

    # body
    post_wrapper = create_html_tag(page, 'div', _class='post-wrapper')

    title = create_html_tag(page, 'h1', _class='post-title')
    a = page.new_tag('a')
    a['href'] = data['url']
    a['target'] = '_blank'
    a.string = data['title']
    title.append(a)
    post_wrapper.append( title )

    author = create_html_tag(page, 'div', _class='post-author')
    author.string = "Author: "
    a = page.new_tag('a')
    a['href'] = data['authorUrl']
    a['target'] = '_blank'
    a.string = data['author']
    author.append(a)
    post_wrapper.append( author )

    date_posted = create_html_tag(page, 'div', _class='post-datetime', text="Posted: " + data['date'])
    post_wrapper.append(date_posted)

    post_content = create_html_tag(page, 'div', _class='post-content')
    post_content.append(post)
    post_wrapper.append(post_content)
    
    body = page.new_tag('body')
    body.append(post_wrapper)
    html.append(body)

    comments_section = create_html_tag(page, 'section', _class='comments-section')
    title = create_html_tag(page, 'h2')
    title.string = 'Comments:'
    comments_section.append(title)
    comments_list = create_html_tag(page, 'ul')
    for comment_item in data['comments']:
        text, author = comment_item['text'], comment_item['author']
        comment_container = create_html_tag(page, 'li', _class='comment-container')
        comment_author = create_html_tag(page, 'div', _class='author')
        comment_author.string = author
        comment_text = create_html_tag(page, 'div', _class='comment')
        comment_text.string = text
        comment_container.append(comment_author)
        comment_container.append(comment_text)
        comments_list.append(comment_container)
    
    comments_section.append(comments_list)
    page.append(comments_section)

    for a in page.find_all('a', href=True):
        # a['target'] = '_blank'
        if a['href'].startswith('/r') or a['href'].startswith('/u') or a['href'].startswith('/user'):
            a['href'] = "https://reddit.com" + a['href']

    return page


# change hrefs to local
def change_a_tags(soup, posts, current_post_id):
    for a in soup.find_all('a', href=True):
        href = a['href']
        if is_user_post(href):
            link_post_id = get_post_id(href)
            if link_post_id != current_post_id:
                post = posts.get(link_post_id)
                if post:
                    fp = get_post_filepath(post)
                    a['data-url'] = href
                    a['href'] = os.path.join( '..', fp )
        else: # media post or title href
            a['target'] = '_blank'
    return soup

# 
def get_comments_from_soup(soup):
    commentArea = soup.find('div', {'class': 'commentarea'})
    comment_parent_els = commentArea.findAll('div', {'class': 'thing'})
    comment_objects = []
    for el in comment_parent_els:
        author_el = el.find(class_='author')
        author = author_el.text if author_el else '[deleted]'
        comment_el = el.find(class_='md')
        comment = comment_el.text.strip()
        comment_objects.append({
            'author': author,
            'text': comment,
        })
    return comment_objects

# 
def create_html_tag(soup, type, _class=None, text=None):
    el = soup.new_tag(type)
    if _class:
        el['class'] = _class
    if text:
        el.string = text
    return el





#### MISC HELPERS ####

def get_post_filepath(obj):
    dirname = get_post_dirname(obj)
    return os.path.join( dirname, '[{}] {}.html'.format(obj['id'], obj['title']) )

def get_post_dirname(obj):
    depth, cLinks, mLinks = obj['depth'], obj['content_links'], obj['media_links']
    if depth == 0:
        return 'root'
    elif len(mLinks) > 0 and len(cLinks) <= 2:
        return 'top'
    elif depth < 2:
        return 'inter'
    else:
        return 'inter3'
