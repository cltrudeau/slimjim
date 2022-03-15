#!/usr/bin/env python
import argparse, subprocess, sys

from asciimatics.widgets import Frame, Layout, TextBox, Button, Label
from asciimatics.effects import Background
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, StopApplication

from codebox import CodeBox

# ===========================================================================

import logging
#logging.basicConfig(filename="debug.log", level=logging.DEBUG)
#logger = logging.getLogger()

content = []
target_app = ''
raw_mode = False

# ===========================================================================

class NewContent(Exception):
    pass


class Content:
    def __init__(self):
        self.instructions = ''
        self.block = ''
        self.doing_block = False
        self.base_indent = 0

    def add_line(self, line):
        if self.doing_block:
            if line.startswith('---:'):
                # next instruction line
                raise NewContent()

            # was block line, continue building the block
            self.block += line
        else:
            # currently taking instructions
            if line.startswith('---:'):
                # still taking instructions
                self.instructions += line[4:].strip()
            else:
                # switch to block mode
                self.doing_block = True
                self.block = line
                self.base_indent = len(line) - len(self.block)

# ===========================================================================

class SlimFrame(Frame):
    def __init__(self, screen):
        global content, raw_mode
        self.current_item = 0
        initial_data = {
            'instructions':content[0].instructions.split('\n'),
            'block':content[0].block.split('\n'),
        }

        super(SlimFrame, self).__init__(screen, screen.height, screen.width, 
            has_border=False, data=initial_data)

        self.palette['block_box'] = (7, 1, 8)

        # Edit Area
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)

        if raw_mode:
            layout.add_widget(Label('RAW MODE!!!'))

        self.instruction_box = TextBox(5, "Instructions:", "instructions", 
            readonly=True)
        self.instruction_box.auto_scroll = False
        layout.add_widget(self.instruction_box)

        self.block_box = TextBox(20, "Block:", "block", readonly=True)
        self.block_box.custom_colour = 'block_box'
        self.block_box.auto_scroll = False
        layout.add_widget(self.block_box)

        # Button Bar
        layout = Layout([1, 1, 1])
        self.add_layout(layout)

        self.send_button = Button("Send", self.do_send)
        layout.add_widget(self.send_button, 0)

        layout.add_widget(Button("Back", self.do_back), 1)
        layout.add_widget(Button("Quit", self.do_quit), 2)

        self.fix()

    def do_send(self):
        global content, target_app, raw_mode

        keyset = ''
        is_first = True
        indent = content[self.current_item].base_indent
        prev_indent = indent
        for line in content[self.current_item].block.split('\n'):
            if is_first:
                # first line, target cursor is meant to be positioned, ignore
                # any leading spaces
                is_first = False
            else:
                # subsequent line: manage auto-indent based on previous indent
                keyset += '<c:enter>'
                indent = len(line) - len(line.lstrip())

                if not raw_mode:
                    if indent > prev_indent:
                        # More indent
                        keyset += '<c:tab>'
                    elif indent < prev_indent:
                        # Less indent, possibly several times
                        outdent = (prev_indent - indent) // 4
                        for _ in range(0, outdent):
                            keyset += '<c:delete>'

            # Add line to key stroke string
            if raw_mode:
                keyset += line
            else:
                keyset += line.lstrip()

            prev_indent = indent

        # Type the block
        subprocess.run([
            '/usr/local/bin/sendkeys',
            '--application-name',
            target_app,
            '--characters',
            f'{keyset}'])

        # Line done, move to next item
        self.current_item += 1
        if self.current_item >= len(content):
            self.send_button.disabled = True
            self.instruction_box.value = ['', ]
            self.block_box.value = ['', ]
        else:
            item = content[self.current_item]
            self.instruction_box.value = item.instructions.split('\n')
            self.block_box.value = item.block.split('\n')

        self.screen.force_update()

    def do_back(self):
        self.current_item -= 1
        if self.current_item < 0:
            self.current_item = 0

        item = content[self.current_item]
        self.instruction_box.value = item.instructions.split('\n')
        self.block_box.value = item.block.split('\n')
        self.screen.force_update()
        self.send_button.disabled = False

    def do_quit(self):
        raise StopApplication('done' + str(self.data))


# ===========================================================================

def make_it_so(screen, scene):
    slim_frame = SlimFrame(screen)

    screen.play([Scene([
        Background(screen),
        slim_frame
    ], -1)], stop_on_resize=True, start_scene=scene, allow_int=True)

# ---------------------------------------------------------------------------

DESCRIPTION = """
Injects content into the target application as typewritten key presses using
the sendkeys application. Content is sourced from a spec file.  Lines
beginning with "---:" are treated as instructions to the user, and are
displayed but not typewritten. All other lines are treated as injection
sources. Groups of lines between instructions are injected as single blocks.
"""

parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument('app', help=('Name of app to target keystrokes to'))
parser.add_argument('spec', help=('Name of spec file containing content and '
    'instructions')) 
parser.add_argument('-r', '--raw', action='store_true', help=("Type exactly "
    "what is seen, don't compensate for auto-indent in the target"))

if __name__ == '__main__':
    last_scene = None
    args = parser.parse_args()
    raw_mode = args.raw

    # Validate target app
    proc = subprocess.run(['/usr/local/bin/sendkeys', 'apps'],
        capture_output=True)
    if args.app in str(proc.stdout):
        target_app = args.app
    else:
        print((f'Target app "{args.app}" not found by sendkeys, run '
            '"sendkeys apps" to see a full list of possible targets'))
        quit()

    # Parse content
    content = [Content()]
    with open(args.spec) as f:
        for line in f:
            try:
                content[-1].add_line(line)
            except NewContent:
                content.append(Content())
                content[-1].add_line(line)

    # Fire up the TUI
    while True:
        try:
            Screen.wrapper(make_it_so, catch_interrupt=False, 
                arguments=[last_scene])
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene
