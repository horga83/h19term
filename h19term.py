#! /usr/bin/python3
# coding=utf-8
#
#-------------------------------------------------------------------------------
#  H19term - Heathkit H19 Terminal emulator
#
#  Copyright (c) 2014 George Farris - farrisga@gmail.com
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#-------------------------------------------------------------------------------

# Release history
# Dec 27, 2014 - V1.0  Initial release
# Dec 28, 2014 - V1.1  Fixed serial port open error not reporting
# Jan 01, 2015 - V1.2  Add popup on CTRL-A,  Now CTRL-A x to exit
#                      Add serial port logging - CTRL-A l to toggle
#                      Add popup window with help and ascii table
#                      Add introduction screen
#                      Changed name to H19term
# Jan 04, 2015 - V1.3  Fix clear to end of line and erase line bug
#                      Fix reset of status line display
# (Ywing2 works now)   Add discard at end of line logic to addchar
#                      Add cursor on and off to mode setting
# Jan 15, 2015 - V1.4  Add loop timer to stop 100% CPU (who needs threads)
#                      Add F12 offline and F11 ERASE key function
#                      Add Auto time and date when booting HDOS or CP/M
#                      Add CTRL keys for DEL and BREAK key
#                      Pass TAB char through
#                      Add preload font to setup.
#                      Speed up serial I/O for Raspbery Pi
# Jan 20, 2015 - V1.5  Add configuration file (.h19termrc) support for settings
#                      Add file prefix support for installing in any directory
#                      Fix erase to beginning of line
#                      Fix reverse linefeed
#                      Fix backspace when not expecting BS echo
#                      Tested PIE editor which now works.
#                      Added CTRL-A CTRL-A to send CTRL-A through to application.
# Jan 29, 2015   V1.6  Fix get config file, was using get instead of getboolean
#                      Change h19term to 27x80 instead of 28x80.
#                      Add probe and selection of serial port on first run.
#                      Added 10x20, 12x24 and 14x28 font.
#                      Fix linefeed indexing - it fixed HDOS MAPLE.
#                      Added configuration of serial port on first run.
#                      Added timer to keyboard repeat to stop over runs
# Feb 07, 2015   V1.7  Added colour support
# Feb 24, 2015   V1.8  Fix keyboard repeat code to not miss char typed
#                      Add change baud rate functions - with Super-19 baud rates
#                      19200 and 38400 added.
# Jan 22, 2016   V1.9  Fix bug in heath_escape_seq  - thanks Jason Kersten
# Nov 28, 2019   V1.10 Add ESC-Z function, identify as VT52
# Jan 03, 2020   V1.11 Fix ANSI shifted keypad mode - fixes Sasix
# Jan 16, 2020   V1.12 Fix backspace, it's a move not a delete
#                      Also better format for serial port logging, each character
#                      output is on a new line with < > around it.
# Apr 02, 2020   V1.13 Add setting of baud rate
#                      Add striping of high bit on incoming characters.
# Apr 03, 2020   V1.14 Add changing the port on the fly.
# Apr 11, 2020   V2.0  Python 3 version
# May 02, 2020   V2.1  Added Heathkit-H19-bitmap font for desktop use.
#                      Many fixes.
# May 16, 2020   V2.2  Added Xmodem support.

import os
import re
import sys
import time
import curses
import locale
import serial
import string
import datetime
import configparser
from pysinewave import SineWave


# This must be set to output unicode characters
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()


# ************* USER MODIFIABLE SETTINGS ************************************
# Do not modify these settings here any more, edit the .h19termrc file instead,
# you will find it in your home directory.

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

# This is the root directory for h19term except for .h19termrc which is in your
# home directory.  All the help files etc live here.
INSTALL_PATH = '/usr/local/share/h19term/'

PRELOAD_FONT = False
FONT = 'H19term16x32.psfu.gz'  # This font works on Raspberry Pi
BEEP = 'beep1.wav'

AUTO_CPM_DATE = False
AUTO_HDOS_DATE = False
CPM_DATE_FORMAT = "Enter today's date (MM/DD/YY): "
CPM_TIME_FORMAT = "Enter the time (HH:MM:SS): "
HDOS_DATE_FORMAT = r"^Date.(\d\d-\w\w\w-\d\d)?."      # Date (01-Jan-77)?
# Haven't tested this as I don't have the date patches in for HDOS

# Colours defined when running on Raspberry Pi or Linux Console.  This does not
# set the colours when running under X11.
LC_WHITE = 'FFFFFF'
LC_GREEN = '00AA00'
LC_YELLOW = 'FFA400'
LC_BLUE = '0000AA'
LC_CYAN = '00AAAA'
LC_MAGENTA = 'AA00AA'
LC_RED = 'AA0000'

BAUD_RATES=[1200,2400,4800,9600,19200,38400,57600]

# Set default colour
# 0 - white, 1 - green, 2 - yellow, 3 - blue, 4 - cyan, 5 - magenta, 6 - red
DEFAULT_COLOUR = 0


# ************  END OF USER MODIFIABLE SETTINGS *****************************

VERSION = 'V2.1 - Python 3'
VERSION_DATE = 'May 02, 2020'

CONFIG_FILE = os.path.join(os.environ['HOME'], '.h19termrc')
LOG_FILE = os.path.join(os.environ['HOME'], 'h19term.log')

SIO_WAIT = None
SIO_NO_WAIT = 0

SHIFT_FKEY = curses.KEY_F9
ENTER_FKEY = curses.KEY_F10
ERASE_FKEY = curses.KEY_F11
OFFLINE_FKEY = curses.KEY_F12

CURSOR_INVISIBLE = 0    # no cursor
CURSOR_NORMAL = 1       # Underline cursor
CURSOR_BLOCK = 2        # Block cursor

NORM = 0    # Index for numkeys array
H_ALT = 1
A_ALT = 2
SHIFT = 3
ASHIFT = 4

LF = '\x0a'
CR = '\x0d'
BS = '\x08'
DEL = '\x7f'
BEL = '\x07'
TAB = '\x09'
ESC = '\x1b'
NUL = '\x00'

KEY = 1  # Used in backspace to tell if key or incoming serial char
BLANK_LINE = "                                                                               "

NOCHAR = -1
CURSOR = [0,0]
SAVED_CURSOR = [0,0]

KEY_REPEAT_RATE = 0.09  #10ish CPS, more than this and PIE editor has char overflows

class H19Keys:

    fnkeys = {
        #                       Key      Heath     Ansi
        #-------------------------------------------------
        curses.KEY_F1:  'S',	# F1     ESC S     ESC O S
        curses.KEY_F2:  'T',	# F2     ESC T     ESC O T
        curses.KEY_F3:  'U',	# F3     ESC U     ESC O U
        curses.KEY_F4:  'V',	# F4     ESC V     ESC O V
        curses.KEY_F5:  'W',	# F5     ESC W     ESC O W

        curses.KEY_F6:	'P',	# BLUE   ESC P     ESC O P
        curses.KEY_F7:  'Q',	# RED    ESC Q     ESC O Q
        curses.KEY_F8:  'R',	# WHITE  ESC R     ESC O R

        curses.KEY_F9:   '*',	# Shift key to change keypad
        curses.KEY_F11:  '*',	# ERASE key
        curses.KEY_F12:  '*',	# Terminal OFFLINE key
    }

    numkeys = {
        # Keypad group: Note F12 is the ENTER key because we can't distinguish
        # between the two ENTER keys, they both return ctrl-j
        #            UNSHIFTED    HEATH     ANSI      SHIFTED     ANSI
        #                       UNSHIFTED UNSHIFTED              SHIFTED
        #                       ALTERNATE ALTERNATE
        #----------------------------------------------------------------
        curses.KEY_IC:    ['0', '\x1b?p', '\x1bOp',   '0',      '0'],
        curses.KEY_END:   ['1', '\x1b?q', '\x1bOq',   '\x1bL',  '\x1b[L'],
        curses.KEY_DOWN:  ['2', '\x1b?r', '\x1bOr',   '\x1bB',  '\x1b[B'],
        curses.KEY_NPAGE: ['3', '\x1b?s', '\x1bOs',   '\x1bM',  '\x1b[M'],
        curses.KEY_LEFT:  ['4', '\x1b?t', '\x1bOt',   '\x1bD',  '\x1b[D'],
        curses.KEY_B2:    ['5', '\x1b?u', '\x1bOu',   '\x1bH',  '\x1b[H'],
        curses.KEY_RIGHT: ['6', '\x1b?v', '\x1bOv',   '\x1bC',  '\x1b[C'],
        curses.KEY_HOME:  ['7', '\x1b?w', '\x1bOw',   '\x1bO'],
        curses.KEY_UP:    ['8', '\x1b?x', '\x1bOx',   '\x1bA',  '\x1b[A'],
        curses.KEY_PPAGE: ['9', '\x1b?y', '\x1bOy',   '\x1bN',  '\x1b[P'],
        curses.KEY_DC:    ['.', '\x1b?n', '\x1bOn',   '.',      '.'],
        curses.KEY_F10:   ['\x13', '\x1b?M', '\x1bOM', '\x13',  '\x13'],
    }



