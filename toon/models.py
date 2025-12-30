"""TOON data models for representing code structures."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class NodeType(Enum):
    """Types of TOON nodes."""
    MODULE = "module"
    FUNCTION = "fn"
    ASYNC_FUNCTION = "async_fn"
    CLASS = "class"
    METHOD = "method"
    IMPORT = "import"
    IMPORT_FROM = "from"
    VARIABLE = "var"
    CONSTANT = "const"
    DECORATOR = "decorator"


@dataclass
class TOONNode:
    """Base class for TOON nodes."""
    node_type: NodeType
    name: str
    line_number: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TOONFunction(TOONNode):
    """Represents a function in TOON format."""
    arguments: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    body_summary: str = ""
    is_async: bool = False
    complexity: int = 1

    def to_toon(self, indent: int = 0) -> str:
        """Convert to TOON string representation."""
        prefix = "  " * indent
        fn_type = "async_fn" if self.is_async else "fn"

        # Function signature
        args = ", ".join(self.arguments)
        ret = f"->{self.return_type}" if self.return_type else ""
        lines = [f"{prefix}{fn_type}:{self.name}({args}){ret}"]

        # Docstring (compressed)
        if self.docstring:
            doc_short = self.docstring.split('\n')[0][:60]
            lines.append(f"{prefix}  doc:\"{doc_short}\"")

        # Decorators
        for dec in self.decorators:
            lines.append(f"{prefix}  @{dec}")

        # Body summary
        if self.body_summary:
            lines.append(f"{prefix}  body:{self.body_summary}")

        # Complexity
        if self.complexity > 1:
            lines.append(f"{prefix}  complexity:{self.complexity}")

        return "\n".join(lines)


@dataclass
class TOONClass(TOONNode):
    """Represents a class in TOON format."""
    bases: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    methods: List[TOONFunction] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)

    def to_toon(self, indent: int = 0) -> str:
        """Convert to TOON string representation."""
        prefix = "  " * indent

        # Class definition
        bases_str = f"({', '.join(self.bases)})" if self.bases else ""
        lines = [f"{prefix}class:{self.name}{bases_str}"]

        # Docstring
        if self.docstring:
            doc_short = self.docstring.split('\n')[0][:60]
            lines.append(f"{prefix}  doc:\"{doc_short}\"")

        # Decorators
        for dec in self.decorators:
            lines.append(f"{prefix}  @{dec}")

        # Attributes
        if self.attributes:
            attrs = ", ".join(self.attributes[:5])
            lines.append(f"{prefix}  attrs:{attrs}")

        # Methods summary
        if self.methods:
            lines.append(f"{prefix}  methods:{len(self.methods)}")
            for method in self.methods[:5]:  # Show first 5 methods
                lines.append(f"{prefix}    - {method.name}")

        return "\n".join(lines)


@dataclass
class TOONImport(TOONNode):
    """Represents an import statement in TOON format."""
    module: Optional[str] = None
    names: List[str] = field(default_factory=list)
    aliases: Dict[str, str] = field(default_factory=dict)
    is_from_import: bool = False

    def to_toon(self, indent: int = 0) -> str:
        """Convert to TOON string representation."""
        prefix = "  " * indent

        if self.is_from_import:
            names_str = ", ".join(self.names)
            return f"{prefix}from:{self.module} import:{names_str}"
        else:
            names_str = ", ".join(self.names)
            return f"{prefix}import:{names_str}"


@dataclass
class TOONVariable(TOONNode):
    """Represents a variable assignment in TOON format."""
    value: str = ""
    type_hint: Optional[str] = None
    is_constant: bool = False

    def to_toon(self, indent: int = 0) -> str:
        """Convert to TOON string representation."""
        prefix = "  " * indent
        var_type = "const" if self.is_constant else "var"

        type_str = f":{self.type_hint}" if self.type_hint else ""
        value_str = self.value[:40] if self.value else ""

        return f"{prefix}{var_type}:{self.name}{type_str}={value_str}"


@dataclass
class TOONModule:
    """Represents a complete module in TOON format."""
    name: str
    docstring: Optional[str] = None
    imports: List[TOONImport] = field(default_factory=list)
    classes: List[TOONClass] = field(default_factory=list)
    functions: List[TOONFunction] = field(default_factory=list)
    variables: List[TOONVariable] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_toon(self) -> str:
        """Convert entire module to TOON string."""
        lines = [f"# Module: {self.name}"]

        # Module docstring
        if self.docstring:
            doc_short = self.docstring.split('\n')[0][:80]
            lines.append(f'doc:"{doc_short}"')

        # Imports
        if self.imports:
            lines.append("\n# Imports")
            for imp in self.imports:
                lines.append(imp.to_toon())

        # Classes
        if self.classes:
            lines.append("\n# Classes")
            for cls in self.classes:
                lines.append(cls.to_toon())
                lines.append("")  # Blank line between classes

        # Functions
        if self.functions:
            lines.append("\n# Functions")
            for func in self.functions:
                lines.append(func.to_toon())
                lines.append("")  # Blank line between functions

        # Module-level variables
        if self.variables:
            lines.append("\n# Variables")
            for var in self.variables:
                lines.append(var.to_toon())

        # Metadata
        if self.metadata:
            lines.append("\n# Metadata")
            lines.append(f"lines:{self.metadata.get('lines', 0)}")
            lines.append(f"complexity:{self.metadata.get('complexity', 0)}")

        return "\n".join(lines)

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the module."""
        return {
            "imports": len(self.imports),
            "classes": len(self.classes),
            "functions": len(self.functions),
            "variables": len(self.variables),
            "total_methods": sum(len(cls.methods) for cls in self.classes),
        }
