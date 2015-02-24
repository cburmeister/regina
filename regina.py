#!/usr/bin/python

import os
import re
import time
import click
import requests
from bs4 import BeautifulSoup

genres = [
    'house',
    'deep-house',
    'techno',
    'minimal-tech-house',
]

windows = [
    'this-week',
    'today',
    'eight-weeks',
]


@click.command()
@click.option('--genre', type=click.Choice(genres), help='Whatchu feel like listening to?')
@click.option('--window', type=click.Choice(windows), help='How far back you feel like lookin?')
@click.option('--sleep', default=3, help='Be Nice :D')
def main(genre, window, sleep):
    """
    Browse new releases from http://www.juno.co.uk/ without leaving the prompt.
    """
    r = requests.get('http://www.juno.co.uk/%s/%s/' % (genre, window))
    soup = BeautifulSoup(r.content)

    urls = soup.findAll('a', href=re.compile('http.*\.mp3'))

    for url in [x['href'] for x in urls]:
        filename = url.rsplit('/', 1)[1]

        dir_path = os.path.join('/tmp', genre, window)
        file_path = os.path.join(dir_path, filename)
        click.echo('Downloading {0} to {1}'.format(url, file_path))

        try:
            os.makedirs(dir_path)
        except OSError:
                pass # already exists

        mp3 = requests.get(url, stream=True)

        with open(file_path, 'wb') as fd:
            for chunk in mp3.iter_content(1024):
                fd.write(chunk)

        time.sleep(sleep)


if __name__ == "__main__":
   main()
