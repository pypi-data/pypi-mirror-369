from typing import Generic

import zmq

from brij.utils.msg import TInput, TOutput, deserialize, serialize


class Client(Generic[TInput, TOutput]):
    """
    Base class for a client.
    """

    def __init__(self, host: str = "localhost", port: int = 5555) -> None:
        """
        Initializes the client base with the specified host and port.
        Args:
            host (str, optional): The hostname or IP address to connect to. Defaults to "localhost".
            port (int, optional): The port number to connect to. Defaults to 5555.
        Initializes:
            self._context (zmq.Context): ZeroMQ context for socket communication.
            self._socket (zmq.Socket): ZeroMQ REQ socket for sending requests.
            self._host (str): Hostname or IP address.
            self._port (int): Port number.
        """

        super().__init__()

        self._context: zmq.Context[zmq.Socket[bytes]] = zmq.Context()
        self._socket: zmq.Socket[bytes] = self._context.socket(socket_type=zmq.REQ)
        self._host, self._port = host, port

    def connect(self) -> bool:
        """
        Attempts to establish a TCP connection to the specified host and port.
        Make sure the brij server is running before calling this function.
        Returns:
            bool: True if the connection is successful, False otherwise.
        """

        try:
            self._socket.connect(addr=f"tcp://{self._host}:{self._port}")
        except Exception:
            return False
        else:
            return True

    def __call__(self, msg: TInput) -> TOutput:
        """
        Sends a serialized message through the socket and returns the deserialized response.
        Args:
            msg (TInput): The input message to be sent.
        Returns:
            TOutput: The deserialized response received from the socket.
        """

        self._socket.send(serialize(msg=msg))  # type: ignore
        return deserialize(msg_bytes=self._socket.recv())  # type: ignore
