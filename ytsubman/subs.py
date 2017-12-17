from PyQt5.QtCore import QObject, pyqtSignal, QAbstractListModel, QModelIndex, Qt
import opml
import feedparser
from pprint import pprint

def load_subs(f):
    """Load subscriptions from an exported youtube subscription xml

    Returns the channel feed URLs
    """
    outline = opml.parse(f)

    recs = outline[0]

    urls = [rec.xmlUrl for rec in recs]

    return urls

def load_channels(subs):
    """Load channels from channel feed urls.

    Returns the whole response which is a dict object.

    The 'feed' key contains information about the channel,
    the 'entries' key contains videos
    """
    channels = []
    for sub in subs:
        channels.append(feedparser.parse(sub))

    return channels

class Channel(QObject):
    loaded = pyqtSignal()

    def __init__(self, parent, download_manager, url, *args, **kwargs):
        QObject.__init__(self, parent, *args, **kwargs)

        self.dlm = download_manager
        self.url = url
        self.rep = self.dlm.downloadFile(url)
        self.rep.finished.connect(self.dl_finished)
        self.feed = None
        self.videos = None

    def dl_finished(self):
        content = self.rep.readAll()
        parsed = feedparser.parse(content)
        self.feed = parsed.feed
        self.videos = parsed.entries
        self.loaded.emit()

class VideoListModel(QAbstractListModel):
    def __init__(self, *args, **kwargs):
        QObject.__init__(self, *args, **kwargs)

        self.__data = []

    def rowCount(self, parent=QModelIndex()):
        return len(self.__data)

    def data(self, index, role):
        if index.isValid():
            channel, video = self.__data[index.row()] or (None, None)
            if role == Qt.DisplayRole:
                if channel and video:
                    return '{channel[title]} - {video[title]}'.format(channel=channel.feed, video=video)
            elif role == Qt.UserRole:
                return (channel, video)
        return None

    def insertRows(self, row, count, parent=QModelIndex()):
        self.beginInsertRows(QModelIndex(), row, row + count - 1)
        self.__data[row:row] = [(None, None)] * count
        self.endInsertRows()
        return True

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole:
            return False

        if not value:
            raise ValueError()

        self.__data[index.row()] = value
        self.dataChanged.emit(index, index)
        return True

    def addItem(self, data):
#        print('data:', self.__data)
        self.insertRows(self.rowCount(), 1)
        idx = self.createIndex(self.rowCount() -1, 0)
        self.setData(idx, data)