class H19Screen:

    def __init__(self, scn, stat):
        self.screen = scn
        self.status = stat


    h19_graphics = [
        '\u25CF',  # ^ '⚫' BLACK CIRCLE.
        '\u25E5',  # - '◥' UPPER RIGHT TRIANGLE.
        '\u2503',  # ` '│' LIGHT VERTICLE LINE.
        '\u2501',  # a '─' LIGHT HORIZONTAL LINE.
        '\u254B',  # b '┼' LIGHT PLUS.
        '\u2513',  # c '┐' LIGHT UPPER RIGHT CORNER.
        '\u251B',  # d '┘' LIGHT LOWER RIGHT CORNER.
        '\u2517',  # e '└' LIGHT LOWER LEFT CORNER.
        '\u250F',  # f '┌' LIGHT UPPER LEFT CORNER.
        '\u00B1',  # g '±' LIGHT PLUS MINUS.
        '\u279C',  # h '→' RIGHT ARROW.
        '\u2591',  # i '▒' MEDIUM SHADE.
        '\u259A',  # j '▚' QUADRANT UPPER LEFT LOWER R.
        '\u2B07',  # k '↓' DOWN ARROW.
        '\u2597',  # l '▗' QUADRANT LOWER RIGHT.
        '\u2596',  # m '▖' QUADRANT LOWER LEFT.
        '\u2598',  # n '▘' QUADRANT UPPER LEFT.
        '\u259D',  # o '▝' QUADRANT UPPER RIGHT.
        '\u2580',  # p '▀' UPPER HALF BLOCK.
        '\u2590',  # q '▐' RIGHT HALF BLOCK.
        '\u25E4',  # r '◤' UPPER LEFT TRIANGLE.
        '\u2533',  # s '┬' LIGHT DOWN HORIZONTAL.
        '\u252B',  # t '┤' LIGHT VERTICAL LEFT.
        '\u253B',  # u '┴' LIGHT UP HORIZONTAL.
        '\u2523',  # v '├' LIGHT VERTICAL RIGHT.
        '\u2573',  # w '╳' LIGHT CROSS.
        '\u2571',  # x '╱' LIGHT RIGHT.
        '\u2572',  # y '╲' LIGHT LEFT.
        '\u2594',  # z '▔' UPPER HORIZONTAL LINE.
        '\u2581',  # { '▁' LOWER HORIZONTAL LINE.
        '\u258F',  # | '▏' LEFT VERTICAL LINE.
        '\u2595',  # } '▕' RIGHT VERTICAL LINE.
        '\u00B6',  # ~ '¶' PILCROW SIGN
    ]

    def update_cursor(self):
        y,x = self.screen.getyx()
        CURSOR = [y,x]


    # Control keys

    #
    def bell(self):
        if time.time() - self.bell_start_time > 1.0 or self.bell_start_time == 0.0:
            try:
                self.sinewave.play()
                self.bell_start_time = time.time()
                time.sleep(0.16)
                self.sinewave.stop()
            except:
                pass    # sometimes this fails with ugly python throw up


    def backspace(self, sio, ch): # H8 will return ^H <SPACE> ^H when we
        y,x = self.screen.getyx()   # send it a ^H key
        if ch == KEY:
            if x > 0:
                self.sio_write(sio, chr(8))
                c = self.sio_read(sio, TIMEOUT=0.01)   # ^H or timeout
                if c == chr(8):
                    c = self.sio_read(sio, TIMEOUT=0.01)     # <SPACE>
                    if c == ' ':
                        c = self.sio_read(sio, TIMEOUT=0.01) # ^H
                        self.screen.delch(y, x-1)
                    else:
                        self.screen.move(y,x-1)  # sometimes we only get 1 ^H
                else:
                    return(c)

        else:
            if x == 0:
                return('')
            #self.screen.delch(y, x-1)
            self.screen.move(y, x-1)

    def tab(self):  # so far don't need this
        pass

    def linefeed(self):
        y,x = self.screen.getyx()
        if y == 24: # if we are in the 25th line don't scroll
            return
        elif y >= 23:
            self.screen.scrollok(True)
            self.screen.scroll(1)
            y = 23
            self.screen.move(y,x)
        else:
            self.screen.move(y+1,x)
        if self.autoCarriageReturnMode:
            self.screen.move(y,0)

    def carriage_return(self):
        y,x = self.screen.getyx()
        if y == 24: # 25th line
            self.screen.move(24,0)
            return
        #self.log("[Y->%s, X->%s]" % (y,x))
        self.screen.move(y, 0)
        if self.autoLinefeedMode:
            #self.log("[Y->%s, X->%s]" % (y,x))
            self.screen.move(y+1,0)

    def escape(self):
        pass

    def delete(self, sio):
        self.sio_write(sio, chr(177))

    def rubout(self):
        #self.screen.delch()
        #self.screen.addch(' ')
        pass

    def scroll_key(self):
        pass

    def break_key(self, sio):
        sio.sendBreak()

    # Cursor functions
    def cursor_home(self):
        y, x = self.screen.getyx()
        if x == 24:
            self.screen.move(0,x)
        else:
            self.screen.move(0,0)

    def cursor_forward(self, n=1):
        y,x = self.screen.getyx()
        if n == 0:
            n = 1
        if x == 79:
            return
        self.screen.move(y, x+n)

    def cursor_backward(self, n=1):
        y,x = self.screen.getyx()
        if n == 0:
            n = 1
        if x == 0:
            return
        self.screen.move(y, x-n)

    def cursor_down(self, n=1):
        y,x = self.screen.getyx()
        if n == 0:
            n = 1
        if y == 23:
            return
        self.screen.move(y+n, x)

    def cursor_up(self, n=1):
        y,x = self.screen.getyx()
        if n == 0:
            n = 1
        if y == 0:
            return
        self.screen.move(y-n, x)

    def reverse_linefeed(self):
        self.screen.scrollok(True)
        y,x = self.screen.getyx()
        if y == 0:
            self.screen.insertln()
        else:
            self.screen.move(y-1,x)
        #self.screen.scrollok(False)

    def cursor_position_report(self, sio):
        if self.ansiMode:
            y,x = self.screen.getyx()
            sio.write(ESC.encode())
            sio.write(b'[')
            sio.write((chr(x + 32)).encode())
            sio.write(b';')
            sio.write((chr(y + 32)).encode())
            sio.write(b'R')
        else:
            y,x = self.screen.getyx()
            sio.write(ESC.encode())
            sio.write(b'Y')
            sio.write((chr(x + 32)).encode())
            sio.write((chr(y + 32)).encode())

    def save_cursor_position(self):
        y,x = self.screen.getyx()
        SAVED_CURSOR[0] = y
        SAVED_CURSOR[1] = x

    def goto_saved_cursor_position(self):
        self.screen.move(SAVED_CURSOR[0],SAVED_CURSOR[1])
        self.screen.refresh()

    def set_cursor_position(self, line, col):
        if line == 24: # heath line 25
            self.screen.scrollok(False)
        else:
            self.screen.scrollok(True)

        if line > 24:
            return
        if col > 79:
            self.screen.move(line, 79)
            return

        self.screen.move(line, col)

    def can_perform_as_vt52(self,sio):
        sio.write(ESC)
        sio.write('/')
        sio.write('K')

    # Erasing and editing

    def clear_display(self, reset=False):
        if reset:   # reset clears both 24x80 and 25th line
            self.screen.erase()
#        if self.ansiMode and self.enable25thLine:
#            self.screen.erase()
        y, x = self.screen.getyx()
        if y < 24:
            for i in range(24):
                self.screen.move(i, 0)
                self.screen.clrtoeol()
            self.screen.move(0, 0)
        if y == 24:
            self.screen.move(24, 0)
            self.screen.clrtoeol()
            #self.screen.move(24, 0) not sure we need this
            self.screen.refresh()

    def erase_to_beginning_of_display(self):
        y,x = self.screen.getyx()

        self.screen.move(y,0)   # first clear beginning of line to cursor
        self.screen.addnstr(BLANK_LINE, x + 1)

        self.screen.move(0,0)   # now home and clear remaining lines
        if y > 0:
            lines = y
            for i in range(lines):
                self.screen.move(i,0)
                self.screen.clrtoeol()
        self.screen.move(0,0)   # set cursor at beginning of display or maybe

    def erase_to_end_of_page(self):
        y,x = self.screen.getyx()
        self.screen.clrtobot()

    def erase_line(self):
        y,x = self.screen.getyx()
        self.screen.move(y,0)
        self.screen.clrtoeol()
        self.screen.move(y,0)

    def erase_beginning_of_line(self):
        y,x = self.screen.getyx()
        self.screen.move(y,0)
        self.screen.addnstr(BLANK_LINE,x)

    def erase_to_end_of_line(self):
        y,x = self.screen.getyx()
        self.screen.clrtoeol()
        if x > 0:
            self.screen.move(y,x-1)
#        self.screen.refresh()

    def insert_line(self):
        self.screen.insertln()

    def delete_line(self):
        self.screen.deleteln()

    def delete_character(self):
        y,x = self.screen.getyx()
        self.screen.delch()

    def enter_insert_mode(self):
        self.insertMode = True

    def exit_insert_mode(self):
        self.insertMode = False


