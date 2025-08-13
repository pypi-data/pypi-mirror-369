from abc import ABC, abstractmethod
from typing import Generic

import zmq

from brij.utils.msg import TInput, TOutput, deserialize, serialize


class BaseServer(Generic[TInput, TOutput], ABC):
    """
    Base server.
    """

    def __init__(self, port: int = 5555) -> None:
        """
        Initializes the server with a ZeroMQ REP socket bound to the specified port.

        Args:
            port (int, optional): The port number to bind the server socket to. Defaults to 5555.
        """
        super().__init__()
        self._context = zmq.Context[zmq.Socket[bytes]]()
        self._socket: zmq.Socket[bytes] = self._context.socket(socket_type=zmq.REP)
        self._socket.bind(f"tcp://*:{port}")

    def _send(self, msg: TOutput) -> None:
        self._socket.send(serialize(msg=msg))  # type: ignore

    def _handle_request(self, msg: bytes) -> None:
        msg_orig: TOutput = deserialize(msg_bytes=msg)  # type: ignore
        response_msg = self.process(msg=msg_orig)  # type: ignore
        self._send(msg=response_msg)

    def run(self) -> None:
        """
        Runs the server on an infinite loop.
        """
        while True:
            msg = self._socket.recv()
            self._handle_request(msg=msg)

    @abstractmethod
    def process(self, msg: TInput) -> TOutput:
        pass

    def close(self) -> None:
        """
        Closes the server and terminates the ZeroMQ context.
        """
        self._socket.close()
        self._context.term()
