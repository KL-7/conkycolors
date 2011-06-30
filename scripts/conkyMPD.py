#!/usr/bin/python
import mpd
import os
import re
import socket
import sys
import textwrap

mpd_host = 'localhost'
mpd_port = 6600
music_dir = '/home/kl-7/Music/Artists'
art_link = '/tmp/mpd.jpg'
wrap_length = 33

client = mpd.MPDClient()

try:
    client.connect(mpd_host, mpd_port)
except socket.error:
    sys.exit(1)

song = client.currentsong()
album_dir = os.path.dirname(os.path.join(music_dir, song['file']))
if re.compile(r'(?i)cd\s*\d+').match(os.path.split(album_dir)[1]):
    album_dir = os.path.split(album_dir)[0]

for art_name in ('artwork.jpg', 'cover.jpg'):
    art_path = os.path.join(album_dir, art_name)
    if os.path.isfile(art_path):
        break
else:
    art_path = None

if art_path and os.path.realpath(art_link) != art_path:
    try:
        if os.path.isfile(art_link):
            os.remove(art_link)
        os.symlink(art_path, art_link)
    except OSError:
        art_link = None

track = '#%s ' % song['track'] if song['track'] else ''
title = textwrap.wrap(track + song['title'], wrap_length, break_on_hyphens=False, subsequent_indent=' '*3)
title[0] = title[0][len(track):]

artist = textwrap.wrap('by ' + song['artist'], wrap_length, break_on_hyphens=False, subsequent_indent=' '*3)
artist[0] = artist[0][len('by '):]

year = ' [%s]' % song['date'] if song['date'] else ''
album = textwrap.wrap('from ' + song['album'] + year, wrap_length, break_on_hyphens=False, subsequent_indent=' '*3)
album[0] = album[0][len('from '):]

layout = []

if os.path.isfile(art_link):
    layout.append('${image /tmp/mpd.jpg -s 210x210 -p 12,274}\n${voffset 212}')
else:
    layout.append('${voffset 7}')

layout.append('${goto 8}${font Droid Sans:style=Bold:size=9}${color2}%s' % track.replace('#', '\#'))
layout.append('\n${goto 16}'.join(line.strip() for line in title))
layout.append('${color}${font}')

layout.append('\n${goto 8}by ${font Droid Sans:style=Bold:size=9}${color2}')
layout.append('\n${goto 16}'.join(line.strip() for line in artist))
layout.append('${color}${font}')

layout.append('\n${goto 8}from ${font Droid Sans:style=Bold:size=9}${color2}')
layout.append('\n${goto 16}'.join(line.strip() for line in album))
layout.append('${color}${font}')

layout.append('\n${goto 8}${voffset 3}${color2}$mpd_elapsed${alignr}$mpd_length')
layout.append('\n${voffset -14}${alignc}${mpd_bar 8,145}${color}')

print >> sys.stdout, ''.join(layout)

