#!/bin/bash
LD_LIBRARY_PATH=~/.pyenv/versions/3.4.10/lib pyinstaller ipchanger.py
if [ $? -eq 0 ] ; then
    ln -fs "$(pwd)"/dist/ipchanger/ipchanger ~/.pyenv/bin/ipchanger
fi