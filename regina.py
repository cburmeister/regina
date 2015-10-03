#!/usr/bin/python

import os
import re
import csv
import time
import click
import shutil
import requests
from bs4 import BeautifulSoup
from itertools import izip_longest

GENRES = ['house', 'deep-house', 'techno', 'minimal-tech-house']
WINDOWS = ['this-week', 'today', 'eight-weeks']
LIMITS = ['10', '20', '50', '100', '500']


def grouper(n, iterable, fillvalue=None):
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)


@click.command()
@click.argument('genre', type=click.Choice(GENRES))
@click.argument('window', type=click.Choice(WINDOWS))
@click.argument('limit', type=click.Choice(LIMITS))
@click.option('--sleep', default=3)
def main(genre, window, limit, sleep):
    """
    Fetch new releases from http://www.juno.co.uk/.
    """
    base_url = 'http://www.juno.co.uk/'
    url = '{}/{}/{}/?items_per_page={}'.format(base_url, genre, window, limit)

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    table = soup.find(class_='product_list')
    products = table.find_all(attrs={'ua_location': re.compile('product')})

    if not os.path.exists(genre):
        os.makedirs(genre)

    with open('{}/{}.csv'.format(genre, genre), 'wb') as out_file:
        csv_writer = csv.writer(out_file)
        csv_writer.writerow([
            'artist', 'title', 'label', 'catno', 'format', 'genre', 'style',
            'tracks', 'images', 'audio',
        ])
        for idx, (row1, row2, row3) in enumerate(grouper(3, products)):
            try:
                url = row1\
                    .find(class_='producttitle')\
                    .find('a', class_='jhighlight')['href']

                r = requests.get(base_url + url)
                soup = BeautifulSoup(r.content, 'lxml')

                image_keys = []
                images = soup.find('div', class_='product-images-large')
                for image_idx, image in enumerate(images.find_all('img')):
                    r = requests.get(image['src'], stream=True)
                    key = '{}-{}-{}.jpeg'.format(genre, idx, image_idx)
                    with open('{}/{}'.format(genre, key), 'wb') as f:
                        r.raw.decode_content = True
                        shutil.copyfileobj(r.raw, f)
                        image_keys.append(key)

                audio_keys = []
                anchors = soup.findAll('a', href=re.compile('http.*\.mp3'))
                for url in [x['href'] for x in anchors]:
                    filename = url.rsplit('/', 1)[1]
                    file_path = os.path.join(genre, filename)
                    mp3 = requests.get(url, stream=True)
                    with open(file_path, 'wb') as fd:
                        for chunk in mp3.iter_content(1024):
                            fd.write(chunk)
                    audio_keys.append(filename)

                title = row1.find(class_='producttitle').find('span').text
                label = row1.find(class_='productlabel').find('span').text
                catno = row2.find('span').text
                artist = row1\
                    .find(class_='productartist')\
                    .find('span')\
                    .find('a')\
                    .text
                format_ = row1\
                    .find(class_='producttitle')\
                    .text.strip('\t\n\r')\
                    .split('(', 1)[1]\
                    .split(')')[0]
                tracks = filter(None, [
                    x.strip() for x in row3.find('span').text
                    .encode('utf8')
                    .replace('\t', '')
                    .replace('\n', '')
                    .replace('\xa0', '')
                    .replace('\xc2', '')
                    .splitlines()
                ])

                csv_writer.writerow([
                    artist,
                    title,
                    label,
                    catno,
                    format_,
                    'Electronic',
                    genre.replace('-', ' ').title(),
                    ', '.join(tracks),
                    ', '.join(image_keys),
                    ', '.join(audio_keys),
                ])
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue

        time.sleep(sleep)


if __name__ == "__main__":
    main()
