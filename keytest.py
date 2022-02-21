#!/usr/bin/env python
import pyautogui
from pynput import keyboard

def callme():
    print("I was called")


keymap = {
    '<f6>': callme,
    '<ctrl>+o': callme,
    '<f13>': callme,
}

print('Starting...')

#with keyboard.GlobalHotKeys(keymap) as m:
#    m.join()

def for_canonical(f):
    return lambda k: f(l.canonical(k))

hotkey = keyboard.HotKey([keyboard.Key.f6, ], callme)
with keyboard.Listener(
        on_press=for_canonical(hotkey.press),
        on_release=for_canonical(hotkey.release)) as l:
    l.join()
