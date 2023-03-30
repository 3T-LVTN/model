from dataclasses import dataclass

@dataclass
class Context: 
    '''context for easily pass object through function'''
    method: str