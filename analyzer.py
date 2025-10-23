import asyncio
import aiohttp
import time
import json
from web3 import Web3
import pyevmasm
from eth_utils import to_bytes
from config import NETWORKS

async def fetch_transaction(session, rpc_url, tx_hash):
    """Fetch transaction data via JSON-RPC."""
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionByHash",
        "params": [tx_hash],
        "id": 1
    }
    async with session.post(rpc_url, json=payload) as response:
        result = await response.json()
        return result.get("result")

async def fetch_transaction_receipt(session, rpc_url, tx_hash):
    """Fetch transaction receipt via JSON-RPC."""
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionReceipt",
        "params": [tx_hash],
        "id": 2
    }
    async with session.post(rpc_url, json=payload) as response:
        result = await response.json()
        return result.get("result")

async def analyze_transaction(rpc_url, tx_hash, output_json=False):
    """Analyze a single transaction with performance focus."""
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        try:
            # Fetch transaction and receipt in parallel
            tx, receipt = await asyncio.gather(
                fetch_transaction(session, rpc_url, tx_hash),
                fetch_transaction_receipt(session, rpc_url, tx_hash)
            )
            if not tx:
                result = {"error": f"Transaction {tx_hash} not found"}
                if output_json:
                    return result
                print(result["error"])
                return

            result = {
                "tx_hash": tx_hash,
                "from": tx.get('from', 'N/A'),
                "to": tx.get('to', 'Contract creation'),
                "gas": int(tx.get('gas', '0x0'), 16),
                "input_data": str(tx.get('input', '0x'))[:100] + "...",
                "status": 'Success' if receipt.get('status') == '0x1' else 'Failed',
                "gas_used": int(receipt.get('gasUsed', '0x0'), 16),
                "analysis_time_ms": round((time.time() - start_time) * 1000, 2)
            }

            # Check if transaction creates a contract
            if not tx.get("to"):
                contract_address = receipt.get("contractAddress")
                if contract_address:
                    result["contract_address"] = contract_address
                    w3 = Web3(Web3.HTTPProvider(rpc_url))
                    bytecode = w3.eth.get_code(contract_address)
                    result["bytecode_preview"] = bytecode.hex()[:100] + "..."

                    # Analyze bytecode
                    try:
                        instructions = pyevmasm.disassemble_all(to_bytes(bytecode))
                        result["bytecode_instructions"] = [str(instr) for instr in list(instructions)[:5]]
                    except Exception as e:
                        result["bytecode_error"] = str(e)
            else:
                result["type"] = "Contract function call"
                w3 = Web3(Web3.HTTPProvider(rpc_url))
                code = w3.eth.get_code(tx.get("to")).hex()
                if code != "0x":
                    result["is_contract"] = True
                    if len(tx.get("input", "")) >= 10:
                        result["function_signature"] = tx.get('input')[:10]

            if output_json:
                return result
            print(f"\nAnalyzing transaction: {tx_hash} (Time: {result['analysis_time_ms']} ms)")
            print(json.dumps(result, indent=2))

        except Exception as e:
            error_result = {"tx_hash": tx_hash, "error": str(e)}
            if output_json:
                return error_result
            print(f"Error analyzing {tx_hash}: {e}")

async def main(rpc_url, tx_hashes, output_json=False):
    """Analyze multiple transactions in parallel."""
    tasks = [analyze_transaction(rpc_url, tx_hash, output_json) for tx_hash in tx_hashes]
    results = await asyncio.gather(*tasks)
    if output_json:
        print(json.dumps(results, indent=2))
    return results