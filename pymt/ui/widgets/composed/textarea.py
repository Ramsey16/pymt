from ...factory import MTWidgetFactory
from ....graphx import set_color
from ....base import getFrameDt
from ....graphx import drawLabel, drawRectangle
from ....core.text import Label
from textinput import MTTextInput
from OpenGL.GL import glPushMatrix, glPopMatrix, glTranslate

class MTTextArea(MTTextInput):
    ''' A multi line text input widget'''
    def __init__(self, **kwargs):
        super(MTTextArea, self).__init__(**kwargs)
        self.value = kwargs.get('label') or ''

    def _get_value(self):
        return '\n'.join(self.lines)
    def _set_value(self, text):
        self.lines = text.split('\n')
        self.line_labels = map(self.create_line_label, self.lines)
        self.line_height = self.line_labels[0].content_height
        self.line_spacing = 2
        self.edit_line = len(self.lines)-1 #line being edited
        self.cursor = 1 #pos inside line
        self.cursor_fade = 0
        self.init_glyph_sizes()
    value = property(_get_value, _set_value)

    def set_line_text(self, line_num, text):
        self.lines[line_num] = text
        self.line_labels[line_num].label = text

    def create_line_label(self, text):
        return Label(text, anchor_x='left', anchor_y='top',
                     font_size= 20,
                     color= (0,0,0,1))

    def glyph_size(self, g):
        if not self._glyph_size.has_key(g):
            l = self.create_line_label(g)
            self._glyph_size[g] = l.content_width
        return self._glyph_size[g]

    def init_glyph_sizes(self):
        self._glyph_size = {}
        for line in self.lines:
            for g in line:
                self.glyph_size(g) #just populating cache

    def line_at_pos(self, pos):
        line = int((self.y+self.height)-pos[1])/(self.line_height+self.line_spacing)
        return max(0, min(line, len(self.lines)-1))

    def place_cursor(self, pos):
        self.edit_line = self.line_at_pos(pos)
        text = self.lines[self.edit_line]
        offset = 0
        cursor = 0
        while offset < (pos[0]-self.x) and cursor < len(text):
            offset += self.glyph_size(text[cursor])
            cursor += 1
        self.cursor = cursor

    def cursor_offset(self):
        offset = 0
        for i in xrange(self.cursor):
            offset += self.glyph_size(self.lines[self.edit_line][i])
        return offset

    def draw_cursor(self):
        set_color(1,0,0, int(self.cursor_fade))
        drawRectangle(size=(2, -self.line_height), pos=(self.cursor_offset(),0))

    def draw(self):
        super(MTTextArea, self).draw_background()
        glPushMatrix()
        glTranslate(self.x, self.y+self.height,0)
        for line_num in xrange(len(self.lines)):
            self.line_labels[line_num].draw()
            if self.edit_line == line_num and  self.is_active_input:
                self.draw_cursor()
            glTranslate(0,-(self.line_height+self.line_spacing),0)
        glPopMatrix()

    def on_update(self):
        self.cursor_fade = (self.cursor_fade+getFrameDt()*2)%2

    def on_press(self, touch):
        if not self.is_active_input:
            self.show_keyboard()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.place_cursor(touch.pos)
            touch.userdata[str(self.id)+'cursor'] = True
        return super(MTTextArea, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.userdata.get(str(self.id)+'cursor'):
            self.place_cursor(touch.pos)
        return super(MTTextArea, self).on_touch_move(touch)

    def _kbd_on_text_change(self, value):
        pass

    def insert_charachter(self, c):
        text = self.lines[self.edit_line]
        new_text = text[:self.cursor] + c + text[self.cursor:]
        self.set_line_text(self.edit_line, new_text)
        self.cursor +=1

    def insert_line_feed(self):
        text  = self.lines[self.edit_line]
        left  = text[:self.cursor]
        right = text[self.cursor:]
        self.set_line_text(self.edit_line, left)
        self.lines.insert(self.edit_line+1, right)
        self.line_labels.insert(self.edit_line+1, self.create_line_label(right))
        self.edit_line += 1
        self.cursor = 0

    def do_backspace(self):
        if self.cursor == 0:
            if self.edit_line == 0:
                return #nothign to do, we all teh way at the top
            text_last_line = self.lines[self.edit_line-1]
            text = self.lines[self.edit_line]
            self.set_line_text(self.edit_line-1, text_last_line+text)
            self.lines.pop(self.edit_line)
            self.line_labels.pop(self.edit_line)
            self.edit_line -= 1
            self.cursor = len(text_last_line)
        else:
            text = self.lines[self.edit_line]
            new_text = text[:self.cursor-1] + text[self.cursor:]
            self.set_line_text(self.edit_line, new_text)
            self.cursor -=1

    def _kbd_on_key_up(self, key):
        displayed_str, internal_str, internal_action, scale = key
        if internal_action is None:
            self.insert_charachter(displayed_str)
        elif internal_action == 'backspace':
            self.do_backspace()
        elif internal_action == 'enter':
            self.insert_line_feed()
        elif internal_action == 'escape':
            self.hide_keyboard()

# Register all base widgets
MTWidgetFactory.register('MTTextArea', MTTextArea)
