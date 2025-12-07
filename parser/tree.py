"""GEDCOM tree builder.

Converts flat GEDCOM lines into a hierarchical tree structure
that can then be parsed into model objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, Optional

from .tokenizer import GedcomLine


@dataclass
class GedcomNode:
    """A node in the GEDCOM tree structure.

    Represents a GEDCOM line with its nested children, forming
    a tree that mirrors the GEDCOM hierarchy.

    Attributes:
        level: Hierarchical level from the original line.
        tag: GEDCOM tag (INDI, NAME, BIRT, etc.).
        value: Optional value after the tag.
        xref: Optional cross-reference identifier.
        line_number: Original line number in the file.
        children: Child nodes nested under this one.
    """

    level: int
    tag: str
    value: Optional[str] = None
    xref: Optional[str] = None
    line_number: int = 0
    children: list["GedcomNode"] = field(default_factory=list)

    @classmethod
    def from_line(cls, line: GedcomLine) -> GedcomNode:
        """Create a node from a tokenized line."""
        return cls(
            level=line.level,
            tag=line.tag,
            value=line.value,
            xref=line.xref,
            line_number=line.line_number,
        )

    def get_child(self, tag: str) -> Optional["GedcomNode"]:
        """Get the first child with the given tag.

        Args:
            tag: Tag to search for.

        Returns:
            First matching child node, or None.
        """
        for child in self.children:
            if child.tag == tag:
                return child
        return None

    def get_children(self, tag: str) -> list["GedcomNode"]:
        """Get all children with the given tag.

        Args:
            tag: Tag to search for.

        Returns:
            List of matching child nodes.
        """
        return [child for child in self.children if child.tag == tag]

    def get_child_value(self, tag: str) -> Optional[str]:
        """Get the value of the first child with the given tag.

        Args:
            tag: Tag to search for.

        Returns:
            Value of the first matching child, or None.
        """
        child = self.get_child(tag)
        return child.value if child else None

    def get_text_with_continuations(self) -> str:
        """Get this node's value with CONT/CONC continuations merged.

        GEDCOM uses CONT for newline continuations and CONC for
        concatenation without newlines.

        Returns:
            Complete text with continuations merged.
        """
        parts = [self.value or ""]

        for child in self.children:
            if child.tag == "CONT":
                parts.append("\n")
                parts.append(child.value or "")
            elif child.tag == "CONC":
                parts.append(child.value or "")

        return "".join(parts)

    def get_custom_tags(self) -> dict[str, list["GedcomNode"]]:
        """Get all custom (underscore-prefixed) child tags.

        Returns:
            Dictionary mapping custom tag names to lists of nodes.
        """
        custom: dict[str, list[GedcomNode]] = {}
        for child in self.children:
            if child.tag.startswith("_"):
                if child.tag not in custom:
                    custom[child.tag] = []
                custom[child.tag].append(child)
        return custom


def build_tree(lines: Iterator[GedcomLine]) -> list[GedcomNode]:
    """Build a tree of nodes from tokenized GEDCOM lines.

    Converts flat lines with level numbers into a hierarchical
    tree structure where child lines become children of their
    parent nodes.

    Args:
        lines: Iterator of tokenized GEDCOM lines.

    Returns:
        List of top-level (level 0) nodes with nested children.
    """
    root_nodes: list[GedcomNode] = []
    stack: list[GedcomNode] = []

    for line in lines:
        node = GedcomNode.from_line(line)

        # Find the parent for this node
        # Pop nodes from stack until we find one with level < current
        while stack and stack[-1].level >= node.level:
            stack.pop()

        if stack:
            # Add as child of the top of stack
            stack[-1].children.append(node)
        else:
            # Top-level node
            root_nodes.append(node)

        # Push this node onto stack (it may have children)
        stack.append(node)

    return root_nodes


def group_by_record_type(nodes: list[GedcomNode]) -> dict[str, list[GedcomNode]]:
    """Group top-level nodes by their record type.

    Args:
        nodes: List of top-level nodes.

    Returns:
        Dictionary mapping record types (INDI, FAM, etc.) to nodes.
    """
    groups: dict[str, list[GedcomNode]] = {}
    for node in nodes:
        if node.tag not in groups:
            groups[node.tag] = []
        groups[node.tag].append(node)
    return groups
