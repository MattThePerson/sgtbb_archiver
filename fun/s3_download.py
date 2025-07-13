import os
import subprocess
import time
import json
from datetime import timedelta

from . import fun


def download_media_links(reddit_urls: list[str], download_dir: str, limit=None, redo_download=False, pause_between: int=1) -> tuple[list, list]:
    """  """
    succ, fail = [], []
    
    os.makedirs(download_dir, exist_ok=True)
    downloaded_videos = { fun.get_page_id_from_filename(fn): os.path.join(download_dir, fn) for fn in os.listdir(download_dir) }
    
    start = time.time()
    downloaded_mb = 0
    
    try:
        for idx, url in enumerate(reddit_urls):
            uptime = str(timedelta(seconds=time.time()-start))[:-5]
            print('  ({:_}/{:_})  |  uptime={}  |  succ={}/{}  |  fails={}  |  downloaded={:.3f}gb  |  current = {:<60}    '
                    .format(idx+1, len(reddit_urls), uptime, len(succ), limit, len(fail), downloaded_mb/1024, url[:58]), end='')
        
            media_id = fun.get_post_id(url)
            if media_id in downloaded_videos and not redo_download:
                print('found local media!')
            else:
                print('downloading ...')
                savepath = _download_redgif_from_reddit(url, download_dir)
                if not os.path.exists(savepath):
                    print('     failed :/')
                    fail.append(url)
                else:
                    print('     success!')
                    succ.append(url)
                    downloaded_mb += _get_file_size_mb(savepath)
                    if limit and len(succ) >= limit:
                        break
                time.sleep(pause_between)

    except KeyboardInterrupt:
        print('\n  ...keyboard interrupt')
    
    print('\ndownload amount: {:.3f} gb'.format(downloaded_mb/1024))
    
    return succ, fail



def _download_redgif_from_reddit(url: str, download_dir: str) -> str:
    """  """
    # get data
    print('getting data...')
    result = subprocess.run(
        ["yt-dlp", "--dump-json", url],
        capture_output=True,
        text=True,
        check=True
    )
    data = json.loads(result.stdout)
    
    # 
    dt = data.get('upload_date')
    date_fmt = '{}-{}-{}'.format( dt[:4], dt[4:6], dt[6:] )
    title =         _sanitize_filename(data.get('title'))[:120]
    display_id =    data.get('display_id')
    secondary_id =  data.get('id')
    ext =           data.get('ext')
    filename = f'[{date_fmt}] {title} [{secondary_id}] [{display_id}].{ext}'
    savepath = download_dir + '/' + filename
    command = [
        'yt-dlp', url,
        '-o', savepath,
    ]
    print('downloading media to:', savepath)
    subprocess.run(command)
    return savepath



def _sanitize_filename(name: str) -> str:
    replacements = {
        '/': '∕',
        '\\': '⧵',
        ':': '꞉',
        '*': '∗',
        '?': '？',
        '"': '＂',
        '<': '‹',
        '>': '›',
        '|': '⎪'
    }
    return ''.join(replacements.get(c, c) for c in name)


def _get_file_size_mb(path):
    size_bytes = os.path.getsize(path)
    return size_bytes / (1024 * 1024)

