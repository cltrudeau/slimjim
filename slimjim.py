#!/usr/bin/env python
import argparse, logging, sys

from asciimatics.widgets import (Frame, TextBox, Layout, Label, Divider, Text, 
    CheckBox, RadioButtons, Button, PopUpDialog, TimePicker, DatePicker, 
    DropdownList, PopupMenu)
from asciimatics.effects import Background
from asciimatics.event import MouseEvent
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import (ResizeScreenError, NextScene, 
    StopApplication, InvalidFields)
from asciimatics.parsers import AsciimaticsParser

import pyautogui
from pynput import keyboard

from codebox import CodeBox

# ===========================================================================

PAUSE = 0.5

logging.basicConfig(filename="debug.log", level=logging.DEBUG)
logger = logging.getLogger()

content = ''
slim_frame = None

# ===========================================================================

class SlimFrame(Frame):
    def __init__(self, screen):
        global content
        initial_data = {
            'prefix':True,
            'content':content.split('\n'),
        }

        super(SlimFrame, self).__init__(screen, screen.height, screen.width, 
            has_border=False, data=initial_data)

        # Edit Area
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)

        self.codebox = CodeBox(25, "Content:", "content", readonly=True)
        self.codebox.auto_scroll = False
        layout.add_widget(self.codebox)

        self.output_box = Text("Output:", readonly=True)
        layout.add_widget(self.output_box)

        # Button Bar
        layout = Layout([1, 1])
        self.add_layout(layout)

        layout.add_widget(Button("Quit", self.do_quit), 1)

        self.fix()

    def do_quit(self):
        raise StopApplication('done' + str(self.data))

# ===========================================================================

def make_it_so(screen, scene):
    global slim_frame
    slim_frame = SlimFrame(screen)

    screen.play([Scene([
        Background(screen),
        slim_frame
    ], -1)], stop_on_resize=True, start_scene=scene, allow_int=True)


def key_caught():
    global slim_frame, PAUSE
    logger.debug('================================')

    box = slim_frame.codebox
    code_line = box._reflowed_text[box._line][0]
    logger.debug('code_line: %s', code_line)
    prev_line = ''
    output = ''

    if box._line > 1:
        logger.debug('prev_line: %s', prev_line)
        prev_line = box._reflowed_text[box._line - 1][0]

    code_indent = len(code_line) - len(code_line.lstrip())
    prev_indent = len(prev_line) - len(prev_line.lstrip())

    logger.debug('code_indent: %s', code_indent)
    logger.debug('prev_indent: %s', prev_indent)

    if not code_line.strip():
        # Empty line
        pyautogui.press('enter')
        output = '<enter>'
    else:
        if code_indent > prev_indent:
            # More indent
            pyautogui.press('tab')
            output += '<tab>'
        elif code_indent < prev_indent:
            # Less indent, possibly several times
            outdent = (prev_indent - code_indent) // 4
            for _ in range(0, outdent):
                pyautogui.press('backspace')
                output += '<bs>'

    # Show result in local debug text box
    output += code_line.lstrip()
    output += '<enter>'
    slim_frame.output_box.value = output

    # Type result in actual window
    pyautogui.write(code_line.lstrip(), PAUSE)
    pyautogui.press('enter')

    # Line done, move to next one
    slim_frame.codebox._change_line(1)
    slim_frame.screen.force_update()

# ---------------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument('filename', help='Name of file to inject with')


def log_keystroke(key):
    if str(key) == 'Key.f13':
        key_caught()


if __name__ == '__main__':
    last_scene = None
    args = parser.parse_args()
    with open(args.filename) as f:
        content = f.read()

    listener = keyboard.Listener(on_release=log_keystroke)
    listener.start()

    while True:
        try:
            Screen.wrapper(make_it_so, catch_interrupt=False, 
                arguments=[last_scene])
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene
