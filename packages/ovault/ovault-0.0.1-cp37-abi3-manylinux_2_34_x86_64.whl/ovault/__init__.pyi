import os
from typing import List, Optional, Set, Dict, Iterator

class ExternalLink:
    render: bool
    url: str
    show_how: str
    options: Optional[str]
    position: Optional[str]

    def label(self) -> str: ...

class InternalLink:
    dest: str
    position: Optional[str]
    show_how: Optional[str]
    options: Optional[str]
    render: bool

    def label(self) -> str: ...

class Callout:
    kind: str
    title: str
    contents: List['Token']
    foldable: bool

class Span:
    start: int
    end: int

class Token:
    """Base class for all token types, with variants as nested classes."""
    span: Span
    def span(self) -> Span: ...
    def span_mut(self) -> Span: ...
    def is_whitespace(self) -> bool: ...
    def __getattr__(self, name: str) -> any: ...
    def __repr__(self) -> str: ...

    class Frontmatter(Token):
        yaml: str

    class Text(Token):
        text: str

    class Tag(Token):
        tag: str

    class Header(Token):
        level: int
        heading: str

    class Code(Token):
        lang: Optional[str]
        code: str

    class Quote(Token):
        contents: List[Token]

    class InlineMath(Token):
        latex: str

    class DisplayMath(Token):
        latex: str

    class Divider(Token):
        pass

    class Callout(Token):
        callout: Callout

    class InternalLink(Token):
        link: InternalLink

    class ExternalLink(Token):
        link: ExternalLink

class Note:
    vault_path: os.PathLike
    path: os.PathLike
    name: str
    length: int
    tags: Set[str]
    backlinks: Set[str]
    links: Set[str]

    def __repr__(self) -> str: ...
    def __len__(self) -> int: ...
    def tokens(self) -> Iterator[Token]: ...
    def full_path(self) -> os.PathLike: ...
    def frontmatter(self) -> Optional[str]: ...
    def read(self) -> str: ...
    def insert_at(self, pos: int, text: str) -> None: ...
    def insert_before_token(self, token: Token, text: str, offset: int = 0) -> None: ...
    def insert_after_token(self, token: Token, text: str, offset: int = 0) -> None: ...

class Attachment:
    path: os.PathLike

class Vault:
    path: os.PathLike
    dangling_links: Dict[str, List[str]]
    ignored: Set[os.PathLike]

    def __init__(self, path: str) -> None: ...
    def notes(self) -> List[Note]: ...
    def attachments(self) -> List[Attachment]: ...
    def tags(self) -> List[str]: ...
    def index(self) -> None: ...
    def get_notes_by_tag(self, tag: str) -> List[Note]: ...
    def get_note_by_name(self, name: str) -> Optional[Note]: ...
