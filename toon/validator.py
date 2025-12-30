"""TOON Validator - Validates TOON format syntax and structure."""

import re
from typing import List, Tuple, Optional


class ValidationError:
    """Represents a validation error."""

    def __init__(self, line_number: int, message: str, severity: str = "error"):
        self.line_number = line_number
        self.message = message
        self.severity = severity

    def __repr__(self):
        return f"Line {self.line_number}: [{self.severity.upper()}] {self.message}"


class TOONValidator:
    """Validates TOON formatted text."""

    def __init__(self):
        self.errors = []
        self.warnings = []

        # Valid TOON keywords
        self.keywords = {
            'fn', 'async_fn', 'class', 'import', 'from', 'var', 'const',
            'doc', 'body', 'complexity', 'methods', 'attrs'
        }

        # Patterns for validation
        self.patterns = {
            'function': re.compile(r'^(async_)?fn:\w+\(.*?\)(?:->.*)?$'),
            'class': re.compile(r'^class:\w+(?:\(.*?\))?$'),
            'import': re.compile(r'^import:.+$'),
            'from_import': re.compile(r'^from:\S+\s+import:.+$'),
            'variable': re.compile(r'^(var|const):\w+(?::.+?)?=.*$'),
            'decorator': re.compile(r'^@\w+(?:\(.*?\))?$'),
        }

    def validate(self, toon_text: str) -> Tuple[bool, List[ValidationError]]:
        """
        Validate TOON formatted text.

        Args:
            toon_text: TOON formatted string

        Returns:
            Tuple of (is_valid, list of errors)
        """
        self.errors = []
        self.warnings = []

        lines = toon_text.strip().split('\n')

        for line_num, line in enumerate(lines, 1):
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('#'):
                continue

            self._validate_line(line, line_num)

        all_issues = self.errors + self.warnings
        return len(self.errors) == 0, all_issues

    def _validate_line(self, line: str, line_num: int):
        """Validate a single line."""
        content = line.strip()

        # Check indentation (must be even number of spaces)
        indent = len(line) - len(line.lstrip())
        if indent % 2 != 0:
            self.warnings.append(ValidationError(
                line_num,
                f"Odd indentation ({indent} spaces). Use multiples of 2.",
                "warning"
            ))

        # Extract the keyword
        if ':' in content:
            keyword = content.split(':')[0].lstrip('@')

            # Check if it's a valid keyword
            if keyword not in self.keywords and not content.startswith('@'):
                self.warnings.append(ValidationError(
                    line_num,
                    f"Unknown keyword '{keyword}'",
                    "warning"
                ))

            # Validate syntax based on keyword
            if keyword in ['fn', 'async_fn']:
                if not self.patterns['function'].match(content):
                    self.errors.append(ValidationError(
                        line_num,
                        f"Invalid function syntax: {content}"
                    ))

            elif keyword == 'class':
                if not self.patterns['class'].match(content):
                    self.errors.append(ValidationError(
                        line_num,
                        f"Invalid class syntax: {content}"
                    ))

            elif keyword == 'import':
                if not self.patterns['import'].match(content):
                    self.errors.append(ValidationError(
                        line_num,
                        f"Invalid import syntax: {content}"
                    ))

            elif keyword == 'from':
                if not self.patterns['from_import'].match(content):
                    self.errors.append(ValidationError(
                        line_num,
                        f"Invalid from...import syntax: {content}"
                    ))

            elif keyword in ['var', 'const']:
                if not self.patterns['variable'].match(content):
                    self.errors.append(ValidationError(
                        line_num,
                        f"Invalid variable syntax: {content}"
                    ))

        elif content.startswith('@'):
            if not self.patterns['decorator'].match(content):
                self.errors.append(ValidationError(
                    line_num,
                    f"Invalid decorator syntax: {content}"
                ))

    def get_errors(self) -> List[ValidationError]:
        """Get all validation errors."""
        return self.errors

    def get_warnings(self) -> List[ValidationError]:
        """Get all validation warnings."""
        return self.warnings

    def is_valid(self) -> bool:
        """Check if last validation had no errors."""
        return len(self.errors) == 0
