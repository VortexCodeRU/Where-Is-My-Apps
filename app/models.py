# класс Shortcuts

from dataclasses import dataclass
from typing import Optional

@dataclass
class Shortcut:
    name: str
    lnk_path: str
    target: str
    icon_path: Optional[str] = None