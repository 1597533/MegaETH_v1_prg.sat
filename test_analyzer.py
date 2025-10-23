import pytest
import asyncio
from analyzer import analyze_transaction
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_analyze_transaction_success():
    with patch('aiohttp.ClientSession.post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value.__aenter__.return_value.json.return_value = {
            "result": {"from": "0x123", "gas": "0x1"}
        }
        result = await analyze_transaction("http://test-rpc", "0x123", output_json=True)
        assert "from" in result
        assert result["tx_hash"] == "0x123"