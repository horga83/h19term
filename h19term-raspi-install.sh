#!/bin/bash

# This script installs the H19term software, sets the systems font and 
# sets the user profile to start in h19term

# Version 1 - July 31, 2019

# Make sure we are user root!!!
if [ "`whoami`" != "root" ] ; then
  echo "This program must be run as user ROOT!"
  exit 1
fi

# Detects ARM (Raspberry Pi) devices, and sets a flag for later use
if (cat /proc/cpuinfo | grep ARM >/dev/null) ; then
  RPI=YES
fi

# Debian Systems

if [ -f /etc/debian_version ] ; then
  OS=Debian
else
  OS=Unknown
fi

# Prepare debian systems for the installation process
if [ "${OS}" = "Debian" ] ; then

    # Detect the version of Debian, and do some custom work for different versions

    if (grep -q "11." /etc/debian_version) ; then
      DEBIAN_VERSION=11
    elif (grep -q "10." /etc/debian_version) ; then
      DEBIAN_VERSION=10
    elif (grep -q "9." /etc/debian_version) ; then
      DEBIAN_VERSION=9
    else
      DEBIAN_VERSION=UNSUPPORTED
    fi

    if [ "${DEBIAN_VERSION}" = "UNSUPPORTED" ] ; then
      echo "This script will only work on Debian 9 (Stretch) or newer installs at this"
      echo "time."
      exit 1
    fi

    ########### START DEBIAN ###########

    clear

    echo "H19TERM"
    echo
    echo "This script is required in order to prepare your Debian ${DEBIAN_VERSION}"
    echo "system to run H19term. "
    echo
    echo "*****ATTENTION******"
    echo "This script has only been tested on a fresh installation..."
    echo
    echo "If you are proficient in Linux, you should view this script in detail"
    echo "before running it."
    echo
    echo -n "Press ENTER to continue, or CTRL-C to exit : " ; read ENTER

    if [ "${RPI}" = "YES" ] ; then
      if [ ${DEBIAN_VERSION} -lt 9 ] ; then 
        echo
        echo "**** ERROR ****"
        echo "This script will only work on Debian 9 (Stretch) or newer Lite images at this"
        echo "time. No other version of Debian is supported. "
        echo "**** EXITING ****"
        exit -1
      fi
    fi

    # Updates the apt database to the latest packages
    echo
    echo -n "Updating the apt-get software repository database, this takes a minute ... "
      apt-get -qq update >/dev/null 2>&1
    echo "[ DONE ]"

    # Ask user if they want to perform an update to the filesystem now. This will take some time
    # but it will make sure the user starts with the latest and greatest software.

    echo
    echo "**** DEBIAN LINUX SOFTWARE UPDATE ****"
    echo "Would you like to perform a software update to ensure this system is running"
    echo "the latest versions of the software packages installed? This process will take"
    echo "some time, but is recommended."
    echo
    echo -n "Press ENTER to continue, or type \"n\" to skip : " ; read CHOOSE

    if [ "${CHOOSE}" = "n" ] || [ "${CHOOSE}" = "N" ] ; then
      echo "Skipping software update"
    else
      echo -n "Updating installed software packages (~5 mins) ... "
      apt-get -y -qq upgrade >/dev/null 2>&1
      echo "[ DONE ]"
    fi


    # Installs required packages:
    echo -n "Installing packages needed for H19term... "

        wget http://www.cowlug.org/Downloads/h19term.zip
        cd /home/pi
        unzip h19term.zip

        echo 
        echo "Making directory /usr/share/H19term..."
        mkdir /usr/share/h19term
        sleep 1
        echo
        echo "Copying H19 fonts to /usr/share/H19term..."
        
        cp h19term-master/H19term* /usr/share/h19term
        mv h19term-master/* .
        chown -R pi /home/pi        
        
        echo 
        echo "Changing locale to en_US.UTF.8..."
        # set locale to en_US.UTF.8        
        perl -pi -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/g' /etc/locale.gen
        locale-gen en_US.UTF-8
        update-locale en_US.UTF-8

        echo 
        echo "Changing keyboard to pc104/us..."
        # Set keyboard to pc104/us
        perl -pi -e 's/XKBMODEL="pc105/XKBMODEL="pc104/g' /etc/default/keyboard
        perl -pi -e 's/XKBLAYOUT="gb/XKBLAYOUT="us/g' /etc/default/keyboard

    if [ "${DEBIAN_VERSION}" = "10" ] ; then 
        apt-get -y -qq install python-serial >/dev/null 2>&1
        echo
        echo "Setting font to H19term16x32..."        
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
./h19term.py
echo
echo -n "Would you like to shutdown the system \"y\" or \"Y\" for yes or \"ENTER\" for no? "
read CHOICE
if [ "${CHOICE}" = "y" ] || [ "${CHOICE}" = "Y" ] ; then
    sudo shutdown -h now
fi
EOF
    # Debian 9 - Several packages depreciated and no longer available
    elif [ "${DEBIAN_VERSION}" = "9" ] ; then 
        apt-get -y -qq install python3-serial >/dev/null 2>&1
        echo
        echo "Setting font to H19term16x32..."        
        cp H19term* /usr/share/h19term
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

        echo "./h19term.py" >> /home/pi/.profile

    else
        apt-get -y -qq install python3-serial >/dev/null 2>&1
        echo
        echo "Setting font to H19term16x32..."        
        cp H19term* /usr/share/h19term
        echo "FONT=/usr/share/h19term/H19term16x32.psfu.gz" >>/etc/default/console-setup

        echo 
        echo "Setting auto run of h19term.py for user pi..."
        cat > /home/pi/.profile << EOF
./h19term.py
echo
echo -n "Would you like to shutdown the system \"y\" or \"Y\" for yes or \"ENTER\" for no? "
read CHOICE
if [ "${CHOICE}" = "y" ] || [ "${CHOICE}" = "Y" ] ; then
    sudo shutdown -h now
fi
EOF

    fi

    echo "[ DONE ]"

    echo
    echo "You may now reboot your Raspberry Pi..."

    echo
    echo "Upon first run h19term will ask which serial port to use and"
    echo "setup some other configuration options which it writes into a "
    echo "~/.h19termrc file."
    echo
    echo "It will only do this on first run."
    echo "Type ./h19term.py from the command line or reboot to run."
    #sleep 5
    #reboot
fi
echo done.
