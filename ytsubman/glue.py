from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import QObject, QUrl
from PyQt5.QtCore import pyqtSignal

class DownloadManager(QObject):
    def __init__(self, *args, **kwargs):
        QObject.__init__(self, *args, **kwargs)

        self.nam = QNetworkAccessManager(self)
        self.reqs = {}

    def rep_finished(self):
        """\
        Remove finished request from the holding set

        This has to be done because we cannot let requests run out of scope.
        """
        sender = self.sender()
        req = sender.request()
        del self.reqs[req.url()]

    def downloadFile(self, url):
        url = QUrl(url)
        req = QNetworkRequest(url)
        self.reqs[url] = req
        rep = self.nam.get(req)
        rep.finished.connect(self.rep_finished)
        return rep



