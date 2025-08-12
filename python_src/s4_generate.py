from bs4 import BeautifulSoup
import json
import os


#region - MAIN ---------------------------------------------------------------------------------------------------------

def generateHtmlPages(site_root: str, data: dict, media_paths: dict[str, str], redo: bool=True) -> None:
    
    catalogue_pages = data["catalogue_pages"]
    media_pages = data["media_pages"]
    
    cont = False
    
    # STEP 1: preprocess
    print(f"preprocessing {len(catalogue_pages)} pages ...")
    for i, (sid, data) in enumerate(catalogue_pages.items()):
        # print("\n  [{}/{}] `{}`".format(i+1, len(catalogue_pages), sid))
        content = data["content_html"]
        # pprint(data)
        data["content_links"] = _getContentLinksCount(content)
        data["dirname"] = _getPostDirname(data)
        
    

    # STEP 2: generate pages
    SIDs_without_pages = set()
    for i, (sid, data) in enumerate(catalogue_pages.items()):
        print("\n  [{}/{}] `{}`".format(i+1, len(catalogue_pages), sid))
        print(json.dumps({k: v for k, v in data.items() if k != "content_html"}, indent=4))
        # print("HTML:\n", data["content_html"])

        # tweak html
        html = data["content_html"]
        html, sids = _modifyATags(html, catalogue_pages, media_pages, media_paths)
        SIDs_without_pages.update(sids)
        data["content_html"] = html
        
        # add data data
        data["parent_links"] = _getParentLinks(data["parents"], catalogue_pages)
        data["parent_titles"] = _getParentTitles(data["parents"], catalogue_pages)
        
        # get media data
        media_data = _getMediaData(data["media_links"], media_pages, media_paths)

        # prune data
        del data["content_links"]
        del data["media_links"]
        
        # save page
        fn = os.path.join(site_root, "pages", data["dirname"], f"{sid}.html")
        if redo or not os.path.exists(fn):
            page_html = _getPageHtml(data, media_data)
            with open(fn, "w") as f:
                f.write(page_html)
        
        # DEV: stop logic
        if not cont:
            match input("> "):
                case "c":
                    cont = True
                case "s":
                    break
                case _:
                    continue
    
    # print("\nREDGIFS POSTS: {}".format(len(REDGIFS_POSTS)))
    
    if len(SIDs_without_pages) > 0:
        print("SIDs without pages:")
        [ print("{:>3} `{}`".format(i+1, sid)) for i, sid in enumerate(SIDs_without_pages) ]



#region - METHODS ------------------------------------------------------------------------------------------------------

IGNORE_HREFS = [
    "https://www.reddit.com/user/katiethebandit2/submitted/?sort=hot",
    "https://www.reddit.com/r/SoGoodtoBeBad/s/Xb3acQOJCP",
    "https://www.reddit.com/r/SoGoodtoBeBad/s/scfa3nnyIu",
]

REDGIFS_POSTS = []

def _modifyATags(html: str, content_pages: dict, media_pages: dict, media_paths: dict) -> tuple[str, list[str]]:
    soup = BeautifulSoup(html, 'html.parser')
    
    unlinked_sids = []
    
    for a_el in soup.select("a"):
        href = a_el["href"]
        assert isinstance(href, str)
        
        href = _standardizeHref(href)
        
        if _isContentLink(href): # - content link -------
            sid = _getHrefSID(href)
            if sid == "":
                raise Exception("No SID extracted from:", href)
            link_page = content_pages.get(sid)
            if link_page is None:
                unlinked_sids.append(sid)
                print("ERROR: No link page found for SID:", sid)
                continue
            a_el["href"] = _getLocalPageHref(link_page["dirname"], sid)
            a_el["data-href"] = href
        
        elif _isMediaLink(href): # - media link --------
            sid = _getHrefSID(href)
            if sid == "":
                raise Exception("No SID extracted from:", href)
            local_href = media_paths.get(sid)
            if local_href is None:
                print("No local media found with sid '{}' (href='{}')".format(sid, href))
                continue
            del a_el["href"]
            a_el["data-sid"] = sid
            a_el["data-href"] = href
            a_el["class"] = "media-post-button"
        
        elif href == "/r/SoGoodtoBeBad":
            a_el["href"] = "https://www.reddit.com/r/SoGoodtoBeBad"
            a_el["traget"] = "_blank"
        
        elif "redgifs" in href:
            REDGIFS_POSTS.append(href)
        
        elif href not in IGNORE_HREFS:
            print("EDGE CASE HREF:")
            print("TEXT: " + a_el.get_text())
            print("SID: " + _getHrefSID(href))
            print("HREF: " + href)
            input("...")
    
    return soup.prettify(), unlinked_sids


