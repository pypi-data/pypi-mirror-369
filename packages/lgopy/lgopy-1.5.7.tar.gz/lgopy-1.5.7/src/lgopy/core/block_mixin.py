import logging

from lgopy.core.block_serializer import BlockSerializer
from lgopy.core.block_builder import BlockBuilder

logger = logging.getLogger(__name__)

class BlockMixin:
    """
    Block mixin class
    """

    def to_dict(self):
        return BlockSerializer.to_dict(self)

    def to_json(self):
        return BlockSerializer.to_json(self)

    @classmethod
    def schema(cls) -> dict:
        return BlockSerializer.schema(cls)

    @classmethod
    def build(cls):
        return BlockBuilder.build(cls)




