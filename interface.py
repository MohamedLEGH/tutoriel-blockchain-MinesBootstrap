import json

from functools import partial

from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Qt, Slot

from chain import Blockchain


class Chain_Dialog(QtWidgets.QDialog):
    def __init__(self, blockchain, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chain")

        self.setWindowFlags(
            self.windowFlags() | QtCore.Qt.WindowType.WindowMaximizeButtonHint
        )

        chain_layout = QtWidgets.QFormLayout()

        chain_label = QtWidgets.QLabel(
            json.dumps(blockchain.to_dict(), indent=4, sort_keys=True)
        )
        chain_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)

        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidget(chain_label)
        self.scrollArea.setWidgetResizable(True)

        chain_layout.addWidget(self.scrollArea)
        self.setLayout(chain_layout)


class Tx_Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Send Transaction")

        self.buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        self.buttonBox.accepted.connect(self.working_click)
        self.buttonBox.rejected.connect(self.reject)

        tx_layout = QtWidgets.QFormLayout()

        self.tx_address = QtWidgets.QLineEdit()

        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        self.tx_address.textChanged.connect(self.allowButton)

        self.tx_amount = QtWidgets.QSpinBox()
        self.tx_amount.setRange(0, 999999999)

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        tx_layout.addRow("Adress of receiver: ", self.tx_address)
        tx_layout.addRow("Amount to send: ", self.tx_amount)
        tx_layout.addWidget(self.buttonBox)
        self.setLayout(tx_layout)

    def allowButton(self):
        if len(self.tx_address.text()) > 0:
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(
                True
            )
        elif self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).isEnabled():
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(
                False
            )

    def get_values(self):
        if self.tx_address and self.tx_amount:
            return {
                "address": self.tx_address.text(),
                "amount": int(self.tx_amount.text()),
            }
        else:
            return False

    def working_click(self):
        self.accept()


class Peer_Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add peer")

        self.buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        self.buttonBox.accepted.connect(self.working_click)
        self.buttonBox.rejected.connect(self.reject)

        tx_layout = QtWidgets.QFormLayout()

        self.peer_address = QtWidgets.QLineEdit()

        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        self.peer_address.textChanged.connect(self.allowButton)

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        tx_layout.addRow("Adress of receiver: ", self.peer_address)

        tx_layout.addWidget(self.buttonBox)
        self.setLayout(tx_layout)

    def allowButton(self):
        if len(self.peer_address.text()) > 0:
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(
                True
            )
        elif self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).isEnabled():
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(
                False
            )

    def get_peer(self):
        return self.peer_address.text()

    def working_click(self):
        self.accept()


