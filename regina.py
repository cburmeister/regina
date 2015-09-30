#!/usr/bin/python

import re
import csv
import click
import shutil
import requests
from bs4 import BeautifulSoup
from itertools import izip_longest


genres = ['house', 'deep-house', 'techno', 'minimal-tech-house']
windows = ['this-week', 'today', 'eight-weeks']
limits = ['10', '20', '50', '100', '500']


@click.command()
@click.option('--genre', type=click.Choice(genres), help='Whatchu feel like listening to?')
@click.option('--window', type=click.Choice(windows), help='How far back you feel like lookin?')
@click.option('--limit', type=click.Choice(limits), help='How many releases you finna download?')
@click.option('--sleep', default=3, help='Be Nice :D')
@click.option('--filename', help='Where do you wanna put this file?')
def main(genre, window, limit, sleep, filename):
    """
    Browse new releases from http://www.juno.co.uk/ without leaving the prompt.
    """
    base_url = 'http://www.juno.co.uk/'
    url = '{}/{}/{}/?items_per_page={}'.format(base_url, genre, window, limit)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    table = soup.find(class_='product_list')
    products = table.find_all(attrs={'ua_location': re.compile('product')})

    def grouper(n, iterable, fillvalue=None):
        args = [iter(iterable)] * n
        return izip_longest(fillvalue=fillvalue, *args)

    with open(filename, 'wb') as out_file:
        csv_writer = csv.writer(out_file)
        csv_writer.writerow([
            'artist', 'title', 'label', 'catno', 'format', 'genre', 'style',
            'tracks', 'images',
        ])
        for idx, (row1, row2, row3) in enumerate(grouper(3, products)):
            try:
                artist = row1\
                    .find(class_='productartist')\
                    .find('span')\
                    .find('a')\
                    .text
                title = row1.find(class_='producttitle').find('span').text
                url = row1.find(class_='producttitle').find('a', class_='jhighlight')['href']
                label = row1.find(class_='productlabel').find('span').text
                catno = row2.find('span').text
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

                r = requests.get(base_url + url)
                soup2 = BeautifulSoup(r.content, 'lxml')

                image_keys = []
                images = soup2.find('div', class_='product-images-large')
                for image_idx, image in enumerate(images.find_all('img')):
                    r = requests.get(image['src'], stream=True)
                    if r.status_code == 200:
                        key = '{}-{}-{}.jpeg'.format(filename, idx, image_idx)
                        with open(key, 'wb') as f:
                            r.raw.decode_content = True
                            shutil.copyfileobj(r.raw, f)
                            image_keys.append(key)

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
                ])
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue


if __name__ == "__main__":
    main()
