from lxml import html
from collections import Counter
import requests
import sys

def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)

def requestTimeout(url, pageType):
    try:
        p = requests.get(url, timeout=10)
        if p:
            return p
        else:
            uprint("Format for " + pageType + " has changed")
            sys.exit()
    except requests.Timeout:
        uprint("Timed out while accessing " + pageType + " list")
        sys.exit()

page = requestTimeout("https://myanimelist.net/animelist/T1nyTim?status=2&tag", "Completed")
tree = html.fromstring(page.content)
animeUrl = tree.xpath('//body/div/table/tr/td/a/@href')
animeUrl = [x for x in animeUrl if x[:6] == "/anime"]
animeTitle = tree.xpath('//body/div/table/tr/td/a/span/text()')
animeScore = tree.xpath('//body/div/table/tr/td[@align="center"][@width="45"]/text()')
animeScore = [x.strip() for x in animeScore]

for i in animeUrl:
    page = requestTimeout("https://myanimelist.net" + i + "/userrecs", animeTitle[animeUrl.index(i)])
    tree = html.fromstring(page.content)
    recs = tree.xpath('//div[@style="margin-bottom: 2px;"]/a/strong/text()')
    num = tree.xpath('//div/a[@href="javascript:void(0);"]/strong/text()')
    num = [int(x) + 1 for x in num]

    for j in range(len(num), len(recs)):
        num.append(1)

    num = [x * int(animeScore[animeUrl.index(i)]) for x in num]
    zippedList = list(zip(recs, num))
    zippedList = [x for x in zippedList if x[0] not in animeTitle]

    if i == animeUrl[0]:
        recDict = dict(zippedList)
    else:
        tmpDict = dict(zippedList)
        input = [dict(x) for x in (recDict, tmpDict)]
        recDict = sum((Counter(y) for y in input), Counter())

recDict = dict(recDict.most_common())

for i in recDict:
    uprint(i, "\tScored:", recDict[i])
