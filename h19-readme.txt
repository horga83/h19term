
  _   _  _   ___   _
 | | | |/ | / _ \ | |_  ___  _ __  _ __ ___
 | |_| || || (_) || __|/ _ \| '__|| '_ ` _ \
 |  _  || | \__, || |_|  __/| |   | | | | | |
 |_| |_||_|   /_/  \__|\___||_|   |_| |_| |_|


 
 H19 TERMINAL EMULATOR
 
 Copyright (c) 2014 George Farris - farrisga@gmail.com
 Licensed under version 3 of the GNU General Public License.
 
 
 TABLE OF CONTENTS
 ---------------------------------------------------------------------------
 
 FEATURES
 USAGE
     Function Keys
     Control Keys
     Serial Port Logging
     Auto Date Function
 COLOUR SUPPORT
     Setting terminal colour
     Customizing colours
     X11 GUI applications
     Linux console
 XMODEM SUPPORT
     Using Xmodem send
     H8/H89 and RX.COM
     .h19termrc configuration
 RASPBERRY PI
     Serial Port
 OTHER INFO

 
 
 FEATURES
 ---------------------------------------------------------------------------
 H19term aims to provide close to 100 percent software emulation of the
 Heathkit H19, also known as Zenith Z19, hardware video terminal. 

 It currently has the following features:
 
 Software bell - User configurable sound
 Heath mode
 Ansi mode
 Supports 25th line.
 Support all graphics characters.
 Custom font files for the Linux console, includes Raspberry Pi
 Custom font for X11 based terminals such as gnome-terminal
 Serial Port logging.
 Selectable serial ports and baud rates
 Help files available for ascii characters, CP/M quick help and user manual.
 Easily configurable in .h19termrc file
 Colour changing mode for Amber and Green or other colours.
 Xmodem send.
 RX.COM - H8/H89 companion Xmodem application
 Help files directly inside h19term.
  Ascii table
  User Manual
  CP/M quick help.
   
 Runs on the Linux console or in most X11 terminal emulators such as
 gnome-terminal, XFCE4-terminal and Konsole.  
 
 Future features planned:

 Add log file viewer.
 Add nmemonics to help.
 Add HDOS quick help
 Add memory and I/O maps
 Maybe some Super 19 features if anyone desires them.
 Embed Z80 emulator.
  
 
 USAGE
 ---------------------------------------------------------------------------
 Once H19term is installed and running there are a couple of things you 
 should be aware of.  Keymappings are as follows:
  
 Function Keys
 ------------- 
 F1-F5     Same as PC keyboard
 BLUE      F6 key on PC
 RED       F7
 WHITE     F8
 SHIFT     F9    Emulate holding SHIFT for Keypad key
 ENTER     F10   This is the Keypad ENTER key
 ERASE     F11   
 OFFLINE   F12
  
 F9 - Is a special key to emulate the SHIFT-ARROW function on the H19.

 At certain times one is required to press the SHIFT key on the H19 to 
 access the arrow and other functions on the H19 keypad.  This must be 
 emulated by toggling the keypad with the F9 key.  
 
 F10 - is equivilant to the H19 Keypad ENTER key.
 
 The PC keyboad Keypad ENTER key is not consistant so we can't use it. 
 I will look at a way to remap this key on the fly but for now please 
 use F10.
 
 F11 - ERASE key on the H19
 
 To use this you must either be on the Linux console or remap the 
 F11 key in your terminal preferences otherwise you will likely just end
 up with your terminal in fullscreen mode.
 
  
 Control Keys
 ------------
 Ctrl-A A   Show ascii table
 Ctrl-A B   Send BREAK
 Ctrl-A C   Set the display colour
 Ctrl-A D   Send DEL key
 Ctrl-A E   Erase screen (H19 SHIFT-ERASE)
 Ctrl-A H   Toggle between Heath and Ansi Mode
 Ctrl-A K   Toggle the Keypad between normal and alternate mode
 Ctrl-A L   Toggle logging of serial data to h19term.log
 Ctrl-A M   Show this user manual
 Ctrl-A Q   CP/M Quick Help
 Ctrl-A P   Select serial port and baud rate
 Ctrl-A R   Reset the terminal to power up mode
 Ctrl-A S   Send file via Xmodem
 Ctrl-A X   Exit h19term
 Ctrl-A Z   Help screen
 Ctrl-A Ctrl-A   Send a CTRL-A through to application.
  

 Serial Port Logging
 -------------------
 When serial data logging is turned on it will show in the bottom right of 
 the status line.  Data is logged to a file with the name "h19term.log".  
 Outgoing bytes are enclosed in a "{{}}" pairs to seperate them from incoming 
 bytes.  The file is opened in append mode so you can turn it on and off 
 as you desire without loosing previous information.
 
 I also have included an h19-keys.odt Open Document file that you can edit 
 with LibreOffice and print a layout of your keyboard.
 

 Auto Date Function
 ------------------
 When CP/M with clock patches or HDOS boots they will request the date and
 in the case of CP/M time.  If you enable this function under editable
 options when installing, H19term will watch for incoming characters and 
 automatically insert todays date and time.
 
 
 COLOUR SUPPORT
 ---------------------------------------------------------------------------
 H19term has support for changing the colour of the characters, for those of 
 us that remember the days of amber and green screens.  Colour support is
 limited to 7 colours: white, green, yellow/amber, blue, cyan, magenta and 
 red.
 
 Colour is configured differently depending on whether you are running 
 H19term under X11 or directly on the Linux console.
 
 Setting terminal colour
 ----------------------
 Setting the display colour is as simple as hitting CTRL-A C, selecting the
 colour with the cursor keys and hitting <Enter>.
 
 Customizing colours
 -------------------
 Setting custom colours is different depending on whether you are running on
 the Linux console or under an X11 application.
 

 X11 GUI applications
 --------------------
 For X11 applications you must adjust the palette in your terminal 
 application. Here is an example using gnome-terminal:
 
 Open the preferences for your profile in gnome-terminal by selecting:
 Edit->Profile Preferences->Colours.

 Make sure "Use colors from system theme" is unchecked.
 Choose "White on Black" for the "Built-in scheme".
 Under "Palette" and "Built-in Schemes", choose "Custom".
 
 Under the "Palette" section you can modify the top row of colours and 
 change the hue and saturation for the select colour.  Once you are 
 finished, run H19term and press CTRL-A C and select the desired colour.

 I find a yellow text #C4A000 with #2E3436 background is nice.
 
 Linux console
 -------------
 Changing colours on the Linux console is of course different.  In the 
 H19term configuration file, .h19termrc, you will find a section that lists
 the colours.  
 
 Each colour is a standard 6 digit hexidecimal number that represents
 Red, Green and Blue colours.  These numbers range from 0 to FF.  You can 
 easily check colour settings and hex values at www.color-hex.com.  Once you
 have colours you want to try, edit your .h19termrc file and change the 
 default values that are set.  Here are the defaults in case you want to 
 reset them at some point:
 
 white = FFFFFF
 green = 00AA00
 yellow = FFA400
 blue = 0000AA
 cyan = 00AAAA
 magenta = AA00AA
 red = AA0000

 Once you have set your colours you can use CTRL-A C to set them.


 XMODEM SUPPORT
 ---------------------------------------------------------------------------
 As of version 2.4 of H19term, XMODEM send support has been included.

 Along with XMODEM support I have included a CP/M companion application 
 called RX.COM, which you can put on your H8 or H89.  RX.COM is an XMODEM
 receive command, but is not actually necessary, you can use ZMP or MAPLE
 if you like.  I get faster transfer speeds with RX.COM, 9600baud at 2MHz
 and 19200 at 4MHz.

 You must use RX.COM for the AUTORUN feature decribed below.

 AUTORUN
 -------
 AUTORUN is a feature that will automatically enter the RX command on the 
 H8 or H89 so you don't need to start it running first.  Sending a file 
 is as simple as hitting Ctrl-A S without worrying about running a receive
 program on the H8 first.

 How it works
 ------------
 - Hit Ctrl-A S  -  A popup for selecting file will appear.
 - Select your file and hit CR.
 - A popup (depending on setting in your ~/.h19termrc) will appear, allowing
   you to hit CR, A or Q to abort.
 - CR  Starts the transfer but you MUST have started a receive program on 
       your H8 first. (RX, ZMP, MAPLE etc).
   A   Will start the transfer but automatically starts RX on the H8.
   Q   Will abort the transfer.
   
 Defaults can be set in ~/.h19termrc see the section below.

 NOTE:  In AUTORUN mode if the file you are sending already exists on the H8,
        RX will automatically rename the file to <filename.RX>
 
 .h19termrc configuration
 ------------------------
 In your .h19termrc file you can set one of 3 modes to deal with XMODEM 
 transfers, USER, AUTO or ANY.  The entry in the .h19termrc file is as 
 follows, USER is the default:

 [AutoRun]
 autorunmode = USER

 USER  - This setting will popup a dialog asking you to hit CR, A or Q
         which is described above.
 AUTO  - This setting will immediately run "RX -n <filename" on the H8
         and start the transfer immediately after entering the filename.
 ANY   - This is similar to USER but will not give you the "A" option.

 If you use ZMP or Maple or some other program on the H8 for XMODEM 
 transfers, you should set "autorunmode=ANY".


 INSTALLATION
 ---------------------------------------------------------------------------
 H19term is written in Python and currently uses version 3.6 or greater.  
 I have found this to be installed on all Linux distributions to date so you 
 shouldn't have to install it. 
 
 Please consult the INSTALLATION.txt file that comes with H19term.   
 

 Setup Terminal
 --------------------
 YOU MUST setup an H8 profile for your terminal.  I use Gnome-Terminal but 
 you may use Mate-Terminal, KDE Konsole or XFCE Terminal.  XFCE4-Terminal
 doesn't allow profiles, too bad.

 Go to the Preferences in your terminal of choice and add an "H8" profile.

 Set these things in your profile or terminal:
   Size:      - Must be 82x31 at least, larger looks odd but it will work.
   Font:      - Set the font to Heathkit-H19-bitmap or Heathkit-H19.
   Backspace: - Set Backspace to generate Control-H
   Delete:    - Set Delete key to generate ASCII DEL
 
 Run the program from a terminal by typing:
 
 $ h19term<enter>
 
 You should be able to find H19term in your desktop menus or search 
 for it by hitting the "Super" or "Windows" key and typing h19.
 
 
 Configuration
 -------------
 
 A sample .h19termrc file in your home directory looks like so:
 
 ------------------------ .h19termrc---------------------------
 [General]
 soundfile = beep1.wav
 
 [SerialComms]
 port = /dev/ttyS1
 baudrate = 9600
 xmodemport = /dev/ttyS2
 xmodembaudrate = 19200

 [AutoRun]
 autorunmode = USER

 [Fonts]
 preload = False
 font = H19term16x32.psfu.gz

 [Colours]
 # custom colours used only for linux console, see manual
 white = FFFFFF
 green = 00AA00
 yellow = FFA400
 blue = 0000AA
 cyan = 00AAAA
 magenta = AA00AA
 red = AA0000
 # default colour of h19term on console or xterm, see manual
 defaultcolour = 2

 [Date]
 autocpmdate = False
 cpmdate = Enter today's date (MM/DD/YY): 
 cpmtime = Enter the time (HH:MM:SS): 
 autohdosdate = False
 hdosdate = ^Date.(\d\d-\w\w\w-\d\d)?.

 ------------------------ end of file---------------------------
 
 soundfile    - The sound file for the terminal beep
 
 port         - The serial port to use
 baudrate     - Speed of the serial link
 xmodemport   - The serial port for xmodem transfers
 xmodembaudrate - The baud rate for xmodem

 autorunmode  - Transfer mode for xmodem 

 preload      - Whether h19term will attempt to preload the font file
 font         - The font file to preload for the Linux console.
 
 
 [Date] section explained below:
 
 You can also enable auto date and time insertion when booting CP/M or HDOS
 Each date/time setting program will display a prompt for setting the date 
 or time.  You must set the format strings to match the prompt.
 
 With "ZSDOS Time Stamp Loader" for CP/M you should be able to use the 
 defaults, just set "autocpmdate" to True.
 
 Basically H19term will look for the string held in cpmdate and cpmtime in 
 the first 50 lines of a fresh boot.  If it finds a match a date and time 
 string is sent.
 
 HDOS is slightly more complex as it will spit out the last date that it 
 stored so we must search for that string using a regex expression.  
 
 r"^Date.(\d\d-\w\w\w-\d\d)?." is described as follows:
 
    r      - means do not interpret escape or other characters such as ?
    ^Date  - means the word "Date" must be at the beginning of the line.
    \d     - means match any character that is a digit (0-9).
    \w     - means match any alphabetic character (a-z and A-Z).
    .      - means match any character.
 
 
 ************************************************************************ 
  
 You must have a terminal that is at least 82x31 in size.  In Gnome-terminal
 you can preset this in the profile preferences or just resize it manually.
  
 
 RASPBERRY PI
 ---------------------------------------------------------------------------
 The Raspberry Pi board running under Raspbian sets the terminal to 60x160,
 60 lines by 160 columns.  While this is fine it is better to have the 
 terminal run with a larger font so it fills the screen.  We do this by 
 re-configuring the console.

 Login and run the following:
   "sudo setfont H19term16x32.psfu.gz"
 You can load it before you run H19term by issuing the setfont command:  
 
 You can set H19term to preload the font automatically if you set it in the
 .h19termrc configuration file.  You will need to load it with 
 "sudo setfont H19term16x32.psfu.gz" at least once before trying auto load.
 
 This font file has all the correct H19 graphics characters which are not
 part of the normal Terminus font.
 
 Now restart your Pi board:  "sudo shutdown -r now"
 

 SERIAL PORT
 -----------
 You will require a USB or other serial port.
 
 You must be a member of the proper group to read and write to a serial 
 Port under Linux.  Debian/Ubuntu/Mint use the DIALOUT group and 
 Arch/Manjaro uses the UUCP group.

 The install.sh script should have added you to the DIALOUT group or 
 UUCP group depending on whether you run Debian/Ubuntu/Mint based 
 Linux or Arch/Manjaro Linux.  You may have to REBOOT for this to take 
 effect.

 You will, at the very least, have to logout and login again.
 If you run the "groups" command and DO NOT see your group, then
 you will have to reboot.

 
 In order for the speaker to beep you will need to plug one into the Pi
 audio jack.
 
 
 OTHER INFO
 ---------------------------------------------------------------------------
 If you have questions, bug reports, patches or feature requests please 
 email me at farrisg@gmsys.com
 
 If you would like to buy me a coffee, beer or just say hello, I live on 
 Vancouver Island, British Columbia, Canada and am always available:-)  
 Please come and visit.
 
 
 
 
 
