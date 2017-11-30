# MeloettaBot


A multi-functional Discord Bot. A rewrite of LurantisBot written in Python.


Invite link: `https://discordapp.com/oauth2/authorize?client_id=378721481250570240&scope=bot&permissions=2146958591`


## Requirements
* `Python 3.6`
* `A code editor. E.g. Atom.`
* `discord.py`
* `PyDictionary`
* `googletrans`
* `youtube-dl`
* `pokebase`
* `opus`
* `ffmpeg`

# Installation

1. Download this repository by clicking the green download button on the top right and choose the .ZIP option. Open the .ZIP file and drag the extracted folder to your Desktop.
2. Go to the [python dowloads page](https://www.python.org/downloads/) and install the latest version of Python 3. **DON'T INSTALL PYTHON 2.** Once the installation is complete, open your Applications folder (on your dock); open the Python 3.6 folder, then click the "Install Ce...ommand". Wait for it to complete.
3. Open the Command Line, (Terminal) on your laptop, and copy+paste the following code:
```
cd ~/Desktop/Meloetta-public/
pip3 install -r requirements.txt
```
4. Once the requirements have finished installing, open your code editor and open `config.ini` in the config folder **inside the editor**.
5. Go to https://discordapp.com/developers/applications/me and create a bot application or open an existing one. **MAKE SURE YOU HAVE CREATED A BOT USER**. Add all the data as instructed into config.ini. **The most important being the bot's token, which is found by scrolling down on your application page after creating a Bot User Account.**
6. Then run this in Terminal,
```
cd ~/Desktop/Meloetta-public/
python3 bot.py
```
7. When the bot prints its details out on the console, it means it's online and working!

## Music Module

Here are the steps to install the Music Module for Meloetta. (Please follow the procedure above before following this one).

1. Go to https://developer.apple.com/account/. Sign in with your Apple ID or create a new one.
2. Go to Downloads, (or Download Tools), scroll down, and click, 'See more downloads'.
3. Search 'command line' in the search bar; then, find the Command Line tool that fits your macOS version. (You can check your version by clicking the Apple logo at the top of your screen, 'About this Mac', then click 'Overview'.
4. Download the command line tool that fits your macOS, open it, then install it.
5. Open Terminal and run the following command into it:
```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```
Wait for the program to finish installing.
6. Then, run the following commands in Terminal ONE AT a time,
```
brew install ffmpeg
brew install opus
```
`Note: You probably won't have to use brew install opus since I've already included the Mac Opus library in the bin folder. However, install it just in case.`
7. After all the steps, you can run the bot again by running in Terminal,
```
cd ~/Desktop/Meloetta-public/
python3 bot.py
```

***

LICENSE: Apache-2.0





