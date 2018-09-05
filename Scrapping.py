#! env/Scripts/python

from lxml import html
import requests
import sys

def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)

p = requests.get("https://myanimelist.net/anime/223/Dragon_Ball/userrecs")
t = html.fromstring(p.content)

r = t.xpath('//div[@style="margin-bottom: 2px;"]/a/strong/text()')
n = t.xpath('//div/a[@href="javascript:void(0);"]/strong/text()')

for i in range(0, len(n)):
    n[i] = int(n[i]) + 1

b = len(r) - len(n)

if b > 0:
    for i in range(0, b):
        n.append(1)

z = zip(r, n)
d = dict(z)

for i in d:
    uprint(i, "\nRecommended", d[i], "times\n")
