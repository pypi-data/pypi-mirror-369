

from typing import Optional
from ..._base_tenant_user_model import BaseTenantUserDBModel as BaseDBModel
from .indexing.message_indexes import Indexes


class Message(BaseDBModel):
    def __init__(self) -> None:
        super().__init__()

        self.content: Optional[str] = None
        self.sender_id: Optional[str] = None

        Indexes(self)