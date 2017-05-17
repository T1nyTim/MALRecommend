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

page = requests.get("https://myanimelist.net/animelist/T1nyTim?status=2&tag")
tree = html.fromstring(page.content)
animeUrl = tree.xpath('//body/div/table/tr/td/a/@href')
animeTitle = tree.xpath('//body/div/table/tr/td/a/span/text()')
animeUrl = [x for x in animeUrl if x[:6] == "/anime"]

for i in animeUrl:
    page = requests.get("https://myanimelist.net" + i + "/userrecs")
    tree = html.fromstring(page.content)
    recs = tree.xpath('//div[@style="margin-bottom: 2px;"]/a/strong/text()')
    num = tree.xpath('//div/a[@href="javascript:void(0);"]/strong/text()')

    for j in range(0, len(num)):
        num[j] = int(num[j]) + 1

    blanks = len(recs) - len(num)

    if blanks > 0:
        for j in range(0, blanks):
            num.append(1)

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
    uprint(i, "\nRecommended", recDict[i], "times\n")
