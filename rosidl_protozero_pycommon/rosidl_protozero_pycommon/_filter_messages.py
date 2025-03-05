from typing import TYPE_CHECKING
from typing import List
from typing import Tuple

if TYPE_CHECKING:
    from google.protobuf.descriptor_pb2 import DescriptorProto


# TODO
def filter_messages(
        messages: List['DescriptorProto'],
        message_names: List[str] = None,
        strict: bool = False,
) -> List[None]:
    if message_names is not None:
        messages = [
            m
            for m in messages
            if m.name in message_names
        ]

    return messages
