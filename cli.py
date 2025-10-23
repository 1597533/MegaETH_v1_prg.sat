#!/usr/bin/env python3
import argparse
import asyncio
import sys
from analyzer import main
from config import NETWORKS, DEFAULT_NETWORK

def load_tx_hashes_from_file(filename):
    """Load transaction hashes from a file (one per line)."""
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
        sys.exit(1)

def main_cli():
    parser = argparse.ArgumentParser(description="MegaETH Transaction Analyzer CLI")
    parser.add_argument('--tx-hash', type=str, help="Single transaction hash to analyze")
    parser.add_argument('--tx-file', type=str, help="File with transaction hashes (one per line)")
    parser.add_argument('--num-txs', type=int, default=1, help="Number of example txs to analyze (if no tx provided)")
    parser.add_argument('--network', choices=list(NETWORKS.keys()), default=DEFAULT_NETWORK, help="Network to use")
    parser.add_argument('--json', action='store_true', help="Output in JSON format")
    args = parser.parse_args()

    rpc_url = NETWORKS[args.network]["rpc_url"]
    tx_hashes = []

    if args.tx_hash:
        tx_hashes = [args.tx_hash]
    elif args.tx_file:
        tx_hashes = load_tx_hashes_from_file(args.tx_file)
    else:
        # Example txs (replace with real ones; for demo)
        tx_hashes = ["0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"] * args.num_txs

    if not tx_hashes:
        print("No transaction hashes provided.")
        sys.exit(1)

    asyncio.run(main(rpc_url, tx_hashes, args.json))

if __name__ == "__main__":
    main_cli()