#
# This program will open a Serializer listener on the default port,
# wait for widget to receive, unserialize them, and add to the tree
#

from pymt.logger import pymt_logger
from serializer import SerializerNetworkServer, Serializer
import time
from pymt import MTWidget, runTouchApp, pymt_logger

class NetworkClientWidget(MTWidget):
    def __init__(self, **kwargs):
        super(NetworkClientWidget, self).__init__()

        # start a network server
        self.server = SerializerNetworkServer(**kwargs)

    def on_update(self):
        super(NetworkClientWidget, self).on_update()
        try:
            clientid, message = self.server.queue.pop()

            # Got a message, unserialize it
            serializer = Serializer()
            widget = serializer.unserialize(message.data)

            # Got a widget, add to tree
            self.add_widget(widget)

        except IndexError:
            pass

        except:
            pymt_logger.exception('Error while unserialize xml')

if __name__ == '__main__':
    w = NetworkClientWidget()
    runTouchApp(w)
