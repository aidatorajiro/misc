import datetime
import struct
import sys

import bitcoin.rpc
import requests
from PyQt6.QtCore import QUrl, QTimer
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


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.vbox = QVBoxLayout()

        btn = QPushButton("Stamp")
        btn.setFixedHeight(50)
        btn.clicked.connect(self.stamp)
        self.vbox.addWidget(btn)

        btn = QPushButton("Verify")
        btn.setFixedHeight(50)
        btn.clicked.connect(self.verify)
        self.vbox.addWidget(btn)

        btn = QPushButton("Batch Verify")
        btn.setFixedHeight(50)
        btn.clicked.connect(self.batch_verify)
        self.vbox.addWidget(btn)

        self.setLayout(self.vbox)

    def stamp(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', os.path.abspath(os.path.dirname(__file__)))
        if os.path.exists(fname[0] + ".ots"):
            self.showMessage("Error: .ots file already exists")
            return
        res = subprocess.run(["ots", "s", fname[0]], capture_output=True)
        if res.returncode == 1:
            self.showMessage("Unknown Error Occurred. Error Log: " + res.stderr.decode())
        else:
            self.showMessage("Successfully stamped the file")

    def verify(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', os.path.abspath(os.path.dirname(__file__)))

        orig_file = os.path.abspath(fname[0])
        ots_file = orig_file + ".ots"

        if not os.path.exists(ots_file):
            self.showMessage("Error: .ots file doesn't exist")
            return

        with open(ots_file, 'rb') as ots_fd:
            ctx = StreamDeserializationContext(ots_fd)
            try:
                detached_timestamp = DetachedTimestampFile.deserialize(ctx)
            except BadMagicError:
                self.showMessage("Error: not an ots file")
            except DeserializationError:
                self.showMessage("Error: ots file deserialization error")

            with open(orig_file, 'rb') as orig_fd:
                orig_digest = detached_timestamp.file_hash_op.hash_fd(orig_fd)

            if orig_digest != detached_timestamp.file_digest:
                self.showMessage("Error: digest mismatch")

        timestamp = detached_timestamp.timestamp

        args = otsclient.args.parse_ots_args(["v", ots_file])

        args.calendar_urls = []
        upgrade_timestamp(timestamp, args)

        def attestation_key(item):
            (msg, attestation) = item
            if attestation.__class__ == BitcoinBlockHeaderAttestation:
                return attestation.height
            else:
                return 2 ** 32 - 1

        good = False
        unix_time = None
        block_height = None
        proxy = None

        try:
            proxy = bitcoin.rpc.Proxy()
        except:
            print("Connecting Local Bitcoin Client Failed. Use blockchain.info API instead")

        for merkle_root, attestation in sorted(timestamp.all_attestations(), key=attestation_key):
            if attestation.__class__ == PendingAttestation:
                pass
            elif attestation.__class__ == BitcoinBlockHeaderAttestation:
                if proxy is not None:
                    header = proxy.getblockheader(proxy.getblockhash(attestation.height))
                    if merkle_root == header.hashMerkleRoot:
                        good = True
                        unix_time = header.nTime
                        block_height = attestation.height
                        break
                else:
                    url = "https://blockchain.info/rawblock/" + str(attestation.height)
                    block = requests.get(url).json()
                    if "".join(map(lambda x: x.hex(), reversed(struct.unpack("32c", merkle_root)))) == block['mrkl_root']:
                        good = True
                        unix_time = block['time']
                        block_height = attestation.height
                        break

        if good:
            LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

            self.showMessage("Verification Success! The file existed at %s [Bitcoin Block Height %s]"
                             % (datetime.datetime.fromtimestamp(unix_time, tz=LOCAL_TIMEZONE)
                                .strftime("%Y/%m/%d %p %H:%M:%S %Z"),
                                block_height))
        else:
            self.showMessage("Error: verification failed")

    def batch_verify(self):
        pass

    def showMessage(self, message_str):
        diag = QDialog(self)
        diag.setWindowTitle("Result")
        layout = QVBoxLayout()
        message = QLabel(message_str)
        layout.addWidget(message)
        diag.setLayout(layout)
        diag.exec()


qAp = QApplication(sys.argv)
mainwindow = MainWindow()
mainwindow.show()
qAp.exec()
