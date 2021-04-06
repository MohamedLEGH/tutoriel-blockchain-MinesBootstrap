import atexit
import json
import os

import sys

from PySide2 import QtWidgets
from PySide2.QtCore import Signal, Slot, QObject

import threading
import zmq

#  files imports
from chain import Blockchain
from key import BitcoinAccount
from interface import MyWidget, generate_scroll


# zmq parameters
peers = set()

port_bind = "5000"
if len(sys.argv) > 1:
    port_bind = sys.argv[1]

context = zmq.Context()
socket = context.socket(zmq.PUB)

socket.bind("tcp://*:%s" % port_bind)

topic = ""
ip = "localhost" + ":" + port_bind
socket_sub = context.socket(zmq.SUB)

socket_sub.setsockopt_string(zmq.SUBSCRIBE, topic)

# wallet generation

wallet = BitcoinAccount()
address = wallet.to_address()
file_name = "wallets/" + address + ".json"
wallet.to_file(file_name)


#  blockchain data

difficulty = 3
blockchain = None


class Connection(QObject):
    chain = Signal(Blockchain)
    clean_tx = Signal()
    add_tx = Signal(dict)
    add_peer = Signal(str)
    define_peer = Signal(str)
    remove_peer = Signal(str)
    mining = Signal()


connectionWrite = Connection()


def reading_network():
    global blockchain
    # connectionWrite.chain.emit(blockchain)
    pass


@Slot(dict)
def add_tx_from_layout(tx_data):
    pass


@Slot()
def mine_from_layout():
    global blockchain
    connectionWrite.clean_tx.emit()
    connectionWrite.chain.emit(blockchain)
    pass


@Slot(str)
def add_peer_from_set(peer_address):
    # connectionWrite.define_peer.emit(peer_address)
    pass


@Slot(str)
def remove_peer_from_set(peer_address):
    pass


#  pyside2 parameter

connectionWrite.add_tx.connect(add_tx_from_layout)
connectionWrite.mining.connect(mine_from_layout)
connectionWrite.add_peer.connect(add_peer_from_set)
connectionWrite.remove_peer.connect(remove_peer_from_set)


def clean_file(file_name):
    os.remove(file_name)


if __name__ == "__main__":

    atexit.register(clean_file, file_name)

    #  start listening in the background

    t = threading.Thread(target=reading_network)
    t.daemon = True  #  to close when main loop close
    t.start()

    #  start the main application

    app = QtWidgets.QApplication([])

    widget = MyWidget(
        address,
        ip,
        connectionWrite,
        blockchain,
    )

    scroll = generate_scroll(widget)
    scroll.showMaximized()

    sys.exit(app.exec_())
