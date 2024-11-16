import pytest
from unittest.mock import patch, AsyncMock

from payout_agent import PayoutAgent

MOCK_INPUT = {
    "recipient": "example.eth",
    "amount": "0.01",
    "currency": "usdc"
}

@pytest.fixture
def payout_agent():
    return PayoutAgent()

@pytest.mark.asyncio
async def test_process_success(payout_agent):
    """Test successful payout processing"""
    mock_transfer_result = {
        "transaction_id": "0x123",
        "some_detail": "value"
    }

    with patch('payout_agent.transfer', AsyncMock(return_value=mock_transfer_result)):
        result = await payout_agent.process(MOCK_INPUT)

        assert result["status"] == "success"
        assert result["transaction_id"] == "0x123"
        assert result["details"] == mock_transfer_result

@pytest.mark.asyncio
async def test_process_missing_fields(payout_agent):
    """Test payout processing with missing required fields"""
    invalid_input = {"recipient": "example.eth"}  # missing amount and currency

    result = await payout_agent.process(invalid_input)

    assert result["status"] == "error"
    assert "Missing required fields" in result["error"]

@pytest.mark.asyncio
async def test_process_transfer_error(payout_agent):
    """Test payout processing when transfer fails"""
    with patch('payout_agent.transfer', AsyncMock(side_effect=Exception("Transfer failed"))):
        result = await payout_agent.process(MOCK_INPUT)

        assert result["status"] == "error"
        assert result["error"] == "Transfer failed"
