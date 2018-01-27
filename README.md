# Send messages to Telegram using Linux terminal.

## What has been done compare to the source?
1. Removed redundant functionality.
2. Rewritten package output.
3. Rewritten help output.

**Tested only on Xubuntu 17.10.**

**Note: setup.py, python.py, termigram.sh must be in the same directory.**

### Installation:

```shell
sudo apt install python
sudo -H pip install python-telegram-bot
sudo -H pip install appdirs
sudo python setup.py install
termigram --configure
```

*Or simply: `chmod +x termigram.sh; sudo ./termigram.sh -i`*

### Uninstallation:

```shell
termigram -c
sudo -H pip uninstall termigram
sudo rm -f /usr/local/bin/termigram
sudo -H pip uninstall python-telegram-bot
sudo -H pip uninstall appdirs
sudo apt autoremove
```

*Or simply: `chmod +x termigram.sh; sudo ./termigram.sh -u`*

### Usage:

**1.** To send text message: `termigram <some_text>`

For instance: `termigram "Find out how to configure this network interface ASAP!"`

There is a maximum message length of 4096 characters, larger messages will be automatically split up into smaller ones and sent separately.

**2.** To configure Termigram to specific channel: `termigram --configure`

**3.** To send text from stdin: `termigram -s, --stdin`

For instance: `lsblk | termigram -s`

**4.** To send monospace text: termigram -m, --monospace

For instance: `termigram -m "Please see this log."`

**5.** To send a file: `termigram -f, --file`

Maximum file size - 50 MB (Telegram Bot API limitation).

For instance: `termigram -f /home/dmitry/kern.log`

**6.** To set the read timeout for network operations (in seconds): `termigram -t <some_time>`

For instance: `termigram -t 3`

**7.** To clean Termigram configuration file: `termigram -c, --clean`

**8.** To show program's version number and exit: `termigram -v, --version`

To send the log file (example): 

```shell
chmod +x configuration.sh
sudo ./configuration.sh > configuration.log
termigram -f configuration.log
```
