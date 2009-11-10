'''
Image: handle loading of images
'''

from __future__ import with_statement

__all__ = ('Image', 'ImageLoader', 'ImageData')

import pymt
from pymt.graphx import DO, gx_color, gx_blending, drawTexturedRectangle, set_color
from pymt.logger import pymt_logger
from pymt.texture import Texture, TextureRegion

class ImageData(object):
    '''Container for data image : width, height, mode and data.
    ..warning ::
        Only RGB and RGBA mode are allowed.
    '''

    __slots__ = ('width', 'height', 'mode', 'data')

    def __init__(self, width, height, mode, data):
        assert mode in ('RGB', 'RGBA')
        self.width = int(width)
        self.height = int(height)
        self.mode = mode
        self.data = data


class ImageLoaderBase(object):
    '''Base to implement an image loader.'''

    __slots__ = ('_texture', '_data', 'filename')

    _texture = None
    _data = None
    filename = ''

    def __init__(self, filename):
        self._data = self.load(filename)

    def load(self, filename):
        '''Load an image'''
        return None

    def _get_width(self):
        return self._data.width
    width = property(_get_width, doc='Image width')

    def _get_height(self):
        return self._data.height
    height = property(_get_height, doc='Image height')

    def _get_size(self):
        return (self._data.width, self._data.height)
    size = property(_get_size,
                   doc='Image size (width, height)')

    def _get_texture(self):
        if self._texture is None:
            if self._data is None:
                return None
            self._texture = Texture.create_from_data(self._data)
        return self._texture
    texture = property(_get_texture,
                      doc='Get the image texture (created on the first call)')

    @pymt.deprecated
    def get_texture(self):
        '''Retreive the texture of image
        @deprecated: use self.texture instead.'''
        return self.texture


class ImageLoader(object):
    __slots__ = ('loaders')
    loaders = []

    @staticmethod
    def register(cls):
        ImageLoader.loaders.append(cls)

    @staticmethod
    def load(filename):
        # extract extensions
        ext = filename.split('.')[-1].lower()
        im = None
        for loader in ImageLoader.loaders:
            if ext not in loader.extensions():
                continue
            im = loader(filename)
            break
        if im is None:
            raise Exception('Unsupported extension <%s>, no loader found.' % ext)
        return im


class Image(object):
    '''Load an image, and store the size and texture.
    
    :Parameters:
        `arg` : can be str or Texture or Image object
            Filename of the image
        `opacity` : float, default to 1.0
            Opacity of the image
        `scale` : float, default to 1.0
            Scale of the image
        `anchor_x` : float, default to 0
            X anchor
        `anchor_y` : float, default to 0
            Y anchor
        `pos` : list, default to (0, 0)
            Position of image
        `x` : float
            X position
        `y` : float
            Y position
    '''

    copy_attributes = ('opacity', 'scale', 'anchor_x', 'anchor_y', '_width',
                       '_height', 'texture', '_filename', 'x', 'y')

    def __init__(self, arg, **kwargs):
        self._filename  = None
        self._width     = 0
        self._height    = 0
        self.texture    = None
        self.image      = None
        self.opacity    = 1.
        self.scale      = 1.
        self.anchor_x   = 0
        self.anchor_y   = 0
        self.x          = 0
        self.y          = 0

        if type(arg) == Image:
            for attr in Image.copy_attributes:
                self.__setattr__(attr, arg.__getattribute__(attr))
        elif type(arg) in (Texture, TextureRegion):
            self.texture    = arg.texture
            self.width      = self.texture.width
            self.height     = self.texture.height
        elif type(arg) == str:
            self.filename   = arg
        else:
            raise Exception('Unable to load image with type %s' % str(type(arg)))

        # after loading, let the user take the place
        if 'opacity' in kwargs:
            self.opacity    = kwargs.get('opacity')
        if 'scale' in kwargs:
           self.scale      = kwargs.get('scale')
        if 'anchor_x' in kwargs:
            self.anchor_x   = kwargs.get('anchor_x')
        if 'anchor_y' in kwargs:
            self.anchor_y   = kwargs.get('anchor_y')
        if 'pos' in kwargs:
            self.x, self.y  = kwargs.get('pos')
        if 'x' in kwargs:
            self.x = kwargs.get('x')
        if 'y' in kwargs:
            self.y = kwargs.get('y')

    @staticmethod
    def load(filename):
        '''Load an image'''
        return Image(filename)

    def _get_filename(self):
        return self._filename
    def _set_filename(self, value):
        if value is None:
            return
        if value == self._filename:
            return
        self._filename = value
        self.image      = ImageLoader.load(self._filename)
        self.texture    = self.image.texture
        self.width      = self.image.width
        self.height     = self.image.height
    filename = property(_get_filename, _set_filename,
            doc='Get/set the filename of image')

    def _get_width(self):
        return self._width * self.scale
    def _set_width(self, value):
        self._width = value
    width = property(_get_width, _set_width)

    def _get_height(self):
        return self._height * self.scale
    def _set_height(self, value):
        self._height = value
    height = property(_get_height, _set_height)

    def _get_size(self):
        return (self.width, self.height)
    def _set_size(self, size):
        self.width, self.height = size
    size = property(_get_size, _set_size,
            doc='tuple(width, height): width/height of image')

    def _set_pos(self, pos):
        if self.x == pos[0] and self.y == pos[1]:
            return
        self.x, self.y = pos
    def _get_pos(self):
        return (self.x, self.y)
    pos = property(_get_pos, _set_pos, doc='tuple(x, y): position of widget')

    @pymt.deprecated
    def get_texture(self):
        '''Retreive the texture of image
        @deprecated: use self.texture instead.'''
        return self.texture

    def draw(self):
        '''Draw the image on screen'''
        imgpos = (self.x - self.anchor_x * self.scale, self.y - self.anchor_y * self.scale)
        with DO(gx_color(1, 1, 1, self.opacity), gx_blending):
            drawTexturedRectangle(texture=self.texture, pos=imgpos, size=self.size)

def load(filename):
    '''Load an image'''
    return Image.load(filename)

# load image loaders
try:
    import img_pygame
    ImageLoader.register(img_pygame.ImageLoaderPygame)
    pymt_logger.info('Image: register Pygame loader')
except:
    pass

try:
    import img_pil
    ImageLoader.register(img_pil.ImageLoaderPIL)
    pymt_logger.info('Image: register PIL loader')
except:
    pass
