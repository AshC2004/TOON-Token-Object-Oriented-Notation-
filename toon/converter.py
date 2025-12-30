"""TOON Converter - Converts Python code to TOON format."""

import ast
from pathlib import Path
from typing import List, Optional, Dict, Any

from .models import (
    TOONModule, TOONFunction, TOONClass, TOONImport,
    TOONVariable, NodeType
)


class TOONConverter:
    """Converts Python code to TOON (Text Object Oriented Notation) format."""

    def __init__(self, max_docstring_length: int = 60):
        """
        Initialize TOON converter.

        Args:
            max_docstring_length: Maximum length for docstrings in TOON output
        """
        self.max_docstring_length = max_docstring_length
        self.current_file = ""

    def convert_file(self, file_path: Path) -> TOONModule:
        """
        Convert Python file to TOON module.

        Args:
            file_path: Path to Python file

        Returns:
            TOONModule object
        """
        self.current_file = str(file_path)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            tree = ast.parse(source_code, filename=str(file_path))

            return self._convert_module(tree, file_path.stem, source_code)

        except SyntaxError as e:
            # Return minimal module with error info
            return TOONModule(
                name=file_path.stem,
                metadata={"error": f"Syntax error: {e}"}
            )
        except Exception as e:
            return TOONModule(
                name=file_path.stem,
                metadata={"error": f"Conversion error: {e}"}
            )

    def convert_string(self, code: str, module_name: str = "code") -> TOONModule:
        """
        Convert Python code string to TOON module.

        Args:
            code: Python source code
            module_name: Name for the module

        Returns:
            TOONModule object
        """
        try:
            tree = ast.parse(code)
            return self._convert_module(tree, module_name, code)
        except Exception as e:
            return TOONModule(
                name=module_name,
                metadata={"error": f"Conversion error: {e}"}
            )

    def _convert_module(self, tree: ast.Module, name: str, source: str) -> TOONModule:
        """Convert AST Module to TOON Module."""
        module = TOONModule(
            name=name,
            docstring=ast.get_docstring(tree),
            metadata={
                "lines": len(source.split('\n')),
                "chars": len(source)
            }
        )

        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                module.functions.append(self._convert_function(node))
            elif isinstance(node, ast.AsyncFunctionDef):
                module.functions.append(self._convert_async_function(node))
            elif isinstance(node, ast.ClassDef):
                module.classes.append(self._convert_class(node))
            elif isinstance(node, ast.Import):
                module.imports.append(self._convert_import(node))
            elif isinstance(node, ast.ImportFrom):
                module.imports.append(self._convert_import_from(node))
            elif isinstance(node, ast.Assign):
                variables = self._convert_assign(node)
                module.variables.extend(variables)

        # Calculate total complexity
        total_complexity = sum(f.complexity for f in module.functions)
        for cls in module.classes:
            total_complexity += sum(m.complexity for m in cls.methods)

        module.metadata["complexity"] = total_complexity

        return module

    def _convert_function(self, node: ast.FunctionDef) -> TOONFunction:
        """Convert function definition to TOON."""
        func = TOONFunction(
            node_type=NodeType.FUNCTION,
            name=node.name,
            line_number=node.lineno,
            arguments=self._extract_arguments(node.args),
            return_type=self._extract_return_type(node),
            docstring=self._compress_docstring(ast.get_docstring(node)),
            decorators=self._extract_decorators(node.decorator_list),
            body_summary=self._summarize_body(node.body),
            is_async=False,
            complexity=self._calculate_complexity(node)
        )
        return func

    def _convert_async_function(self, node: ast.AsyncFunctionDef) -> TOONFunction:
        """Convert async function to TOON."""
        func = self._convert_function(node)
        func.is_async = True
        func.node_type = NodeType.ASYNC_FUNCTION
        return func

    def _convert_class(self, node: ast.ClassDef) -> TOONClass:
        """Convert class definition to TOON."""
        cls = TOONClass(
            node_type=NodeType.CLASS,
            name=node.name,
            line_number=node.lineno,
            bases=[self._extract_base_name(base) for base in node.bases],
            docstring=self._compress_docstring(ast.get_docstring(node)),
            decorators=self._extract_decorators(node.decorator_list),
        )

        # Extract methods and attributes
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method = self._convert_function(item) if isinstance(item, ast.FunctionDef) else self._convert_async_function(item)
                method.node_type = NodeType.METHOD
                cls.methods.append(method)
            elif isinstance(item, ast.Assign):
                # Class-level attributes
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        cls.attributes.append(target.id)

        return cls

    def _convert_import(self, node: ast.Import) -> TOONImport:
        """Convert import statement to TOON."""
        return TOONImport(
            node_type=NodeType.IMPORT,
            name="import",
            line_number=node.lineno,
            names=[alias.name for alias in node.names],
            aliases={alias.name: alias.asname for alias in node.names if alias.asname},
            is_from_import=False
        )

    def _convert_import_from(self, node: ast.ImportFrom) -> TOONImport:
        """Convert from...import statement to TOON."""
        return TOONImport(
            node_type=NodeType.IMPORT_FROM,
            name="from_import",
            line_number=node.lineno,
            module=node.module or "",
            names=[alias.name for alias in node.names],
            aliases={alias.name: alias.asname for alias in node.names if alias.asname},
            is_from_import=True
        )

    def _convert_assign(self, node: ast.Assign) -> List[TOONVariable]:
        """Convert assignment to TOON variables."""
        variables = []

        for target in node.targets:
            if isinstance(target, ast.Name):
                var = TOONVariable(
                    node_type=NodeType.VARIABLE,
                    name=target.id,
                    line_number=node.lineno,
                    value=self._extract_value(node.value),
                    is_constant=target.id.isupper()
                )
                variables.append(var)

        return variables

    def _extract_arguments(self, args: ast.arguments) -> List[str]:
        """Extract function arguments with type hints."""
        arg_list = []

        for arg in args.args:
            if arg.annotation:
                try:
                    type_hint = ast.unparse(arg.annotation)
                    arg_list.append(f"{arg.arg}:{type_hint}")
                except:
                    arg_list.append(arg.arg)
            else:
                arg_list.append(arg.arg)

        return arg_list

    def _extract_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation."""
        if node.returns:
            try:
                return ast.unparse(node.returns)
            except:
                return None
        return None

    def _extract_decorators(self, decorator_list: List[ast.expr]) -> List[str]:
        """Extract decorator names."""
        decorators = []
        for dec in decorator_list:
            try:
                decorators.append(ast.unparse(dec))
            except:
                pass
        return decorators

    def _extract_base_name(self, base: ast.expr) -> str:
        """Extract base class name."""
        try:
            return ast.unparse(base)
        except:
            return "Unknown"

    def _extract_value(self, value_node: ast.expr) -> str:
        """Extract and compress value expression."""
        try:
            value_str = ast.unparse(value_node)
            # Truncate long values
            if len(value_str) > 40:
                return value_str[:37] + "..."
            return value_str
        except:
            return "?"

    def _compress_docstring(self, docstring: Optional[str]) -> Optional[str]:
        """Compress docstring to first line, limited length."""
        if not docstring:
            return None

        # Get first line
        first_line = docstring.split('\n')[0].strip()

        # Truncate if too long
        if len(first_line) > self.max_docstring_length:
            return first_line[:self.max_docstring_length - 3] + "..."

        return first_line

    def _summarize_body(self, body: List[ast.stmt]) -> str:
        """Summarize function body with control flow."""
        summary_parts = []

        for node in body:
            if isinstance(node, ast.Return):
                summary_parts.append("ret")
            elif isinstance(node, ast.If):
                summary_parts.append("if")
            elif isinstance(node, ast.For):
                summary_parts.append("for")
            elif isinstance(node, ast.While):
                summary_parts.append("while")
            elif isinstance(node, ast.Try):
                summary_parts.append("try")
            elif isinstance(node, ast.With):
                summary_parts.append("with")
            elif isinstance(node, ast.Raise):
                summary_parts.append("raise")
            elif isinstance(node, ast.Assert):
                summary_parts.append("assert")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                summary_parts.append("nested_fn")
            elif isinstance(node, ast.ClassDef):
                summary_parts.append("nested_class")

        if summary_parts:
            return ", ".join(summary_parts[:10])  # Limit to 10 elements
        else:
            return f"{len(body)} stmts"

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1

        for child in ast.walk(node):
            # Branch points increase complexity
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def estimate_compression(self, original_code: str, toon_output: str) -> Dict[str, Any]:
        """
        Estimate compression ratio and token savings.

        Args:
            original_code: Original Python code
            toon_output: TOON format output

        Returns:
            Dictionary with compression statistics
        """
        original_size = len(original_code)
        toon_size = len(toon_output)

        # Rough token estimation (1 token ≈ 4 chars)
        original_tokens = original_size // 4
        toon_tokens = toon_size // 4

        compression_ratio = (1 - toon_size / original_size) * 100 if original_size > 0 else 0

        return {
            "original_chars": original_size,
            "toon_chars": toon_size,
            "compression_ratio": round(compression_ratio, 2),
            "chars_saved": original_size - toon_size,
            "estimated_original_tokens": original_tokens,
            "estimated_toon_tokens": toon_tokens,
            "estimated_tokens_saved": original_tokens - toon_tokens,
            "token_savings_percent": round((1 - toon_tokens / original_tokens) * 100, 2) if original_tokens > 0 else 0
        }
