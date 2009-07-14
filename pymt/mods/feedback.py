'''
A global feedback effect (aka Surface)
'''

import pyglet
from pymt import *
import os

particle_fn = os.path.join(pymt_data_dir, 'particle.png')
particle2_fn = os.path.join(pymt_data_dir, 'particle2.png')
ring_fn = os.path.join(pymt_data_dir, 'ring.png')
ring_img = pyglet.image.load(ring_fn)
ring_img.anchor_x = ring_img.width / 2
ring_img.anchor_y = ring_img.height / 2

class GlobalFeedbackTouch(MTWidget):
    def __init__(self, **kwargs):
        super(GlobalFeedbackTouch, self).__init__(**kwargs)

        # max times of a move position (after that, it will be deleted)
        self.maxtimemove = .1

        # minimum time before the nomove particle appear
        self.mintimenomove = 1

        # maximum moves available
        self.maxmoves = 20

        # prepare list of moves
        self.timer = 0
        self.moves = []
        self.moves.append([self.x, self.y, self.maxtimemove])

    def on_move(self, x, y):

        # reset nomove timer
        self.timer = 0

        # append a new move in list
        self.moves.append([x, y, self.maxtimemove])
        if len(self.moves) > self.maxmoves:
            self.moves = self.moves[1:]

    def draw(self):
        # advance nomove timer
        self.timer += getFrameDt()

        # nomove timeout, show it !
        if self.timer > self.mintimenomove:
            alpha = min(0.9, (self.timer - self.mintimenomove) * 4)
            set_color(1, 1, 1, alpha)
            set_brush(particle2_fn, size=alpha * 50)
            paintLine((self.x, self.y, self.x + 1, self.y + 1))

        # show moves
        move_to_delete = []
        have_first = False
        ox, oy = 0, 0
        alphastep = 1.0 / max(1, len(self.moves))
        alpha = 0

        # prepare brush
        set_brush(particle2_fn, size=5)

        # show all moves
        for idx in xrange(0, len(self.moves)):

            # decrease timeout
            self.moves[idx][2] -= getFrameDt()
            x, y, timer = self.moves[idx]

            # move timeout, delete it
            if timer < 0:
                move_to_delete.append(idx)
                continue

            # save the first move to draw line
            if not have_first:
                have_first = True
                ox, oy = x, y
                continue

            # calcute steps for having a nice line
            numsteps = max(20, int(Vector(ox, oy).distance(Vector(x, y)))/20)

            # draw the line !
            set_color(1, 1, 1, alpha)
            paintLine((ox, oy, x, y), numsteps=10)

            # prepare next move
            ox, oy = x, y
            alpha += alphastep

class GlobalFeedback(MTWidget):
    def __init__(self, **kwargs):
        super(GlobalFeedback, self).__init__(**kwargs)
        self.touches = {}
        self.rings = []

    def on_touch_down(self, touches, touchID, x, y):
        self.touches[touchID] = GlobalFeedbackTouch(pos=(x, y))
        self.add_widget(self.touches[touchID])

        # prepare ring
        newsprite = pyglet.sprite.Sprite(ring_img, x=x, y=y)
        newsprite.opacity = 195
        newsprite.scale = 0.10
        self.rings.append(newsprite)

    def on_touch_move(self, touches, touchID, x, y):
        if not touchID in self.touches:
            return
        self.touches[touchID].pos = (x, y)

    def on_touch_up(self, touches, touchID, x, y):
        if touchID in self.touches:
            self.remove_widget(self.touches[touchID])
            del self.touches[touchID]

    def on_draw(self):
        # Uncomment the line below to always see feedback.
	#self.bring_to_front()
        super(GlobalFeedback, self).on_draw()

    def draw(self):
        rings_to_delete = []
        for i in xrange(0, len(self.rings)):
            self.rings[i].draw()
            self.rings[i].opacity -= getFrameDt() * 400
            self.rings[i].scale += getFrameDt() * 2
            if self.rings[i].opacity <= 0:
                rings_to_delete.append(i)
        for i in rings_to_delete:
            del self.rings[i]


def start(win, ctx):
    ctx.w = GlobalFeedback()
    win.add_widget(GlobalFeedback())

def stop(win, ctx):
    win.remove_widget(ctx.w)