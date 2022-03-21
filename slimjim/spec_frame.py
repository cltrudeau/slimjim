# slimjim.spec_frame
import subprocess

from asciimatics.widgets import Frame, Layout, Button, Label
from asciimatics.exceptions import StopApplication

from slimjim.matics_box import TextBox
from slimjim.codebox import CodeBox

# ===========================================================================

#import logging
#logging.basicConfig(filename="debug.log", level=logging.DEBUG)
#logger = logging.getLogger()

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
                self.instructions += line[4:].strip() + '\n'
            else:
                # switch to block mode
                self.doing_block = True
                self.block = line
                self.base_indent = len(line) - len(self.block)

# ===========================================================================

class SpecFrame(Frame):
    def __init__(self, screen, target_app, specfile, raw_mode):
        self.content = [Content()]
        self.current_item = 0
        self.target_app = target_app
        self.raw_mode = raw_mode

        self.parse_content(specfile)

        # Initial values for the widgets
        initial_data = {
            'instructions':self.content[0].instructions.split('\n'),
            'block':self.content[0].block.split('\n'),
        }

        super(SpecFrame, self).__init__(screen, screen.height, screen.width, 
            has_border=False, data=initial_data)

        self.palette['block_box'] = (7, 1, 8)
        self.build_layout()
        self.fix()

    def build_layout(self):
        # Edit Area
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)

        if self.raw_mode:
            layout.add_widget(Label('RAW MODE!!!'))

        self.instruction_box = TextBox(5, "Instructions:", "instructions", 
            readonly=True)
        self.instruction_box.auto_scroll = False
        layout.add_widget(self.instruction_box)

        self.block_box = CodeBox(20, "Block:", "block", readonly=True)
        self.block_box.custom_colour = 'block_box'
        self.block_box.auto_scroll = False
        layout.add_widget(self.block_box)

        # Button Bar
        layout = Layout([1, 1, 1, 1, 1])
        self.add_layout(layout)

        self.send_button = Button("Send", self.do_send)
        layout.add_widget(self.send_button, 0)

        self.line_button = Button("Line", self.do_line)
        layout.add_widget(self.line_button, 1)

        layout.add_widget(Button("Back", self.do_back), 2)

        self.next_button = Button("Next", self.do_next)
        layout.add_widget(self.next_button, 3)

        layout.add_widget(Button("Quit", self.do_quit), 4)

    def parse_content(self, specfile):
        with open(specfile) as f:
            for line in f:
                try:
                    self.content[-1].add_line(line)
                except NewContent:
                    self.content.append(Content())
                    self.content[-1].add_line(line)

    def do_send(self):
        keyset = ''
        is_first = True
        indent = self.content[self.current_item].base_indent
        prev_indent = indent
        blocks = self.content[self.current_item].block.split('\n')
        for line in blocks:
            if is_first:
                # first line, target cursor is meant to be positioned, ignore
                # any leading spaces
                is_first = False
            elif not line.lstrip():
                # line is blank, leave the auto-indent alone
                keyset += '<c:enter>'
            else:
                # subsequent line: manage auto-indent based on previous indent
                keyset += '<c:enter>'
                indent = len(line) - len(line.lstrip())

                if not self.raw_mode:
                    if indent > prev_indent:
                        # More indent
                        keyset += '<c:tab>'
                    elif indent < prev_indent:
                        # Less indent, possibly several times
                        outdent = (prev_indent - indent) // 4
                        for _ in range(0, outdent):
                            keyset += '<c:delete>'

            # Add line to key stroke string
            if self.raw_mode:
                keyset += line
            else:
                keyset += line.lstrip()

            prev_indent = indent

        # Type the block
        subprocess.run([
            '/usr/local/bin/sendkeys',
            '--application-name',
            self.target_app,
            '--characters',
            f'{keyset}'])

        # Advance to the next block
        self.do_next()

    def do_next(self):
        self.current_item += 1
        if self.current_item >= len(self.content):
            self.send_button.disabled = True
            self.next_button.disabled = True
            self.instruction_box.value = ['', ]
            self.block_box.value = ['', ]
        else:
            item = self.content[self.current_item]
            self.instruction_box.value = item.instructions.split('\n')
            self.block_box.value = item.block.split('\n')

        self.screen.force_update()

    def do_line(self):
        # Sends only the highlighted line, ignoring any indent
        box = self.block_box
        code_line = box._reflowed_text[box._line][0]
        keyset = code_line.lstrip() + '<c:enter>'

        subprocess.run([
            '/usr/local/bin/sendkeys',
            '--application-name',
            self.target_app,
            '--characters',
            f'{keyset}'])

        # Line done, move to next one
        box._change_line(1)
        self.screen.force_update()

    def do_back(self):
        self.current_item -= 1
        if self.current_item < 0:
            self.current_item = 0

        item = self.content[self.current_item]
        self.instruction_box.value = item.instructions.split('\n')
        self.block_box.value = item.block.split('\n')
        self.send_button.disabled = False
        self.next_button.disabled = False
        self.screen.force_update()

    def do_quit(self):
        raise StopApplication('done' + str(self.data))
