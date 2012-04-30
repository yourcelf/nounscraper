import os
import re
import sys
import time
import json
import codecs
import urlparse
import subprocess
from collections import namedtuple

import requests
from PIL import Image
from bs4 import BeautifulSoup

MIN_SECONDS_BETWEEN_REQUESTS = 5
thumbs = [100, 32, 16]

def get_cached_page(url):
    """
    Get the url from the cache, if it's there, or request it from the web if
    not.  Throttle requests to a max speed of MIN_SECONDS_BETWEEN_REQUESTS.
    """

    name = os.path.join(
        os.path.dirname(__file__),
        "cache",
        url.split("://")[1].replace("/", "---")
    )
    if not os.path.exists(name):
        time_since_last_request = time.time() - get_cached_page.last_request
        if time_since_last_request < MIN_SECONDS_BETWEEN_REQUESTS:
            time.sleep(MIN_SECONDS_BETWEEN_REQUESTS - time_since_last_request)
        content = requests.get(url).content
        get_cached_page.last_request = time.time()
        try:
            os.makedirs(os.path.dirname(name))
        except OSError:
            pass
        with open(name, 'w') as fh:
            fh.write(content)
    with open(name, 'r') as fh:
        content = fh.read()
    return content
get_cached_page.last_request = 0 # epoch, baby!

def scrape_index(index_url):
    contents = get_cached_page(index_url)
    soup = BeautifulSoup(contents)
    links = soup.find_all("a")
    urls = set()
    for link in links:
        url = link.get('href')
        if url.startswith("/noun/"):
            urls.add(urlparse.urljoin(index_url, url))
    return urls

def scrape_icons(url):
    contents = get_cached_page(url)
    soup = BeautifulSoup(contents)
    noun = soup.find("h2", attrs={'id': 'noun-name'}).text
    thumbs = soup.find_all("li", attrs={'class': "icon"})
    icons = []
    for li in thumbs:
        svg = li.find("svg")
        del svg['height']
        del svg['width']
        icons.append({
                'id': li.get("id"),
                'noun': noun,
                'source': li.get("data-source"),
                'svg': str(svg),
                'view_box': svg.get("viewbox"),
                'collection_url': li.get("data-organizations-url"),
                'collection': li.get("data-organizations"),
                'year': li.get("data-year"),
                'location': li.get("data-location"),
                'attributeas': li.get("data-attributeas"),
                'designers': li.get("data-designers"),
                'tags': [a for a in li.get("data-tags").split(",") if a],
                'license_url': li.get("data-license-url"),
                'license': li.get("data-license"),
        })
    return icons

def store_icon(icon):
    print icon['noun'], icon['id'], icon['view_box']
    out = os.path.join(os.path.dirname(__file__), "icons")
    try:
        os.makedirs(out)
    except OSError:
        pass
    basename = os.path.join(out, "%s-%s" % (
        icon['noun'].lower().replace(" ", "-"), 
        icon['id'][len("icon-"):]
    ))
    with open(basename + ".svg", 'w') as fh:
        fh.write('<?xml version="1.0" encoding="utf-8"?>\n')
        fh.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">\n')
        fh.write(icon['svg'])
    with open(basename + ".json", 'w') as fh:
        json.dump(icon, fh, indent=4)
    with codecs.open(basename + "-attribution.html", 'w', 'utf-8') as fh:
        attrib_url = "<a href='http://thenounproject.com'>The Noun Project</a>"
        if icon['attributeas']:
            attribution = "by " + icon['attributeas'].replace("The Noun Project", attrib_url)
        elif icon['designers']:
            attribution = "by %s, from %s" % (icon['designers'], attrib_url)
        else:
            attribution = "from %s" % attrib_url
            
        fh.write(u""""%(noun)s" symbol %(attribution)s. <a href='%(license_url)s'>%(license)s</a>.""" % {
            'noun': icon['noun'],
            'attribution': attribution,
            'license_url': icon['license_url'],
            'license': icon['license'],
        })

    procs = []

    for size in thumbs:
        cmd = "inkscape --export-png=%(out)s --export-dpi=%(dpi)s --export-area-drawing --export-background-opacity=0 --without-gui %(in)s" % {
            'out': "%s-%s.png" % (basename, size),
            'in': basename + ".svg",
            'dpi': icon_dpi(size, icon),
            'area': icon['view_box'].replace(" ", ":"),
        }
        procs.append(subprocess.Popen(cmd, shell=True))

    for proc in procs:
        proc.communicate()

    normalize_icons()

def icon_dpi(px, icon):
    """
    Inkscape default: 90dpi == 1-to-1 for 100px.
    """
    x1,y1,x2,y2 = [float(a) for a in icon['view_box'].split(" ")]
    width = x2-x1
    height = y2-y1
    # Fallback for invalid viewbox
    if width < 0:
        width = 100
    if height < 0:
        height = 100
    return 90. / max(width, height) * px

def normalize_icons():
    """
    Normalize the sizes of icons so they are all square, by adding transparent
    space around them.
    """
    base = os.path.join(os.path.dirname(__file__), "icons")
    for filename in os.listdir(base):
        match = re.match("^.*?(\d+).png$", filename)
        if match:
            path = os.path.join(base, filename)
            size = int(match.group(1))
            im = Image.open(path)
            x,y = im.size
            if x < size or y < size:
                fixed = Image.new('RGBA', (size, size))
                xoff = (size - x) / 2
                yoff = (size - y) / 2
                fixed.paste(im, [xoff, yoff, xoff + x, yoff + y])
                fixed.save(path)
                print filename, im.size
            


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: python scrape.py <nounproject url> [<more urls>...]"
        print "Example: python scrape.py http://thenounproject.com/collections/modern-pictograms/"
        sys.exit(1)
    for index_url in sys.argv[1:]:
        index_url = sys.argv[1]
        icon_urls = scrape_index(index_url)
        for url in list(icon_urls):
            for icon in scrape_icons(url):
                store_icon(icon)