class H19Term(H19Keys, H19Screen):
    """ H19 terminal.

        Supports I/O using a serial port.
    """

    def __init__(self):
        self.screen = None
        self.status = None
        self.logio = False
        self.baudrate = [110, 150, 300, 600, 1200, 1800, 2000, 2400, 3600, 4800, 7200, 9600, 19200, 38400]

        H19Screen.__init__(self, self.screen, self.status)

    def get_h19config(self):
        global SERIAL_PORT, BAUD_RATE, PRELOAD_FONT, FONT, BEEP
        global AUTO_CPM_DATE, CPM_DATE_FORMAT, CPM_TIME_FORMAT
        global AUTO_HDOS_DATE, HDOS_DATE_FORMAT, INSTALL_PATH
        global KEY_REPEAT_RATE, DEFAULT_COLOUR
        global LC_WHITE, LC_GREEN, LC_YELLOW
        global LC_BLUE, LC_CYAN, LC_MAGENTA, LC_RED
        Config = configparser.ConfigParser(allow_no_value = True)

        updateFile = True
        # If it exists get the settings otherwise write them to a file
        if os.path.isfile(CONFIG_FILE):
            updateFile = False

            try:
                Config.read(CONFIG_FILE)
                #if Config.has_option('General', 'installpath'):
                #    INSTALL_PATH = Config.get('General', 'installpath')
                #else: updateFile = True
                if Config.has_option('General','KeyRepeatRate'):
                    KEY_REPEAT_RATE = Config.getfloat('General','KeyRepeatRate')
                else: updateFile = True
                if Config.has_option('General','SoundFile'):
                    BEEP = Config.get('General','SoundFile')
                else: updateFile = True

                if Config.has_option('SerialComms', 'port'):
                    SERIAL_PORT = Config.get('SerialComms', 'port')
                else: updateFile = True
                if Config.has_option('SerialComms', 'baudRate'):
                    BAUD_RATE = Config.getint('SerialComms', 'baudRate')
                else: updateFile = True

                if Config.has_option('Fonts','Preload'):
                    PRELOAD_FONT = Config.getboolean('Fonts','Preload')
                else: updateFile = True
                if Config.has_option('Fonts','Font'):
                    FONT = Config.get('Fonts','Font')
                else: updateFile = True

                if Config.has_option('Colours','DefaultColour'):
                    DEFAULT_COLOUR = Config.getint('Colours','DefaultColour')
                else: updateFile = True
                if Config.has_option('Colours','White'):
                    LC_WHITE = Config.get('Colours','White')
                else: updateFile = True
                if Config.has_option('Colours','Green'):
                    LC_GREEN = Config.get('Colours','Green')
                else: updateFile = True
                if Config.has_option('Colours','Yellow'):
                    LC_YELLOW = Config.get('Colours','Yellow')
                else: updateFile = True
                if Config.has_option('Colours','Blue'):
                    LC_BLUE = Config.get('Colours','Blue')
                else: updateFile = True
                if Config.has_option('Colours','Cyan'):
                    LC_CYAN = Config.get('Colours','Cyan')
                else: updateFile = True
                if Config.has_option('Colours','Magenta'):
                    LC_MAGENTA = Config.get('Colours','Magenta')
                else: updateFile = True
                if Config.has_option('Colours','Red'):
                    LC_RED = Config.get('Colours','Red')
                else: updateFile = True

                if Config.has_option('Date','AutoCpmDate'):
                    AUTO_CPM_DATE = Config.getboolean('Date','AutoCpmDate')
                else: updateFile = True
                if Config.has_option('Date','CpmDate'):
                    CPM_DATE_FORMAT = Config.get('Date','CpmDate')
                else: updateFile = True
                if Config.has_option('Date','CpmTime'):
                    CPM_TIME_FORMAT = Config.get('Date','CpmTime')
                else: updateFile = True
                if Config.has_option('Date','AutoHdosDate'):
                    AUTO_HDOS_DATE = Config.getboolean('Date','AutoHdosDate')
                else: updateFile = True
                if Config.has_option('Date','HdosDate'):
                    HDOS_DATE_FORMAT = Config.get('Date','HdosDate')
                else: updateFile = True

            except:
                print("Problem reading configuration file .h19termrc, skipping...")

        if updateFile:
            print("\nConfiguration file ~/.h19termrc not found:")
            print("    A new one will be created after serial port selection...")
            print("    You may edit this file to set your defaults...\n")
            print("\nChecking serial ports...")

            enterOne = -1
            availablePorts = []
            try:
                from serial.tools.list_ports import comports
                print("    These are a list of ports found on this system, there may be others")
                print("    but they didn't show up in the probe...\n")

                i = 0
                for port, desc, hwid in sorted(comports()):
                    if hwid != 'n/a':
                        i += 1
                        availablePorts.append(port)
                        print('%s.  %-15s %s' % (i,port, desc))
                print('%s.  %-15s %s' % (i+1,'Enter one', ''))
                enterOne = i+1
            except:
                print("Your python serial package doesn't have the serial port probe")
                print("We'll have to work around it and just offer a couple of standard")
                print("ports without knowing if they actually exist...\n")
                print('%s.  %-15s %s' % ('1','/dev/ttyS0', 'Builtin port '))
                print('%s.  %-15s %s' % ('2','/dev/ttyUSB0', 'USB to RS232 cable'))
                print('%s.  %-15s %s' % ('3','Enter one', ''))
                enetrOne = 3
                availablePorts.append('/dev/ttyS0')
                availablePorts.append('/dev/ttyUSB0')

            print("\n   Please select one of these, or press <Enter> if you would")
            print("   like to enter your own by editing your ~/.h19termrc configuration file.")
            print("   A default baud rate of 9600 will be choosen.\n")

            portno = input("Enter number: ")

            if len(portno) > 0:
                if int(portno) == enterOne:
                    while True:
                        print('\nEnter a port in the form of /dev/<devicename> or <enter> to quit')
                        s = input('Enter port: ')
                        if s == '':
                            print("Using default port -> %s" % SERIAL_PORT)
                            break
                        if not os.path.exists(s):
                            print('That port device doesn\'t exist...')
                        else:
                            SERIAL_PORT = s
                            print("Setting port to -> %s" % SERIAL_PORT)
                            break
                else:
                    SERIAL_PORT = availablePorts[int(portno)-1]
                    print("Setting port to -> %s" % SERIAL_PORT)
            else:
                print("Using default port -> %s" % SERIAL_PORT)
            print("Writing new ~/.h19termrc file...")

            self.write_h19config(True)  # True if it's a new file not a rewrite

    def write_h19config(self, new=False):
        cfgfile = ''
        Config = configparser.ConfigParser(allow_no_value = True)
        try:
            cfgfile = open(CONFIG_FILE, 'w')
        except:
            print("Problem opening configuration file .h19term, skipping...")

        # add the settings to the structure of the file, and lets write it out...
        Config.add_section('General')
        Config.add_section('SerialComms')
        Config.add_section('Fonts')
        Config.add_section('Colours')
        Config.add_section('Date')
        Config.set('General','SoundFile', BEEP)
        #Config.set('General','InstallPath', INSTALL_PATH)
        Config.set('General','# Use caution when increasing repeat rate to avoid overruns')
        Config.set('General','KeyRepeatRate', str(KEY_REPEAT_RATE))
        Config.set('SerialComms','Port', SERIAL_PORT)
        Config.set('SerialComms','BaudRate', str(BAUD_RATE))
        Config.set('Fonts','Preload',str(PRELOAD_FONT))
        Config.set('Fonts','Font',FONT)

        Config.set('Colours','# Custom colours used only for Linux console, see manual')
        Config.set('Colours', 'White', LC_WHITE)
        Config.set('Colours', 'Green', LC_GREEN)
        Config.set('Colours', 'Yellow', LC_YELLOW)
        Config.set('Colours', 'Blue', LC_BLUE)
        Config.set('Colours', 'Cyan', LC_CYAN)
        Config.set('Colours', 'Magenta', LC_MAGENTA)
        Config.set('Colours', 'Red', LC_RED)
        Config.set('Colours','# Default colour of H19term on console or Xterm, see manual')
        Config.set('Colours','DefaultColour', str(DEFAULT_COLOUR))

        Config.set('Date','AutoCpmDate',str(AUTO_CPM_DATE))
        Config.set('Date','CpmDate',CPM_DATE_FORMAT)
        Config.set('Date','CpmTime',CPM_TIME_FORMAT)
        Config.set('Date','AutoHdosDate',str(AUTO_HDOS_DATE))
        Config.set('Date','HdosDate',HDOS_DATE_FORMAT)
        Config.write(cfgfile)
        cfgfile.close()
        if new:
            sys.exit()

    def setup_screen(self):
        self.cur = curses.initscr()  # Initialize curses.
        curses.start_color()

        if curses.termname() == b'linux':
            if PRELOAD_FONT:
                os.system("setfont %s" % os.path.join(INSTALL_PATH, FONT))

            # setup colours for console only, X11 colours are set in the
            # terminal application such as gnome-terminal
            #
            # a hex colour number such as FFA400 is converted as follows
            # curses uses 0-1000 so hex 0xAA = 170 dec which then converts to
            # roughly to int(170*3.92) = 666
            # My amber is FFA400

            r = int(int(LC_WHITE[0:2],16) * 3.92)
            g = int(int(LC_WHITE[2:4],16) * 3.92)
            b = int(int(LC_WHITE[4:6],16) * 3.92)
            curses.init_color(curses.COLOR_WHITE, r,g,b)

            r = int(int(LC_GREEN[0:2],16) * 3.92)
            g = int(int(LC_GREEN[2:4],16) * 3.92)
            b = int(int(LC_GREEN[4:6],16) * 3.92)
            curses.init_color(curses.COLOR_GREEN, r,g,b)

            r = int(int(LC_YELLOW[0:2],16) * 3.92)
            g = int(int(LC_YELLOW[2:4],16) * 3.92)
            b = int(int(LC_YELLOW[4:6],16) * 3.92)
            curses.init_color(curses.COLOR_YELLOW,r,g,b)

            r = int(int(LC_BLUE[0:2],16) * 3.92)
            g = int(int(LC_BLUE[2:4],16) * 3.92)
            b = int(int(LC_BLUE[4:6],16) * 3.92)
            curses.init_color(curses.COLOR_BLUE, r,g,b)

            r = int(int(LC_CYAN[0:2],16) * 3.92)
            g = int(int(LC_CYAN[2:4],16) * 3.92)
            b = int(int(LC_CYAN[4:6],16) * 3.92)
            curses.init_color(curses.COLOR_CYAN, r,g,b)

            r = int(int(LC_MAGENTA[0:2],16) * 3.92)
            g = int(int(LC_MAGENTA[2:4],16) * 3.92)
            b = int(int(LC_MAGENTA[4:6],16) * 3.92)
            curses.init_color(curses.COLOR_MAGENTA,r,g,b)

            r = int(int(LC_RED[0:2],16) * 3.92)
            g = int(int(LC_RED[2:4],16) * 3.92)
            b = int(int(LC_RED[4:6],16) * 3.92)
            curses.init_color(curses.COLOR_RED,r,g,b)
        else:
            self.cur.box()
            self.cur.refresh()

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)


        y, x = self.cur.getmaxyx()
        if y < 31 or x < 82:
            curses.endwin()
            print("\nYour screen is to small to run h19term, it must be")
            print("at least 31 lines by 82 columns...\n")
            print("Consider changing your terminal profile so you do not have")
            print("to change this all the time...\n")
            sys.exit(1)
        #curses.resize_term(31,82)
        curses.cbreak()
        curses.raw()
        curses.noecho()
        curses.nonl()
        self.cur.refresh()
        self.screen = curses.newwin(25,80,1,1)
        self.status = curses.newwin(4,80,26,1)
        self.screen.attrset(curses.color_pair(1))
        self.status.attrset(curses.color_pair(1))
        self.set_colour(DEFAULT_COLOUR)     # set our default colour
        self.screen.refresh()
        self.screen.nodelay(1)
        self.status.nodelay(1)
        self.screen.keypad(1)
        self.status.keypad(1)
        self.screen.scrollok(True)
        self.screen.idlok(1)
        self.screen.setscrreg(0,23)
        self.status.scrollok(False)

        return self.screen, self.status

    def reset(self):
        self.enter_heath_mode()
        self.enable25thLine = False
        self.noKeyClick = False
        self.insertMode = False
        self.holdScreenMode = False
        self.reverseVideoMode = False
        self.graphicsMode = False
        self.keypadShiftedMode = False
        self.keypadAlternateMode = False
        self.status.addstr(1, 40, "   ")
        self.status.addstr(1, 41, "-")
        self.status.refresh()
        self.autoLinefeedMode = False
        self.visibleCursor = True
        self.autoCarriageReturnMode = False
        self.autoLineFeedMode = False
        self.keyboardDisabled = False
        self.wrapAtEndOfLine = False
        self.linesSinceBoot = 0 # used to auto set date
        self.clear_display(True)
        self.cursor_home()
        curses.curs_set(CURSOR_NORMAL)


    def terminate(self):
        curses.endwin() # End screen (ready to draw new one, but instead we exit)

    def open_port(self):
        try:
            sp = serial.Serial(SERIAL_PORT, BAUD_RATE, xonxoff=True, timeout=0)
            return sp
        except:
            print("\nATTENTION!! - Could not open serial port...\n\n")
            print("Please edit the ~/.h19termrc configuration file in your home directory")
            print("and set your serial port.  Most Linux installations will use either")
            print("/dev/ttyS0 or /dev/ttyS1 for the built in motherboard ports or ")
            print("/dev/ttyUSB0 if you have a USB to RS232 converter.\n")
            sys.exit(1)

    def sio_write(self,sio, c):
        if self.offline:
            return
        if self.logio:
            self.log("\n{{%s}}" % c)
            #pass
        while sio.out_waiting > 0:
            pass
        sio.write(str.encode(c))
        #sio.write(c)

    # Sometimes we need to wait for a character so we use this function
    def sio_read(self, sio, TIMEOUT=SIO_WAIT):
        if not self.offline:
            if TIMEOUT == 0:
                c = sio.read(1)
            else:
                sio.timeout = TIMEOUT
                c = sio.read(1)
                sio.timeout = SIO_NO_WAIT
            if len(c) > 0:
                c = chr(ord(c) & 0x7F)
                if self.logio:
                    self.log("%s" % c)
                return(c)
            else:
                return('')
        else:
            return('')

    def log(self, s):
        try:
            log = open(LOG_FILE, 'a')
        except:
            self.bell()
            self.popup_error("Can't open %s for writing" % LOG_FILE)
            return

        log.write(s)
        log.close()

    def process_escape_seq(self, sio):
        if self.ansiMode:
            self.ansi_escape_seq(sio)
        else:
            self.heath_escape_seq(sio)

    def heath_escape_seq(self, sio):
        c = self.sio_read(sio)

        if c == 'A':
            self.cursor_up()
        elif c == 'B':
            self.cursor_down()
        elif c == 'C':
            self.cursor_forward()
        elif c == 'D':
            self.cursor_backward()
        elif c == 'E':
            self.clear_display()
        elif c == 'F':
            self.enter_graphics_mode()
        elif c == 'G':
            self.exit_graphics_mode()
        elif c == 'H':
            self.cursor_home()
        elif c == 'I':
            self.reverse_linefeed()
        elif c == 'J':
            self.erase_to_end_of_page()
        elif c == 'K':
            self.erase_to_end_of_line()
        elif c == 'L':
            self.insert_line()
        elif c == 'M':
            self.delete_line()
        elif c == 'N':
            self.delete_character()
        elif c == 'O':
            self.exit_insert_mode()
        elif c == 'Y':  #H19 starts at line & col 1, curses at line & col 0
            ch = self.sio_read(sio)
            line = (ord(ch) - 31) -1
            ch = self.sio_read(sio)
            col = (ord(ch) - 31) -1
            c = ''
            self.set_cursor_position(line,col)
        elif c == 'Z':
            self.can_perform_as_vt52(sio)
        elif c == 'b':
            self.erase_to_beginning_of_display()
        elif c == 'j':
            self.save_cursor_position()
        elif c == 'k':
            self.goto_saved_cursor_position()
        elif c == 'l':
            self.erase_line()
        elif c == 'n':
            self.cursor_position_report(sio)
        elif c == 'o':
            self.erase_beginning_of_line()
        elif c == 'p':
            self.enter_reverse_video_mode()
        elif c == 'q':
            self.exit_reverse_video_mode()
        elif c == 'r':
            rate = ord(self.sio_read(sio))
            self.modify_baudrate(sio, self.baudrate[rate - 65]) #'A' - 65 = 0
        elif c == 't':
            self.enter_keypad_shifted_mode()
        elif c == 'u':
            self.exit_keypad_shifted_mode()
        elif c == 'v':
            self.wrap_at_end_of_line()
        elif c == 'w':
            self.discard_at_end_of_line()
        elif c == 'x':
            mode = self.sio_read(sio)
            self.set_mode('set', mode)
        elif c == 'y':
            mode = self.sio_read(sio)
            self.set_mode('reset', mode)
        elif c == 'z':
            self.reset_to_powerup_mode()
        elif c == '@':
            self.enter_insert_mode()
        elif c == '#':
            self.transmit_page()
        elif c == '{':
            self.keyboard_enabled()
        elif c == '}':
            self.keyboard_disabled()
        elif c == '[':
                self.enter_hold_screen_mode()
        elif c == ']':
            self.transmit_25th_line()
        elif c == '=':
            self.enter_alternate_keypad_mode()
        elif c == '<':
            self.enter_ansi_mode()
        elif c == '>':
            self.exit_alternate_keypad_mode()
        elif c == '\\':
            self.exit_hold_screen_mode()
        self.screen.refresh()

    def ansi_escape_seq(self, sio):
        ansi_cmds = "ABCDHJKLMNPfhlmnpqrsuz"
        illegal_chars = "<@!$%^&*+-"
        seq = ""

        while True:
            ch = self.sio_read(sio)
            if ch in illegal_chars:
                return
            seq += ch
            if ch in ansi_cmds:  # we're out if it's an ansi code
                break

        # now seq will hold a code such as
        # len(seq) = 2  ESC[C        keypad shifted 6
        # len(seq) = 3  ESC[6n       cursor position report
        # len(seq) = 6  ESC[0;11m    exit reverse video AND exit graphics mode
        # len(seq) = 8  ESC[>1;3;5l  rest - disable 25th line, exit hold screen,cursor on

        c = seq[len(seq) -1]    # get command (last char in seq)
        if len(seq) == 2:
            seq += '1'

        if c == 'A':    # ESC [ Pn A
            self.cursor_up(int(seq[2]))

        elif c == 'B':  # ESC [ Pn B
            self.cursor_down(int(seq[2]))

        elif c == 'C':  # ESC [ Pn C
            self.cursor_forward(int(seq[2]))

        elif c == 'D':  # ESC [ Pn D
            self.cursor_backward(int(seq[2]))
            return

        elif c == 'H':  # ESC [ H or ESC [ Pn;Pn H
            #time.sleep(.5)
            if len(seq) == 2:
                self.cursor_home()
            else:
                idx1 = seq.find('[')
                idx2 = seq.find(';')
                idx3 = seq.find('H')
                line = int(seq[idx1+1:idx2])
                col = int(seq[idx2+1:idx3])
                if line > 0:
                    line -= 1
                if col > 0:
                    col -= 1
                self.set_cursor_position(line,col)

        elif c == 'J':
            if len(seq) == 3:   #valid
                if seq[1] == '0':
                    self.erase_to_end_of_page()
                elif seq[1] == '1':
                    self.erase_to_beginning_of_display()
                elif seq[1] == '2':
                    self.clear_display()

        elif c == 'K':
            if len(seq) == 3:   #valid
                if seq[1] == '0':
                    self.erase_to_end_of_line()
                elif seq[1] == '1':
                    self.erase_beginning_of_line()
                elif seq[1] == '2':
                    self.erase_line()

        elif c == 'L':
            if len(seq) == 3:
                idx1 = string.find(seq, '[')
                idx2 = string.find(seq, 'L')
                lines = string.atoi(seq[idx1+1:idx2])

                while lines > 0:
                    self.insert_line()
                    lines -= 1
                self.carriage_return()
                self.linefeed()

        elif c == 'M':
            if len(seq) == 1:
                self.reverse_linefeed()
            elif len(seq) == 3:
                idx1 = string.find(seq, '[')
                idx2 = string.find(seq, 'M')
                lines = string.atoi(seq[idx1+1:idx2])

                while lines > 0:
                    self.delete_line()
                    lines -= 1

                self.carriage_return()
                self.linefeed()

        elif c == 'P':
            if len(seq) == 3:
                idx1 = string.find(seq, '[')
                idx2 = string.find(seq, 'P')
                chars = string.atoi(seq[idx1+1:idx2])

                while chars > 0:
                    self.delete_character()
                    chars -= 1

        elif c == 'f':  # ESC [ f or ESC [ Pn;Pn f
            if len(seq) == 2:
                self.cursor_home()
            else:
                idx1 = string.find(seq, '[')
                idx2 = string.find(seq, ';')
                idx3 = string.find(seq, 'f')
                line = string.atoi(seq[idx1+1:idx2])
                col = string.atoi(seq[idx2+1:idx3])
                if line > 0:
                    line -= 1
                if col > 0:
                    col -= 1
                self.set_cursor_position(line,col)

        elif c == 'h':
            if seq[1] == '>':   # Set modes
                for i in seq:
                    if i == 'h':
                        break
                    self.set_mode('set', i)

            elif seq[1] == '2':
                self.keyboard_disabled()
            elif seq[1] == '4':
                self.enter_insert_mode()
            elif seq[1] == '?':
                if seq[2] == '7':
                    self.wrap_at_end_of_line()

        elif c == 'l':
            if seq[1] == '>':   # Reset modes
                for i in seq:
                    if i == 'l':
                        break
                    self.set_mode('reset', i)

            elif seq[1] == '2':
                self.keyboard_enabled()
            elif seq[1] == '4':
                self.exit_insert_mode()
            elif seq[1] == '?':
                if seq[2] == '2':
                    self.enter_heath_mode()
                elif seq[2] == '7':
                    self.discard_at_end_of_line()

        elif c == 'm':
            if len(seq) == 2:
                self.exit_reverse_video_mode()
            if len(seq) >= 3:
                if seq[1] == '0':
                    self.exit_reverse_video_mode()
                elif seq[1] == '7':
                    self.enter_reverse_video_mode()
                elif seq[1] == '1' and seq[2] == '0':
                    self.enter_graphics_mode()
                elif seq[1] == '1' and seq[2] == '1':
                    self.exit_graphics_mode()

        elif c == 'n':
            self.cursor_position_report(sio)

        elif c == 'p':
            self.transmit_page()

        elif c == 'q':
            self.transmit_25th_line()

        elif c == 'r':
            rate = 12   # default to 9600
            if len(seq) == 3:  #len(seq) = 3, ex: ESC[8r  2400 baud
                rate = int(seq[1])
            elif len(seq) == 4: # ex: ESC[12r  9600 baud
                rate = int(seq[1:3])
            self.modify_baudrate(sio, self.baudrate[rate - 1])

        elif c == 's':
            self.save_cursor_position()

        elif c == 'u':
            self.goto_saved_cursor_position()

        elif c == 'z':
            self.reset_to_powerup_mode()

    # Configuration
    def reset_to_powerup_mode(self):
        self.reset()

    def set_mode(self, modeType, mode):
        if modeType == 'set':
            set_mode = True
        else:
            set_mode = False

        # disabling the 25th line also clears it.
        if mode == '1':
            if set_mode:
                self.enable25thLine = True
            else:
                self.enable25thLine = False
                self.save_cursor_position()
                self.set_cursor_position(24,0)
                self.clear_display()
                self.goto_saved_cursor_position()

        elif mode == '2':
            self.noKeyClick = set_mode
        elif mode == '3':
            self.holdScreenMode = set_mode
        elif mode == '4':
            self.blockCursor = set_mode
            if set_mode:
                curses.curs_set(CURSOR_BLOCK)
            else:
                curses.curs_set(CURSOR_NORMAL)
        elif mode == '5':
            self.cursorOff = set_mode
            if set_mode:
                curses.curs_set(CURSOR_INVISIBLE)
            else:
                curses.curs_set(CURSOR_NORMAL)
        elif mode == '6':
            self.keypadShiftedMode = set_mode
            if set_mode:
                self.enter_keypad_shifted_mode()
            else:
                self.exit_keypad_shifted_mode()
        elif mode == '7':
            self.alternateKeypadMode = set_mode
            if set_mode:
                self.enter_alternate_keypad_mode()
            else:
                self.exit_alternate_keypad_mode()
        elif mode == '8':
            self.autoLinefeedMode = set_mode
        elif mode == '9':
            self.autoCarriageReturnMode = set_mode


    def enter_ansi_mode(self):
        y,x = self.screen.getyx()
        self.ansiMode = True
        self.status.addstr(1, 45, "ANSI ")
        self.screen.move(y,x)
        self.status.refresh()

    def enter_heath_mode(self):
        y,x = self.screen.getyx()
        self.ansiMode = False
        self.status.addstr(1, 45, "HEATH")
        self.screen.move(y,x)
        self.status.refresh()

	# Modes of operation

    def enter_hold_screen_mode(self):
        pass

    def exit_hold_screen_mode(self):
        pass

    def enter_reverse_video_mode(self):
        self.screen.attron(curses.A_REVERSE)

    def exit_reverse_video_mode(self):
        self.screen.attroff(curses.A_REVERSE)

    def enter_graphics_mode(self):
        self.graphicsMode = True

    def exit_graphics_mode(self):
        self.graphicsMode = False

    def enter_keypad_shifted_mode(self):
        y,x = self.screen.getyx()
        self.keypadShiftedMode = True
        self.status.addstr(1, 40, "S")
        self.screen.move(y,x)
        self.status.refresh()

    def exit_keypad_shifted_mode(self):
        y,x = self.screen.getyx()
        self.keypadShiftedMode = False
        self.status.addstr(1, 40, " ")
        self.screen.move(y,x)
        self.status.refresh()

    def enter_alternate_keypad_mode(self):
        y,x = self.screen.getyx()
        self.keypadAlternateMode = True
        self.status.addstr(1, 42, "A")
        self.screen.move(y,x)
        self.status.refresh()

    def exit_alternate_keypad_mode(self):
        y,x = self.screen.getyx()
        self.keypadAlternateMode = False
        self.status.addstr(1, 42, " ")
        self.screen.move(y,x)
        self.status.refresh()

	# Additional functions

    def keyboard_disabled(self):
        pass
    def keyboard_enabled(self):
        pass

    def wrap_at_end_of_line(self):
        self.wrapAtEndOfLine = True

    def discard_at_end_of_line(self):
        self.wrapAtEndOfLine = False

    def transmit_25th_line(self):
        pass
    def transmit_page(self):
        pass

    def modify_baudrate(self, sio, rate):
        sio.baudrate = rate
        self.status.addstr(1,23, '      ')
        self.status.addstr(1,23, str(sio.baudrate))
        self.status.refresh()

    def set_colour(self, idx):
        global DEFAULT_COLOUR
        if idx == 0:
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        elif idx == 1:
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        elif idx == 2:
            curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        elif idx == 3:
            curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
        elif idx == 4:
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        elif idx == 5:
            curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        elif idx == 6:
            curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)

        DEFAULT_COLOUR = idx
        self.write_h19config()

    def popup_colour(self):
        cl = []
        cl.append('Select White  ')
        cl.append('Select Green  ')
        cl.append('Select Yellow ')
        cl.append('Select Blue   ')
        cl.append('Select Cyan   ')
        cl.append('Select Magenta')
        cl.append('Select Red    ')
        try:
            popup = curses.newwin(12, 32, 8, 20)
            popup.attrset(curses.color_pair(1))
            for i in range(len(cl)):
                popup.addstr(i+2, 9, cl[i],curses.color_pair(i+1))
                popup.addstr(10, 2, "<Enter> to select, 'q' quits")
            popup.border('|','|','-','-','+','+','+','+')
            popup.addstr(0,7,'[Colour Selection]')
            popup.nodelay(0)
            popup.keypad(1)
            curses.curs_set(0)
            popup.refresh()
        except:
            pass

        idx = 0
        popup.addstr(idx+2,9,cl[idx],curses.color_pair(idx+1)|curses.A_REVERSE)

        while True:
            c = popup.getch()

            if c == curses.KEY_DOWN:
                if idx + 1 < len(cl):
                    popup.addstr(idx+2,9,cl[idx],curses.color_pair(idx+1)|curses.A_NORMAL)
                    idx += 1
                    popup.addstr(idx+2,9,cl[idx],curses.color_pair(idx+1)|curses.A_REVERSE)
                    popup.refresh()
            elif c == curses.KEY_UP:
                if idx -1 >= 0:
                    popup.addstr(idx+2,9,cl[idx],curses.color_pair(idx+1)|curses.A_NORMAL)
                    idx -= 1
                    popup.addstr(idx+2,9,cl[idx],curses.color_pair(idx+1)|curses.A_REVERSE)
                    popup.refresh()

            elif curses.keyname(c) == b'^M':
                self.set_colour(idx)
                self.screen.touchwin()
                self.screen.refresh()
                curses.curs_set(1)
                return

            elif chr(c) == 'q':
                self.screen.touchwin()
                self.screen.refresh()
                curses.curs_set(1)
                return


    def popup_error(self, text):
        try:
            popup = curses.newwin(6, 49, 10, 20)
            x = (49 - len(text)) / 2
            popup.addstr(2, x, text)
            popup.addstr(3, 8, "Hit <ENTER> to return...")
            popup.border('|','|','-','-','+','+','+','+')
            popup.nodelay(0)
            curses.curs_set(CURSOR_INVISIBLE)
            popup.refresh()
        except:
            pass
        c = popup.getch()
        curses.curs_set(CURSOR_NORMAL)
        self.screen.touchwin()
        self.screen.refresh()
        return curses.keyname(c)


    def popup_help(self):
        helptext = """
          Commands can be called by CTRL-A <key>
        
    Exit H19 Terminal..............X  |  F1........F1 
    Erase screen...................E  |  F2........F2
    Toggle serial I/O logging......L  |  F3........F3
    Toggle HEATH/ANSI mode.........H  |  F4........F4
    Toggle alternate Keypad........K  |  F5........F5
    Reset terminal.................R  |  BLUE......F6
    View log file..................V  |  RED.......F7
    User manual....................M  |  WHITE.....F8
    Ascii table....................A  |  SHIFT.....F9
    H19 BREAK Key..................B  |  KP_ENTER..F10
    H19 DEL Key....................D  |  ERASE.....F11
    CP/M Quick Help................Q  |  OFFLINE...F12
    Set H19term colours............C  |
    Set Baud Rate..................P  |
                                      
    Press command key or <Enter> to close help.
        """
        try:
            popup = curses.newwin(22, 64, 2, 6)
            popup.addstr(1, 1, helptext)
            popup.border('|','|','-','-','+','+','+','+')
            popup.addstr(0,18, "[ H19term Command Summary ]")
            popup.nodelay(0)
            curses.curs_set(CURSOR_INVISIBLE)
            popup.refresh()
        except:
            pass
        c = popup.getch()
        curses.curs_set(CURSOR_NORMAL)
        self.screen.touchwin()
        self.screen.refresh()
        return chr(c)

    def parse_ctrl_a(self, sio, scr, scn, st):
        c = NOCHAR
        while c == NOCHAR:
            c = scn.getch()
        s = chr(c)
        while True:

            if s == 'x' or s == 'X':    # Exit
                sys.exit(0)

            elif s == '^A':             # Send Ctrl-A through, HDOS debug uses this
                self.sio_write(sio, '\x01')
                break

            elif s == 'a' or s == 'A':  # Show ascii table
                self.show_ascii_file('ascii.txt')
                break

            elif s == 'b' or s == 'B':  # H19 BREAK
                self.break_key(sio)
                break

            elif s == 'c' or s == 'C':  # Set colours
                self.popup_colour()
                break

            elif s == 'd' or s == 'D':  # H19 DEL
                self.delete(sio)
                break

            elif s == 'e' or s == 'E':  # Erase screen
                self.clear_display()
                break

            elif s == 'h' or s == 'H':  # Toggle HEATH/ANSI mode
                if self.ansiMode:
                    self.enter_heath_mode()
                else:
                    self.enter_ansi_mode()
                break

            elif s == 'k' or s == 'K':  # Toggle Alternate Keypad mode
                if self.keypadAlternateMode:
                    self.exit_alternate_keypad_mode()
                else:
                    self.enter_alternate_keypad_mode()
                break

            elif s == 'l' or s == 'L':  # Toggle logging
                y,x = self.screen.getyx()
                if self.logio:
                    self.logio = False
                    st.addstr(1, 71, "LOG: ", curses.A_BOLD)
                    st.addstr(1, 76, "Off")
                    st.refresh()
                else:
                    self.logio = True
                    st.addstr(1, 71, "LOG: ", curses.A_BOLD)
                    st.addstr(1, 76, "On ")
                    st.refresh()
                self.screen.move(y,x)
                self.status.refresh()
                break

            elif s == 'm' or s == 'M':  # Show user manual
                self.show_ascii_file('h19-readme.txt')
                break

            elif s == 'p' or s == 'P':  # Set baud rate
                self.popup_baud_rate(sio)
                break

            elif s == 'q' or s == 'Q':  # Show CP/M quick help
                self.show_ascii_file('cpm-help.txt')
                break

            elif s == 'r' or s == 'R':  # Reset terminal
                self.reset()
                self.clear_display()
                self.screen.addstr(5,3, "Resetting...")
                self.screen.refresh()
                time.sleep(.65)
                self.show_status_line()
                curses.curs_set(CURSOR_INVISIBLE)
                self.show_intro(scn)
                self.firstChar = True
                break
            elif s == 's' or s == 'S':  # Reset terminal
                self.xmodem_send()

            elif s == 'z' or s == 'Z':
                s = self.popup_help()

            else:
                break  # get out on ^M or any non command key

    def popup_filename(self):
