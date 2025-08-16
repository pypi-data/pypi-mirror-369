from typing import Any, List

class Not:
    def __init__(self, value: Any):
        self.value = value

class LessThan:
    def __init__(self, value: Any):
        self.value = value

class LessThanOrEqual:
    def __init__(self, value: Any):
        self.value = value

class MoreThan:
    def __init__(self, value: Any):
        self.value = value

class MoreThanOrEqual:
    def __init__(self, value: Any):
        self.value = value

class Equal:
    def __init__(self, value: Any):
        self.value = value

class Like:
    def __init__(self, value: str):
        self.value = value

class ILike:
    def __init__(self, value: str):
        self.value = value

class Between:
    def __init__(self, min: Any, max: Any):
        self.min = min
        self.max = max

class In:
    def __init__(self, values: List[Any]):
        self.values = values

class IsNull:
    def __init__(self):
        pass