# PureChainLib Python Conversion Guide

## Overview
This comprehensive guide details how to convert the PureChainLib npm package (TypeScript/JavaScript) to a Python library (pip package). PureChainLib is a blockchain library providing zero gas cost transactions, smart contracts, and blockchain interaction APIs.

## Table of Contents
1. [Project Structure](#project-structure)
2. [Dependency Mapping](#dependency-mapping)
3. [Core Module Conversion](#core-module-conversion)
4. [TypeScript to Python Patterns](#typescript-to-python-patterns)
5. [Build and Distribution](#build-and-distribution)
6. [Testing Strategy](#testing-strategy)
7. [API Compatibility](#api-compatibility)
8. [Example Implementations](#example-implementations)

## Project Structure

### Recommended Python Package Structure
```
purechainlib-python/
├── README.md
├── LICENSE
├── setup.py
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
├── tox.ini
├── MANIFEST.in
├── docs/
│   └── conf.py
├── tests/
│   ├── __init__.py
│   ├── test_blockchain.py
│   ├── test_wallet.py
│   ├── test_contracts.py
│   └── test_network.py
├── examples/
│   ├── basic_usage.py
│   ├── smart_contracts.py
│   ├── wallet_usage.py
│   └── network_usage.py
└── purechainlib/
    ├── __init__.py
    ├── __version__.py
    ├── core/
    │   ├── __init__.py
    │   ├── blockchain.py
    │   ├── block.py
    │   ├── transaction.py
    │   ├── wallet.py
    │   ├── consensus.py
    │   ├── smart_contract.py
    │   ├── contract_engine.py
    │   └── network_config.py
    ├── network/
    │   ├── __init__.py
    │   ├── peer.py
    │   ├── discovery.py
    │   └── provider.py
    ├── api/
    │   ├── __init__.py
    │   ├── server.py
    │   ├── realtime.py
    │   └── middleware/
    │       ├── __init__.py
    │       ├── auth.py
    │       ├── error_handler.py
    │       └── validation.py
    ├── storage/
    │   ├── __init__.py
    │   └── database.py
    └── utils/
        ├── __init__.py
        ├── crypto.py
        ├── validators.py
        ├── explorer.py
        └── performance_monitor.py
```

## Dependency Mapping

### NPM to Python Package Equivalents

| NPM Package | Python Equivalent | Purpose |
|------------|------------------|---------|
| express | FastAPI/Flask | Web framework for API |
| ws | websockets | WebSocket support |
| crypto-js | pycryptodome | Cryptographic operations |
| axios | requests/httpx | HTTP client |
| joi | pydantic/marshmallow | Data validation |
| dotenv | python-dotenv | Environment variables |
| events | Built-in (asyncio) | Event emitter pattern |
| cors | fastapi-cors | CORS middleware |
| express-rate-limit | slowapi | Rate limiting |

### requirements.txt
```txt
# Core dependencies
pycryptodome>=3.19.0
fastapi>=0.109.0
uvicorn>=0.27.0
websockets>=12.0
httpx>=0.26.0
pydantic>=2.5.0
python-dotenv>=1.0.0
slowapi>=0.1.9

# Database
sqlalchemy>=2.0.0
aiosqlite>=0.19.0

# Utilities
python-dateutil>=2.8.2
click>=8.1.7
colorama>=0.4.6
```

### requirements-dev.txt
```txt
-r requirements.txt

# Testing
pytest>=7.4.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0

# Development
black>=23.12.0
flake8>=7.0.0
mypy>=1.8.0
isort>=5.13.0
pre-commit>=3.6.0

# Documentation
sphinx>=7.2.0
sphinx-rtd-theme>=2.0.0
```

## Core Module Conversion

### 1. Main Entry Point (index.ts → __init__.py)

**TypeScript (src/index.ts):**
```typescript
export class PureChain {
  public blockchain: Blockchain;
  public contractEngine: ContractEngine;
  
  constructor(config: IPureChainConfig = {}) {
    this.blockchain = new Blockchain(config.blockchain);
    this.contractEngine = new ContractEngine(this.blockchain);
  }
  
  async start(): Promise<void> {
    await this.provider.connect();
  }
}
```

**Python (purechainlib/__init__.py):**
```python
from typing import Optional, Dict, Any
from .core.blockchain import Blockchain, BlockchainConfig
from .core.contract_engine import ContractEngine
from .network.provider import NetworkProvider

class PureChain:
    """Main PureChain client class."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize PureChain instance.
        
        Args:
            config: Configuration dictionary
        """
        config = config or {}
        
        self.blockchain = Blockchain(config.get('blockchain', {}))
        self.contract_engine = ContractEngine(
            self.blockchain,
            config.get('gas_price'),
            self.wallet
        )
        self.provider: Optional[NetworkProvider] = None
    
    async def start(self) -> None:
        """Start the PureChain client."""
        self.provider = NetworkProvider(self.network_config)
        await self.provider.connect()
        print(f"Connected to {self.network_config['name']}")

# Export main classes
__all__ = [
    'PureChain',
    'Blockchain',
    'Block',
    'Transaction',
    'Wallet',
    'SmartContract',
    'ContractEngine',
]
```

### 2. Blockchain Core (blockchain.ts → blockchain.py)

**TypeScript:**
```typescript
export interface IBlockchainConfig {
  difficulty?: number;
  consensusType?: ConsensusType;
}

export class Blockchain {
  private chain: Block[];
  private difficulty: number;
  
  constructor(config: IBlockchainConfig = {}) {
    this.difficulty = config.difficulty || 4;
    this.chain = [this.createGenesisBlock()];
  }
}
```

**Python:**
```python
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

@dataclass
class BlockchainConfig:
    """Configuration for blockchain."""
    difficulty: int = 4
    consensus_type: str = 'proof_of_work'
    enable_performance_monitoring: bool = True

class Blockchain:
    """Core blockchain implementation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize blockchain.
        
        Args:
            config: Configuration dictionary
        """
        self.config = BlockchainConfig(**(config or {}))
        self.chain: List[Block] = [self._create_genesis_block()]
        self.difficulty = self.config.difficulty
        self.pending_transactions: List[Transaction] = []
    
    def _create_genesis_block(self) -> 'Block':
        """Create the genesis block."""
        from .block import Block
        return Block(0, [], "0", timestamp=0)
```

### 3. Cryptographic Utilities (crypto.ts → crypto.py)

**TypeScript:**
```typescript
import * as CryptoJS from 'crypto-js';

export class CryptoUtils {
  static hash(data: string): string {
    return CryptoJS.SHA256(data).toString();
  }
}
```

**Python:**
```python
import hashlib
import json
from typing import Any, Union
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

class CryptoUtils:
    """Cryptographic utility functions."""
    
    @staticmethod
    def hash(data: Union[str, bytes, dict]) -> str:
        """Generate SHA256 hash.
        
        Args:
            data: Data to hash
            
        Returns:
            Hexadecimal hash string
        """
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def generate_keypair() -> tuple[str, str]:
        """Generate RSA key pair.
        
        Returns:
            Tuple of (private_key, public_key) as PEM strings
        """
        key = RSA.generate(2048)
        private_key = key.export_key().decode('utf-8')
        public_key = key.publickey().export_key().decode('utf-8')
        return private_key, public_key
```

### 4. Web API Server (server.ts → server.py)

**TypeScript (Express):**
```typescript
import express from 'express';

export class BlockchainAPI {
  private app: express.Application;
  
  constructor(blockchain: Blockchain) {
    this.app = express();
    this.setupRoutes();
  }
  
  private setupRoutes(): void {
    this.app.get('/blocks', (req, res) => {
      res.json(this.blockchain.getChain());
    });
  }
}
```

**Python (FastAPI):**
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

class BlockchainAPI:
    """REST API for blockchain interaction."""
    
    def __init__(self, blockchain: 'Blockchain', config: Optional[dict] = None):
        """Initialize API server.
        
        Args:
            blockchain: Blockchain instance
            config: API configuration
        """
        self.blockchain = blockchain
        self.app = FastAPI(title="PureChain API", version="1.0.0")
        self.config = config or {}
        self._setup_middleware()
        self._setup_routes()
    
    def _setup_middleware(self):
        """Configure middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.get("/blocks")
        async def get_blocks():
            """Get all blocks in the chain."""
            return [block.to_dict() for block in self.blockchain.chain]
        
        @self.app.post("/transactions")
        async def create_transaction(transaction: dict):
            """Create a new transaction."""
            tx = self.blockchain.create_transaction(
                transaction['from'],
                transaction['to'],
                transaction['amount']
            )
            return {"transaction_id": tx.hash}
    
    async def start(self, host: str = "0.0.0.0", port: int = 3000):
        """Start the API server."""
        import uvicorn
        await uvicorn.run(self.app, host=host, port=port)
```

## TypeScript to Python Patterns

### 1. Interfaces → Dataclasses/TypedDict

**TypeScript:**
```typescript
interface ITransaction {
  from: string;
  to: string;
  amount: number;
  timestamp?: number;
}
```

**Python:**
```python
from dataclasses import dataclass, field
from typing import Optional
import time

@dataclass
class TransactionData:
    """Transaction data structure."""
    from_address: str
    to_address: str
    amount: float
    timestamp: Optional[float] = field(default_factory=time.time)
```

### 2. Enums

**TypeScript:**
```typescript
export enum ConsensusType {
  PROOF_OF_WORK = 'proof-of-work',
  PROOF_OF_STAKE = 'proof-of-stake'
}
```

**Python:**
```python
from enum import Enum

class ConsensusType(Enum):
    """Consensus mechanism types."""
    PROOF_OF_WORK = 'proof-of-work'
    PROOF_OF_STAKE = 'proof-of-stake'
```

### 3. Async/Await Patterns

**TypeScript:**
```typescript
async function connectToNetwork(): Promise<void> {
  await this.provider.connect();
}
```

**Python:**
```python
async def connect_to_network(self) -> None:
    """Connect to the network."""
    await self.provider.connect()
```

### 4. Event Emitters

**TypeScript:**
```typescript
import { EventEmitter } from 'events';

class Blockchain extends EventEmitter {
  addBlock(block: Block): void {
    this.emit('block-added', block);
  }
}
```

**Python:**
```python
import asyncio
from typing import Dict, List, Callable

class EventEmitter:
    """Event emitter implementation."""
    
    def __init__(self):
        self._events: Dict[str, List[Callable]] = {}
    
    def on(self, event: str, callback: Callable):
        """Register event listener."""
        if event not in self._events:
            self._events[event] = []
        self._events[event].append(callback)
    
    async def emit(self, event: str, *args, **kwargs):
        """Emit an event."""
        if event in self._events:
            for callback in self._events[event]:
                if asyncio.iscoroutinefunction(callback):
                    await callback(*args, **kwargs)
                else:
                    callback(*args, **kwargs)
```

## Build and Distribution

### 1. setup.py
```python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="purechainlib",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="PureChain blockchain library - Zero gas cost blockchain with smart contracts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/purechainlib-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pycryptodome>=3.19.0",
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "websockets>=12.0",
        "httpx>=0.26.0",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=4.1.0",
            "black>=23.12.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "purechain=purechainlib.cli:main",
        ],
    },
)
```

### 2. pyproject.toml
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "purechainlib"
version = "1.0.0"
description = "PureChain blockchain library - Zero gas cost blockchain"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
keywords = ["blockchain", "purechain", "cryptocurrency", "smart-contracts"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
]

dependencies = [
    "pycryptodome>=3.19.0",
    "fastapi>=0.109.0",
    "uvicorn>=0.27.0",
    "websockets>=12.0",
    "httpx>=0.26.0",
    "pydantic>=2.5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.23.0",
    "black>=23.12.0",
    "mypy>=1.8.0",
]

[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310', 'py311']

[tool.isort]
profile = "black"
line_length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --cov=purechainlib --cov-report=term-missing"
```

## Testing Strategy

### 1. Test Structure
```python
# tests/test_blockchain.py
import pytest
from purechainlib import PureChain, Blockchain

@pytest.mark.asyncio
async def test_blockchain_initialization():
    """Test blockchain initialization."""
    chain = PureChain()
    assert chain.blockchain is not None
    assert len(chain.blockchain.chain) == 1  # Genesis block

@pytest.mark.asyncio
async def test_add_transaction():
    """Test adding a transaction."""
    chain = PureChain()
    await chain.start()
    
    tx = await chain.blockchain.create_transaction(
        from_address="alice",
        to_address="bob",
        amount=100
    )
    
    assert tx is not None
    assert tx.from_address == "alice"
    assert tx.amount == 100
```

### 2. Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=purechainlib

# Run specific test file
pytest tests/test_blockchain.py

# Run with verbose output
pytest -v
```

## API Compatibility

### Maintaining API Compatibility
The Python library should maintain similar API patterns to the JavaScript version:

**JavaScript:**
```javascript
const purechain = new PureChain({ networkConfig: 'testnet' });
await purechain.start();
const blocks = purechain.blockchain.getChain();
```

**Python:**
```python
purechain = PureChain({'network_config': 'testnet'})
await purechain.start()
blocks = purechain.blockchain.get_chain()
```

### Naming Conventions
- JavaScript camelCase → Python snake_case
- Keep class names in PascalCase
- Constants in UPPER_SNAKE_CASE

## Example Implementations

### 1. Basic Usage (examples/basic_usage.py)
```python
import asyncio
from purechainlib import PureChain

async def main():
    """Basic PureChain usage example."""
    
    # Initialize PureChain
    purechain = PureChain({
        'network_config': 'testnet',
        'enable_performance_monitoring': True
    })
    
    # Start the client
    await purechain.start()
    print(f"Connected to {purechain.network_config['name']}")
    
    # Create a wallet
    wallet = purechain.wallet
    address = wallet.get_address()
    print(f"Wallet address: {address}")
    
    # Create a transaction
    tx = await purechain.blockchain.create_transaction(
        from_address=address,
        to_address="recipient_address",
        amount=100
    )
    print(f"Transaction created: {tx.hash}")
    
    # Mine a block
    block = await purechain.blockchain.mine_pending_transactions(address)
    print(f"Block mined: {block.hash}")
    
    # Get blockchain stats
    stats = purechain.get_performance_stats()
    print(f"Average latency: {stats['average_latency']}ms")
    print(f"Current TPS: {purechain.get_current_tps()}")
    
    # Stop the client
    await purechain.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Smart Contract Usage (examples/smart_contracts.py)
```python
import asyncio
from purechainlib import PureChain, SmartContract

async def main():
    """Smart contract deployment example."""
    
    purechain = PureChain({'network_config': 'testnet'})
    await purechain.start()
    
    # Create a simple token contract
    contract_code = '''
    class TokenContract:
        def __init__(self):
            self.balances = {}
            self.total_supply = 1000000
        
        def transfer(self, from_addr, to_addr, amount):
            if self.balances.get(from_addr, 0) >= amount:
                self.balances[from_addr] -= amount
                self.balances[to_addr] = self.balances.get(to_addr, 0) + amount
                return True
            return False
    '''
    
    # Deploy contract
    contract = SmartContract(
        contract_type='TOKEN',
        code=contract_code,
        initial_state={'name': 'PureToken', 'symbol': 'PURE'}
    )
    
    result = await purechain.contract_engine.deploy(contract)
    print(f"Contract deployed at: {result['address']}")
    
    # Execute contract method
    execution = await purechain.contract_engine.execute(
        contract_address=result['address'],
        method='transfer',
        params={
            'from_addr': 'alice',
            'to_addr': 'bob',
            'amount': 100
        }
    )
    
    print(f"Transfer result: {execution['result']}")
    
    await purechain.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## Building and Publishing

### 1. Build the Package
```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# This creates:
# - dist/purechainlib-1.0.0.tar.gz (source distribution)
# - dist/purechainlib-1.0.0-py3-none-any.whl (wheel)
```

### 2. Test Locally
```bash
# Install locally for testing
pip install -e .

# Or install from wheel
pip install dist/purechainlib-1.0.0-py3-none-any.whl
```

### 3. Publish to PyPI
```bash
# Test on TestPyPI first
twine upload --repository testpypi dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ purechainlib

# Publish to PyPI
twine upload dist/*
```

## Development Workflow

### 1. Setup Development Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 2. Code Quality Tools
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

### 3. Documentation
```bash
# Generate API documentation
cd docs
sphinx-quickstart
sphinx-apidoc -o source ../purechainlib
make html
```

## Migration Checklist

- [ ] Set up Python project structure
- [ ] Convert TypeScript interfaces to Python dataclasses
- [ ] Implement core blockchain modules
- [ ] Convert crypto utilities using pycryptodome
- [ ] Implement API server with FastAPI
- [ ] Convert WebSocket functionality
- [ ] Implement storage layer
- [ ] Convert network modules
- [ ] Write comprehensive tests
- [ ] Create example scripts
- [ ] Write documentation
- [ ] Set up CI/CD pipeline
- [ ] Publish to PyPI

## Common Pitfalls and Solutions

### 1. Async/Await Differences
- Python requires `asyncio.run()` for top-level async
- Use `asyncio.create_task()` for concurrent operations
- Remember to await all async operations

### 2. Type Hints
- Use `typing` module for complex types
- Consider using `mypy` for static type checking
- Use `Optional[]` for nullable types

### 3. Module Imports
- Use relative imports within package
- Avoid circular imports by careful module design
- Use `__all__` to control public API

### 4. Performance Considerations
- Use `asyncio` for I/O-bound operations
- Consider `multiprocessing` for CPU-bound tasks
- Profile code with `cProfile` for optimization

## Support and Resources

- Original NPM Package: https://www.npmjs.com/package/purechainlib
- Python Packaging Guide: https://packaging.python.org/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Pydantic Documentation: https://docs.pydantic.dev/

## Conclusion

This guide provides a comprehensive roadmap for converting PureChainLib from TypeScript/JavaScript to Python. The key is maintaining API compatibility while leveraging Python's strengths and ecosystem. Focus on:

1. Clean, Pythonic code structure
2. Comprehensive type hints
3. Async/await for performance
4. Thorough testing
5. Clear documentation

By following this guide, you can create a fully functional Python version of PureChainLib that maintains feature parity with the original npm package while providing a native Python experience for developers.