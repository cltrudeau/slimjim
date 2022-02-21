# -*- coding: utf-8 -*-
"""This module implements a multi line editing text box"""
from asciimatics.widgets.utilities import _find_min_start, _enforce_width, logger, _get_offset
from asciimatics.widgets import TextBox

import logging
logger = logging.getLogger()

class CodeBox(TextBox):
    def update(self, frame_no):
        self._draw_label()

        # Calculate new visible limits if needed.
        height = self._h
        if not self._line_wrap:
            self._start_column = min(self._start_column, self._column)
            self._start_column += _find_min_start(
                str(self._value[self._line][self._start_column:self._column + 1]),
                self.width,
                self._frame.canvas.unicode_aware,
                self._column >= self.string_len(str(self._value[self._line])))

        # Clear out the existing box content
        (colour, attr, background) = self._pick_colours("readonly" if self._readonly else "edit_text")
        self._frame.canvas.clear_buffer(
            colour, attr, background, self._x + self._offset, self._y, self.width, height)

        # Convert value offset to display offsets
        # NOTE: _start_column is always in display coordinates.
        display_text = self._reflowed_text
        display_start_column = self._start_column
        display_line, display_column = 0, 0
        for i, (_, line, col) in enumerate(display_text):
            if line < self._line or (line == self._line and col <= self._column):
                display_line = i
                display_column = self._column - col

        # Restrict to visible/valid content.
        self._start_line = max(0, max(display_line - height + 1,
                                      min(self._start_line, display_line)))

        # Render visible portion of the text.
        for line, (text, _, _) in enumerate(display_text):
            if self._start_line <= line < self._start_line + height:
                paint_text = _enforce_width(
                    text[display_start_column:], self.width, self._frame.canvas.unicode_aware)
                self._frame.canvas.paint(
                    str(paint_text),
                    self._x + self._offset,
                    self._y + line - self._start_line,
                    colour, attr, background,
                    colour_map=paint_text.colour_map if hasattr(paint_text, "colour_map") else None)

        #------ Up to here has been a copy of TextWidget, now it changes ----

        # Since we switch off the standard cursor, we need to emulate our own
        # if we have the input focus.
        if self._has_focus or self._readonly:
            line = str(display_text[display_line][0])
            text_width = self.string_len(
                line[display_start_column:display_column])

            if self._readonly:
                padding = (self.width - text_width) * ' '
                self._draw_cursor(
                    line + padding,
                    0,
                    self._x + self._offset,
                    self._y + display_line - self._start_line)
            else:
                self._draw_cursor(
                    " " if display_column >= len(line) else line[display_column],
                    frame_no,
                    self._x + self._offset + text_width,
                    self._y + display_line - self._start_line)

    def reset_cursor(self):
        self._change_line(-1)

        #self._line = 0
        #self._column = 0
        #self.update(0)
        self._frame.screen.force_update()
