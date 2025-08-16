from __future__ import annotations

import functools
import inspect
import itertools
import logging
import typing
from abc import abstractmethod
from pathlib import Path
from typing import Callable

import numpy as np
import pydantic
from pydantic import BaseModel
from pydantic import Field

from .block import Block
from .block_mixin import BlockMixin
from ..utils import Singleton

logger = logging.getLogger(__name__)

def logify_sklearn_estimator(cls):
    """
    This function patch a sklearn estimator to be a block
    :param cls:
    :return:
    """
    return type(cls.__name__, (cls, BlockMixin), {})

class BlockSchema(BaseModel):
    """
    Block registry model
    """
    name: typing.Optional[str] = Field(None, title="The name of the block")
    display_name: str = Field(..., title="The display name of the block")
    category: str = Field(..., title="The category of the block")
    description: str = Field(..., title="The description of the block")
    extras: dict = Field({}, title="The extra attributes of the block")
    passthroughBlock : bool = Field(False, title="The block is a passthrough block")

    class Config:
        extra = "allow"

def register_block(
    registry: dict,
    block_class: typing.Type,
    **kwargs,
):
    """
    Register the class attributes.
    :param registry:
    :param block_class:
    :param kwargs:
    :return:
    """
    try:
        block_info = BlockSchema(**kwargs)
    except pydantic.ValidationError as e:
        logger.error(f"Error registering block {block_class.__name__}, {e}")
        raise e
    if hasattr(block_class, "__wrapped__"):
        raise Exception("Cannot register a class that which has been wrapped")

    block_name = block_info.name or block_class.__name__
    registry[block_name] = block_class
    for attr_name, attr_val in block_info.dict().items():
        if not hasattr(block_class, attr_name):
            # add attribute to a class
            setattr(block_class, attr_name, attr_val)



class BlockHub:
    """ Internal registry for available data exporter classes """
    registry: typing.Dict[str, typing.Type] = {}

    @classmethod
    def register(
            cls,
            block_cls: typing.Optional[typing.Union[typing.Type, Callable]] = None,
            **kwargs,
    ):
        """
        Register a DataExporter class for a given extension.
        :param block_cls: the class to register
        :param kwargs: the block class attributes
        :return:
        """
        if inspect.isclass(block_cls):
            if not issubclass(block_cls, Block):
                block_cls = logify_sklearn_estimator(block_cls)
            register_block(cls.registry, block_cls, **kwargs)  # type: ignore
        else:

            @functools.wraps(cls.register)
            def wrapper(block_cls: Block) -> Callable:
                """
                Wrapper function to register a DataExporter class for a given extension.
                :param block_cls:  the class to register
                :return:
                """
                register_block(cls.registry, block_cls, **kwargs)  # type: ignore
                return block_cls

            return wrapper

    @classmethod
    def get_block(cls, key: str) -> Block:
        """
        Get a block instance from the registry.
        :param key: The name of the block
        :return: The block instance
        """
        block_cls = cls.registry.get(key)
        if block_cls is None:
            raise NotImplementedError(f"Block with name {key} not found")
        return block_cls()

    @classmethod
    def create(cls, key: typing.Union[str, typing.Type], **kwargs) -> Block:
        """
        Create a block instance.
        :param key: The name or type of the block
        :param kwargs: The keyword arguments to pass to the block constructor
        :return: The created block instance
        """
        if isinstance(key, str):
            block_cls = cls.registry.get(key)
            if block_cls is None:
                raise NotImplementedError(f"Block with name {key} not found")
        elif isinstance(key, type):
            block_name = getattr(key, "name") or key.__name__
            block_cls = cls.registry.get(block_name)
        else:
            raise NotImplementedError(f"Invalid key argument {key}")

        if block_cls is None:
            raise NotImplementedError(f"Block with key {key} not found")

        return block_cls(**kwargs)

    @classmethod
    def list_blocks(cls) -> typing.List[str]:
        """
        List the available blocks.
        :return: The list of block names
        """
        return list(cls.registry.keys())

    @classmethod
    def list_categories(cls) -> typing.List[str]:
        """
        List the available block categories.
        :return: The list of block categories
        """
        return list(set([getattr(block, "category") for block in cls.registry.values()]))

    @classmethod
    def blocks_json(cls, groups_by :str = None) -> typing.Union[typing.List[dict], dict]:
        """
        List available blocks in json format.
        :return:
        """
        blocks = [
            block.schema()
            for key, block in cls.registry.items()
        ]

        # Step 2: If groups_by is specified, group and sort blocks by that key
        if groups_by:
            blocks.sort(key=lambda x: x[groups_by])  # Sort the blocks once
            blocks = {key: list(group) for key, group in itertools.groupby(blocks, key=lambda x: x[groups_by])}

        # Return the final blocks (could be a dict or list based on grouping)
        return blocks


