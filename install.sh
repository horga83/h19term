#!/bin/bash

# This script installs the H19term software on a Linux X11 desktop such
# as GNOME or KDE.


# Version 1 - May 02, 2020

# Make sure we are user root!!!
if [ "`whoami`" != "root" ] ; then
  echo "This program must be run as user ROOT!"
  exit 1
fi


    clear

    echo "H19TERM"
    echo
    echo "Installation script for installing H19term. "
    echo
    echo "*****ATTENTION******"
    echo "This script has only been tested on a fresh installation..."
    echo
    echo "If you are proficient in Linux, you should view this script in detail"
    echo "before running it."
    echo
    echo -n "Press ENTER to continue, or CTRL-C to exit : " ; read ENTER


    echo 
    echo "Making directories under /usr/local/share..."
    mkdir -pv /usr/local/share/applications
    mkdir -pv /usr/local/share/h19term
    mkdir -pv /usr/local/share/icons
    mkdir -pv /usr/local/share/fonts


    # I put sleeps in here just for human comfort:-)        
    sleep .5
    echo
    echo "Changing to /usr/local/share/h19term..."
    mwd=`pwd`
    cd /usr/local/share/h19term
    sleep .2
    echo "Untaring H19term files..."
    tar xvzf $mwd/h19term-distribution.tar.gz
    sleep .2        
    echo "Copying Python and resource files..."
    sleep .1
    cp -v h19term.desktop /usr/local/share/applications
    sleep .1
    cp -v h19term /usr/local/bin
    sleep .1
    cp -v h19term.py /usr/local/bin
    sleep .1
    cp -v h19term.xpm /usr/local/share/icons
    sleep .1
    cp -v Heathkit-H19-bitmap.otb /usr/local/share/fonts
    sleep .2
    echo "Making sure h19term and h19term.py are executable..."
    chmod +x /usr/local/bin/h19term
    chmod +x /usr/local/bin/h19term.py

    echo
    echo "We now need to select a default terminal when running under a"
    echo "Linux Graphical Desktop."
    re='^[0-9]+$'
    while [ 1 ]
    do
        echo
        echo "Please select one of the following:"
        echo "1) GNOME - gnome-terminal"
        echo "2) Mate  - mate-terminal"
        echo "3) XFCE  - xfce4-terminal"
        echo "4) KDE   - konsole" 
        echo -n "Your choice, or CTRL-C to exit : " ; read MYTERM

        # Is it a digit?
        if ! [[ $MYTERM =~ $re ]] ; then
            echo
            echo "Error: Not a number..."
            sleep .5
            continue
        fi
        if [ $MYTERM -lt 1 ] || [ $MYTERM -gt 4 ]; then
            echo
            echo "Must select between 1 and 4..."
            sleep .5
            continue
        else
            break
        fi
    done

    case "$MYTERM" in
        1)
            echo "You have selected Gnome Terminal..."
            ;;
        2)
            echo "You have selected Mate Terminal..."
            ;;
        3)
            echo "You have selected XFCE4 Terminal..."
            ;;
        4)
            echo "You have selected KDE Konsole Terminal..."
            ;;
    esac
    
    echo "Editing /usr/local/bin/h19term script.."    
    sed -i "s/TERMINAL=[1234]/TERMINAL=$MYTERM/g" /usr/local/bin/h19term
    echo
    
    echo "[ FINISHED... ]"

    echo
    echo "Upon first run h19term will ask which serial port to use and"
    echo "setup some other configuration options which it writes into a "
    echo "~/.h19termrc file."
    echo
    echo "It will only do this on first run."
    echo "run H19term from your desktop menus or search or type \"h19term\""
    echo "from gnome-terminal or similar."
    echo
    
