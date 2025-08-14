# PureChainLib Python

A Python implementation of the PureChain blockchain library - Zero gas cost blockchain with smart contracts, explorer API, and complete toolkit.

## Features

- **Zero Gas Costs** - Revolutionary blockchain with NO gas fees for any operation
- **Smart Contract Platform** - 6 contract types fully implemented
- **Performance Monitoring** - Built-in latency tracking and TPS calculation
- **PureChain Network Integration** - Built-in connection to PureChain testnet
- **Complete Blockchain Implementation** - Mining, validation, consensus, and chain management
- **Enhanced Explorer API** - Network stats, rich list, faucet, printable receipts
- **WebSocket Support** - Real-time blockchain events and updates

## Installation

```bash
pip install purechainlib
```

## Quick Start

```python
import asyncio
from purechainlib import PureChain

async def main():
    # Connect to PureChain network
    purechain = PureChain({'network_config': 'testnet'})
    
    await purechain.start()
    print(f"Connected to {purechain.network_config['name']}!")
    
    # Check performance metrics
    tps = purechain.get_current_tps()
    print(f"Current TPS: {tps}")
    
    await purechain.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## Usage Guide

### 1. Connect to PureChain Network

```python
from purechainlib import PureChain

# Connect to the real PureChain network
purechain = PureChain({'network_config': 'testnet'})

await purechain.start()
print(f"Connected to: {purechain.network_config['name']}")
```

### 2. Monitor Your Performance

```python
# Track your operations in real-time
stats = purechain.get_performance_stats()
print(f"Your average latency: {stats['average_latency']}ms")
print(f"Your current TPS: {purechain.get_current_tps()}")
print(f"Your P99 latency: {stats['p99_latency']}ms")

# Get detailed performance report
print(purechain.get_performance_report(detailed=True))

# Export metrics for analysis
metrics = purechain.export_performance_metrics()
```

### 3. Create Transactions

```python
# Create a transaction (local operation)
purechain.blockchain.create_transaction(
    from_address='alice',
    to_address='bob',
    amount=100,
    timestamp=time.time()
)

# Check your transaction creation performance
tx_stats = purechain.get_performance_stats('create_transaction')
print(f"Avg transaction creation: {tx_stats['average_latency']}ms")
```

### 4. Deploy Smart Contracts

```python
from purechainlib import ContractType

# Deploy a token contract
result = await purechain.contract_engine.deploy_contract({
    'type': ContractType.TOKEN,
    'name': 'MyToken',
    'symbol': 'MTK',
    'initial_supply': 1000000
}, 'deployer', 0)

print(f"Contract address: {result['contract_address']}")
```

## Smart Contracts

### Available Contract Types

1. **TOKEN** - ERC20-like token contract with pause, vesting, and minting capabilities
2. **NFT** - NFT collection contract with royalties, creator tracking, and metadata
3. **ESCROW** - Secure payment escrow with dispute resolution and arbitration
4. **VOTING** - Advanced governance voting with weighted votes and quorum requirements
5. **STORAGE** - Access-controlled key-value storage with permissions and versioning
6. **CUSTOM** - User-defined contract logic

### Deploy Contracts

```python
from purechainlib import ContractType

# Token Contract
token = await purechain.contract_engine.deploy_contract({
    'type': ContractType.TOKEN,
    'name': 'MyToken',
    'symbol': 'MTK',
    'initial_supply': 1000000,
    'decimals': 18
}, 'deployer_address', 0)  # 0 gas cost!

# NFT Collection
nft = await purechain.contract_engine.deploy_contract({
    'type': ContractType.NFT,
    'name': 'MyNFTs',
    'metadata': {
        'description': 'My NFT Collection',
        'max_supply': 10000
    }
}, 'artist_address', 0)
```

### Contract Interaction

```python
# Get deployed contract
contract = result['contract']

# Execute methods (all free!)
contract.execute('method_name', [param1, param2], 'caller_address')

