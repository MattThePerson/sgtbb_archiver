import os


def get_page_id_and_title(url):
    c_parts = url.split('/comments/')
    if len(c_parts) < 2:
        print('ERROR: id or title: "{}"'.format(url))
        return None, None
    parts = [ p for p in c_parts[-1].split('/') if p != '' ]
    if len(parts) < 2:
        print('ERROR: id or title: "{}"'.format(url))
        return None, None
    id_ = parts[0]
    title = parts[1].replace('_rsogoodtobebad', '').replace('_', ' ').title()
    return id_, title

def get_post_id(url):
    c_parts = url.split('/comments/')
    if len(c_parts) < 2:
        c_parts = url.split('/duplicates/')
        if len(c_parts) < 2:
            print('ERROR: id: "{}"'.format(url))
            return None
    return c_parts[-1].split('/')[0]

def is_user_post(href):
    return is_full_url(href) and ('/user/katiethebandit2/comments' in href or 'r/u_katiethebandit2/comments' in href)

def is_subreddit_post(href):
    return is_full_url(href) \
            and 'reddit.com/r/' in href \
            and not is_user_post(href)

def is_full_url(href):
    return 'https://' in href

def is_post_url(href):
    return '/comments/' in href

def get_post_type(data, depth):
    if depth == 0:
        return 'root'
    elif len(data['media_links']) > 0:
        return 'top'
    return 'depth-' + str(depth)



def get_page_id_from_filename(fp: str) -> str:
    fn = os.path.basename(fp)
    if ']' in fn:
        return fn.split('[')[-1].split(']')[0]
    return fn.split('.')[0]


def get_page_id_and_title_from_filename(fn: str):
    fn = os.path.basename(fn)
    parts = fn.split('] ')
    if len(parts) != 2:
        print('ERROR: Unable to extract id and title from:', fn)
        return None, None
    id_ = parts[0].split('[')[-1]
    title = parts[1].split('.')[0]
    return id_, title

