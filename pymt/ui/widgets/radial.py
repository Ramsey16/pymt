'''
Various radial widgets for PyMT
Initially written by xelapond <xelapond@gmail.com>
'''

from __future__ import with_statement
from __future__ import division

from pyglet import *
from pyglet.gl import *
from math import *
from pymt.ui.factory import MTWidgetFactory
from pymt.ui.widgets.widget import MTWidget

__all__ = ['MTVectorSlider']

### HELP NEEDED IN THE COLORING DEPARTMENT ###

#Get the linear distance between two points
def _get_distance(Pos1, Pos2):
    return math.sqrt((Pos2[0] - Pos1[0])**2 + (Pos2[1] - Pos1[1])**2)

def prot(p, d, rp=(0, 0)):
    '''Rotates a given point(p) d degrees clockwise around rp'''
    d = -radians(d)
    p = list(p)
    p[0] -= rp[0]
    p[1] -= rp[1]
    np = [p[0]*cos(d) + p[1]*sin(d), -p[0]*sin(d) + p[1]*cos(d)]
    np[0] += rp[0]
    np[1] += rp[1]
    return tuple(np)

class MTVectorSlider(MTWidget):
    '''
    This is a slider that provides an arrow, and allows you to manipulate
    it just like any other vector, adjusting its angle and amplitude.
    
    :Parameters:
        'bgcolor' : The background color of the widget
        'vcolor' : The color for the vector
        'radius': The radius of the whole widget
        
    :Parameters Inherited through MTWidget:
        'pos' : Position
        'size' : Size
        'color' : Has no effect on this widget
        'visible' : visibility

    '''

    def __init__(self, **kwargs):
        super(MTVectorSlider, self).__init__(**kwargs)

        kwargs.setdefault('radius', 200)
        kwargs.setdefault('vcolor', (1, .28, 0))
        kwargs.setdefault('bgcolor', (.2, .4, .9))
        
        self.radius = kwargs.get('radius')
        self.vcolor = kwargs.get('vcolor')
        self.bgcolor = kwargs.get('bgcolor')
        
        #The vector hand
        self.vector = [0, 0]
        #A vector for the x axis
        self.xvec = (10, 0)

        #Vector Stuff, for the callback
        self.amplitude = _get_distance(self.pos, self.vector)
        self.angle = 0

        self.register_event_type('on_amplitude_change')
        self.register_event_type('on_angle_change')
        #This is just a combination of the last two
        self.register_event_type('on_vector_change')

    def collide_point(self, x, y):
        '''Because this widget is a circle, and this method as
        defined in MTWidget is for a square, we have to override
        it.'''
        return _get_distance(self.pos, (x, y)) <= self.radius

    def _calc_stuff(self):
        '''Recalculated the args for the callbacks'''
        #AMPLITUDE
        self.amplitude = _get_distance(self.pos, self.vector)
        #ANGLE
        #Make a new vector relative to the origin
        tvec = [self.vector[0], self.vector[1]]
        tvec[0] -= self.pos[0]
        tvec[1] -= self.pos[1]

        #Incase python throws float div or div by zero exception, ignore them, we will be close enough
        try:
            self.angle = degrees(atan((int(tvec[1])/int(tvec[0]))))
        except:
            pass

        #Ajdust quadrants so we have 0-360 degrees
        if tvec[0] < 0 and tvec[1] > 0:
            self.angle = 90 + (90 + self.angle)
        elif tvec[0] < 0 and tvec[1] < 0:
            self.angle += 180
        elif tvec[0] > 0 and tvec[1] < 0:
            self.angle = 270 + (self.angle + 90)
        elif tvec[0] > 0 and tvec[1] > 0:
            pass

    def on_touch_down(self, touches, touchID, x, y):
        if self.collide_point(x, y):
            #The blob is in the widget, do stuff
            self.vector[0], self.vector[1] = x, y
            self._calc_stuff()

            self.dispatch_event('on_aplitude_change', self.amplitude)
            self.dispatch_event('on_angle_change', self.angle)
            self.dispatch_event('on_vector_change', self.amplitude, self.angle)
            
    def on_touch_move(self, touches, touchID, x, y):
        if self.collide_point(x, y):
            #The blob is in the widget, do stuff
            self.vector[0], self.vector[1] = x, y
            self._calc_stuff()

            self.dispatch_event('on_aplitude_change', self.amplitude)
            self.dispatch_event('on_angle_change', self.angle)
            self.dispatch_event('on_vector_change', self.amplitude, self.angle)
    
    def draw(self):
        set_color(*self.bgcolor)
        drawCircle(self.pos, self.radius)
        
        set_color(*self.vcolor)
        drawCircle(self.pos, 30)
        #Rotate the triangle so its not skewed
        l = prot((self.pos[0] - 30, self.pos[1]), self.angle-90, self.pos)
        h = prot((self.pos[0] + 30, self.pos[1]), self.angle-90, self.pos)
        with gx_begin(GL_POLYGON):
            print h
            glVertex2f(*l)
            glVertex2f(*h)
            glVertex2f(self.vector[0], self.vector[1])

MTWidgetFactory.register('MTVectorSlider', MTVectorSlider)

if __name__ == '__main__':
    def on_vector_change(amp, ang):
        print amp, ang

    from pymt import *
    w = MTWindow(fullscreen=False)
    mms = MTVectorSlider(pos=(200,200))
    mms.push_handlers('on_vector_change', on_vector_change)
    w.add_widget(mms)
    runTouchApp()