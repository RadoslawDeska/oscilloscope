from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass
class Channel:
    Enabled: bool
    Vdiv: Decimal
    Offset: Decimal
    Coupling: str
    BW_limit: str
    Adjust: str
    Probe: float
    Impedance: float
    Unit: str
    Invert: bool
    
    def __init__(self, **kwargs: dict):
        self.__dict__.update(kwargs)
    
    def __getattr__(self, name: str):
        return self.__dict__.get(name)
    
    def __setattr__(self, name: str, value: Any):
        self.__dict__[name] = value
    
    def __getitem__(self, key: str):
        return self.__dict__[key]
    
    def __setitem__(self, key: str, value):
        self.__dict__[key] = value
    
    def __repr__(self):
        # Include all attributes in the representation of the object
        return f'{self.__class__.__name__}({self.__dict__})'
    
    def to_dict(self) -> dict:
        return self.__dict__ # type: ignore

if __name__ == "__main__":
    c = Channel()
    c.Enabled = True
    c.new_key = 1
    
    print(c)