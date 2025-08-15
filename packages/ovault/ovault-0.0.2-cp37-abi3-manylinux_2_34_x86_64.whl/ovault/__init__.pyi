"""Obsidian Vault Python Interface (ovault)"""

import os
from typing import List, Optional, Set, Dict, Iterator

class ExternalLink:
    """Represents an external link token.

    Attributes:
        render (bool): Whether the link should be rendered (i.e., starts with '!' for an embedded link).
        url (str): The URL of the external link.
        show_how (str): The text to display for the link.
        options (Optional[str]): Optional rendering options.
        position (Optional[str]): An optional position within the URL, often an anchor.
    """
    render: bool
    url: str
    show_how: str
    options: Optional[str]
    position: Optional[str]

    def label(self) -> str:
        """Gets the label for the external link."""
        ...

class InternalLink:
    """Represents an internal link token to another note or attachment.

    Attributes:
        dest (str): The destination note's name or path.
        position (Optional[str]): An optional position within the note (e.g., a heading).
        show_how (Optional[str]): An optional alias or display text for the link.
        options (Optional[str]): Optional rendering options.
        render (bool): Whether the link should be rendered (i.e., starts with '!' for an embedded link).
    """
    dest: str
    position: Optional[str]
    show_how: Optional[str]
    options: Optional[str]
    render: bool

    def label(self) -> str:
        """Gets the label for the internal link."""
        ...

class Callout:
    """Represents a callout block.

    Attributes:
        kind (str): The type of callout (e.g., 'info', 'warning').
        title (str): The title of the callout.
        contents (List['Token']): A list of tokens representing the content inside the callout.
        foldable (bool): Whether the callout is collapsible.
    """
    kind: str
    title: str
    contents: List['Token']
    foldable: bool

class Span:
    """Represents a span of text in a source document.

    Attributes:
        start (int): The starting byte index of the span.
        end (int): The ending byte index of the span.
    """
    start: int
    end: int

class Token:
    """
    Base class for all token types, with variants as nested classes.
    Each token represents a structural or content element parsed from a markdown note.
    """
    span: Span
    def span(self) -> Span:
        """Returns the span of the token."""
        ...
    def span_mut(self) -> Span:
        """Returns a mutable reference to the span of the token."""
        ...
    def is_whitespace(self) -> bool:
        """Returns true if the token is a text token consisting only of whitespace."""
        ...
    def __getattr__(self, name: str) -> any:
        """Dynamic attribute access for token variants."""
        ...
    def __repr__(self) -> str:
        """A string representation of the token."""
        ...

    class Frontmatter(Token):
        """Represents a YAML frontmatter block at the start of a note.

        Attributes:
            yaml (str): The content of the YAML frontmatter.
        """
        yaml: str

    class Text(Token):
        """Represents a plain text token.

        Attributes:
            text (str): The text content.
        """
        text: str

    class Tag(Token):
        """Represents a tag token.

        Attributes:
            tag (str): The name of the tag (e.g., without the '#').
        """
        tag: str

    class Header(Token):
        """Represents a header token.

        Attributes:
            level (int): The heading level (1-6).
            heading (str): The heading text.
        """
        level: int
        heading: str

    class Code(Token):
        """Represents a code block or inline code.

        Attributes:
            lang (Optional[str]): The programming language of the code block.
            code (str): The code content.
        """
        lang: Optional[str]
        code: str

    class Quote(Token):
        """Represents a blockquote token.

        Attributes:
            contents (List[Token]): A list of tokens representing the content inside the quote.
        """
        contents: List[Token]

    class InlineMath(Token):
        """Represents an inline LaTeX math token.

        Attributes:
            latex (str): The LaTeX content.
        """
        latex: str

    class DisplayMath(Token):
        """Represents a display LaTeX math token.

        Attributes:
            latex (str): The LaTeX content.
        """
        latex: str

    class Divider(Token):
        """Represents a horizontal divider token (e.g., '---')."""
        pass

    class Callout(Token):
        """Represents a callout token.

        Attributes:
            callout (Callout): The Callout object containing details about the callout.
        """
        callout: Callout

    class InternalLink(Token):
        """Represents an internal link token.

        Attributes:
            link (InternalLink): The InternalLink object containing details about the link.
        """
        link: InternalLink

    class ExternalLink(Token):
        """Represents an external link token.

        Attributes:
            link (ExternalLink): The ExternalLink object containing details about the link.
        """
        link: ExternalLink

