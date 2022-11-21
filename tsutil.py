import base64
import datetime
import struct
import sys

import bitcoin.rpc
import requests
from PyQt6.QtCore import QUrl, QTimer, QRunnable, pyqtSlot, QObject, pyqtSignal, QThreadPool, Qt, QSize
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QFileDialog, QPushButton, QVBoxLayout, QTableWidget, \
    QTableWidgetItem, QHeaderView
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

class StampWorker(QRunnable):
    def __init__(self, filename):
        super(StampWorker, self).__init__()
        self.filename = filename
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        res = subprocess.run(["ots", "s", self.filename], capture_output=True)
        return_data = (res.returncode, res.stderr, res.stdout)
        if res.returncode == 1:
            self.signals.error.emit(return_data)
        elif res.returncode == 0:
            self.signals.success.emit(return_data)
        else:
            self.signals.error.emit(return_data)

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
            self.signals.error.emit(("pending confirmations", list(timestamp.all_attestations())))
            return

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.main_layout = QVBoxLayout()

        self.buttons = []

        self.add_buttons()

        self.message: QLabel = None
        self.table: QTableWidget = None
        self.return_btn: QPushButton = None

        self.setLayout(self.main_layout)

        self.threadpool = QThreadPool()

    def add_buttons(self):
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

    def delete_buttons(self):
        for b in self.buttons:
            b.deleteLater()
            self.main_layout.removeWidget(b)
        self.buttons = []

    def add_message_field(self):
        self.message = QLabel('')
        self.main_layout.addWidget(self.message)

    def add_table_field(self, rows, columns):
        self.table = QTableWidget(rows, columns)
        self.main_layout.addWidget(self.table)

    def add_return_button(self, callback=None):
        def default_callback():
            self.delete_return_field()
            self.add_buttons()

        if callback is None:
            callback = default_callback

        self.return_btn = QPushButton("OK")
        self.return_btn.setFixedHeight(50)
        self.return_btn.clicked.connect(callback)
        self.main_layout.addWidget(self.return_btn)

    def delete_return_field(self):
        if self.message is not None:
            self.message.deleteLater()
            self.main_layout.removeWidget(self.message)
            self.message = None

        if self.table is not None:
            self.table.deleteLater()
            self.main_layout.removeWidget(self.table)
            self.table = None

        self.return_btn.deleteLater()
        self.main_layout.removeWidget(self.return_btn)
        self.return_btn = None

    def stamp(self):
        self.delete_buttons()
        self.add_message_field()

        fname = QFileDialog.getOpenFileName(self, 'Open file', os.path.abspath(os.path.dirname(__file__)))
        if fname[0] == '':
            self.show_message("Error: file not selected")
            return
        if os.path.exists(fname[0] + ".ots"):
            self.show_message("Error: .ots file already exists")
            return

        def handle_success(x):
            code, err, out = x
            self.show_message("Successfully stamped the file!\n[Details]\nCode %s\nstderr %s\nstdout %s" % (code, err, out))

        def handle_error(x):
            code, err, out = x
            self.show_message("Error!\n[Details]\nCode %s\nstderr %s\nstdout %s" % (code, err, out))

        worker = StampWorker(fname[0])
        worker.signals.success.connect(handle_success)
        worker.signals.error.connect(handle_error)
        self.threadpool.start(worker)

    def verify(self):
        self.delete_buttons()
        self.add_message_field()

        fname = QFileDialog.getOpenFileName(self, 'Open file', '', "OTS Timestamp Files (*.ots)")

        if fname[0] == '':
            self.show_message("Error: file not selected")
            return

        ots_file = os.path.abspath(fname[0])
        orig_file = ots_file[:-4]

        def handle_success(x):
            unix_time, block_height = x

            local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
            self.show_message("Verification Success!\nThe file existed at %s [Bitcoin Block Height %s]"
                             % (datetime.datetime.fromtimestamp(unix_time, tz=local_timezone)
                                .strftime("%Y/%m/%d %p %H:%M:%S %Z"),
                                block_height))

        def handle_error(x):
            mes, data = x
            self.show_message("Verification Error: %s\n[Debug Log]\n%s" % (mes, data))

        worker = VerifyWorker(orig_file, ots_file)
        worker.signals.success.connect(handle_success)
        worker.signals.error.connect(handle_error)
        self.threadpool.start(worker)

    def batch_verify(self):
        self.delete_buttons()
        self.add_table_field(0, 6)

        files = list(QFileDialog.getOpenFileNames(self, 'Open file', '', "OTS Timestamp Files (*.ots)")[0])

        if len(files) == 0:
            self.add_return_button()
            return

        def create_item(x, sizehint=None):
            it = QTableWidgetItem(x)

            # Enabled and Selectable. See https://github.com/qt/qtbase/blob/33cf9d32da0ba78ec90df063a3dda91ea793634d/src/corelib/global/qnamespace.h
            it.setFlags(Qt.ItemFlag(1 | 32))

            if sizehint is not None:
                it.setSizeHint(sizehint)

            return it

        self.table.setHorizontalHeaderItem(0, create_item("File"))
        self.table.setHorizontalHeaderItem(1, create_item("Status"))
        self.table.setHorizontalHeaderItem(2, create_item("Date"))
        self.table.setHorizontalHeaderItem(3, create_item("Block Number"))
        self.table.setHorizontalHeaderItem(4, create_item("Error"))
        self.table.setHorizontalHeaderItem(5, create_item("Error Detail"))

        header_view: QHeaderView = self.table.horizontalHeader()
        header_view.setSectionResizeMode(QHeaderView.ResizeMode(3))
        header_view.setSectionResizeMode(5, QHeaderView.ResizeMode(0))

        def advance(data, filename, is_success):
            if data is not None:
                timestamp_formatted = ""

                if is_success:
                    local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
                    timestamp_formatted = datetime.datetime.fromtimestamp(data[0], tz=local_timezone).strftime("%Y/%m/%d %p %H:%M:%S %Z")

                self.table.setRowCount(self.table.rowCount() + 1)
                self.table.setItem(self.table.rowCount() - 1, 0, create_item(filename))
                self.table.setItem(self.table.rowCount() - 1, 1, create_item("OK" if is_success else "ERROR"))
                self.table.setItem(self.table.rowCount() - 1, 2, create_item(timestamp_formatted))
                self.table.setItem(self.table.rowCount() - 1, 3, create_item(str(data[1]) if is_success else ""))
                self.table.setItem(self.table.rowCount() - 1, 4, create_item("" if is_success else data[0]))
                self.table.setItem(self.table.rowCount() - 1, 5, create_item("" if is_success else str(data[1])))
                self.table.setVerticalHeaderItem(self.table.rowCount() - 1, create_item("✅" if is_success else "❌"))

            if len(files) == 0:
                self.add_return_button()
                return

            ots_file = files.pop(0)
            orig_file = ots_file[:-4]
            worker = VerifyWorker(orig_file, ots_file)
            worker.signals.success.connect(lambda x: advance(x, worker.orig_file, True))
            worker.signals.error.connect(lambda x: advance(x, worker.orig_file, False))
            self.threadpool.start(worker)

        advance(None, None, None)

    def show_message(self, message_str):
        self.message.setText(message_str)
        self.add_return_button()

qAp = QApplication(sys.argv)
mainwindow = MainWindow()
mainwindow.show()
qAp.exec()
