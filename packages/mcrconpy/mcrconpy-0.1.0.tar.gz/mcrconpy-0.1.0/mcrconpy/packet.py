# -*- coding: utf-8 -*-
"""
Packet of RCON protocol - TCP

Defined structure for authentication and command sending.

The packet format is the same both for the request and the response.

Packet:
    * 4 bytes    (32 bits) - length (int) of packet in `little-endian`.
    * 4 bytes    (32 bits) - ID of the request (int) in `little-endian`.
    * 4 bytes    (32 bits) - packet type (int) in `little-endian`.
    * N bytes    (N bits)  - body/command of packet in `ascii`.
    * '\x00\x00' (2 bits)  - end of packet.
"""


from typing import Union


class Packet:
    """
    This class is responsible for creating packets to send them in the correct
    format and decoding data from the server.
    """

    SERVERDATA_RESPONSE_VALUE = 0
    SERVERDATA_EXECCOMMAND = 2
    SERVERDATA_AUTH = 3
    END = b"\x00\x00"

    @staticmethod
    def build(
        req_id: int,
        packet_type: int,
        data: str,
    ) -> Union[bytes, None]:
        """
        Prepares the data and creates the packet to send to the server.

        Args
            req_id: int, request ID.
            packet_type: int, packet type.
            data: str, data to be sent to the server.

        Returns
            bytes: packet with the data ready to be sent to the server.
            None: if `req_id` and `packet_type` are not `int` and `data` is
                  not `str`.
        """
        checks = [
            isinstance(req_id, int),
            isinstance(packet_type, int),
            isinstance(data, str),
        ]
        if not all(checks):
            return None

        req_id_bytes = req_id.to_bytes(4, byteorder="little")
        packet_type_bytes = packet_type.to_bytes(4, byteorder="little")
        body_bytes = data.encode("ascii")

        packet = req_id_bytes + packet_type_bytes + body_bytes + Packet.END

        length_packet = len(packet).to_bytes(4, byteorder="little")

        packet = length_packet + packet

        # print(
        #     len(length_packet),
        #     len(req_id_bytes),
        #     len(packet_type_bytes),
        #     len(Packet.END)
        # )

        return packet

    @staticmethod
    def decode(
        data: bytes
    ) -> tuple:
        """
        Decodes the packet data coming from the server.

        Args
            data: bytes of the packet coming from the server.

        Returns
            tuple: length (int), id (int), packet_type (int), body (str). With
                   the decoded data coming from the server. Empty tuple if
                   `data` are not `bytes`.
        """
        if not isinstance(data, bytes):
            return ()

        end_body = len(data) - 2

        body = data[12:end_body]

        length = int.from_bytes(data[0:4], byteorder="little")

        id = int.from_bytes(data[4:8], byteorder="little", signed=True)
        packet_type = int.from_bytes(data[8:12], byteorder="little")

        body = data[12:end_body].decode("ascii")

        # print(length, id, packet_type, body)

        return length, id, packet_type, body