#         cl = os.listdir('.')
        try:
            popup = curses.newwin(5, 58, 10, 10)
            popup.attrset(curses.color_pair(0))
            #popup.addstr(0,2, "Current directory is: [ ")
            #popup.addstr(os.getcwd())
            #popup.addstr(" ]")

#
#             for i in range(len(cl)):
#                 popup.addstr(i + 3, 2, cl[i], curses.color_pair(0))
#                 popup.addstr(23, 2, "<Enter> to select, 'q' quits")
            popup.border('|', '|', '-', '-', '+', '+', '+', '+')
            popup.addstr(0, 2, "[ ")
            popup.addstr(os.getcwd())
            popup.addstr(" ]")
            popup.addstr(2, 2, "File: ")
            curses.echo()
            s = popup.getstr().decode(encoding="utf-8")
            file = os.path.join(os.getcwd(), s)
#             popup.addstr(0, 3, '[Baud Rate and Port Selection]')
#             popup.nodelay(0)
#             popup.keypad(1)
#             curses.curs_set(0)
            popup.refresh()
            return file
        except:
            pass
#
#         # get the index to place the cursor
#         idx = 0
#         popup.addstr(idx + 4, 9, cl[idx], curses.color_pair(0) | curses.A_REVERSE)
#
#         while True:
#             c = popup.getch()
#             if c == curses.KEY_DOWN:
#                 if idx == -1:
#                     popup.addstr(idx + 3, 23, str(SERIAL_PORT)[5:], curses.color_pair(0) | curses.A_NORMAL)
#                     idx += 1
#                     popup.addstr(idx + 4, 9, cl[idx], curses.color_pair(0) | curses.A_REVERSE)
#                 elif idx + 1 < len(cl):
#                     popup.addstr(idx + 4, 9, cl[idx], curses.color_pair(0) | curses.A_NORMAL)
#                     idx += 1
#                     popup.addstr(idx + 4, 9, cl[idx], curses.color_pair(0) | curses.A_REVERSE)
#             elif c == curses.KEY_UP:
#                 if idx == 0:
#                     popup.addstr(idx + 4, 9, cl[idx], curses.color_pair(0) | curses.A_NORMAL)
#                     idx -= 1
#                     popup.addstr(idx + 3, 23, str(SERIAL_PORT)[5:], curses.color_pair(0) | curses.A_REVERSE)
#                 elif idx - 1 >= 0:
#                     popup.addstr(idx + 4, 9, cl[idx], curses.color_pair(0) | curses.A_NORMAL)
#                     idx -= 1
#                     popup.addstr(idx + 4, 9, cl[idx], curses.color_pair(0) | curses.A_REVERSE)
#                 popup.refresh()
#
#             elif curses.keyname(c) == b'^M':
#                 if idx == -1:
#                     self.popup_port_select(sio)
#                 else:
#                     pass
# #                    BAUD_RATE = BAUD_RATES[idx]
# #                    sio.baudrate = BAUD_RATE
#                 self.show_status_line()
#                 self.write_h19config()
#                 self.screen.touchwin()
#                 self.screen.refresh()
#                 curses.curs_set(1)
#                 return
#
#             elif chr(c) == 'q':
#                 self.screen.touchwin()
#                 self.screen.refresh()
#                 curses.curs_set(1)
#                 return

    def popup_baud_rate(self, sio):
        global BAUD_RATE, BAUD_RATES
        cl = []
        cl.append('Select   1200')
        cl.append('Select   2400')
        cl.append('Select   4800')
        cl.append('Select   9600')
        cl.append('Select  19200')
        cl.append('Select  38400')
        cl.append('Select  57600')
        try:
            popup = curses.newwin(14, 36, 8, 20)
            popup.attrset(curses.color_pair(0))
            popup.addstr(2,4, "Current port is: [ ")
            popup.addstr(str(SERIAL_PORT)[5:],curses.A_BOLD)
            popup.addstr(" ]")
            for i in range(len(cl)):
                popup.addstr(i + 4, 9, cl[i], curses.color_pair(0))
                popup.addstr(12, 2, "<Enter> to select, 'q' quits")
            popup.border('|', '|', '-', '-', '+', '+', '+', '+')
            popup.addstr(0, 3, '[Baud Rate and Port Selection]')
            popup.nodelay(0)
            popup.keypad(1)
            curses.curs_set(0)
            popup.refresh()
        except:
            pass

        # get the index to place the cursor
        idx = BAUD_RATES.index(BAUD_RATE)
        popup.addstr(idx + 4, 9, cl[idx], curses.color_pair(0) | curses.A_REVERSE)

        while True:
            c = popup.getch()
            if c == curses.KEY_DOWN:
                if idx == -1:
                    popup.addstr(idx + 3, 23, str(SERIAL_PORT)[5:], curses.color_pair(0) | curses.A_NORMAL)
                    idx += 1
                    popup.addstr(idx + 4, 9, cl[idx], curses.color_pair(0) | curses.A_REVERSE)
                elif idx + 1 < len(cl):
                    popup.addstr(idx + 4, 9, cl[idx], curses.color_pair(0) | curses.A_NORMAL)
                    idx += 1
                    popup.addstr(idx + 4, 9, cl[idx], curses.color_pair(0) | curses.A_REVERSE)
            elif c == curses.KEY_UP:
                if idx == 0:
                    popup.addstr(idx + 4, 9, cl[idx], curses.color_pair(0) | curses.A_NORMAL)
                    idx -= 1
                    popup.addstr(idx + 3, 23, str(SERIAL_PORT)[5:], curses.color_pair(0) | curses.A_REVERSE)
                elif idx - 1 >= 0:
                    popup.addstr(idx + 4, 9, cl[idx], curses.color_pair(0) | curses.A_NORMAL)
                    idx -= 1
                    popup.addstr(idx + 4, 9, cl[idx], curses.color_pair(0) | curses.A_REVERSE)
                popup.refresh()

            elif curses.keyname(c) == b'^M':
                if idx == -1:
                    self.popup_port_select(sio)
                else:
                    BAUD_RATE = BAUD_RATES[idx]
                    sio.baudrate = BAUD_RATE
                self.show_status_line()
                self.write_h19config()
                self.screen.touchwin()
                self.screen.refresh()
                curses.curs_set(1)
                return

            elif chr(c) == 'q':
                self.screen.touchwin()
                self.screen.refresh()
                curses.curs_set(1)
                return

    def popup_port_select(self, sio):
        global SERIAL_PORT
        cl = []
        try:
            from serial.tools.list_ports import comports
            for port, desc, hwid in sorted(comports()):
                cl.append(port)
        except:
            pass

        popup = curses.newwin(14, 36, 8, 20)
        popup.attrset(curses.color_pair(0))
        for i in range(len(cl)):
            popup.addstr(i + 4, 9, cl[i], curses.color_pair(0))
            popup.addstr(12, 2, "<Enter> to select, 'q' quits")
        popup.border('|', '|', '-', '-', '+', '+', '+', '+')
        popup.addstr(0, 9, '[Port Selection]')
        popup.nodelay(0)
        popup.keypad(1)
        curses.curs_set(0)
        popup.refresh()

        # get the index to place the cursor
        idx = cl.index(SERIAL_PORT)
        popup.addstr(idx + 4, 9, cl[idx], curses.color_pair(0) | curses.A_REVERSE)

        while True:
            c = popup.getch()
            if c == curses.KEY_DOWN:
                if idx + 1 < len(cl):
                    popup.addstr(idx + 4, 9, cl[idx], curses.color_pair(0) | curses.A_NORMAL)
                    idx += 1
                    popup.addstr(idx + 4, 9, cl[idx], curses.color_pair(0) | curses.A_REVERSE)
            elif c == curses.KEY_UP:
                if idx - 1 >= 0:
                    popup.addstr(idx + 4, 9, cl[idx], curses.color_pair(0) | curses.A_NORMAL)
                    idx -= 1
                    popup.addstr(idx + 4, 9, cl[idx], curses.color_pair(0) | curses.A_REVERSE)
                popup.refresh()

            elif curses.keyname(c) == b'^M':
                SERIAL_PORT = cl[idx]
                sio.port = SERIAL_PORT
                self.show_status_line()
                self.write_h19config()
                self.screen.touchwin()
                self.screen.refresh()
                curses.curs_set(1)
                return

            elif chr(c) == 'q':
                self.screen.touchwin()
                self.screen.refresh()
                curses.curs_set(1)
                return

    def show_ascii_file(self, filename):
        curses.curs_set(CURSOR_INVISIBLE)
        try:
            fd = open(os.path.join(INSTALL_PATH, filename), 'r')
        except:
            self.bell()
            self.popup_error("Can't find file \"%s\"" % filename)

            return
        data = fd.readlines()
        fd.close()
        self.show_help_status()
        self.show_data(data)
        self.show_status_line()
        curses.curs_set(CURSOR_NORMAL)
        # self.cur.box()
        # self.cur.refresh()
        # self.screen.refresh()
        # self.status.refresh()

    def show_data(self,data):
        wy,wx=self.screen.getmaxyx()

        if type(data) == str:
            data = data.split('\n')

        pady = max(len(data)+1,wy)
        padx = wx

        max_x = wx
        max_y = pady-wy

        pad = curses.newpad(pady,padx)

        for i,line in enumerate(data):
            pad.addstr(i,0,str(line))

        x=0
        y=0

        inkey=0
        self.screen.nodelay(0)
        while inkey != 'q':
            pad.refresh(y,x,1,1,wy-1,wx)
            inkey = self.screen.getkey()

            if inkey=='KEY_UP':y=max(y-1,0)
            elif inkey=='KEY_DOWN':y=min(y+1,max_y)
            elif inkey=='KEY_LEFT':x=max(x-1,0)
            elif inkey=='KEY_RIGHT':x=min(x+1,max_x)
            elif inkey=='KEY_NPAGE':y=min(y+wy,max_y)
            elif inkey=='KEY_PPAGE':y=max(y-wy,0)
            elif inkey=='KEY_HOME':y=0
            elif inkey=='KEY_END':y=max_y

        curses.flushinp()
        pad.clear()
        self.screen.nodelay(1)
        self.screen.touchwin()
        self.screen.refresh()


    def getmax(self,lines):
        return max([len(str(l)) for l in lines])

    def show_intro(self, scn):
        helptext = """
          Welcome to:

           _   _  _   ___   _          
          | | | |/ | / _ \ | |_  ___  _ __  _ __ ___  
          | |_| || || (_) || __|/ _ \| '__|| '_ ` _ \ 
          |  _  || | \__, || |_|  __/| |   | | | | | |
          |_| |_||_|   /_/  \__|\___||_|   |_| |_| |_|     """



        self.clear_display()
        scn.addstr(2, 2, helptext)
        scn.addstr(12,27, VERSION)
        scn.addstr(13,27, VERSION_DATE)
        scn.addstr(14,27,"By George Farris - farrisg@gmsys.com")
        scn.addstr(18,10, "A Heathkit H19 Terminal emulator for Linux...")
        scn.addstr(20,10, "Press CTRL-A Z for help on special keys...")
        scn.refresh()


    def show_help_status(self):
        self.status.hline(0, 0, curses.ACS_HLINE, 79)
        self.status.move(1,0)
        self.status.clrtoeol()
        self.status.addstr(1, 0, "Usable keys: ", curses.A_BOLD)
        self.status.addstr(1, 13, "UP - DOWN - PAGE-UP - PAGE-DOWN - HOME - END - 'q' to quit")
        self.status.refresh()


    def show_status_line(self):
        global BAUD_RATE
        y,x = self.screen.getyx()   # save cursor
        self.status.hline(0, 0, curses.ACS_HLINE, 80)
        self.status.hline(2, 0, curses.ACS_HLINE, 80)
        self.status.move(1,0)
        self.status.clrtoeol()
        self.status.addstr(1, 0, "Port:", curses.A_BOLD)
        if self.offline:
            self.status.addstr(1, 6, "Offline      ")
        else:
            self.status.addstr(1, 6, SERIAL_PORT)
        self.status.addstr(1, 20, "|")
        self.status.addstr(" B", curses.A_BOLD)
        self.status.addstr(1,23, str(BAUD_RATE))
        self.status.addstr(1, 29, "|")
        self.status.addstr(" Keypad: [",curses.A_BOLD)
        self.status.addstr(1, 40, "    ")
        self.status.addstr(1, 41, "-")
        self.status.addstr(" ]",curses.A_BOLD)
        self.status.addstr(1, 45, "HEATH")
        self.status.addstr(1, 52, "|")
        self.status.addstr(" Ctrl-A Z: ",curses.A_BOLD)
        self.status.addstr("HELP")
        self.status.addstr(1, 69, "| ")
        self.status.addstr("LOG: ", curses.A_BOLD)
        self.status.addstr(1, 76, "off")

        # F keys
        self.status.addstr(3, 0, "F1-F5 = F1-F5")
        self.status.addstr(3, 13, " | ")
        self.status.addstr("BLUE", curses.color_pair(4) | curses.A_BOLD)
        self.status.addstr(" = F6")
        self.status.addstr(3, 25, " | ")
        self.status.addstr("RED",curses.color_pair(7) | curses.A_BOLD)
        self.status.addstr(" = F7")
        self.status.addstr(3, 36, " | ")
        self.status.addstr("WHITE",curses.A_BOLD)
        self.status.addstr(" = F8")
        self.status.addstr(3, 49, " | ")
        self.status.addstr("SHIFT = F9")
        self.status.addstr(3, 62, " | ")
        self.status.addstr("KP_ENTER = F10")

        self.screen.move(y,x)   # restore cursor
        self.status.refresh()


