from dataclasses import dataclass
from typing import Protocol


@dataclass
class BalanceModel:
    id: str
    date: str
    amount: int

@dataclass
class BalanceNotFound:
    message: str

class BalanceRepository(Protocol):
    def balance_by_date(self, date_string: str)-> BalanceModel | BalanceNotFound:
        ...