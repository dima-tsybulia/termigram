#! /usr/bin/python
# Rewritten by Dmitry Tsybulia (fork of telegram-send):
# --> removed redundant functionality;
# --> rewritten package output;
# --> rewritten help output.
# For personal use only
# v.0.2.85 - 01/22/2018

from os.path import dirname, exists, expanduser, join
from telegram.constants import MAX_MESSAGE_LENGTH
from os import makedirs, remove
from appdirs import AppDirs
import telegram
import argparse
import sys
import re

if sys.version_info >= (3, ):
    import configparser
else:
    import ConfigParser as configparser
    input = raw_input

def main():

    class delete_usage(argparse.HelpFormatter):
    	def add_usage(self, usage, actions, groups, prefix=None):
    		return super(delete_usage, self)

    parser = argparse.ArgumentParser(
	    add_help=False,
	    formatter_class=delete_usage,
	    description="Send messages to Telegram using Linux terminal.",
		epilog="Homepage: https://github.com/dmitry-tsybulia/termigram"
	)

    parser.add_argument("message", help="Send a message.", nargs="*")
    parser.add_argument("--configure", help="Configure Termigram to specific channel.", action="store_true")
    parser.add_argument("--config", type=str, dest="configuration", help=argparse.SUPPRESS)
    parser.add_argument("--format", dest="parse_mode", help=argparse.SUPPRESS)
    parser.add_argument("-s", "--stdin", help="Send text from stdin.", action="store_true")
    parser.add_argument("-m", "--monospace", help="Send monospace.", action="store_true")
    # r - to open file for reading; b - for reading bytes from the file.
    parser.add_argument("-f", "--file", help="Send file.", nargs="+", type=argparse.FileType("rb"))
    parser.add_argument("-t", "--timeout", help="Set the read timeout for network operations (sec).", type=float, default=30)
    parser.add_argument("-c", "--clean", help="Clean Termigram configuration file.", action="store_true")
    parser.add_argument("-v", "--version", help="Show program's version number and exit.", action="version", version="0.2.85")
    parser.add_argument("-h", "--help", help=argparse.SUPPRESS, action="help")
    parser._positionals.title = 'Positional arguments'
    parser._optionals.title = 'Optional arguments'

    if len(sys.argv)==1: parser.print_help()
    args = parser.parse_args()
    set_configuration = args.configuration

    if args.configure:
        return configure(set_configuration, channel=True)

    if args.monospace:
        args.parse_mode = "markdown"

    if args.clean:
        return clean()

    if args.stdin:
        message = sys.stdin.read()
        if len(message) == 0:
            sys.exit(0)
        if args.monospace:
            message = monospace(message)
        return send(messages=[message], configuration=set_configuration, parse_mode=args.parse_mode)

    try:
        if args.monospace:
            args.message = [monospace(message) for message in args.message]
        send(
            messages=args.message,
            configuration=set_configuration,
            parse_mode=args.parse_mode,
            files=args.file,
            timeout=args.timeout
        )

    except ConfigError as e:
        print(markup(str(e), "red"))
        line = "termigram --configure"
        print("To create the configuration: " + markup(line, "bold") + ".")
        sys.exit(1)

    except telegram.error.NetworkError as e:
        if "timed out" in str(e).lower():
            print(markup("\nError: Connection timed out!", "red"))
            print("Please set a longer timeout.\n"
                  "Try with the option: " + markup("--timeout {}".format(args.timeout + 10), "bold"))
            sys.exit(1)
        else:
            raise(e)

