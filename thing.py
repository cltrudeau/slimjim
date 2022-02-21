#!/usr/bin/env python
from pynput.keyboard import Listener, Key

def log_keystroke(key):
    key = str(key).replace("'", "")

    if key == 'Key.space':
        key = ' '
    if key == 'Key.shift_r':
        key = ''
    if key == "Key.enter":
        key = '\n'
    print(key,[key])

    if str(key) == 'Key.f13':
        print('Yay')


with Listener(on_press=log_keystroke) as l: l.join()
