import importlib.util
import inspect
import logging
import subprocess
import sys
import tempfile
from pathlib import Path

import black
from pylint.lint import Run

from lgopy.utils import DependencyAnalyzer, LibUtils, FileUtils

logger = logging.getLogger(__name__)


class BlockBuilder:
    """
    Builds a block class into a standalone folder with formatted source,
    requirements, and an __init__ file.
    """

    @classmethod
    def build(cls, block_cls):
        """Orchestrates the block building process."""
        class_file_path = inspect.getfile(block_cls)
        class_name = block_cls.__name__
        logger.info(f"Building block: {class_name} from {class_file_path}...")

        try:
            source_code = Path(class_file_path).read_text()
            analysis_results = DependencyAnalyzer.analyze(source_code, class_name)
        except (ValueError, SyntaxError, FileNotFoundError) as e:
            logger.error(f"Failed to analyze dependencies for {class_name}: {e}")
            return None

        # Process the code in a temporary file to ensure atomicity
        initial_code = "\n".join(analysis_results['imports']) + "\n\n\n" + analysis_results['class_code']
        processed_result = cls._process_code(initial_code)

        # If formatting or linting fails, we can halt the build
        if processed_result.get("lint_errors"):
            logger.error(f"Linting failed for {class_name}, build aborted.")
            # Optionally print errors: print(processed_result["lint_errors"])
            return None

        final_code = processed_result["formatted_code"]

        # --- Create final output directory and files ---
        lib_home = LibUtils.get_lib_home()
        block_folder = lib_home / "blocks" / class_name
        block_folder.mkdir(parents=True, exist_ok=True)
        FileUtils.clear_folder_contents(block_folder)

        # Write the final, cleaned block.py
        (block_folder / "block.py").write_text(final_code)
        logger.info(f"Wrote cleaned and formatted source to {block_folder / 'block.py'}")

        # Write __init__.py
        (block_folder / "__init__.py").write_text(f"from .block import {class_name}\n")

        # Write requirements.txt
        cls._write_requirements(block_folder, analysis_results.get("packages", {}))

        logger.info(f"Block '{class_name}' built successfully!")
        return cls._load_built_class(block_folder / "block.py", class_name)

    @staticmethod
    def _process_code(source_code: str) -> dict:
        """
        Cleans, formats, and checks code in a single, robust operation.
        This runs autoflake, isort, black, pylint, and bandit.
        """
        results = {"formatted_code": source_code, "lint_errors": "", "security_warnings": ""}

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = Path(temp_dir) / "block.py"
            temp_file_path.write_text(source_code)

            # 1. Remove unused imports FIRST
            _run_tool("autoflake", [
                sys.executable, "-m", "autoflake", "--in-place",
                "--remove-all-unused-imports", "--remove-unused-variables",
                str(temp_file_path)
            ])

            # 2. Sort the remaining imports
            _run_tool("isort", [sys.executable, "-m", "isort", str(temp_file_path)])

            # 3. Format the code with black
            _run_tool("black", [sys.executable, "-m", "black", str(temp_file_path)])

            # Read the cleaned code back
            cleaned_code = temp_file_path.read_text()
            results["formatted_code"] = cleaned_code

            # 4. Run checks on the final code
            try:
                # You might want to capture the output of pylint to a string
                Run(['--errors-only', str(temp_file_path)], exit=False)
            except Exception as e:
                results["lint_errors"] = f"Linting failed: {str(e)}"

            try:
                security_result = subprocess.run(
                    ["bandit", "-r", str(temp_file_path)],
                    capture_output=True, text=True, check=False
                )
                results["security_warnings"] = security_result.stdout
            except FileNotFoundError:
                logger.warning("Security check skipped: 'bandit' not found.")
            except Exception as e:
                results["security_warnings"] = f"Security check failed: {str(e)}"

        return results

    @staticmethod
    def _write_requirements(block_folder: Path, packages: dict):
        """Writes the requirements.txt file."""
        requirements_path = block_folder / "requirements.txt"
        if packages:
            content = "\n".join(f"{pkg}=={ver}" for pkg, ver in sorted(packages.items())) + "\n"
            requirements_path.write_text(content)
            logger.info(f"Generated requirements.txt with {len(packages)} packages.")
        else:
            requirements_path.write_text("")  # Create an empty file
            logger.info("No external dependencies found. Wrote empty requirements.txt.")

    @staticmethod
    def _load_built_class(filepath: Path, class_name: str):
        """Dynamically loads the newly built class from its file."""
        spec = importlib.util.spec_from_file_location(class_name, filepath)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return getattr(module, class_name, None)
        logger.error(f"Could not dynamically load the built module for {class_name}.")
        return None


def _run_tool(name: str, command: list):
    """Helper to run an external command-line tool."""
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        logger.debug(f"Successfully ran {name}.")
    except FileNotFoundError:
        logger.warning(f"Tool '{name}' not found. Skipping this step.")
    except subprocess.CalledProcessError as e:
        logger.warning(f"Tool '{name}' failed: {e.stderr}")
