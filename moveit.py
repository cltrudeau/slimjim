#!/usr/bin/env python
import sys

from asciimatics.widgets import Frame, TextBox, Layout
from asciimatics.effects import Background
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError 

# ===========================================================================

initial_data = {
    'content':[str(i) for i in range(7)],
}

class SlimFrame(Frame):
    def __init__(self, screen):
        super(SlimFrame, self).__init__(screen, screen.height, screen.width, 
            has_border=False, data=initial_data)

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        self.codebox = TextBox(5, "Content:", "content")
        layout.add_widget(self.codebox)

        self.fix()

        self.codebox._change_line(-3)
        self.screen.force_update()

def make_it_so(screen, scene):
    screen.play([Scene([
        Background(screen),
        SlimFrame(screen)
    ], -1)], stop_on_resize=True, start_scene=scene, allow_int=True)


last_scene = None
while True:
    try:
        Screen.wrapper(make_it_so, catch_interrupt=False, arguments=[last_scene])
        sys.exit(0)
    except ResizeScreenError as e:
        last_scene = e.scene
