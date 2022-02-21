#!/usr/bin/env python
import argparse, subprocess, sys

from asciimatics.widgets import Frame, Layout, Text, Button
from asciimatics.effects import Background
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, StopApplication

from codebox import CodeBox

# ===========================================================================

import logging
#logging.basicConfig(filename="debug.log", level=logging.DEBUG)
#logger = logging.getLogger()

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

        layout.add_widget(Button("Send", self.do_send), 0)
        layout.add_widget(Button("Quit", self.do_quit), 1)

        self.fix()

    def do_quit(self):
        raise StopApplication('done' + str(self.data))

    def do_send(self):
        send_next_line()


# ===========================================================================

def make_it_so(screen, scene):
    global slim_frame
    slim_frame = SlimFrame(screen)

    screen.play([Scene([
        Background(screen),
        slim_frame
    ], -1)], stop_on_resize=True, start_scene=scene, allow_int=True)


def send_next_line():
    global slim_frame, PAUSE

    box = slim_frame.codebox
    code_line = box._reflowed_text[box._line][0]
    prev_line = ''
    output = ''
    keyset = ''

    if box._line > 1:
        prev_line = box._reflowed_text[box._line - 1][0]

    code_indent = len(code_line) - len(code_line.lstrip())
    prev_indent = len(prev_line) - len(prev_line.lstrip())

    if code_indent > prev_indent:
        # More indent
        keyset += '<c:tab>'
        output += '<tab>'
    elif code_indent < prev_indent:
        # Less indent, possibly several times
        outdent = (prev_indent - code_indent) // 4
        for _ in range(0, outdent):
            keyset += '<c:delete>'
            output += '<bs>'

    # Show result in local debug text box
    output += code_line.lstrip()
    output += '<enter>'
    slim_frame.output_box.value = output

    # Type result in actual window
    keyset += code_line.lstrip()
    keyset += '<c:enter>'

    subprocess.run([
        '/usr/local/bin/sendkeys',
        '--application-name',
        'PyCharm',
        '--characters',
        f'{keyset}'])

    # Line done, move to next one
    slim_frame.codebox._change_line(1)
    slim_frame.screen.force_update()

# ---------------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument('filename', help='Name of file to inject with')

if __name__ == '__main__':
    last_scene = None
    args = parser.parse_args()
    with open(args.filename) as f:
        content = f.read()

    while True:
        try:
            Screen.wrapper(make_it_so, catch_interrupt=False, 
                arguments=[last_scene])
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene
