#!/bin/bash

# This script uninstalls the H19term software on Linux


# Version 1 - May 02, 2020

# Make sure we are user root!!!
if [ "`whoami`" != "root" ] ; then
    echo
    echo "This program must be run as user ROOT!"
    echo "You can invoke with sudo: \"sudo ./uninstall.sh\""
    echo
    exit 1
fi


    clear

    echo "H19TERM"
    echo
    echo "Uninstallation script for removing H19term. "
    echo
    echo "If you are proficient in Linux, you should view this script in detail"
    echo "before running it."
    echo
    echo -n "Press ENTER to continue, or CTRL-C to exit : " ; read ENTER


    # I put sleeps in here just for human comfort:-)        
    sleep .5
    echo
    echo "Changing to /usr/local/share/h19term..."
    cd
    mwd=`pwd`
    cd /usr/local/share/h19term
    sleep .2
    echo "Removing H19term files..."
    rm -v *
    sleep .1
    rm -v /usr/local/share/applications/h19term.desktop 
    sleep .1
    rm -v /usr/local/bin/h19term
    sleep .1
    rm -v /usr/local/bin/h19term.py
    sleep .1
    rm -v /usr/local/share/icons/h19term.xpm
    sleep .1
    rm -v /usr/local/share/fonts/Heathkit-H19-bitmap.otb
    sleep .1
    echo "Removing /usr/local/share/h19term..."
    rmdir -v /usr/local/share/h19term
    cd $mwd

    echo "[ FINISHED... ]"


