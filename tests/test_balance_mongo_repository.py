from unittest.mock import MagicMock
from agent_loop_from_scratch.adapters.repository.balance_mongo import BalanceMongoRepositoryImpl, BalanceModel, BalanceNotFound


def test_balance_by_date_returns_balance():
    """Happy path: valid date with a matching record."""
    # ARRANGE
    fake_client = MagicMock()
    repo = BalanceMongoRepositoryImpl(fake_client)
    repo.balance_collection.find_one.return_value = {
        "date": "2026-01-01",
        "balance": 500000,
    }

    # ACT
    result = repo.balance_by_date("2026-01-01")

    # ASSERT
    assert isinstance(result,BalanceModel)
    repo.balance_collection.find_one.assert_called_once_with(filter={"date": "2026-01-01"})


# def test_balance_by_date_invalid_date():
#     """Sad path: the date string is not a real date."""
#     # ARRANGE
#     fake_client = MagicMock()
#     repo = BalanceMongoRepository(fake_client)

#     # ACT
#     result = repo.balance_by_date("not-a-date")

#     # ASSERT
#     assert result["message"] == "the submitted date format is wrong"
#     repo.balance_collection.find_one.assert_not_called()


def test_balance_by_date_no_record():
    """Sad path: valid date, but no matching document in MongoDB."""
    # ARRANGE
    fake_client = MagicMock()
    repo = BalanceMongoRepositoryImpl(fake_client)
    repo.balance_collection.find_one.return_value = None

    # ACT
    result = repo.balance_by_date("2099-12-31")

    # ASSERT
    assert isinstance(result, BalanceNotFound)
    # assert result["message"] == "there is no record for date 2099-12-31"
