import re

from enum import Enum


class CaseStyle(Enum):
    camel = 'camel'
    pascal = 'pascal'
    snake = 'snake'


def to_case_style(text: str, case_style: CaseStyle) -> str:
    match case_style:
        case CaseStyle.camel:
            return to_camel_case(text)
        case CaseStyle.pascal:
            return to_pascal_case(text)
        case CaseStyle.snake:
            return to_snake_case(text)
        case _:
            raise ValueError(f'Unknown case style: {case_style}')


def to_camel_case(text: str) -> str:
    text = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', text)
    text = re.sub(r'([A-Z])([A-Z]+)(?![a-z])', lambda x: f"{x.group(1).upper()}{x.group(2).lower()}", text)
    text = re.sub(r'[^a-zA-Z0-9]+(.)', lambda x: x.group(1).upper(), text)
    text = re.sub(r'^([A-Z])', lambda x: x.group(1).lower(), text, 1)
    return text


def to_pascal_case(text: str) -> str:
    text = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', text)
    text = re.sub(r'([A-Z])([A-Z]+)(?![a-z])', lambda x: f"{x.group(1).upper()}{x.group(2).lower()}", text)
    text = re.sub(r'[^a-zA-Z0-9]+(.)', lambda x: x.group(1).upper(), text)
    text = re.sub(r'^([a-z])', lambda x: x.group(1).upper(), text, 1)
    return text


def to_snake_case(text: str) -> str:
    text = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', text)
    text = re.sub(r'[^a-zA-Z0-9]+', r'_', text)
    text = re.sub(r'([^A-Z_])([A-Z][a-z])', r'\1_\2', text)
    text = re.sub(r'([^0-9_])([0-9])', r'\1_\2', text)
    text = re.sub(r'([0-9])([^0-9_])', r'\1_\2', text)
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', text)
    return text.lower()
