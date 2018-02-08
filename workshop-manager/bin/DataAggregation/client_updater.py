import webdata_aggregator, time
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin


class SocketIOApp(object):
    """Stream sine values"""
    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith('/socket.io'):
            socketio_manage(environ, {'': QueueStatusHandler})


class QueueStatusHandler(BaseNamespace, BroadcastMixin):
    def on_run(self):
        workshops = webdata_aggregator.getAvailableWorkshops()
        sizes = []
        for w in workshops:
            tmp = [w.workshopName, w.q.qsize()]
            sizes.append(tmp)
            self.emit('sizes', tmp)

        while True:
            curr_workshops = webdata_aggregator.getAvailableWorkshops()
            for w in curr_workshops:
                wq = filter(lambda x: x[0] == w.workshopName, sizes)[0]

                if wq[1] is not w.q.qsize():
                    wq[1] = w.q.qsize()
                    self.emit('sizes', wq)
            time.sleep(1)
