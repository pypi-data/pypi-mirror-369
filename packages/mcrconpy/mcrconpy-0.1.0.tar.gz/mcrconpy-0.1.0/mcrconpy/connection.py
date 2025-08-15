# -*- coding: utf-8 -*-
"""
"""

import socket


class Connection:

    def __init__(
        self,
    ) -> None:
        """
        Set up the socket for connection.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def is_connected(
        self,
    ) -> bool:
        """
        Check if the connection to the server is active.
        """
        try:
            self.send(b'')
            return True
        except socket.error as e:
            return False

    def connect(
        self,
        address: str,
        port: int
    ) -> None:
        """
        Connect to the server with the specified address and port.

        Args
            address: str, address of the server.
            port: int, port used by the server.
        """
        self.socket.connect((address, port))

    def send(
        self,
        data: bytes
    ) -> bytes:
        """
        Sends data to the server.

        Args
            data: bytes, data to send to the server.

        Returns
            bytes: response from the server.
        """
        if self.socket is not None:
            rawdata = self.socket.send(data)
            return rawdata

    def read(
        self,
        length: int = 1024
    ) -> bytes:
        """
        Reads data from the server.

        Args
            length: int, size of buffer to read.

        Returns
            bytes: data from the server.
        """
        data = b''
        while True:
            response = self.socket.recv(length)
            data += response
            if response[-1] == 0:
                break
        return data

    def close(
        self,
    ) -> None:
        """
        Closes the current socket, whether connected to the server or not.
        """
        if self.socket is not None:
            self.socket.close()
            self.socket = None