class Note:
    """
    A note in an Obsidian vault, represented as a markdown file.

    Attributes:
        vault_path (os.PathLike): The absolute path to the vault's root directory.
        path (os.PathLike): The path of the note relative to the vault's root.
        name (str): The name of the note (file stem).
        length (int): The total number of characters in the note's content.
        tags (Set[str]): A set of all tags found in the note.
        backlinks (Set[str]): A set of normalized note names that link to this note.
        links (Set[str]): A set of normalized note names that this note links to.
    """
    vault_path: os.PathLike
    path: os.PathLike
    name: str
    length: int
    tags: Set[str]
    backlinks: Set[str]
    links: Set[str]

    def __repr__(self) -> str:
        """Returns a string representation of the Note."""
        ...
    def __len__(self) -> int: 
        """Returns the length of the note in characters."""
        ...
    def tokens(self) -> Iterator[Token]:
        """Returns an iterator over the tokens in the note's content."""
        ...
    def full_path(self) -> os.PathLike:
        """Returns the absolute path to the note file."""
        ...
    def frontmatter(self) -> Optional[str]:
        """Returns the YAML frontmatter content if present."""
        ...
    def read(self) -> str:
        """Reads and returns the full content of the note file."""
        ...
    def insert_at(self, pos: int, text: str) -> None:
        """Inserts text at a specific position in the note.

        Args:
            pos (int): The character position to insert at.
            text (str): The text to insert.
        """
        ...
    def insert_before_token(self, token: Token, text: str, offset: int = 0) -> None:
        """Inserts text before a given token in the note.

        Args:
            token (Token): The token to insert text before.
            text (str): The text to insert.
            offset (int): An optional character offset from the token's start.
        """
        ...
    def insert_after_token(self, token: Token, text: str, offset: int = 0) -> None:
        """Inserts text after a given token in the note.

        Args:
            token (Token): The token to insert text after.
            text (str): The text to insert.
            offset (int): An optional character offset from the token's end.
        """
        ...

class Attachment:
    """
    An attachment in an Obsidian vault.

    Attributes:
        path (os.PathLike): The path of the attachment relative to the vault's root.
    """
    path: os.PathLike

class Vault:
    """
    An Obsidian vault containing notes and attachments.

    The vault is indexed on creation and can be re-indexed with the `index` method.

    Attributes:
        path (os.PathLike): The absolute path to the vault's root directory.
        dangling_links (Dict[str, List[str]]): A dictionary mapping a source note's
            normalized name to a list of non-existent links it contains.
        ignored (Set[os.PathLike]): A set of paths that were ignored during indexing.
    """
    path: os.PathLike
    dangling_links: Dict[str, List[str]]
    ignored: Set[os.PathLike]

    def __init__(self, path: str) -> None:
        """Initializes and indexes a new Vault instance.

        Args:
            path (str): The path to the Obsidian vault directory.
        """
        ...
    def notes(self) -> List[Note]:
        """Returns a list of all notes in the vault."""
        ...
    def attachments(self) -> List[Attachment]:
        """Returns a list of all attachments in the vault."""
        ...
    def tags(self) -> List[str]:
        """Returns a list of all unique tags found in the vault."""
        ...
    def index(self) -> None:
        """Re-indexes the entire vault, updating all note and link data."""
        ...
    def get_notes_by_tag(self, tag: str) -> List[Note]:
        """Returns a list of notes containing a specific tag."""
        ...
    def get_note_by_name(self, name: str) -> Optional[Note]:
        """Returns a single note by its normalized name, if it exists."""
        ...
