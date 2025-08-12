from bs4 import BeautifulSoup
from pprint import pprint
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
        print("HTML:\n", data["content_html"])

        # tweak html
        html = data["content_html"]
        html, sids = _modifyATags(html, catalogue_pages, media_pages)
        SIDs_without_pages.update(sids)
        data["content_html"] = html
        data["parent_links"] = _getParentLinks(data["parents"], catalogue_pages)
        data["parent_titles"] = _getParentTitles(data["parents"], catalogue_pages)
        
        # save page
        fn = os.path.join(site_root, "pages", data["dirname"], f"{sid}.html")
        if redo or not os.path.exists(fn):
            page_html = _getPageHtml(data)
            with open(fn, "w") as f:
                f.write(page_html)
        
        if not cont:
            match input("> "):
                case "c":
                    cont = True
                case "s":
                    break
                case _:
                    continue
    
    if len(SIDs_without_pages) > 0:
        print("SIDs without pages:")
        [ print("{:>3} `{}`".format(i+1, sid)) for i, sid in enumerate(SIDs_without_pages) ]


#region - METHODS ------------------------------------------------------------------------------------------------------


def _modifyATags(html: str, content_pages: dict, media_pages: dict) -> tuple[str, list[str]]:
    soup = BeautifulSoup(html, 'html.parser')
    
    unlinked_sids = []
    
    for a_el in soup.select("a"):
        href = a_el["href"]
        assert isinstance(href, str)
        
        if _isContentLink(href): # - content link -------
            sid = _getHrefSID(href)
            assert sid != ""
            link_page = content_pages.get(sid)
            if link_page is None:
                unlinked_sids.append(sid)
                print("ERROR: No link page found for SID:", sid)
                continue
                # raise Exception("No link page found for SID:", sid)
            a_el["href"] = _getLocalPageHref(link_page["dirname"], sid)
            a_el["data-href"] = href
        
        elif _isMediaLink(href): # - media link --------
            sid = _getHrefSID(href)
            assert sid != ""
    
    return soup.prettify(), unlinked_sids


#region - HELPERS ------------------------------------------------------------------------------------------------------

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

def _isMediaLink(href: str) -> bool:
    return href.startswith("https://") and "/r/sogoodtobebad/comments/" in href

def _isContentLink(href: str) -> bool:
    return href.startswith("https://") and "/user/katiethebandit2/comments/" in href

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
def _getPageHtml(data: dict) -> str:
    
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

                    const data = {json.dumps(data, indent=4)}

                </script>

            </body>
            </html>
    """
