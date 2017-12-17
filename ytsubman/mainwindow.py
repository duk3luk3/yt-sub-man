import os
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import pyqtSlot, Qt

import subs
from settings import settings
from glue import DownloadManager

from pprint import pformat

FormClass, BaseClass = uic.loadUiType("res/main.ui")

class MainWindow(FormClass, BaseClass):
    def __init__(self, *args, **kwargs):
        BaseClass.__init__(self, *args, **kwargs)
        self.setupUi(self)

        for subfile, download_path in settings.subfiles:
            self.subFileBox.insertItem(0, subfile, download_path)

        self.subFileBox.currentIndexChanged.connect(self.subFileBoxChanged)

        self.lastFileIndex = self.subFileBox.currentIndex()
        self.dlm = DownloadManager(self)
        self.dls = set()
        self.channels = []

        self.vlm = subs.VideoListModel()
        self.availVideoList.setModel(self.vlm)
        self.availVideoList.clicked.connect(self.videoClicked)

    @pyqtSlot(int)
    def subFileBoxChanged(self, index):
        self.subFileBox.blockSignals(True)
        print(index, self.subFileBox.count())
        if index == self.subFileBox.count() - 1:
            filename, filter = QtWidgets.QFileDialog.getOpenFileName(self,
                    "Open Subs File", "", "XML Files (*.xml)")
            print(filename)
            if filename:
                dl_path = os.path.dirname(filename)
                settings.subfiles.insert(0, (filename, dl_path))
                settings.save_settings()
                self.subFileBox.insertItem(0, filename, dl_path)
                self.subFileBox.setCurrentIndex(0)
                self.load_sub_file()
            else:
                self.subFileBox.setCurrentIndex(self.lastFileIndex)
        else:
            self.load_sub_file()
        self.lastFileIndex = self.subFileBox.currentIndex()
        self.subFileBox.blockSignals(False)

    def videoClicked(self, index):
        sender = self.sender()
        model = sender.model()

        channel, video = model.data(index, Qt.UserRole)

        self.videoBrowser.setText(pformat(channel.feed) + '\n' + pformat(video))

    def load_sub_file(self):
        subfile = self.subFileBox.currentText()
        dl_path = self.subFileBox.currentData()

        self.downloadPathEdit.setText(dl_path)

        channels = subs.load_subs(subfile)

        self.channelFilterBox.clear()
        self.channelFilterBox.addItem('All', None)
        self.channels = []
        for url in channels:
            channel = subs.Channel(self, self.dlm, url)
            channel.loaded.connect(self.channel_loaded)
            self.channels.append(channel)

    def channel_loaded(self):
        channel = self.sender()
        self.channelFilterBox.addItem('{title}'.format(**channel.feed), channel)
        for video in channel.videos:
            try:
                self.vlm.addItem((channel, video))
            except:
                print(channel, video)
                raise


