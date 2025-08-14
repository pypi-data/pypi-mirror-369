"""
Direct PureChain Network Connection
Connects directly to the PureChain node RPC endpoint
"""

import json
from typing import Any, Dict, List, Optional, Union
from web3 import Web3, HTTPProvider
try:
    from web3 import WebsocketProvider
except ImportError:
    from web3 import WebSocketProvider as WebsocketProvider
from web3.contract import Contract
from web3.types import TxParams, Wei
from eth_typing import Address
from rich.console import Console
from rich.panel import Panel

from purechainlib.account import Account
from purechainlib.compiler import SolidityCompiler
from purechainlib.exceptions import PureChainException, NetworkException

console = Console()


class PureChainDirect:
    """
    Direct connection to PureChain network via RPC
    This bypasses the REST API and connects directly to the blockchain
    """
    
    # Network configurations with proper RPC endpoints
    NETWORKS = {
        'mainnet': {
            'name': 'PureChain Mainnet',
            'rpc_url': 'https://rpc.purechain.network',  # Need actual RPC URL
            'chain_id': 1,
            'explorer': 'https://explorer.purechain.network'
        },
        'testnet': {
            'name': 'PureChain Testnet',
            'rpc_url': 'https://testnet-rpc.purechain.network',  # Need actual RPC URL
            'chain_id': 3,
            'explorer': 'https://testnet-explorer.purechain.network'
        },
        'local': {
            'name': 'Local PureChain',
            'rpc_url': 'http://localhost:8545',
            'chain_id': 1337,
            'explorer': 'http://localhost:3000'
        }
    }
    
    def _setup_middleware(self):
        """Setup Web3 middleware with compatibility for all versions"""
        try:
            # First try Web3 v6+ with geth_poa_middleware
            from web3.middleware import geth_poa_middleware
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        except (ImportError, AttributeError):
            try:
                # Try importing with module patch for compatibility
                import web3.middleware
                from web3.middleware import geth_poa_middleware
                
                # Patch for older Web3 versions expecting ExtraDataToPOAMiddleware
                if not hasattr(web3.middleware, "ExtraDataToPOAMiddleware"):
                    web3.middleware.ExtraDataToPOAMiddleware = geth_poa_middleware
                
                self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            except ImportError:
                try:
                    # Fallback to older Web3 versions
                    from web3.middleware import ExtraDataToPOAMiddleware
                    self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
                except ImportError:
                    # If all fails, PureChain may work without POA middleware
                    pass
    
    def __init__(self, network: str = 'testnet', rpc_url: Optional[str] = None):
        """
        Initialize direct connection to PureChain
        
        Args:
            network: Network name ('mainnet', 'testnet', 'local')
            rpc_url: Custom RPC URL (overrides network setting)
        """
        if rpc_url:
            # Use custom RPC
            self.rpc_url = rpc_url
            self.network_name = 'custom'
            self.chain_id = None  # Will be fetched from network
        else:
            # Use predefined network
            if network not in self.NETWORKS:
                raise NetworkException(f"Unknown network: {network}")
            config = self.NETWORKS[network]
            self.rpc_url = config['rpc_url']
            self.network_name = config['name']
            self.chain_id = config['chain_id']
        
        # Initialize Web3 connection
        self._init_web3()
        
        # Initialize compiler
        self.compiler = SolidityCompiler()
        
        # Account management
        self._account: Optional[Account] = None
        
        # Display connection info
        self._display_connection_info()
    
    def _init_web3(self):
        """Initialize Web3 connection"""
        try:
            # Create provider based on URL type
            if self.rpc_url.startswith('ws://') or self.rpc_url.startswith('wss://'):
                provider = WebsocketProvider(self.rpc_url)
            else:
                provider = HTTPProvider(self.rpc_url)
            
            # Initialize Web3
            self.w3 = Web3(provider)
            
            # Add POA middleware for PureChain - handle all Web3 versions
            self._setup_middleware()
            
            # Check connection
            if not self.w3.is_connected():
                raise NetworkException(f"Cannot connect to {self.rpc_url}")
            
            # Get chain ID if not set
            if self.chain_id is None:
                self.chain_id = self.w3.eth.chain_id
            
            # Get network info
            self.latest_block = self.w3.eth.block_number
            
            console.print(f"[green]✓[/green] Connected to PureChain")
            
        except Exception as e:
            raise NetworkException(f"Failed to connect: {str(e)}")
    
    def _display_connection_info(self):
        """Display connection information"""
        console.print(Panel.fit(
            f"[bold green]PureChain Direct Connection[/bold green]\n"
            f"Network: {self.network_name}\n"
            f"RPC URL: {self.rpc_url}\n"
            f"Chain ID: {self.chain_id}\n"
            f"Latest Block: {self.latest_block}\n"
            f"[bold yellow]Gas Price: 0 (Zero cost!)[/bold yellow]",
            title="🔗 Direct Connection",
            border_style="green"
        ))
    
    def connect_account(self, private_key: str) -> Account:
        """
        Connect an account using private key
        
        Args:
            private_key: Private key hex string
            
        Returns:
            Connected Account
        """
        self._account = Account.from_key(private_key)
        
        # Check balance
        balance_wei = self.w3.eth.get_balance(self._account.address)
        balance_eth = self.w3.from_wei(balance_wei, 'ether')
        
        console.print(f"[green]✓[/green] Account connected: {self._account.address}")
        console.print(f"  Balance: {balance_eth} PURE")
        
        return self._account
    
    def get_balance(self, address: Optional[str] = None) -> float:
        """
        Get balance for an address
        
        Args:
            address: Address to check (uses connected account if None)
            
        Returns:
            Balance in PURE tokens
        """
        if not address:
            if not self._account:
                raise PureChainException("No account connected")
            address = self._account.address
        
        balance_wei = self.w3.eth.get_balance(Web3.to_checksum_address(address))
        return float(self.w3.from_wei(balance_wei, 'ether'))
    
    def compile_contract(self, source_code: str) -> Dict[str, Any]:
        """
        Compile Solidity contract
        
        Args:
            source_code: Solidity source code
            
        Returns:
            Compiled contract data with ABI and bytecode
        """
        compiled = self.compiler.compile_source(source_code)
        
        # Get the first (or main) contract
        contract_name = list(compiled.keys())[0]
        contract_data = compiled[contract_name]
        
        return {
            'name': contract_name,
            'abi': contract_data.abi,
            'bytecode': contract_data.bytecode,
            'contract': contract_data
        }
    
    def deploy_contract(self, abi: List, bytecode: str, *constructor_args) -> Contract:
        """
        Deploy a smart contract to PureChain
        
        Args:
            abi: Contract ABI
            bytecode: Contract bytecode
            *constructor_args: Constructor arguments
            
        Returns:
            Deployed contract instance
        """
        if not self._account:
            raise PureChainException("No account connected")
        
        # Create contract instance
        contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)
        
        # Build constructor transaction
        constructor_tx = contract.constructor(*constructor_args).build_transaction({
            'from': self._account.address,
            'nonce': self.w3.eth.get_transaction_count(self._account.address),
            'gas': 3000000,  # Gas limit (computation units)
            'gasPrice': 0,   # GAS PRICE IS ZERO!
            'chainId': self.chain_id
        })
        
        console.print(f"[yellow]Deploying contract...[/yellow]")
        console.print(f"  Gas Limit: {constructor_tx['gas']} units")
        console.print(f"  Gas Price: 0 (FREE!)")
        
        # Sign transaction
        signed_tx = self._account._account.sign_transaction(constructor_tx)
        
        # Send transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        console.print(f"  Transaction: {tx_hash.hex()}")
        
        # Wait for receipt
        console.print(f"  Waiting for confirmation...")
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if tx_receipt.status == 1:
            contract_address = tx_receipt.contractAddress
            console.print(f"[green]✓[/green] Contract deployed at: {contract_address}")
            console.print(f"  Block: {tx_receipt.blockNumber}")
            console.print(f"  Gas Used: {tx_receipt.gasUsed} units")
            console.print(f"  Cost: 0 PURE (Zero gas price!)")
            
            # Return contract instance
            return self.w3.eth.contract(address=contract_address, abi=abi)
        else:
            raise PureChainException("Contract deployment failed")
    
    def call_contract(self, contract: Contract, method: str, *args) -> Any:
        """
        Call a contract method (read-only)
        
        Args:
            contract: Contract instance
            method: Method name
            *args: Method arguments
            
        Returns:
            Method result
        """
        func = contract.functions[method](*args)
        return func.call()
    
    def send_transaction(self, contract: Contract, method: str, *args) -> Dict[str, Any]:
        """
        Send a transaction to contract (state-changing)
        
        Args:
            contract: Contract instance
            method: Method name
            *args: Method arguments
            
        Returns:
            Transaction receipt
        """
        if not self._account:
            raise PureChainException("No account connected")
        
        # Get function
        func = contract.functions[method](*args)
        
        # Build transaction
        tx = func.build_transaction({
            'from': self._account.address,
            'nonce': self.w3.eth.get_transaction_count(self._account.address),
            'gas': 200000,  # Gas limit
            'gasPrice': 0,  # ZERO GAS PRICE!
            'chainId': self.chain_id
        })
        
        # Sign and send
        signed_tx = self._account._account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for receipt
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            'transactionHash': receipt.transactionHash.hex(),
            'blockNumber': receipt.blockNumber,
            'gasUsed': receipt.gasUsed,
            'gasCost': 0,  # Always 0 on PureChain!
            'status': receipt.status
        }
    
    def transfer_pure(self, to_address: str, amount: float) -> Dict[str, Any]:
        """
        Transfer PURE tokens to another address
        
        Args:
            to_address: Recipient address
            amount: Amount in PURE
            
        Returns:
            Transaction receipt
        """
        if not self._account:
            raise PureChainException("No account connected")
        
        # Build transaction
        tx = {
            'from': self._account.address,
            'to': Web3.to_checksum_address(to_address),
            'value': self.w3.to_wei(amount, 'ether'),
            'nonce': self.w3.eth.get_transaction_count(self._account.address),
            'gas': 21000,  # Standard transfer gas
            'gasPrice': 0,  # ZERO GAS PRICE!
            'chainId': self.chain_id
        }
        
        console.print(f"[yellow]Sending {amount} PURE to {to_address[:10]}...[/yellow]")
        console.print(f"  Gas Price: 0 (FREE!)")
        
        # Sign and send
        signed_tx = self._account._account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for receipt
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt.status == 1:
            console.print(f"[green]✓[/green] Transfer successful!")
            console.print(f"  Transaction: {receipt.transactionHash.hex()}")
            console.print(f"  Gas Used: {receipt.gasUsed} units")
            console.print(f"  Cost: 0 PURE")
        
        return {
            'transactionHash': receipt.transactionHash.hex(),
            'blockNumber': receipt.blockNumber,
            'gasUsed': receipt.gasUsed,
            'gasCost': 0,
            'status': receipt.status
        }
    
    def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction details"""
        tx = self.w3.eth.get_transaction(tx_hash)
        receipt = self.w3.eth.get_transaction_receipt(tx_hash)
        
        return {
            'hash': tx.hash.hex(),
            'from': tx['from'],
            'to': tx['to'],
            'value': str(tx['value']),
            'gas': tx['gas'],
            'gasPrice': tx['gasPrice'],  # Should be 0
            'blockNumber': receipt.blockNumber,
            'status': receipt.status,
            'gasUsed': receipt.gasUsed,
            'totalCost': 0  # Always 0 on PureChain!
        }
    
    def get_block(self, block_number: Union[int, str] = 'latest') -> Dict[str, Any]:
        """Get block information"""
        block = self.w3.eth.get_block(block_number)
        
        return {
            'number': block.number,
            'hash': block.hash.hex() if block.hash else None,
            'timestamp': block.timestamp,
            'miner': block.miner,
            'transactions': [tx.hex() for tx in block.transactions],
            'gasUsed': block.gasUsed,
            'gasLimit': block.gasLimit
        }
    
    def close(self):
        """Close connection"""
        # Web3 doesn't need explicit closing for HTTP provider
        console.print("[yellow]Connection closed[/yellow]")