# Examples:
# Token transfer
contract.execute('transfer', ['recipient', 100], 'sender')

# NFT minting
contract.execute('mint_nft', ['recipient', {'token_id': 1, 'name': 'NFT #1'}], 'minter')
```

## Complete Example

```python
import asyncio
from purechainlib import PureChain, ContractType

async def build_dapp():
    purechain = PureChain({'network_config': 'testnet'})
    await purechain.start()
    
    print("Building a complete DApp on PureChain...\n")
    
    # Deploy governance token
    token = await purechain.contract_engine.deploy_contract({
        'type': ContractType.TOKEN,
        'name': 'GovernanceToken',
        'symbol': 'GOV',
        'initial_supply': 10000000,
        'decimals': 18
    }, 'dapp_owner', 0)
    
    # Deploy voting contract
    voting = await purechain.contract_engine.deploy_contract({
        'type': ContractType.VOTING,
        'name': 'Governance'
    }, 'dapp_owner', 0)
    
    if token['success'] and voting['success']:
        print("DApp contracts deployed:")
        print(f"  Token: {token['contract_address']}")
        print(f"  Voting: {voting['contract_address']}")
        
        # Distribute tokens
        token_contract = token['contract']
        token_contract.execute('transfer', ['user1', 1000], 'dapp_owner')
        token_contract.execute('transfer', ['user2', 1000], 'dapp_owner')
        
        # Create a proposal
        voting_contract = voting['contract']
        voting_contract.execute('create_proposal', [
            'Should we add new features?',
            time.time() + 86400
        ], 'user1')
        
        # Cast votes
        voting_contract.execute('vote', [0, True], 'user1')
        voting_contract.execute('vote', [0, True], 'user2')
        
        print("\nDApp is live with:")
        print("  2 users with tokens")
        print("  1 active proposal")
        print("  2 votes cast")
        print("  Total gas cost: 0!")
    
    await purechain.stop()

if __name__ == "__main__":
    asyncio.run(build_dapp())
```

## API Documentation

### PureChain Class

```python
purechain = PureChain(config)

# Core Methods
await purechain.start()                     # Start blockchain
await purechain.stop()                      # Stop blockchain
await purechain.switch_network(network)     # Switch network

# Performance Monitoring Methods
purechain.get_current_tps()                 # Get real-time TPS
purechain.get_average_tps(period_ms)        # Get average TPS over period
purechain.get_performance_stats(operation)  # Get detailed performance metrics
purechain.get_performance_report(detailed)  # Get formatted performance report
purechain.reset_performance_metrics()       # Reset all metrics
purechain.export_performance_metrics()      # Export metrics as JSON

# Wallet Methods
purechain.wallet.create_wallet(label)                     # Create new wallet
purechain.wallet.import_wallet(private_key, label)        # Import from private key
purechain.wallet.get_wallet(label_or_address)             # Get specific wallet
purechain.wallet.list_wallets()                           # List all wallets
purechain.wallet.sign_transaction(tx_data, wallet)        # Sign transaction
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/purechainlib-python.git
cd purechainlib-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=purechainlib

# Run specific test file
pytest tests/test_blockchain.py
```

### Code Quality

```bash
# Format code
black purechainlib tests

# Sort imports
isort purechainlib tests

# Lint code
flake8 purechainlib tests

# Type checking
mypy purechainlib
```

## License

MIT

## Links

- [GitHub Repository](https://github.com/yourusername/purechainlib-python)
- [PyPI Package](https://pypi.org/project/purechainlib/)
- [Documentation](https://purechainlib-python.readthedocs.io/)
- [Original NPM Package](https://www.npmjs.com/package/purechainlib)

## Support

For questions and support, please open an issue on GitHub.

---

**Version:** 1.0.0  
**Python:** 3.8+  
**Network:** PureChain Testnet (Chain ID: 900520900520)  
**Gas Cost:** 0 (Free transactions)  
**Status:** Development