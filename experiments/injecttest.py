#!/usr/bin/env python
import pyautogui
from pynput import keyboard

from pynput.keyboard import Key, Listener


#def on_press(key):
#    print('> {} ({})'.format(str(key), listener.canonical(key)))
#
#def on_release(key):
#    print('< {} ({})'.format(str(key), listener.canonical(key)))
#    if key == Key.esc:
#        return False
#
#
#with Listener(
#        on_press=on_press,
#        on_release=on_release) as listener:
#    listener.join()


def code_to_keypresses(code, pause=0.0):
    lines = code.split('\n')
    last_indent = len(lines[0]) - len(lines[0].lstrip())

    for line in lines:
        print(f'Processing line *{line}*')
        if not line.strip():
            # Empty line
            print('Line empty')
            pyautogui.press('enter')
            continue

        indent = len(line) - len(line.lstrip())
        print('Indent', indent)
        if indent > last_indent:
            # More indent
            print('Pressing tab')
            pyautogui.press('tab')
        elif indent < last_indent:
            # Less indent, possibly several times
            outdent = (last_indent - indent) // 4
            for _ in range(0, outdent):
                print('Pressing bs')
                pyautogui.press('backspace')

        print('Calling typewrite', pause)
        pyautogui.typewrite(line.lstrip(), pause)
        pyautogui.press('enter')
        last_indent = indent


print('Clicking')
pyautogui.click(1000, 1100)
#print('sending cmd-end')
#pyautogui.hotkey('command', 'end')
print('typing')

content = '''
def foo(thing, bob):
    return 3

# and things

def bar(painful, stuff):
    """PyDoc is your friend

    @param painful: stuff
    """
    # indented comment
    if painful == 4:
        print("man I hate this", stuff)
        painful += 1

    return 42

# Outdented Comment  
'''

code_to_keypresses(content, 0.1)
