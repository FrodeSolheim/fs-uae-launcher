from dataclasses import dataclass


@dataclass
class ConfigEvent:
    key: str
    value: str
