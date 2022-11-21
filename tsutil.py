import base64
import datetime
import struct
import sys

import bitcoin.rpc
import requests
from PyQt6.QtCore import QUrl, QTimer, QRunnable, pyqtSlot, QObject, pyqtSignal, QThreadPool
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QFileDialog, QPushButton, QVBoxLayout, QDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
import otsclient.args
import logging
import subprocess

import os

from opentimestamps.core.notary import BitcoinBlockHeaderAttestation, PendingAttestation
from opentimestamps.core.serialize import StreamDeserializationContext, DeserializationError, BadMagicError
from opentimestamps.core.timestamp import DetachedTimestampFile
from otsclient.cmds import upgrade_timestamp

class WorkerSignals(QObject):
    error = pyqtSignal(tuple)
    success = pyqtSignal(tuple)

class VerifyWorker(QRunnable):
    def __init__(self, orig_file, ots_file):
        super(VerifyWorker, self).__init__()
        self.orig_file = orig_file
        self.ots_file = ots_file
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        ots_file = self.ots_file
        orig_file = self.orig_file

        if not os.path.exists(ots_file):
            self.signals.error.emit((".ots file doesn't exist", ots_file))
            return

        with open(ots_file, 'rb') as ots_fd:
            ctx = StreamDeserializationContext(ots_fd)
            try:
                detached_timestamp = DetachedTimestampFile.deserialize(ctx)
            except BadMagicError as e:
                self.signals.error.emit(("not an ots file", e))
                return
            except DeserializationError as e:
                self.signals.error.emit(("ots file deserialization error", e))
                return

            with open(orig_file, 'rb') as orig_fd:
                orig_digest = detached_timestamp.file_hash_op.hash_fd(orig_fd)

            if orig_digest != detached_timestamp.file_digest:
                self.signals.error.emit(("digest mismatch", (orig_digest, detached_timestamp.file_digest)))
                return

        timestamp = detached_timestamp.timestamp

        args = otsclient.args.parse_ots_args(["v", ots_file])

        args.calendar_urls = []
        upgrade_timestamp(timestamp, args)

        good = False
        unix_time = None
        block_height = None

        all_attestations = timestamp.all_attestations()

        block_attestations = filter(lambda x: x[1].__class__ == BitcoinBlockHeaderAttestation, all_attestations)

        for merkle_root, attestation in sorted(block_attestations, key=lambda x: x[1].height):
            try:
                proxy = bitcoin.rpc.Proxy()
                header = proxy.getblockheader(proxy.getblockhash(attestation.height))
                if merkle_root == header.hashMerkleRoot:
                    good = True
                    unix_time = header.nTime
                    block_height = attestation.height
                    break
                proxy.close()
            except Exception as e:
                print("Connecting Local Bitcoin Client Failed. Use blockchain.info API instead. Error Log: " + str(e))
                url = "https://blockchain.info/rawblock/" + str(attestation.height)
                block = requests.get(url).json()
                if "".join(map(lambda x: x.hex(), reversed(struct.unpack("32c", merkle_root)))) == block['mrkl_root']:
                    good = True
                    unix_time = block['time']
                    block_height = attestation.height
                    break

        if good:
            self.signals.success.emit((unix_time, block_height))
            return
        else:
            self.signals.error.emit(("verification failed.", all_attestations))
            return

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.main_layout = QVBoxLayout()

        self.buttons = []

        self.addButtons()

        self.message = None
        self.return_btn = None

        self.setLayout(self.main_layout)

        self.threadpool = QThreadPool()

    def addButtons(self):
        btn = QPushButton("Stamp")
        btn.setFixedHeight(50)
        btn.clicked.connect(self.stamp)
        self.buttons.append(btn)
        self.main_layout.addWidget(btn)

        btn = QPushButton("Verify")
        btn.setFixedHeight(50)
        btn.clicked.connect(self.verify)
        self.buttons.append(btn)
        self.main_layout.addWidget(btn)

        btn = QPushButton("Batch Verify")
        btn.setFixedHeight(50)
        btn.clicked.connect(self.batch_verify)
        self.buttons.append(btn)
        self.main_layout.addWidget(btn)

    def deleteButtons(self):
        for b in self.buttons:
            b.deleteLater()
            self.main_layout.removeWidget(b)
        self.buttons = []

    def addMessageField(self):
        self.message = QLabel('')
        self.main_layout.addWidget(self.message)

    def addReturnButton(self, callback=None):
        def default_callback():
            self.deleteMessageField()
            self.addButtons()

        if callback is None:
            callback = default_callback

        self.return_btn = QPushButton("OK")
        self.return_btn.setFixedHeight(50)
        self.return_btn.clicked.connect(callback)
        self.main_layout.addWidget(self.return_btn)

    def deleteMessageField(self):
        self.message.deleteLater()
        self.main_layout.removeWidget(self.message)
        self.message = None
        self.return_btn.deleteLater()
        self.main_layout.removeWidget(self.return_btn)
        self.return_btn = None

    def stamp(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', os.path.abspath(os.path.dirname(__file__)))
        if fname[0] == '':
            self.show_message("Error: file not selected")
            return
        if os.path.exists(fname[0] + ".ots"):
            self.show_message("Error: .ots file already exists")
            return
        res = subprocess.run(["ots", "s", fname[0]], capture_output=True)
        if res.returncode == 1:
            self.show_message("Unknown Error Occurred. Error Log: " + res.stderr.decode())
            return
        else:
            self.show_message("Successfully stamped the file")
            return

    def verify(self):
        self.deleteButtons()
        self.addMessageField()

        fname = QFileDialog.getOpenFileName(self, 'Open file', '', "OTS Timestamp Files (*.ots)")

        if fname[0] == '':
            self.show_message("Error: file not selected")
            return

        ots_file = os.path.abspath(fname[0])
        orig_file = ots_file[:-4]

        def handle_success(x):
            unix_time, block_height = x

            LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
            self.show_message("Verification Success!\nThe file existed at %s [Bitcoin Block Height %s]"
                             % (datetime.datetime.fromtimestamp(unix_time, tz=LOCAL_TIMEZONE)
                                .strftime("%Y/%m/%d %p %H:%M:%S %Z"),
                                block_height))
            self.addReturnButton()

        def handle_error(x):
            mes, data = x
            self.show_message("Verification Error: %s\n[Debug Log]\n%s" % (mes, data))
            self.addReturnButton()

        worker = VerifyWorker(orig_file, ots_file)
        worker.signals.success.connect(handle_success)
        worker.signals.error.connect(handle_error)
        self.threadpool.start(worker)

    def batch_verify(self):
        fname = QFileDialog.getOpenFileNames(self, 'Open file', '', "OTS Timestamp Files (*.ots)")
        for f in fname[0]:
            pass

    def show_message(self, message_str):
        self.message.setText(message_str)


qAp = QApplication(sys.argv)
mainwindow = MainWindow()
mainwindow.show()
qAp.exec()
