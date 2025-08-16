import json
import logging
import sys
import traceback
import typing
from collections import defaultdict
from pathlib import Path

from sklearn.base import BaseEstimator, TransformerMixin

from . import Block
from .stores import InMemoryMetadataStore, InMemoryArtifactStore
import joblib
from sklearn.pipeline import Pipeline as SklearnPipeline


logger = logging.getLogger(__name__)

class TransformLogger(BaseEstimator, TransformerMixin):
    """
    A logger transform to run callbacks
    """

    def __init__(self, step_name, callbacks):
        super().__init__()
        self.step_name = step_name
        self.callbacks = callbacks

    def fit(self, X, y=None, **fit_params):
        return self


    def transform(self, X):
        """
        Log the step
        :param X:
        :return:
        """
        for callback in self.callbacks:
            callback.on_step(self.step_name, X)
        return X


class LgoPipeline(SklearnPipeline):
    """
    A pipeline to run lego blocks
    """

    def __init__(
        self, steps, name="default", memory=None, verbose=False, callbacks=None, metadata=None, artifacts=None
    ):
        self.name = name
        self.callbacks = callbacks
        self.metadata = metadata
        self.artifacts = artifacts

        if callbacks:
            # add intermediate steps
            new_steps = []
            for name, step in steps:
                new_steps.append((name, step))
                if isinstance(step, Block):
                    new_steps.append(
                        (f"{name}_logger", TransformLogger(name, callbacks))
                    )
            steps = new_steps

        for step_name, step in steps:
            if hasattr(step, "metadata"):
                step.metadata = metadata
            if hasattr(step, "artifacts"):
                step.artifacts = artifacts

        super(LgoPipeline, self).__init__(steps, memory=memory, verbose=verbose)



    def fit_transform(self, X, y=None, **fit_params):
        """
        Fit to data, then transform it.

        Args:
            X (array-like): Input data.
            y (array-like, optional): Target values.
            **fit_params: Additional fit parameters.

        Returns:
            array-like: Transformed data.

        Raises:
            Exception: Propagates any exceptions that occur during fitting and transforming.
        """
        return super().fit_transform(X, y, **fit_params)

    def fit(self, X, y=None, **params):
        """
        Fit the pipeline
        :param X:
        :param y:
        :param params:
        :return:
        """
        return super().fit(X, y, **params)

    def save(self, file: typing.Union[str, Path]):
        """
        Save the pipeline to a file
        :param file:
        :return:
        """
        json_str = self.to_json(indent=4)
        with open(file, "w") as f:
            f.write(json_str)


    def run_pipeline(self, X=None, y=None, **fit_params):
        """
        Run the pipeline
        :param X:
        :param y:
        :param fit_params:
        :return:
        """
        try:
            # run callbacks if any
            if self.callbacks:
                for cb in self.callbacks:
                    cb.on_start()

            # run the pipeline
            if all([hasattr(step, "fit_transform") for step_name, step in self.steps]):
                results = self.fit_transform(X, y, **fit_params)
            else:
                results = self.fit(X, y, **fit_params) if X is not None else X

            # run callbacks if any
            if self.callbacks:
                for cb in self.callbacks:
                    cb.on_end()
        except Exception:
            exc_type, exc_value, _ = sys.exc_info()
            exc_message = traceback.format_exception_only(exc_type, exc_value)[0].strip()
            logger.exception(f"Error in running pipeline: {exc_message}")
            raise
        return results


    def __call__(self, X=None, y=None, **fit_params):
        # run callbacks if any
        return self.run_pipeline(X, y, **fit_params)

    @classmethod
    def from_steps(cls, *steps, memory=None, verbose=False, callbacks=None,  **kwargs):
        """
        Create a pipeline from steps
        :param steps:
        :param memory:
        :param verbose:
        :param callbacks:
        :return:
        """
        return make_pipeline(
            *steps, memory=memory, verbose=verbose, callbacks=callbacks, **kwargs
        )
    @classmethod
    def from_list(cls, steps: typing.List[typing.Dict], **kwargs):
        """
        Create a pipeline from a dictionary
        :param steps:
        :return:
        """
        from lgopy.core import BlockHub

        for step in steps:
            if step["block"] not in BlockHub.registry:
                raise ValueError(f"Block {step['block']} is not registered")
        blocks = [
            BlockHub.registry[step["block"]](**step["args"]) for step in steps
        ]
        return make_pipeline(*blocks, **kwargs)

    @classmethod
    def from_json(cls, json_str: str, **kwargs):
        """
        Create a pipeline from json
        :param json_str:
        :return:
        """
        steps = json.loads(json_str)
        # check if blocks are registered
        return cls.from_list(steps, **kwargs)

    @classmethod
    def from_file(cls, file_name: typing.Union[str, Path], **kwargs):
        """
        Create a pipeline from a file
        :param file_name:
        :return:
        """
        with open(file_name, "r") as f:
            json_str = f.read()
        return cls.from_json(json_str, **kwargs)

    def to_json(self, **kwargs):
        """
        Convert the pipeline to json
        :return:
        """
        return json.dumps([
                {"block": getattr(step.__class__, "name", None) or str(step),
                 "args": step.to_dict()}
                for step_name, step in self.steps
                if not isinstance(step, TransformLogger)
            ],
            **kwargs,
        )


    def serve(self, *args, **kwargs):
        """
        it serves the block
        """
        raise NotImplementedError()


# copy from sklearn api
def _name_estimators(estimators):
    """
    Generate names for estimators.
    :param estimators:  list of estimators
    :return:
    """

    names = [
        estimator if isinstance(estimator, str) else type(estimator).__name__.lower()
        for estimator in estimators
    ]
    namecount = defaultdict(int)
    for est, name in zip(estimators, names):
        namecount[name] += 1

    for k, v in list(namecount.items()):
        if v == 1:
            del namecount[k]

    for i in reversed(range(len(estimators))):
        name = names[i]
        if name in namecount:
            names[i] += "-%d" % namecount[name]
            namecount[name] -= 1

    return list(zip(names, estimators))


def make_pipeline(*steps, memory=None, verbose=False, callbacks=None, **kwargs):
    """
    Construct a Pipeline from the given estimators.
    :param steps:  list of estimators
    :param memory:  cachedir or Memory object
    :param verbose:  boolean
    :param callbacks:  list of callbacks
    :return: pipeline
    """
    metadata = kwargs.pop("metadata", InMemoryMetadataStore())
    artifacts = kwargs.pop("artifacts", InMemoryArtifactStore())

    return LgoPipeline(
        _name_estimators(steps),
        memory=memory,
        verbose=verbose,
        callbacks=callbacks,
        metadata=metadata,
        artifacts=artifacts,
        **kwargs,
    )


def load_pipeline(file_name: typing.Union[str, Path]):
    """
    Load a pipeline from a file
    :param file_name:
    :return:
    """
    return joblib.load(file_name)
