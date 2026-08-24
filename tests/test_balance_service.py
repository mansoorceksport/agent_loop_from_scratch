import agent_loop_from_scratch
from unittest.mock import MagicMock
from agent_loop_from_scratch.service.balance_service import BalanceServiceImpl
from agent_loop_from_scratch.ports.service.balance import BalanceSuccessModel, BalanceFailureModel
from agent_loop_from_scratch.adapters.repository.balance_mongo import BalanceNotFound, BalanceModel

def test_get_balance_by_date_returns_balance():
    """Happy Path: valid date with matching recored"""
    # ARRANGE
    fake_repo = MagicMock()
    svc = BalanceServiceImpl(fake_repo)
    date_string = "2026-08-10"
    svc.repo.balance_by_date.return_value = BalanceModel(id="", date=date_string, amount=1000)


    # ACT
    result = svc.get_balance_by_date(date_string)

    # ASSERT
    assert isinstance(result, BalanceSuccessModel)

def test_get_balance_by_date_returns_invalid_date():
    """Sad Path: invalid date"""
    # ARRANGE
    fake_repo = MagicMock()
    date_string = "10-08-2026"
    svc = BalanceServiceImpl(fake_repo)
    

    # ACT
    result = svc.get_balance_by_date(date_string)

    # ASSERT
    assert isinstance(result, BalanceFailureModel)

def test_get_balance_by_date_returns_balance_not_found():
    """Sad Path: repo return Model Balance Not found"""
    # ARRANGE
    fake_repo = MagicMock()
    svc = BalanceServiceImpl(fake_repo)
    date_string = "2026-08-10"
    svc.repo.balance_by_date.return_value = BalanceNotFound(message="balance not found")


    # ACT
    result = svc.get_balance_by_date(date_string)

    # ASSERT
    assert isinstance(result, BalanceFailureModel)