# Historically curses won't write to the last line and column if
# scrolling isn't allowed. The only way to get a char in the last
# position is to add it before and then insert the previous char which
# we saved with inch()
    def addchar(self, ch, sio):
        cn = ord(ch)
        y, x = self.screen.getyx()
        if self.graphicsMode and cn >=94 and cn <= 126:
            if self.wrapAtEndOfLine:
                if x == 79:
                    self.screen.insstr(self.h19_graphics[cn - 94])
                    self.screen.move(y+1, 0)
                else:
                    self.screen.addstr(self.h19_graphics[cn - 94])
            else:
                if x == 79:
                    self.screen.insstr(self.h19_graphics[cn - 94])
                else:
                   if self.insertMode:
                       self.screen.insstr(self.h19_graphics[cn - 94])
                   else:
                       self.screen.addstr(self.h19_graphics[cn - 94])
        else:
            if self.wrapAtEndOfLine:
                if x == 79:
                    self.screen.insstr(ch)
                    self.screen.move(y+1, 0)
                else:
                    self.screen.addch(ch)
            else:   # discard at end of line
                if x == 79:
                    self.screen.insstr(ch)
                else:
                    if self.insertMode:
                        self.screen.insch(ch)
                    else:
                        self.screen.addch(ch)

    def check_command_history(self, ch):
        history = ['','era a:help.txt', 'dir', 'pip a:g.com=c:h.com', 'ren help.txt=doit.txt']
        y,x = self.screen.getyx()
        self.screen.move(y,x)
        self.screen.clrtoeol()

        if ch == curses.KEY_SR:
            self.idx += 1
            self.screen.move(y,x-self.mycp)
            self.screen.clrtoeol()
            self.screen.addstr("%s" % (history[self.idx]))
            self.mycp = len(history[self.idx])
        elif ch == curses.KEY_SF:
            self.idx -= 1
            self.screen.move(y,x-self.mycp)
            self.screen.clrtoeol()
            self.screen.addstr("%s" % (history[self.idx]))
            self.mycp = len(history[self.idx])

    def process_key(self, c, sio, scr, scn, st):
        if c in self.fnkeys:
            if c == OFFLINE_FKEY:
                if self.offline:
                    self.offline = False
                    self.show_status_line()
                else:
                    self.offline = True
                    self.show_status_line()
            elif c == ERASE_FKEY:
                self.erase_to_end_of_page()
            elif c == SHIFT_FKEY:
                if self.keypadShiftedMode:
                    self.exit_keypad_shifted_mode()
                else:
                    self.enter_keypad_shifted_mode()
            else:
                self.sio_write(sio, ESC)
                if self.ansiMode:
                    self.sio_write(sio, 'O')
                self.sio_write(sio, self.fnkeys[c])
            return

        elif c in self.numkeys:
            if self.keypadShiftedMode:
                if self.ansiMode:
                    self.sio_write(sio, self.numkeys[c][ASHIFT])
                else:
                    self.sio_write(sio, self.numkeys[c][SHIFT])
                return
            elif self.keypadAlternateMode and not self.keypadShiftedMode:
                if self.ansiMode:
                    self.sio_write(sio, self.numkeys[c][A_ALT])
                else:
                    self.sio_write(sio, self.numkeys[c][H_ALT])
                return

            # elif self.commandHistory:
            #     self.check_command_history(c)
            else:
                self.sio_write(sio, self.numkeys[c][NORM])

        elif c == self.BACKSPACE:
            bsc = self.backspace(sio, KEY)  # PIE editor will send ESC
            if bsc == ESC:                  # seq after BS
                self.process_escape_seq(sio)

        elif curses.keyname(c) == '^\\':  # History key
            pass
            #self.commandHistory = True

        elif curses.keyname(c) == b'^A':  # Command Key
            self.parse_ctrl_a(sio, scr, scn, st)

        else:
            if c <= 255:
                self.sio_write(sio, chr(c))
            else:
                self.bell()
