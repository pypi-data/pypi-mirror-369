# def serve(self, *args, **kwargs):
#     """
#     it serves the block
#
#     """
#     from fastapi import FastAPI
#     from fastapi.responses import JSONResponse
#     from ray import serve
#
#     app = FastAPI()
#     block = self
#     block_name = block.__class__.__name__.lower()
#
#     @serve.deployment
#     @serve.ingress(app)
#     class BlockDeployment:
#         """
#         Block deployment class
#         """
#
#         @app.get("/health")
#         def root(self):
#             """
#             health check
#             :return:
#             """
#             return f"Block {block_name} is up and running"
#
#         @app.post("/")
#         def call(self, request_data: RequestData):
#             """
#             it calls the block
#             :param request_data:
#             :return:
#             """
#             if request_data.args:
#                 arguments = request_data.args
#                 for key, value in arguments.items():
#                     setattr(block, key, value)
#             result = block(request_data.data)
#             return JSONResponse(content={"output": result})
#
#     deployment = BlockDeployment.bind()
#     serve.run(deployment, route_prefix=f"/{block_name}", *args, **kwargs)
#
#
# import importlib
# import inspect
# import logging
# import sys
# from io import StringIO
# from typing import Annotated, Any, get_args, get_origin
#
# from pydantic import ConfigDict, Field, create_model
#
# # Assume the new analyzer is in your utils module
# from lgopy.utils import (
#     LibUtils,
#     analyze_class_dependencies,
#     format_and_check_code,
# )
#
# logger = logging.getLogger(__name__)
#
#
# class BlockMixin:
#     """
#     Block mixin class
#     """
#
#     # ... (to_pydantic_model, to_json, schema, and to_dict methods are unchanged) ...
#     @classmethod
#     def to_pydantic_model(cls):
#         """
#         Dynamically generate a Pydantic model from the class's __init__ signature.
#         - Supports Annotated[T, description] for inline descriptions.
#         - Infers field types and default values.
#         - Injects class-level metadata (description, category, output_type).
#         """
#         model_fields = {}
#
#         # Parse __init__ parameters into model fields
#         for name, param in inspect.signature(cls.__init__).parameters.items():
#             if name == "self":
#                 continue
#
#             annotation = param.annotation
#             default = None if param.default is inspect.Parameter.empty else param.default
#             description = None
#
#             if annotation is inspect.Parameter.empty:
#                 if default is None:
#                     raise ValueError(
#                         f"Parameter '{name}' in class '{cls.__name__}' must have a type annotation or a default value."
#                     )
#                 field_type = type(default)
#             else:
#                 field_type = annotation
#                 origin = get_origin(annotation)
#                 args = get_args(annotation)
#
#                 # Handle Annotated[T, description]
#                 if origin is Annotated and len(args) >= 2:
#                     field_type = args[0]
#                     description = args[1]
#
#             model_fields[name] = (
#                 field_type,
#                 Field(default, description=description)
#             )
#
#         # Enforce return type on `call`
#         call_annotations = getattr(cls.call, "__annotations__", {})
#         return_annot = call_annotations.get("return", None)
#
#         if return_annot is None or return_annot is inspect.Parameter.empty:
#             raise TypeError(
#                 f"The `call` method in class '{cls.__name__}' must define an explicit return type annotation."
#             )
#
#         # Extract type name string for output_type
#         if isinstance(return_annot, type):
#             output_type_str = return_annot.__name__
#         else:
#             output_type_str = str(return_annot)
#
#         # Optional class-level metadata
#         model_title = cls.__name__
#         model_description = getattr(cls, "description", None)
#         category = getattr(cls, "category", None)
#         display_name = getattr(cls, "display_name", None)
#
#         # Pydantic config with schema metadata
#         config = ConfigDict(
#             title=model_title,
#             extra="allow",
#             arbitrary_types_allowed=True,
#             json_schema_extra={
#                 "category": category,
#                 "display_name": display_name,
#                 "output_type": output_type_str,
#             }
#         )
#
#         return create_model(
#             model_title,
#             __doc__=model_description,
#             __config__=config,
#             **model_fields
#         )
#
#     def to_json(self):
#         """
#         Serialize the object into a JSON string using its Pydantic model,
#         excluding any attributes not defined in the model.
#         """
#         pydantic_model = self.to_pydantic_model()
#
#         # Only keep keys that are valid fields in the Pydantic model
#         valid_fields = pydantic_model.model_fields.keys()
#         filtered_fields = {k: v for k, v in self.__dict__.items() if k in valid_fields}
#
#         pivot_model_instance = pydantic_model(**filtered_fields)
#         return pivot_model_instance.model_dump_json(exclude_none=True)
#
#     @classmethod
#     def schema(cls) -> dict:
#         """
#         Returns the JSON schema for the block
#         """
#         pydantic_model = cls.to_pydantic_model()
#         return pydantic_model.model_json_schema()
#
#     @classmethod
#     def build(cls):
#         """
#         Builds the block by isolating its source code, dependencies, and
#         package requirements into a self-contained folder.
#
#         This process performs the following steps:
#         1.  Locates the source file of the block class.
#         2.  Parses the file to extract the class's source code and its specific imports.
#         3.  Analyzes imports to identify third-party package dependencies and their versions.
#         4.  Creates a dedicated directory for the block.
#         5.  Writes the clean, formatted class code to a `block.py` file.
#         6.  Generates a `requirements.txt` file for pip.
#         7.  Creates an `__init__.py` to make the block importable.
#         """
#         class_file_path = inspect.getfile(cls)
#         class_name = cls.__name__
#         logger.info(f"Building block: {class_name} from {class_file_path}...")
#
#         with open(class_file_path, "r") as file:
#             source_code = file.read()
#
#         try:
#             analysis = analyze_class_dependencies(source_code, class_name)
#         except (ValueError, SyntaxError) as e:
#             logger.error(f"Failed to analyze dependencies for {class_name}: {e}")
#             return None
#
#         # Combine the necessary imports and the class code into one string
#         full_code = "\n".join(analysis['imports']) + "\n\n\n" + analysis['class_code']
#
#         # Format the final code using your existing utility
#         format_result = format_and_check_code(full_code)
#         formatted_code = format_result.get("formatted_code", full_code)
#
#         # --- Create the block's directory and files ---
#         lib_home = LibUtils.get_lib_home()
#         block_folder = lib_home / "blocks" / class_name
#         block_folder.mkdir(parents=True, exist_ok=True)
#         logger.info(f"Created block directory at: {block_folder}")
#
#         # Write the main block.py file
#         (block_folder / "block.py").write_text(formatted_code)
#         logger.info(f"Wrote block source to {block_folder / 'block.py'}")
#
#         # Write the __init__.py file
#         (block_folder / "__init__.py").write_text(f"from .block import {class_name}\n")
#
#         # Write the requirements.txt file
#         requirements = analysis.get("packages", {})
#         if requirements:
#             req_file = block_folder / "requirements.txt"
#             with open(req_file, "w") as f:
#                 for package, version in sorted(requirements.items()):
#                     f.write(f"{package}=={version}\n")
#             logger.info(f"Generated requirements.txt with {len(requirements)} packages.")
#         else:
#             logger.info("No external package requirements found for this block.")
#
#         logger.info(f"Block '{class_name}' built successfully!")
#
#         # --- Dynamically load and return the new class (optional) ---
#         spec = importlib.util.spec_from_file_location(class_name, block_folder / "block.py")
#         if spec and spec.loader:
#             block_module = importlib.util.module_from_spec(spec)
#             spec.loader.exec_module(block_module)
#             return getattr(block_module, class_name, None)
#
#         logger.error(f"Could not dynamically load the built module for {class_name}.")
#         return None
#
#     def to_dict(self):
#         """
#         it returns a json schema for the block
#         """
#         pydantic_model = self.to_pydantic_model()
#         model = pydantic_model(**self.__dict__)
#         return model.model_dump(exclude_none=True, exclude_unset=True)