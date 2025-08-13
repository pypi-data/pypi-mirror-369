from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class CBEReceipt:
    success: bool
    payer: Optional[str] = None
    payer_account: Optional[str] = None
    receiver: Optional[str] = None
    receiver_account: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[datetime] = None
    reference: Optional[str] = None
    error: Optional[str] = None