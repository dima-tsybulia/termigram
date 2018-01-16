#! /usr/bin/python

from setuptools import setup

setup( 
    install_requires=["python-telegram-bot>=5.0", "appdirs"],
    entry_points={"console_scripts": ["termigram=termigram:main"]},
    description="Send messages to Telegram using Linux terminal.",
    author_email="dmitry.tsybulia@gmail.com",
    py_modules=["termigram"],
    author="Dmitry Tsybulia",
    version="0.2.82",
    name="Termigram"
)