def _getMediaData(media_links: list[str], media_pages: dict, media_paths: dict) -> dict:
    mp = {}
    for link in media_links:
        sid = _getHrefSID(link)
        page = media_pages.get(sid)
        local_path = media_paths.get(sid)
        if page is None:
            print("404: No media page found with sid: "+sid)
            continue
        if local_path is None:
            print("404: No local media found for SID: "+sid)
            continue
        media_data = {}
        media_data["local_path"] = f"../../{local_path}"
        media_data["reddit_url"] = link
        media_data = media_data | page
        mp[sid] = media_data
    return mp


#region - HELPERS ------------------------------------------------------------------------------------------------------


def _standardizeHref(href: str) -> str:
    href = href.replace("/duplicates/", "/comments/")
    href = href.replace("http://", "https://")
    # https://www.reddit.com/pby4gm
    if len(href.replace("https://www.reddit.com/", "")) == 6:
        href = href.replace(
            "https://www.reddit.com/",
            "https://www.reddit.com/r/SoGoodtoBeBad/comments/"
        )
    return href


def _iterateLinks(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    els = soup.select("a")
    for el in els:
        href = el["href"]
        assert isinstance(href, str)
        print(href)

def _getContentLinksCount(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    els = soup.select("a")
    cLinks = []
    for el in els:
        href = el["href"]
        assert isinstance(href, str)
        if _isContentLink(href):
            cLinks.append(href)
    return cLinks
    
def _getPostDirname(obj: dict) -> str:
    depth, cLinks, mLinks = obj['depth'], obj['content_links'], obj['media_links']
    if depth == 0:
        return 'root'
    elif len(mLinks) > 0 and len(cLinks) <= 2:
        return 'top'
    elif depth < 2:
        return 'inter'
    else:
        return 'inter3'


# _isMediaLink
def _isMediaLink(href: str) -> bool:
    if not href.startswith("https://"):
        return False
    
    return "/r/sogoodtobebad/comments/" in href.lower() \
        or "/r/angelawhite/comments/" in href.lower() \
        or "/r/sinnsage/comments/" in href.lower()


# _isContentLink
def _isContentLink(href: str) -> bool:
    if not href.startswith("https://"):
        return False
    return "/user/katiethebandit2/comments/" in href.lower() \
        or "/r/u_katiethebandit2/comments/" in href.lower()

def _getHrefSID(href: str) -> str:
    if "/comments/" not in href:
        return ""
    return href.split("/comments/")[-1].split("/")[0]

def _getLocalPageHref(dirname: str, sid: str) -> str:
    return f"../{dirname}/{sid}.html"

def _getParentLinks(parents: list[str], content_pages: dict) -> dict[str, str]:
    mp = {}
    for p in parents:
        if p == "home":
            mp[p] = "../../index.html"
        else:
            page = content_pages[p]
            mp[p] = _getLocalPageHref(page["dirname"], p)
    return mp

def _getParentTitles(parents: list[str], content_pages: dict) -> dict[str, str]:
    mp = {}
    for p in parents:
        if p == "home":
            mp[p] = "root"
        else:
            mp[p] = content_pages[p]["title"]
    return mp


# _getPageHtml
def _getPageHtml(data: dict, media_data: dict) -> str:
    
    return  f"""
        <!DOCTYPE html> <!-- {data['id']} -->
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{data['title']}</title>
                <link rel="stylesheet" href="../../styles.css">
                
                <script src="../../lib/jquery.js"></script>
                <script src="../../lib/playerjs.js"></script>
                <script defer src="../../builder.js"></script>

            </head>
            <body>

                <div id="app"></div>
                
                <!-- DATA -->
                <script>

                    const page_data = {json.dumps(data, indent=4)}

                    const media_data = {json.dumps(media_data, indent=4)}

                </script>

            </body>
            </html>
    """