class MyWidget(QtWidgets.QWidget):
    def __init__(
        self,
        address,
        ip,
        connectionWrite,
        blockchain,
    ):
        super().__init__()

        self.text_address = QtWidgets.QLabel("My address: ")
        self.address_value = QtWidgets.QLabel(address)
        self.address_value.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByMouse
        )
        self.text_ip = QtWidgets.QLabel("My IP: ")
        self.ip_value = QtWidgets.QLabel(ip)
        self.ip_value.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        self.button_tx = QtWidgets.QPushButton("Send transaction")
        self.button_chain = QtWidgets.QPushButton("Chain")
        self.button_mine = QtWidgets.QPushButton("Mine")
        self.button_add_peer = QtWidgets.QPushButton("Add peer")

        self.text_peerlist = QtWidgets.QLabel("Peers: ")

        self.text_pending = QtWidgets.QLabel("Pending tx: ")

        self.text_block = QtWidgets.QLabel("Last block: ")

        self.layout = QtWidgets.QVBoxLayout()

        # layout for the address
        layout_address = QtWidgets.QHBoxLayout()
        layout_address.addWidget(self.text_address)
        layout_address.addWidget(self.address_value)
        self.layout.addLayout(layout_address)

        # layout for the ip
        layout_ip = QtWidgets.QHBoxLayout()
        layout_ip.addWidget(self.text_ip)
        layout_ip.addWidget(self.ip_value)
        self.layout.addLayout(layout_ip)

        # layout for the buttons

        layout_buttons = QtWidgets.QHBoxLayout()
        layout_buttons.addWidget(self.button_tx)
        layout_buttons.addWidget(self.button_chain)
        layout_buttons.addWidget(self.button_mine)
        layout_buttons.addWidget(self.button_add_peer)
        self.layout.addLayout(layout_buttons)

        self.layout.addWidget(self.text_peerlist)
        self.peers_layout = QtWidgets.QFormLayout()
        self.tx_layout = QtWidgets.QFormLayout()
        self.block_data = QtWidgets.QLabel()
        self.block_data.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByMouse
        )

        self.layout.addLayout(self.peers_layout)
        self.layout.addWidget(self.text_pending)
        self.layout.addLayout(self.tx_layout)
        self.layout.addWidget(self.text_block)
        self.layout.addWidget(self.block_data)

        self.setLayout(self.layout)

        self.button_tx.clicked.connect(self.add_tx_from_layout)
        self.button_chain.clicked.connect(self.print_chain)
        self.button_mine.clicked.connect(self.mine_click)
        self.button_add_peer.clicked.connect(self.add_peer)

        connectionWrite.chain.connect(self.get_chain)
        connectionWrite.clean_tx.connect(self.clean_tx_layout)
        connectionWrite.define_peer.connect(self.define_peer)

        self.address = address
        self.ip = ip
        self.connection = connectionWrite
        self.blockchain = blockchain

    def print_chain(self):
        if self.blockchain:
            chain_window = Chain_Dialog(self.blockchain)
            chain_window.exec_()

        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText(
                "No chain: you need to mine the first block or get the chain "
                "from another peer before seeing the chain"
            )
            msg.setWindowTitle("No blockchain")

            msg.exec_()

    def mine_click(self):
        self.connection.mining.emit()

    @Slot(Blockchain)
    def get_chain(self, blockchain):
        self.block_data.setText(str(blockchain.chain[-1]))
        self.blockchain = blockchain

    @Slot()
    def clean_tx_layout(self):
        for row in range(self.tx_layout.rowCount()):
            self.tx_layout.removeRow(0)

    def add_tx_from_layout(self):
        # open the tx dialog window
        if self.blockchain:
            tx_window = Tx_Dialog()
            ret_val = tx_window.exec_()
            if ret_val == 1 and self.blockchain is not None:
                tx_data = tx_window.get_values()
                self.define_tx(tx_data)
                # also need to add tx to the list of pending tx
                self.connection.add_tx.emit(tx_data)

        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText(
                "No chain: you need to mine the first block or get the chain "
                "from another peer before sending transactions"
            )
            msg.setWindowTitle("No blockchain")

            msg.exec_()

    def define_tx(self, elem):
        text = (
            "Tx: { address : "
            + elem["address"]
            + ", amount : "
            + str(elem["amount"])
            + " }"
        )
        text_tx = QtWidgets.QLabel(text)
        text_tx.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.tx_layout.addRow(text_tx)

    @Slot(str)
    def define_peer(self, peer_address):
        text_peer = QtWidgets.QLabel(peer_address)
        text_peer.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        button_peer = QtWidgets.QPushButton("X")
        button_peer.setFixedSize(20, 20)
        button_peer.clicked.connect(
            partial(self.remove_peer, peer_address, text_peer, button_peer)
        )
        self.peers_layout.addRow(text_peer, button_peer)

    def add_peer(self):
        peer_window = Peer_Dialog()
        ret_val = peer_window.exec_()
        if ret_val == 1:
            peer_address = peer_window.get_peer()
            self.connection.add_peer.emit(peer_address)

    @Slot(str, str, QtWidgets.QPushButton)
    def remove_peer(self, peer_address, text_peer, button_peer):
        self.connection.remove_peer.emit(peer_address)
        button_peer.deleteLater()
        text_peer.deleteLater()


def generate_scroll(widget):
    scrollArea = QtWidgets.QScrollArea()

    scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    scrollArea.setWidgetResizable(True)

    scrollArea.resize(800, 600)
    scrollArea.setWindowTitle("Blockchain")
    scrollArea.setWidget(widget)
    return scrollArea
