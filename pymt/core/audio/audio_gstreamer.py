'''
AudioGstreamer: implementation of Sound with GStreamer
'''

try:
    import pygst
    if not hasattr(pygst, '_gst_already_checked'):
        pygst.require('0.10')
        pygst._gst_already_checked = True
    import gst
except:
    raise

from . import Sound, SoundLoader
import os
from pymt.logger import pymt_logger

class SoundGstreamer(Sound):
    @staticmethod
    def extensions():
        return ('wav', 'ogg', 'mp3', )

    def __init__(self, **kwargs):
        self._data = None
        super(SoundGstreamer, self).__init__(**kwargs)

    def __del__(self):
        if self._data is not None:
            self._data.set_state(gst.STATE_NULL)

    def _on_gst_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self._data.set_state(gst.STATE_NULL)
            self.stop()
        elif t == gst.MESSAGE_ERROR:
            self._data.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            pymt_logger.error('AudioGstreamer: %s' % err)
            pymt_logger.debug(str(debug))
            self.stop()

    def play(self):
        if not self._data:
            return
        self._data.set_state(gst.STATE_PLAYING)

    def stop(self):
        if not self._data:
            return
        self._data.set_state(gst.STATE_NULL)

    def load(self):
        self.unload()
        if self.filename is None:
            return
        if self.filename[0] == '/':
            filepath = 'file://' + self.filename
        else:
            filepath = 'file://' + os.path.join(os.getcwd(), self.filename)

        self._data = gst.element_factory_make('playbin2', 'player')
        bus = self._data.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self._on_gst_message)

        self._data.set_property('uri', filepath)

    def unload(self):
        self.stop()
        self._data = None

    def seek(self, position):
        if self._data is None:
            return
        self._data.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_SKIP,
                               position / 1000000000.)

    def _get_volume(self):
        if self._data is not None:
            self._volume = self._data.get_property('volume')
        return super(SoundPygame, self)._get_volume()

    def _set_volume(self, volume):
        if self._data is not None:
            self._data.set_property('volume', volume)
        return super(SoundPygame, self)._set_volume(volume)

SoundLoader.register(SoundGstreamer)