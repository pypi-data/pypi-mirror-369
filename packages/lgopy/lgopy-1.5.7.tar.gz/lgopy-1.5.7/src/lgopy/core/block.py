from __future__ import annotations

import inspect

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.base import TransformerMixin
import typing
from multimethod import multimethod
from sklearn.exceptions import NotFittedError
from pydantic import BaseModel
from sklearn.utils.validation import check_is_fitted
from .block_mixin import BlockMixin
from .stores import InMemoryArtifactStore, InMemoryMetadataStore
import logging

logger = logging.getLogger(__name__)


class RequestData(BaseModel):
    data: typing.Any | None = None
    args: dict | None = None

def is_step_fitted(block):
    """
    Check if a step is fitted
    :param step:
    :return:
    """
    try:
        check_is_fitted(block)
    except NotFittedError:
        return False
    return True

@multimethod
def apply_transform(x: typing.Any,  block: Block = None):
    """
    it applies the transform to the input array
    :param block: block
    :param x: input data
    :param y: target data (optional)
    :return:
    """
    return block.call(x)


@apply_transform.register(np.ndarray)
def _(x: np.ndarray, block: Block = None):
    """
    it applies the transform to the input array
    :param block: block
    :param x: input data
    :param y: target data (optional)
    :return:
    """
    return block.call(x)


@apply_transform.register(list)
def _(x: list, block: Block = None):
    """
    it applies the transform to the input array
    :param block: block
    :param x: input data
    :param y: target data (optional)
    :return:
    """
    return [block.call(xi) for xi in x]

class Block(BaseEstimator, TransformerMixin, BlockMixin):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.artifacts = kwargs.get("artifacts", InMemoryArtifactStore())
        self.metadata = kwargs.get("metadata", InMemoryMetadataStore())

    def fit(self, X: typing.Any, y: typing.Any = None, **fit_params) -> typing.Any:
        """
        it fits the block to the input data
        :param X:
        :param y:
        :param fit_params:
        :return:
        """
        if 'X' in inspect.signature(self.setup).parameters:
            self.setup(X)
        else:
            self.setup()
        return self

    def transform(self, x: typing.Any, y=None):
        """
        it applies the transform to the input data
        :param x:
        :param X:
        :return:
        """
        return apply_transform(x, self)

    def setup(self, *args, **kwargs):
        """
        it setups the block
        """

    def call(self, *args, **kwargs):
        """
        it applies the transform to the input array
        :param x: input data
        :return:
        """
        raise NotImplementedError()

    # single array transformation
    def __call__(self, x: typing.Any = None):
        """
        it applies the transform to the input array
        :param x: input data
        :return:
        """
        return self.transform(x)
