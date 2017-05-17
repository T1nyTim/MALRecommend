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

p = requests.get("https://myanimelist.net/animelist/T1nyTim?status=2&tag")
t = html.fromstring(p.content)
aID = t.xpath('//body/div/div/@id')
aT = t.xpath('//body/div/table/tr/td/a/span/text()')

for i in range(0, len(aID)):
    if aID[i - 1][:4] == "more":
        aID[i - 1] = aID[i - 1][4:]
    else:
        del aID[i - 1]

a = []

for i in range(0, len(aID)):
    p = requests.get("https://myanimelist.net/anime/" + str(aID[i]))
    t = html.fromstring(p.content)
    a = a + (t.xpath('//head/link[1]/@href'))

for i in range(0, len(a)):
    p = requests.get(a[i] + "/userrecs")
    t = html.fromstring(p.content)
    r = t.xpath('//div[@style="margin-bottom: 2px;"]/a/strong/text()')
    n = t.xpath('//div/a[@href="javascript:void(0);"]/strong/text()')

    for j in range(0, len(n)):
        n[j] = int(n[j]) + 1

    b = len(r) - len(n)

    if b > 0:
        for j in range(0, b):
            n.append(1)

    z = list(zip(r, n))
    z = [x for x in z if x[0] not in aT]

    if i == 0:
        d = dict(z)
    else:
        tmp = dict(z)
        input = [dict(x) for x in (d, tmp)]
        d = sum((Counter(y) for y in input), Counter())

d = dict(d.most_common())

for i in d:
    uprint(i, "\nRecommended", d[i], "times\n")
