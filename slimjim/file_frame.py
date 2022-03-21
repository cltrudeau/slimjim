#!/usr/bin/env python
import subprocess

from asciimatics.widgets import Button, Frame, Label, Layout
from asciimatics.exceptions import StopApplication

from slimjim.codebox import CodeBox

# ===========================================================================

class FileFrame(Frame):
    def __init__(self, screen, target_app, filename, raw_mode):
        with open(filename) as f:
            content = f.read()

        self.target_app = target_app
        self.raw_mode = raw_mode

        initial_data = {
            'content':content.split('\n'),
        }

        super(FileFrame, self).__init__(screen, screen.height, screen.width, 
            has_border=False, data=initial_data)

        self.palette['block_box'] = (7, 1, 8)
        self.build_layout()
        self.fix()

    def build_layout(self):
        # Edit Area
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)

        if self.raw_mode:
            layout.add_widget(Label('RAW MODE!!!!'))

        self.codebox = CodeBox(25, "Content:", "content", readonly=True)
        self.codebox.auto_scroll = False
        layout.add_widget(self.codebox)

        # Button Bar
        layout = Layout([1, 1])
        self.add_layout(layout)

        layout.add_widget(Button("Send", self.do_send), 0)
        layout.add_widget(Button("Quit", self.do_quit), 1)

    def do_quit(self):
        raise StopApplication('done' + str(self.data))

    def do_send(self):
        box = self.codebox
        code_line = box._reflowed_text[box._line][0]
        prev_line = ''
        keyset = ''

        if box._line > 1:
            prev_line = box._reflowed_text[box._line - 1][0]

        code_indent = len(code_line) - len(code_line.lstrip())
        prev_indent = len(prev_line) - len(prev_line.lstrip())

        if code_indent > prev_indent:
            # More indent
            keyset += '<c:tab>'
        elif code_indent < prev_indent:
            # Less indent, possibly several times
            outdent = (prev_indent - code_indent) // 4
            for _ in range(0, outdent):
                keyset += '<c:delete>'

        # Type result in actual window
        keyset += code_line.lstrip()
        keyset += '<c:enter>'

        subprocess.run([
            '/usr/local/bin/sendkeys',
            '--application-name',
            self.target_app,
            '--characters',
            f'{keyset}'])

        # Line done, move to next one
        box._change_line(1)
        self.screen.force_update()
