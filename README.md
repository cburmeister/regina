![Juno](https://raw.githubusercontent.com/cburmeister/regina/master/image.jpg)

regina
===========

Fetch new releases from http://www.juno.co.uk/.

---

## Install

```bash
$ python setup.py install
```

## Usage

The script performs three functions:

- Generates a CSV of release information
- Downloads images of new releases
- Downloads audio samples of new releases

```bash
$ regina deep-house today 10
$ regina minimal-tech-house eight-weeks 500
$ regina house this-week 50
```

Check out the help for all available arguments:

```bash
$ regina --help
```

## Examples

Run this weekly with `cron` to browse new releases via iTunes:

```bash
python regina.py deep-house this-week 500 && \
    mv deep-house/*.mp3 \
    ~/Music/iTunes/iTunes\ Media/Automatically\ Add\ to\ iTunes.localized/ && \
    rm -rf deep-house
```
