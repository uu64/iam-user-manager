#!/usr/bin/env python3

from typing import Dict, List


class User:
    name: str
    tags: Dict[str, str]
    groups: List[str]

    def __init__(self, name: str, tags: Dict[str, str], groups: List[str]):
        self.name = name
        self.tags = tags if tags else {}
        self.groups = groups if groups else []
