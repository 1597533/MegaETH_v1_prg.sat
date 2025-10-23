# Configuration for different networks
NETWORKS = {
    "ethereum": {
        "rpc_url": "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID",
        "chain_id": 1
    },
    "megaeth_testnet": {
        "rpc_url": "https://rpc.testnet.megaeth.com",  # Official MegaETH testnet RPC (as of Oct 2025)
        "chain_id": 6342
    }
}

# Default network
DEFAULT_NETWORK = "ethereum"