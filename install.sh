#!/bin/bash

# This script installs the H19term software on a Linux X11 desktop such
# as GNOME or KDE.



REMOVE()
{
    #I put sleeps in here just for human comfort:-)        
    sleep .5
    echo
    echo "Changing to /usr/local/share/h19term..."
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
}

# Version 1 - May 02, 2020

# Make sure we are user root!!!
if [ "`whoami`" != "root" ] ; then
  echo "This program must be run as user ROOT!"
  echo "Try: \"sudo ./install.sh\""
  echo
  exit 1
fi

clear
echo "H19TERM"
echo
echo "Installation script for installing H19term. "
echo
echo "If you are proficient in Linux, you should view this script in detail"
echo "before running it."
echo
echo -n "Press ENTER to continue, or CTRL-C to exit : " ; read ENTER
if [ -d "/usr/local/share/h19term" ]; then
    echo "H19term is already installed, we will remove the old"
    echo "installation before installing this version"
    echo -n "Press ENTER to continue, or CTRL-C to exit : " ; read ENTER
    REMOVE
    echo
    echo "Proceeding with installation..."
    sleep 2
fi

RPI=NO

# Detects ARM (Raspberry Pi) devices, and sets a flag for later use
if (cat /proc/cpuinfo | grep ARM >/dev/null) ; then
  RPI=YES
fi

if [ $RPI == "YES" ]; then
    echo "Looks like you are installing on a Raspberry Pi..."
    
    V=`cat /etc/debian_version`
    # convert to int
    DEBIAN_VERSION=${V%.*}

    if [ "${DEBIAN_VERSION}" -lt 9 ] ; then
      echo "This script will only work on Debian 9 (Stretch) or newer installs at this"
      echo "time."
      exit 1
    fi

    echo "For H19term to function correctly your locale must be set"
    echo "to en_US.UTF-8..."
    echo
    echo -n "If your are not ok with this please hit CTRL-C to exit" 
    echo " or <Enter> to continue"; read ENTER
    echo "Changing locale to en_US.UTF.8..."
    # set locale to en_US.UTF.8        
    perl -pi -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/g' /etc/locale.gen
    locale-gen en_US.UTF-8
    update-locale en_US.UTF-8

    echo "Setting Linux Console font to H19term16x32..."        
    echo "FONT=/usr/share/h19term/H19term16x32.psfu.gz" >>/etc/default/console-setup
    echo
    echo "Would you like to enable autologin of the \"pi\" user? "
    echo "Press ENTER to enable autologin or \"n\" to skip :" ; read CHOOSE

    if [ "${CHOOSE}" = "n" ] || [ "${CHOOSE}" = "N" ] ; then
        echo "Skipping autologin setup"
    else
        echo -n "Enabling autologin... "
        systemctl set-default multi-user.target
        ln -fs /lib/systemd/system/getty@.service /etc/systemd/system/getty.target.wants/getty@tty1.service
        cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf << EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin $SUDO_USER --noclear %I \$TERM
EOF
        echo "[ DONE ]"
    fi

    echo 
    echo "Setting auto run of h19term.py for user pi..."
    cat > /home/pi/.profile << EOF
/usr/local/bin/h19term.py
echo
echo -n "Would you like to shutdown the system \"y\" or \"Y\" for yes or \"ENTER\" for no? "
read CHOICE
if [ "${CHOICE}" = "y" ] || [ "${CHOICE}" = "Y" ] ; then
    sudo shutdown -h now
fi
EOF
fi

# Check distro
if ( cat /proc/version | grep -i debian >/dev/null ) ; then
  OS=Debian
elif ( cat /proc/version | grep -i arch >/dev/null ) ; then
  OS=Arch
elif ( cat /proc/version | grep -i ubuntu >/dev/null ) ; then
  OS=Debian  
fi

if [ $OS == "Debian" ]; then
    echo "It looks like you are running a Debian/Ubuntu/Mint"
    echo "distribution.  Installing requirements with apt-get..."
    echo
    apt-get install python3-pyserial
    apt-get install python3-pip
    pip3 install pysinewave
    pip3 install pyaudio
elif [ $OS == "arch" ]; then
    echo "It looks like you are running an Arch based distribution."
    echo "Installing requirements with pacman..."
    echo
    pacman -S python-pyserial
    pacman -S python-pip
    pip3 install pysinewave
    pip3 install pyaudio
fi

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
cp -v Heathkit-H19.otf /usr/local/share/fonts
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
    echo "5) Other" 
    echo -n "Your choice, or CTRL-C to exit : " ; read MYTERM
    # Is it a digit?
    if ! [[ $MYTERM =~ $re ]] ; then
        echo
        echo "Error: Not a number..."
        sleep .5
        continue
    fi
    if [ $MYTERM -lt 1 ] || [ $MYTERM -gt 5 ]; then
        echo
        echo "Must select between 1 and 5..."
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
    5)
        echo "You have selected OTHER as your terminal..."
        echo "You will have to hand edit the /usr/local/bin/h19term file."
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
    
