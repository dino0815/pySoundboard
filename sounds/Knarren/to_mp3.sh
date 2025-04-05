#!/bin/bash
#sox "$1" "${1%.*}.mp3"
for file in "$1"/*.{wav,ogg,flac}; do
  ffmpeg -i "$1" "${1%.*}.mp3"    ...
done

