from dataclasses import dataclass
from typing import Protocol

@dataclass
class BalanceSuccessModel:
    message: str
    agent_rules: str

@dataclass
class BalanceFailureModel:
    message: str
    agent_rules: str
    

class BalanceService(Protocol):

    def get_balance_by_date(self, date_string: str)->BalanceSuccessModel | BalanceFailureModel:
        ...