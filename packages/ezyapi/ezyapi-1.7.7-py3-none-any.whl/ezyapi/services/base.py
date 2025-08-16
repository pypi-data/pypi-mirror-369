from typing import Optional

from ezyapi.repositories.base import EzyRepository

class EzyService:    
    def __init__(self, repository: Optional[EzyRepository] = None):
        self.repository = repository