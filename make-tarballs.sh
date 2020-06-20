#!/bin/bash

# lets clean it first
rm h19term-distribution.tar.gz
rm h19term-install.tar.gz

# Make tarballs for h19term

mkdir h19term-src

cp -v h19-readme.txt h19term-src
cp -v h19-keys.odt h19term-src
cp -v ascii.txt h19term-src
cp -v beep1.wav h19term-src
cp -v h19term h19term-src
cp -v h19term.py h19term-src
cp -v h19term.xpm h19term-src
cp -v h19term.desktop h19term-src
cp -v install.sh h19term-src
cp -v cpm-help.txt h19term-src
cp -v H19term16x32.psfu.gz h19term-src
cp -v Heathkit-H19-bitmap.otb h19term-src
cp -v Heathkit-H19.otf h19term-src
cp -v INSTALLATION.txt h19term-src
cp -v RX.COM h19term-src

cd h19term-src

find . -maxdepth 1 -name '*' -printf '%P\0' \
| tar --null -C '.' --files-from=- -czf '../h19term-distribution.tar.gz'

cd ..
tar cvzf h19term-install.tar.gz h19term-distribution.tar.gz install.sh INSTALLATION.txt README.md

rm -rf h19term-src

