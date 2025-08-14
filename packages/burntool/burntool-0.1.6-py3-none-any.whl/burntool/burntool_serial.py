import os
import sys
import logging, traceback
import re
import queue
import threading
import time
import signal

import serial
from serial.tools import list_ports
from serial.serialutil import SerialException

LOGGER = logging.getLogger('btl.serial')

PARITY_DICT = {
    'None': serial.PARITY_NONE,
    'Even': serial.PARITY_EVEN,
    'Odd': serial.PARITY_ODD,
    'Mask': serial.PARITY_MARK,
    'Space': serial.PARITY_SPACE
}

def burn_tool_serial_get_ports():
    ports = []
    ports_name = [
        '/dev/ttyACM',
        '/dev/ttyUSB',
        'COM',
        '/dev/cu.'
    ]

    for comport in list_ports.comports():
        port = comport[0]
        for name in ports_name:
            if port.startswith(name):
                ports.append(port)
                break
    ports.sort()

    return ports

class BurnToolSerial(object):
    def __init__(self, on_received=None, on_event=None, auto_reconnect=False):

        self.on_received = on_received
        self.on_event = on_event
        self.auto_reconnect = auto_reconnect

        self.tx_queue = queue.Queue()
        self.rx_queue = queue.Queue()
        self.serial = None
        self.tx_thread = None
        self.rx_thread = None
        self.guard_thread = None

        self.stop_event = threading.Event()
        self.guard_stop_event = threading.Event()
        self.reconnect_event = threading.Event()

        if self.auto_reconnect:
            self.guard_thread = threading.Thread(target=self._guard)
            self.guard_thread.start()

    def set_rts(self, value):
        if self.serial:
            self.serial.rts = value

    def set_baudrate(self, baudrate):
        if self.serial:
            self.serial.baudrate = baudrate
        self.baud = baudrate

    def reset_input_buffer(self):
        if self.serial:
            self.serial.reset_input_buffer()

    def start(self, port, baud, bytesize, stopbits, parity):
        self.port = port
        self.baud = baud
        self.bytesize = bytesize
        self.stopbits = stopbits
        self.parity = parity

        LOGGER.debug(f"serial start, {port}/{baud}/{bytesize}/{stopbits}/{parity}")
        ret = self._connect()
        if not ret:
            if self.auto_reconnect:
                self.reconnect_event.set()
        return ret

    def _connect(self):
        if self.serial:
            self.serial.close()
        try:
            self.serial = serial.Serial(port=self.port,
                                        baudrate=self.baud,
                                        bytesize=self.bytesize,
                                        stopbits=self.stopbits,
                                        parity=PARITY_DICT[self.parity],
                                        write_timeout = 1,
                                        timeout=0.005)

            # Simulate a reset signal through RTS pin
            self.set_rts(False)
            time.sleep(0.01)
            self.serial.reset_input_buffer()
            self.set_rts(True)

            self.tx_queue.queue.clear()
            self.rx_queue.queue.clear()
            self.stop_event.clear()
            self.tx_thread = threading.Thread(target=self._send)
            self.rx_thread = threading.Thread(target=self._recv)
            self.tx_thread.start()
            self.rx_thread.start()
            LOGGER.info(f"connected to the serial port {self.port}")
            self.reconnect_event.clear()  # Reset the reconnect event upon successful connection
            if self.on_event:
                self.on_event(True)
            return True
        except (serial.SerialException, IOError)  as e:
            LOGGER.warning(f"_connect {e} {traceback.format_exc()}")
            if self.on_event:
                self.on_event(False)
        return False

    def stop(self):
        LOGGER.info(f"stop enter")
        self.stop_event.set()
        if self.tx_thread:
            self.tx_thread.join()
        if self.rx_thread:
            self.rx_thread.join()

        self.guard_stop_event.set()
        if self.guard_thread:
            self.guard_thread.join()

        self._close()

        LOGGER.info(f"stop exit")

    def write(self, data):
        self.tx_queue.put(data)

    def read(self):
        return self.rx_queue.get()

    def _close(self):
        if self.serial:
            self.serial.close()
            self.serial = None

    def _error(self):
        self._close()

        self.stop_event.set()

        if self.on_event:
            self.on_event(False)

        if self.auto_reconnect:
            self.reconnect_event.set()

    def _send(self):
        LOGGER.info('tx thread is started')
        while not self.stop_event.is_set():
            try:
                data = self.tx_queue.get(True, 0.1)
                LOGGER.debug(f'serial wr')
                self.serial.write(data)
                LOGGER.debug(f'serial tx:{data.hex()}')
            except queue.Empty:
                continue
            except IOError as e:
                LOGGER.warning(f"{e} {traceback.format_exc()}")
                self._error()

        LOGGER.info('tx thread exits')

    def _recv(self):
        LOGGER.info('rx thread is started')
        while not self.stop_event.is_set():
            try:
                data = self.serial.read(1)
                if data and len(data) > 0:
                    LOGGER.debug(f'{self.port} rx:{data.hex()}')
                    if self.on_received:
                        self.on_received(data)
                    else:
                        self.rx_queue.put(data)
            except IOError as e:
                LOGGER.warning(f"{e} {traceback.format_exc()}")
                self._error()

        LOGGER.info('rx thread exits')

    def _guard(self):
        LOGGER.info('guard thread is started')
        while not self.guard_stop_event.is_set():
            if self.reconnect_event.is_set():
                LOGGER.info('Attempting to reconnect...')
                self._connect()
            time.sleep(1)  # Delay to prevent tight loop in case of repeated failures
        LOGGER.info('guard thread exits')