#                self.popup_error("For SHIFT ARROW keys, press F9, see help.")

    def xmodem_send(self):
        SOH = b'\x01'
        EOT = b'\x04'
        ACK = b'\x06'
        NAK = b'\x15'

        ser = serial.Serial('/dev/ttyS2', timeout=0)  # or whatever port you need
        ser.baudrate = 19200
        ser.xonoff = False
        ser.rtscts = False
        ser.dsrdtr = False

        filename = self.popup_filename()
        file = open(filename, 'rb')

        t, anim = 0, '|/-\\'

        ser.timeout = 1
        while 1:
            c = ser.read(1)
            if c != NAK:
                t = t + 1
                sys.stdout.write(anim[t % len(anim)])
                sys.stdout.write('\r')
                if t == 60:
                    return
            else:
                break

        #print("Got NAK...")

        p = 1
        s = file.read(128)

        while s:
            if len(s) < 128:
                s = s.ljust(128, b'\x1a')
            chk = 0
            for c in s:
                chk += c
            while 1:
                ser.write(SOH)  # send SOH
                ser.write(bytes([p]))  # send packet number
                ser.write(bytes([0xFF - p]))  # send invert of packet number
                ser.write(s)
                ser.write(bytes([chk % 256]))  # send checksum
                ser.flush()
                answer = ser.read(1)
                if answer == NAK:
                    continue
                if answer == ACK:
                    break
                return
            s = file.read(128)
            p = (p + 1) % 256

            print('.', end='')

        ser.write(EOT)
        return True

    def main(self, scr, term, sio):

        scn, st = term.setup_screen()
        term.reset()

        # Create a sine wave, with a pitch of 25, for use with the H19 BELL.
        self.sinewave = SineWave(pitch=25)
        self.bell_start_time = 0.0

        # if curses.termname() == 'linux':
        self.BACKSPACE = curses.KEY_BACKSPACE
        #else:
        #    self.BACKSPACE = 127  # xterms do this

        self.offline = False

        date_string = ''
        first_char = True
        today = datetime.datetime.today()

        self.show_status_line()
        curses.curs_set(CURSOR_INVISIBLE)
        self.show_intro(scn)
        curses.curs_set(CURSOR_NORMAL)

        # command history is a work in process do not enable
        self.commandHistory = False
        self.idx = 0  # command history index
        self.mycp = 0 # initial command length

        lasttime = time.time()
        lastchar = ''
        charcount = 0  # char count before repeat rate kicks in

        # Loop here getting keys doing serial I/O
        loop_time = 0.0

        while True:
            c = NOCHAR

            # reset bell after a second, don't ask it will be fixed.
            if time.time() - self.bell_start_time > 1.0:
                self.bell_start_time = 0.0
            # Make sure keys don't repeat too fast.
            nowtime = time.time()
            c = scn.getch()
            if c != NOCHAR:
                if c == lastchar:
                    charcount += 1
                else:
                    charcount = 0

                if (nowtime - lasttime) < KEY_REPEAT_RATE and charcount > 20:
                    lastchar = c
                    c = NOCHAR
                else:
                    lastchar = c
                    lasttime = nowtime

            if c != NOCHAR:
                loop_time = 0.0

                if first_char:
                    term.clear_display(reset=True)
                    first_char = False
                    curses.curs_set(CURSOR_NORMAL)

                self.process_key(c, sio, scr, scn, st)

            sc = ''
            sc = term.sio_read(sio, TIMEOUT=SIO_NO_WAIT)
            if len(sc) >= 1:
                loop_time = 0.0
                if first_char:
                    term.clear_display(reset=True)
                    first_char = False

                # Don't bother with this after a couple of screens, resets with CTRL-A R
                if self.linesSinceBoot < 50:
                    if sc == LF:
                        date_string = ''
                        self.linesSinceBoot += 1
                    else:
                        date_string += sc

                    if AUTO_CPM_DATE:
                        if date_string == CPM_DATE_FORMAT:
                            ds = today.strftime('%m/%d/%y\n')
                            term.sio_write(sio, ds)
                        elif date_string == CPM_TIME_FORMAT:
                            ts = today.strftime('%I/%M/%S\n')
                            term.sio_write(sio, ts)

                    if AUTO_HDOS_DATE:
                        if re.search(HDOS_DATE_FORMAT, date_string):
                            ds = today.strftime('%d-%b-%y\n')
                            term.sio_write(sio, ds)

                if 31 < ord(sc) < 127:  # not a control char just print it
                    term.addchar(sc, sio)
                elif sc == TAB:
                    term.addchar(sc,sio)
                elif sc == CR:
                    term.carriage_return()
                elif sc == LF:
                    term.linefeed()
                elif sc == ESC:
                    term.process_escape_seq(sio)
                    sc=""
                elif sc == BS:
                    term.backspace(sio, sc)
                elif sc == NUL:
                    pass
                elif sc == BEL:
                    term.bell()
                elif sc == DEL:
                    term.rubout()

            if loop_time <= 0.1:
                loop_time += 0.000001
            else:
                time.sleep(loop_time)


if __name__ == "__main__":
    term = H19Term()
    term.get_h19config()
    sio = term.open_port()
    curses.wrapper(term.main, term, sio)