def send(messages=None, configuration=None, parse_mode=None, files=None, timeout=30):

    configuration = expanduser(set_configuration) if configuration else get_config_path()
    configuration_container = configparser.ConfigParser()

    if not configuration_container.read(configuration) or not configuration_container.has_section("telegram"):
        raise ConfigError("\nConfiguration not found!")

    missing_options = set(["token", "chat_id"]) - set(configuration_container.options("telegram"))
    
    if len(missing_options) > 0:
        raise ConfigError("Missing options in configuration file: {}".format(", ".join(missing_options)))
    
    token = configuration_container.get("telegram", "token")
    chat_id = int(configuration_container.get("telegram", "chat_id")) if configuration_container.get("telegram", "chat_id").isdigit() else configuration_container.get("telegram", "chat_id")
    request = telegram.utils.request.Request(read_timeout=timeout)
    bot = telegram.Bot(token, request=request)

    if messages:
        for characters in messages:
            if len(characters) > MAX_MESSAGE_LENGTH:
                print(markup("\nYour message longer than %d characters!" %MAX_MESSAGE_LENGTH, "red"))
                print(markup("The message was split into smaller messages and sent.", "green"))
                message = split_message(characters, MAX_MESSAGE_LENGTH)
                for characters in message:
                    bot.send_message(chat_id=chat_id, text=characters, parse_mode=parse_mode)
            elif len(characters) == 0:
                continue
            else:
                bot.send_message(chat_id=chat_id, text=characters, parse_mode=parse_mode)

    if files:
        for bits in files:
            bot.send_document(chat_id=chat_id, document=bits)

def configure(configuration, channel=None):

    pointer = ">>> "
    configuration = expanduser(configuration) if configuration else get_config_path()

    print("Create your bot using {}. Please insert its token:"
    	 .format(markup("BotFather", "bold")))

    try:
        token = input(pointer).strip()
        bot = telegram.Bot(token)
        bot_name = bot.get_me().username
    except:
        print(markup("Something went wrong, please try again.\n", "red"))
        return configure()

    print("Connected with {}.\n".format(markup(bot_name, "cyan")))

    if channel:
        print("Do you want to send to a {} or a {} channel?"
             .format(markup("public", "bold"), markup("private", "bold")))
        channel_type = input(pointer).strip()

        if channel_type.startswith("public"):
    		print("Enter your {} channel's link (e.g. @simple_channel):"
    			.format(markup("public","bold")))
    		chat_id = input(pointer).strip()
    		if "/" in chat_id:
        		chat_id = "@" + chat_id.split("/")[-1]
    		elif chat_id.startswith("@"):
        		pass
    		else:
        		chat_id = "@" + chat_id
        else:
            print("\nOpen {} in your browser, sign in and open your private channel."
            	.format(markup("web.telegram.org","bold")))
            print("Copy the URL in the address bar and enter it here:")

            url = input(pointer).strip()
            # "-100" is used like a prefix (only for private channels),
            # because channel's IDs are always negative and 13 characters long.
            # The "1" in match.group(1) represents the first parenthesised subgroup.
            chat_id = "-100" + re.match(".+web\.telegram\.org\/#\/im\?p=c(\d+)", url).group(1)

    authorized = False
    while not authorized:
        try:
            bot.send_chat_action(chat_id=chat_id, action="typing")
            authorized = True
        except (telegram.error.Unauthorized, telegram.error.BadRequest):
            input("Please add {} as administrator to your channel and press <Enter>"
                      .format(markup(bot_name, "cyan")))
    
    print(markup("\nCongratulations! Termigram can now post to your channel!", "green"))

    configuration_container = configparser.ConfigParser()
    configuration_container.add_section("telegram")
    configuration_container.set("telegram", "TOKEN", token)
    configuration_container.set("telegram", "chat_id", str(chat_id))
    
    configuration_directory = dirname(configuration)
    if configuration_directory:
        makedirs_check(configuration_directory)
    with open(configuration, "w") as file:
        configuration_container.write(file)

def clean():
    configuration = get_config_path()
    if exists(configuration):
        remove(configuration)

class ConfigError(Exception):
    pass

def markup(text, style):
    ansi_codes = {"bold": "\033[1m", "red": "\033[31m", "green": "\033[32m", "cyan": "\033[36m"}
    return ansi_codes[style] + text + "\033[0m"

def monospace(text):
    return "```\n" + text + "```"

def get_config_path():
    return AppDirs("termigram").user_config_dir + ".conf"

def makedirs_check(path):
    if not exists(path):
        makedirs(path)

def split_message(characters, MAX_MESSAGE_LENGTH):
    message = []
    while len(characters) > MAX_MESSAGE_LENGTH:
        message.append(characters[:MAX_MESSAGE_LENGTH])
        characters = characters[MAX_MESSAGE_LENGTH:]
    message.append(characters)
    return message
