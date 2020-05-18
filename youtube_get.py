#!/usr/bin/python

import urllib2
import urlparse
import argparse

parser = argparse.ArgumentParser(description='get flv url from youtube')
parser.add_argument('video_id', help='video id of the movie')
args = parser.parse_args()

f = urllib2.urlopen('https://www.youtube.com/get_video_info?el=detailpage&video_id=' + args.video_id)
vinfo = urlparse.parse_qs(f.read())
f.close()

url_encoded_fmt_stream_map = urlparse.parse_qs(vinfo['url_encoded_fmt_stream_map'][0])
print(url_encoded_fmt_stream_map['url'][0])