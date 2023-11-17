import requests
from bs4 import BeautifulSoup
import json
import re

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

url = 'https://www.pikiran-rakyat.com/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}
berita = {}

req = requests.get(url, headers=headers)
soup = BeautifulSoup(req.text, 'html.parser')
section = soup.findAll('section', 'most mt2 clearfix')

for i in section:
    x = str(i.find('h3','title title6'))
    # print(x)
    if 'Terpopuler' in x:
        links = i.findAll('a', 'most__link')
        break

berita['totalBerita'] = len(links)
berita['berita'] = []
print(req)

for i in links:
    page = i
    state = 0
    tempDict = {}
    isi = []
    while True:
        try:
            req = requests.get(page.get('href'), headers=headers)
            soup = BeautifulSoup(req.text, 'html.parser')
        except:
            print('Halaman Tidak Ditemukan')
            break

        #get paragraph
        artikel = soup.find('article', 'read__content clearfix')
        if artikel is None:
            print('artikel tidak ditemukan')
            berita['totalBerita'] -= 1
            break
        paragraf = artikel.findAll('p')

        #get title
        judul = soup.find('h1')
        published_date = soup.find('div','read__info__date')
        published_date = re.findall(r'(\d.*WIB)',published_date.text)
        editor = soup.find_all('p')
        p = artikel.findAll('p')
        editor = editor[len(p)].find('a')
        # print(editor)

        if state == 0:
            if judul is not None:
                tempDict['judul'] = removeNonAscii(judul.text)
                tempDict['publishedDate'] = removeNonAscii(published_date[0])
                tempDict['editor'] = removeNonAscii(editor.text)
                tempDict['url'] = page.get('href')
                state = 1
            else:
                print('Judul tidak ditemukan')

        #adding paragraph text to the list
        for i in range(len(paragraf)):
            for tags in ['div', 'strong']:
                unwanted = paragraf[i].find(tags)
                if unwanted is not None:
                    unwanted.extract()
            if paragraf[i].text.strip() != '':
                isi.append(paragraf[i].text.strip())
              
        # print(len(paragraf))
        # print('\n')
        tempDict['paragraf'] = isi

        #cheking next page
        page = soup.find('a', attrs={"rel": "next"})
        if page is None:
            break
    
    print(isi)
    berita['berita'].append(tempDict)

with open("output.json", "w") as outfile:
    json.dump(berita, outfile)