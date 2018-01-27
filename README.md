Send messages to Telegram using Linux terminal.

What has been done compare to telegram-send?
1. Removed redundant functionality.
2. Rewritten package output.
3. Rewritten help output.

Tested only on Xubuntu 17.10.
Note: setup.py, python.py, termigram.sh must be in the same directory.

Installation:
sudo apt install python
sudo -H pip install python-telegram-bot
sudo -H pip install appdirs
sudo python setup.py install
termigram --configure

Or simply:
chmod +x termigram.sh; sudo ./termigram.sh -i

Uninstallation:
termigram -c
sudo -H pip uninstall termigram
sudo rm -f /usr/local/bin/termigram
sudo -H pip uninstall python-telegram-bot
sudo -H pip uninstall appdirs
sudo apt autoremove

Or simply:
chmod +x termigram.sh; sudo ./termigram.sh -u

Usage:
To send text message: termigram <some_text>

For instance: termigram "Find out how to configure this network interface ASAP!"
There is a maximum message length of 4096 characters, larger messages will be automatically split up into smaller ones and sent separately.
To configure Termigram to specific channel: termigram --configure
To send text from stdin: termigram -s, --stdin
For instance: lsblk | termigram -s
To send monospace text: termigram -m, --monospace
For instance: termigram -m "Please see this log."
To send a file: termigram -f, --file
Maximum file size - 50 MB (Telegram Bot API limitation).
For instance: termigram -f /home/dmitry/kern.log
To set the read timeout for network operations (in seconds): termigram -t <some_time>
For instance: termigram -t 3
To clean Termigram configuration file: termigram -c, --clean
To show program's version number and exit: termigram -v, --version

To send the log file: chmod +x configuration.sh; sudo ./configuration.sh > configuration.log; termigram -f configuration.log