class DataExporterFactory:
    """ Factory class for DataExporter instances """
    registry = {}
    """ Internal registry for available data exporter classes """

    @classmethod
    def register(cls, *exts) -> Callable:
        """
        Register a DataExporter class for the given extensions.
        :param exts:
        :return:
        """

        def wrapper(wrapped_class: DataExporter) -> Callable:
            """
            Register a DataExporter class for the given extensions.
            """
            for ext in exts:
                if ext in cls.registry:
                    logger.warning(
                        "Data Exporter Class %s already registered. it will be override",
                        ext,
                    )
                cls.registry[ext] = wrapped_class
            return wrapped_class

        return wrapper

    @classmethod
    def build(cls, ext: str, **kwargs) -> DataExporter:
        """
        Build a DataExporter instance for the given extension.
        ext: str  - The extension of the file to export.
        kwargs: dict - The keyword arguments to pass to the DataExporter constructor.
        :rtype: DataExporter - The DataExporter instance.
        """
        ext = ext.lower()
        if ext not in cls.registry:
            raise NotImplementedError(f"{ext} not supported")
        exporter_class = cls.registry[ext]
        exporter = exporter_class(**kwargs)
        logger.info(
            f"using {exporter_class.__name__} to export file with {ext} extension"
        )
        return exporter


class DataExporter(metaclass=Singleton):
    """ " Abstract class for data exporters"""

    def __init__(self, **kwargs):
        ...

    @abstractmethod
    def __call__(
            self, data_arr: np.ndarray, file_path: typing.Union[str, Path], **kwargs
    ):
        pass


class DataReaderFactory:
    registry = {}
    """ Internal registry for available data readers classes """

    @classmethod
    def register(cls, *exts) -> Callable:
        def wrapper(wrapped_class: DataReader) -> Callable:
            """
            Register a DataReader class for the given extensions.
            :param wrapped_class:
            :return:
            """
            for ext in exts:
                if ext in cls.registry:
                    logger.warning(
                        "Data Reader Class %s already registered. it will be override",
                        ext,
                    )
                cls.registry[ext] = wrapped_class
            return wrapped_class

        return wrapper

    @classmethod
    def build(cls, ext: str, **kwargs) -> DataReader:
        """Build a DataReader instance for the given extension.
        ext: str  - The extension of the file to read.
        kwargs: dict - The keyword arguments to pass to the DataReader constructor.
        :rtype: DataReader - The DataReader instance.
        """
        ext = ext.lower()
        if ext not in cls.registry:
            raise NotImplementedError(f"{ext} not supported")
        reader_class = cls.registry[ext]
        logger.debug(f"using {reader_class.__name__} to read file with {ext} extension")
        reader = reader_class(**kwargs)
        return reader


class DataReader(metaclass=Singleton):
    """Abstract class for data reader"""

    def __init__(self, **kwargs):
        ...

    @abstractmethod
    def __call__(self, file_path: typing.Union[str, Path]) -> xr.DataArray:
        """Read the data from the given file path and return a DataArray.
        file_path: str - The path to the file to read.
        :rtype: xr.DataArray - The data array.
        """
        ...





