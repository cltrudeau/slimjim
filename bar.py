#!/usr/bin/env python
import pyautogui

pause = 0.0

print('Clicking')
pyautogui.click(1000, 1100)

#print('sending cmd-end')
#pyautogui.hotkey('command', 'end')

print('fox')
pyautogui.write('the quick brown fox jumped over', pause)
print('sent')

print('dog')
pyautogui.press('enter')
pyautogui.write('the lazy yellow dog', pause)
print('sent')
