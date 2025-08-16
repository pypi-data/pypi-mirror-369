import inspect
from typing import Annotated, get_args, get_origin, Any

from pydantic import Field, create_model
from pydantic.config import ConfigDict


class BlockSerializer:
    """
    Converts block class into a Pydantic model and serializes instances to JSON, dict, and schema.
    """

    @classmethod
    def to_pydantic_model(cls, block_cls):
        """
        Converts a block class into a Pydantic model.
        :param block_cls:
        :return:
        """
        model_fields = {}

        for name, param in inspect.signature(block_cls.__init__).parameters.items():
            if name == "self":
                continue

            annotation = param.annotation
            default = None if param.default is inspect.Parameter.empty else param.default
            description = None

            if annotation is inspect.Parameter.empty:
                if default is None:
                    raise ValueError(f"Parameter '{name}' in class '{block_cls.__name__}' must have a type or default.")
                field_type = type(default)
            else:
                field_type = annotation
                origin = get_origin(annotation)
                args = get_args(annotation)
                if origin is Annotated and len(args) >= 2:
                    field_type = args[0]
                    description = args[1]

            model_fields[name] = (field_type, Field(default, description=description))

        call_annotations = getattr(block_cls.call, "__annotations__", {})
        return_annot = call_annotations.get("return", None)
        if return_annot is None or return_annot is inspect.Parameter.empty:
            raise TypeError(f"The `call` method in '{block_cls.__name__}' must define an explicit return type.")

        output_type_str = return_annot.__name__ if isinstance(return_annot, type) else str(return_annot)

        config = ConfigDict(
            title=block_cls.__name__,
            extra="allow",
            arbitrary_types_allowed=True,
            json_schema_extra={
                "category": getattr(block_cls, "category", None),
                "display_name": getattr(block_cls, "display_name", None),
                "output_type": output_type_str,
            }
        )

        return create_model(
            block_cls.__name__,
            __doc__=getattr(block_cls, "description", None),
            __config__=config,
            **model_fields
        )

    @classmethod
    def to_dict(cls, instance) -> dict:
        """
        Converts a block instance to a dictionary using its Pydantic model.
        :param instance:
        :return:
        """
        model = cls.to_pydantic_model(instance.__class__)
        data = {k: v for k, v in instance.__dict__.items() if k in model.model_fields}
        return model(**data).model_dump(exclude_none=True, exclude_unset=True)

    @classmethod
    def to_json(cls, instance) -> str:
        """
        Converts a block instance to a JSON string using its Pydantic model.
        :param instance:
        :return:
        """
        model = cls.to_pydantic_model(instance.__class__)
        data = {k: v for k, v in instance.__dict__.items() if k in model.model_fields}
        return model(**data).model_dump_json(exclude_none=True)

    @classmethod
    def schema(cls, block_cls) -> dict:
        """
        Generates the JSON schema for a block class using its Pydantic model.
        :param block_cls:
        :return:
        """
        return cls.to_pydantic_model(block_cls).model_json_schema()
