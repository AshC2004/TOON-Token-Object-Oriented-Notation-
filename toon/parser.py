"""TOON Parser - Parses TOON format back to structured data."""

from typing import Dict, List, Optional
import re

from .models import TOONModule, TOONFunction, TOONClass, TOONImport


class TOONParser:
    """Parses TOON formatted text back to structured objects."""

    def __init__(self):
        self.patterns = {
            'function': re.compile(r'^(async_)?fn:(\w+)\((.*?)\)(?:->(.+))?$'),
            'class': re.compile(r'^class:(\w+)(?:\((.*?)\))?$'),
            'import': re.compile(r'^import:(.+)$'),
            'from_import': re.compile(r'^from:(\S+)\s+import:(.+)$'),
            'variable': re.compile(r'^(var|const):(\w+)(?::(.+?))?=(.*)$'),
            'docstring': re.compile(r'^doc:"(.*)"$'),
            'decorator': re.compile(r'^@(.+)$'),
            'body': re.compile(r'^body:(.+)$'),
            'complexity': re.compile(r'^complexity:(\d+)$'),
        }

    def parse(self, toon_text: str) -> TOONModule:
        """
        Parse TOON formatted text to TOONModule.

        Args:
            toon_text: TOON formatted string

        Returns:
            TOONModule object
        """
        lines = toon_text.strip().split('\n')
        module = TOONModule(name="parsed_module")

        current_context = None
        current_indent = 0

        for line in lines:
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('#'):
                continue

            # Calculate indentation
            indent = len(line) - len(line.lstrip())
            content = line.strip()

            # Parse based on pattern
            if content.startswith('fn:') or content.startswith('async_fn:'):
                func = self._parse_function(content)
                if func:
                    module.functions.append(func)
                    current_context = func
                    current_indent = indent

            elif content.startswith('class:'):
                cls = self._parse_class(content)
                if cls:
                    module.classes.append(cls)
                    current_context = cls
                    current_indent = indent

            elif content.startswith('import:'):
                imp = self._parse_import(content)
                if imp:
                    module.imports.append(imp)

            elif content.startswith('from:'):
                imp = self._parse_from_import(content)
                if imp:
                    module.imports.append(imp)

            elif indent > current_indent and current_context:
                # This is a property of the current context
                self._parse_property(content, current_context)

        return module

    def _parse_function(self, line: str) -> Optional[TOONFunction]:
        """Parse function line."""
        is_async = line.startswith('async_fn:')
        pattern = self.patterns['function']

        match = pattern.match(line)
        if match:
            _, name, args_str, return_type = match.groups()

            # Parse arguments
            args = [arg.strip() for arg in args_str.split(',')] if args_str else []

            from .models import TOONFunction, NodeType
            return TOONFunction(
                node_type=NodeType.ASYNC_FUNCTION if is_async else NodeType.FUNCTION,
                name=name,
                arguments=args,
                return_type=return_type,
                is_async=is_async
            )

        return None

    def _parse_class(self, line: str) -> Optional[TOONClass]:
        """Parse class line."""
        pattern = self.patterns['class']
        match = pattern.match(line)

        if match:
            name, bases_str = match.groups()
            bases = [b.strip() for b in bases_str.split(',')] if bases_str else []

            from .models import TOONClass, NodeType
            return TOONClass(
                node_type=NodeType.CLASS,
                name=name,
                bases=bases
            )

        return None

    def _parse_import(self, line: str) -> Optional[TOONImport]:
        """Parse import line."""
        pattern = self.patterns['import']
        match = pattern.match(line)

        if match:
            names_str = match.group(1)
            names = [n.strip() for n in names_str.split(',')]

            from .models import TOONImport, NodeType
            return TOONImport(
                node_type=NodeType.IMPORT,
                name="import",
                names=names,
                is_from_import=False
            )

        return None

    def _parse_from_import(self, line: str) -> Optional[TOONImport]:
        """Parse from...import line."""
        pattern = self.patterns['from_import']
        match = pattern.match(line)

        if match:
            module, names_str = match.groups()
            names = [n.strip() for n in names_str.split(',')]

            from .models import TOONImport, NodeType
            return TOONImport(
                node_type=NodeType.IMPORT_FROM,
                name="from_import",
                module=module,
                names=names,
                is_from_import=True
            )

        return None

    def _parse_property(self, line: str, context):
        """Parse property line and add to context."""
        # Docstring
        doc_match = self.patterns['docstring'].match(line)
        if doc_match:
            context.docstring = doc_match.group(1)
            return

        # Decorator
        dec_match = self.patterns['decorator'].match(line)
        if dec_match:
            if hasattr(context, 'decorators'):
                context.decorators.append(dec_match.group(1))
            return

        # Body summary
        body_match = self.patterns['body'].match(line)
        if body_match:
            if hasattr(context, 'body_summary'):
                context.body_summary = body_match.group(1)
            return

        # Complexity
        comp_match = self.patterns['complexity'].match(line)
        if comp_match:
            if hasattr(context, 'complexity'):
                context.complexity = int(comp_match.group(1))
            return
