from agent_loop_from_scratch.ports.repository.balance import BalanceRepository, BalanceNotFound
from agent_loop_from_scratch.ports.service.balance import BalanceSuccessModel, BalanceFailureModel
from datetime import date

class BalanceServiceImpl():
    def __init__(self, balance_repo: BalanceRepository):
        self.repo = balance_repo
    
    def get_balance_by_date(self, date_string: str)->BalanceSuccessModel | BalanceFailureModel:

        # validate the date format
        if not self._is_valid_date(date_string):
            return BalanceFailureModel(
                message="the submitted date format is wrong",
                agent_rules="bad date format. date format must be YYYY-MM-DD. fix the date format can call the tool again"
            )
        
        # get the balance by date from repo
        result = self.repo.balance_by_date(date_string)

        # check the response type.
        if isinstance(result,BalanceNotFound):
            return BalanceFailureModel(
                message= f"there is no record for date {date_string}",
                agent_rules= "ask the user if the date is correct",
            )
        
        # compose success response
        message = f"your balance on {date_string} is {result.amount}"
        return BalanceSuccessModel(
            message= message,
            agent_rules= "report exactly as in the message and do not invent any information"
        )
    
    def _is_valid_date(self, date_string:str)->bool:
        try:
            date.fromisoformat(date_string)
            return True
        except ValueError:
            return False