from __future__ import annotations
from typing import Any

from .enums.PrintMode import PrintMode

class TreeTypes:
    
    obj_to_analyse: Any
    type: Any = None
    children: list[tuple[TreeTypes|None, TreeTypes|None]] = []
    print_mode: PrintMode
    
    def __init__(self, obj: Any, print_mode: PrintMode = PrintMode.CLASS) -> None:
        self.obj_to_analyse = obj
        self.children = []
        self.print_mode = print_mode
    
    def __repr__(self):
        if self.type:
            return f"<TreeTypes(type={self.as_type()})>"
        return f"<TreeTypes(status=NOT_PROCESSED)>"
    
    def __str__(self, ident:int=0):
        if self.print_mode == PrintMode.CLASS:
            return self.__repr__()
        if self.print_mode == PrintMode.PRETTY:
            if self.type in ('list', 'set') and len(self.children) > 0:
                text = f"{self.type}"
                for index, (_, value) in enumerate(self.children):
                    text += '\n' + '    '*(ident+1) + f"{self.type}[{index}] <> "
                    if value:
                        text += f"{value.__str__(ident+1)}"
                return text
            if self.type == 'dict' and len(self.children) > 0:
                text = f"{self.type}"
                for key, value in self.children:
                    text += '\n' + '    '*(ident+1) + f"key({key}) <> value"
                    if value and not value.type in ('list', 'set', 'dict'):
                        text += f"({value.__str__(ident+1)})"
                    elif value:
                        text += f" -> {value.__str__(ident+1)}"
                return text
            if self.type in ['DataFrame', 'Serie']:
                return f"PRINTABLE_NOT_FORMATED -> {self.type}"
            text = str(self.obj_to_analyse)
            return f"'{text[:min(len(text), 100)]}' -> {self.type}"
        if self.print_mode == PrintMode.PRETTY_SIMPLIFIED:
            if self.type in ('list', 'set') and len(self.children) > 0:
                text = f"{self.type}"
                for index, (_, value) in enumerate(self.children):
                    text += '\n' + '    '*(ident+1) + f"{index} -> "
                    if value:
                        text += f"{value.__str__(ident+1)}"
                return text
            if self.type == 'dict' and len(self.children) > 0:
                text = f"{self.type}"
                for key, value in self.children:
                    text += '\n' + '    '*(ident+1) + f"{key} <> "
                    if value and not value.type in ('list', 'set', 'dict'):
                        text += f"{value.__str__(ident+1)}"
                    elif value:
                        text += f" -> {value.__str__(ident+1)}"
                return text
            if self.type in ['DataFrame', 'Serie']:
                return f"PRINTABLE_NOT_FORMATED -> {self.type}"
            text = str(self.obj_to_analyse)
            return f"'{text[:min(len(text), 100)]}' -> {self.type}"
        return ""
    
    def as_type(self):
        type_text = f"{self.type}"
        if len(self.children) > 0:
            type_text += '['
            key_type, value_type = zip(*self.children)
            if any(key_type):
                key_type = {kt.as_type() for kt in key_type}
                type_text += '|'.join(key_type) + ','
            value_type = {vt.as_type() for vt in value_type}
            type_text += '|'.join(value_type) + ']'
        return type_text
    
    def process(self):
        obj = self.obj_to_analyse
        self.type = type(obj).__name__
        if isinstance(obj, dict):
            for k, v in obj.items():
                kt = TreeTypes(k, print_mode=self.print_mode)
                kt.process()
                vt = TreeTypes(v, print_mode=self.print_mode)
                vt.process()
                self.children.append((kt, vt))
        elif isinstance(obj, list) or isinstance(obj, set):
            for v in obj:
                vt = TreeTypes(v, print_mode=self.print_mode)
                vt.process()
                self.children.append((None, vt))
