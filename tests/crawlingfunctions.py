from urllib.request import urlopen


def finduniquepages(listofpages):
    uniquepages = []
    for p in listofpages:
        if p not in uniquepages:
            uniquepages = uniquepages + [p]

    return uniquepages


def findlinksonpage(pagename):
    if isinstance(pagename, bytes):
        pagename = pagename.decode("utf-8")

    url = "http://en.wikipedia.org/wiki/{}".format(pagename)
    html = urlopen(url).read()

    split1 = html.split(b"\"")

    pages = []

    for chunk in split1:
        if chunk.startswith(b"/wiki/") and (b":" not in chunk and b"#" not in chunk and b"%" not in chunk):
            pages = pages + [chunk[6:]]

    uniquepages = finduniquepages(pages)

    return uniquepages
