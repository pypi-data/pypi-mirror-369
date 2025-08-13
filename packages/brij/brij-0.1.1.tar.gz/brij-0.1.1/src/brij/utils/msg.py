from typing import Mapping, TypeVar

import blosc
import msgpack
import msgpack_numpy as mnp

mnp.patch()


# Generic types to be used in client and server classes
MsgMapping = Mapping[str, object]
TInput = TypeVar("TInput", bound=MsgMapping)
TOutput = TypeVar("TOutput", bound=MsgMapping)


def serialize(msg: MsgMapping) -> bytes:
    """
    Serializes and compresses a message for transmission.

    Args:
        msg (MsgMapping): A mapping from `str` to `object` that is serializable by `msgpack`.
            Supports NumPy arrays and other types via `msgpack_numpy`.

    Returns:
        bytes: The compressed and serialized message bytes.

    Raises:
        msgpack.PackException: If packing fails.
        blosc.Error: If compression fails.
        Exception: For other encoding errors.
    """
    msg_packed = msgpack.packb(msg, default=mnp.encode)
    msg_compressed = blosc.compress(msg_packed)
    return msg_compressed


def deserialize(msg_bytes: bytes) -> dict:
    """
    Deserializes a compressed and packed message.

    Args:
        msg_bytes (bytes): The compressed and serialized message bytes.

    Returns:
        dict: The deserialized Python dictionary obtained after decompression and unpacking.

    Raises:
        blosc.Error: If decompression fails.
        msgpack.ExtraData: If unpacking fails due to extra data.
        Exception: For other decoding errors.
    """
    decompressed = blosc.decompress(msg_bytes)
    msg_decoded = msgpack.unpackb(decompressed, object_hook=mnp.decode)
    return msg_decoded
