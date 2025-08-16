import ast
import importlib.metadata
import sys
from typing import Set, Dict, Tuple, Optional


class DependencyAnalyzer:
    """
    Utility class for analyzing class-level dependencies in a source file.
    Extracts the class code, required imports, and external package requirements.
    """

    class _Collector(ast.NodeVisitor):
        def __init__(self, class_name: str):
            self.class_name = class_name
            self.imports: Dict[str, str] = {}  # {alias or name: full import line}
            self.used_names: Set[str] = set()
            self._in_target_class = False
            self._class_node: Optional[ast.ClassDef] = None

        def visit_ClassDef(self, node: ast.ClassDef):
            if node.name == self.class_name:
                self._in_target_class = True
                self._class_node = node
                # Also collect names used in base classes (e.g., `Block`)
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        self.used_names.add(base.id)
                self.generic_visit(node)
                self._in_target_class = False

        def visit_Name(self, node: ast.Name):
            # Add a check to ignore 'self'
            if self._in_target_class and node.id != 'self':
                self.used_names.add(node.id)
            self.generic_visit(node)

        def visit_Attribute(self, node: ast.Attribute):
            if self._in_target_class:
                current = node
                while isinstance(current, ast.Attribute):
                    current = current.value
                # Add a check to ignore 'self' as the root of an attribute
                if isinstance(current, ast.Name) and current.id != 'self':
                    self.used_names.add(current.id)
            self.generic_visit(node)

        def visit_Import(self, node: ast.Import):
            for alias in node.names:
                self.imports[alias.asname or alias.name] = ast.unparse(node)

        def visit_ImportFrom(self, node: ast.ImportFrom):
            if node.level == 0 and node.module:
                for alias in node.names:
                    self.imports[alias.asname or alias.name] = ast.unparse(node)

    # ... rest of the DependencyAnalyzer class is unchanged ...
    @classmethod
    def analyze(cls, source_code: str, class_name: str) -> Dict:
        """
        Analyze a specific class to extract its code, necessary import statements,
        and external package requirements.

        Returns:
            dict: {
                'class_code': str,
                'imports': List[str],
                'packages': Dict[str, str]
            }
        """
        tree = ast.parse(source_code)
        collector = cls._Collector(class_name)
        collector.visit(tree)

        if not collector._class_node:
            raise ValueError(f"Class '{class_name}' not found in source code.")

        class_code = ast.unparse(collector._class_node)
        required_import_statements: Set[str] = set()
        required_packages: Dict[str, str] = {}

        for name in sorted(collector.used_names):
            if name in collector.imports:
                import_statement = collector.imports[name]
                required_import_statements.add(import_statement)

                module_name = cls._get_module_name(import_statement)
                if module_name:
                    package_info = cls._get_package_info(module_name)
                    if package_info:
                        pkg_name, version = package_info
                        required_packages[pkg_name] = version

        return {
            "class_code": class_code,
            "imports": sorted(required_import_statements),
            "packages": required_packages,
        }

    @staticmethod
    def _get_module_name(import_stmt: str) -> Optional[str]:
        """Extract module name from a parsed import statement."""
        try:
            node = ast.parse(import_stmt).body[0]
            if isinstance(node, ast.Import):
                return node.names[0].name
            elif isinstance(node, ast.ImportFrom):
                return node.module
        except Exception:
            pass
        return None

    @staticmethod
    def _get_stdlib_modules() -> Set[str]:
        """Return a set of standard library modules."""
        if sys.version_info >= (3, 10):
            return set(sys.stdlib_module_names)
        return {"os", "sys", "typing", "logging", "inspect", "io", "importlib", "pathlib"}

    @classmethod
    def _get_package_info(cls, module_name: str) -> Optional[Tuple[str, str]]:
        """
        Return the installable package name and version given a module name.
        Returns None if it's a standard library module.
        """
        stdlib = cls._get_stdlib_modules()
        root = module_name.split('.')[0]
        if module_name in stdlib or root in stdlib:
            return None

        try:
            dist = importlib.metadata.distribution(module_name)
            return dist.metadata["Name"], dist.version
        except importlib.metadata.PackageNotFoundError:
            if '.' in module_name:
                return cls._get_package_info(root)
            return None