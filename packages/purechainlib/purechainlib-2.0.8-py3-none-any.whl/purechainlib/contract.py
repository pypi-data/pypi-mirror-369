"""
Smart contract deployment and interaction for PureChain
Handles contract deployment, function calls, and transaction execution
"""

from typing import Any, Dict, List, Optional, Union
from web3 import Web3
from web3.contract import Contract as Web3Contract
from eth_abi import encode, decode
from eth_utils import function_signature_to_4byte_selector

from purechainlib.exceptions import ContractException


class Contract:
    """
    Deployed contract instance for PureChain
    Provides methods to interact with deployed smart contracts
    """
    
    def __init__(self, address: str, abi: List[Dict], web3: Web3):
        """
        Initialize contract instance
        
        Args:
            address: Contract address
            abi: Contract ABI
            web3: Web3 instance
        """
        self.address = Web3.to_checksum_address(address)
        self.abi = abi
        self.web3 = web3
        
        # Create Web3 contract instance
        self._contract = self.web3.eth.contract(address=self.address, abi=self.abi)
        
        # Parse ABI for quick access
        self._parse_abi()
    
    def _parse_abi(self) -> None:
        """Parse ABI to extract functions and events"""
        self.functions = {}
        self.events = {}
        
        for item in self.abi:
            if item.get('type') == 'function':
                self.functions[item['name']] = item
            elif item.get('type') == 'event':
                self.events[item['name']] = item
    
    async def call(self, method: str, *args, **kwargs) -> Any:
        """
        Call a read-only contract method
        
        Args:
            method: Method name
            *args: Method arguments
            **kwargs: Additional call parameters
            
        Returns:
            Method return value
        """
        try:
            # Get function from contract
            if not hasattr(self._contract.functions, method):
                raise ContractException(f"Method '{method}' not found in contract ABI")
            
            func = getattr(self._contract.functions, method)
            
            # Call the function
            result = func(*args).call(**kwargs)
            
            return result
        except Exception as e:
            raise ContractException(f"Failed to call method '{method}': {str(e)}")
    
    async def execute(self, method: str, *args, account=None, **kwargs) -> Dict[str, Any]:
        """
        Execute a state-changing contract method
        
        Args:
            method: Method name
            *args: Method arguments
            account: Account instance for signing
            **kwargs: Additional transaction parameters
            
        Returns:
            Transaction receipt
        """
        try:
            if not account:
                raise ContractException("Account required for executing transactions")
            
            # Get function from contract
            if not hasattr(self._contract.functions, method):
                raise ContractException(f"Method '{method}' not found in contract ABI")
            
            func = getattr(self._contract.functions, method)
            
            # Build transaction with zero gas (PureChain feature)
            transaction = func(*args).build_transaction({
                'from': account.address,
                'nonce': self.web3.eth.get_transaction_count(account.address),
                'gas': 0,  # Zero gas for PureChain
                'gasPrice': 0,  # Zero gas price for PureChain
                **kwargs
            })
            
            # Sign transaction
            signed_tx = account.sign_transaction(transaction)
            
            # Send transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx['rawTransaction'])
            
            # Wait for receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'transactionHash': receipt['transactionHash'].hex(),
                'blockNumber': receipt['blockNumber'],
                'gasUsed': 0,  # Always 0 for PureChain
                'status': receipt['status'],
                'logs': receipt.get('logs', [])
            }
        except Exception as e:
            raise ContractException(f"Failed to execute method '{method}': {str(e)}")
    
    def encode_abi(self, method: str, *args) -> str:
        """
        Encode function call data
        
        Args:
            method: Method name
            *args: Method arguments
            
        Returns:
            Encoded function call data
        """
        try:
            if not hasattr(self._contract.functions, method):
                raise ContractException(f"Method '{method}' not found in contract ABI")
            
            func = getattr(self._contract.functions, method)
            return func(*args)._encode_transaction_data()
        except Exception as e:
            raise ContractException(f"Failed to encode ABI for '{method}': {str(e)}")
    
    def get_function(self, name: str) -> Optional[Dict]:
        """Get function ABI by name"""
        return self.functions.get(name)
    
    def get_event(self, name: str) -> Optional[Dict]:
        """Get event ABI by name"""
        return self.events.get(name)
    
    async def get_past_events(self, event_name: str, from_block: int = 0, to_block: str = 'latest') -> List[Dict]:
        """
        Get past events from the contract
        
        Args:
            event_name: Event name to filter
            from_block: Starting block number
            to_block: Ending block number or 'latest'
            
        Returns:
            List of event logs
        """
        try:
            if not hasattr(self._contract.events, event_name):
                raise ContractException(f"Event '{event_name}' not found in contract ABI")
            
            event = getattr(self._contract.events, event_name)
            event_filter = event.create_filter(fromBlock=from_block, toBlock=to_block)
            
            return event_filter.get_all_entries()
        except Exception as e:
            raise ContractException(f"Failed to get past events: {str(e)}")
    
    def __repr__(self) -> str:
        """String representation"""
        return f"<Contract address='{self.address}'>"


class ContractFactory:
    """
    Factory for deploying new contracts on PureChain
    """
    
    def __init__(self, abi: List[Dict], bytecode: str, web3: Web3):
        """
        Initialize contract factory
        
        Args:
            abi: Contract ABI
            bytecode: Contract bytecode
            web3: Web3 instance
        """
        self.abi = abi
        self.bytecode = bytecode
        self.web3 = web3
        
        # Create Web3 contract factory
        self._contract = self.web3.eth.contract(abi=self.abi, bytecode=self.bytecode)
    
    async def deploy(self, *constructor_args, account=None, **kwargs) -> Contract:
        """
        Deploy a new contract instance
        
        Args:
            *constructor_args: Constructor arguments
            account: Account instance for deployment
            **kwargs: Additional deployment parameters
            
        Returns:
            Deployed Contract instance
        """
        try:
            if not account:
                raise ContractException("Account required for contract deployment")
            
            # Build deployment transaction with zero gas
            transaction = self._contract.constructor(*constructor_args).build_transaction({
                'from': account.address,
                'nonce': self.web3.eth.get_transaction_count(account.address),
                'gas': 0,  # Zero gas for PureChain
                'gasPrice': 0,  # Zero gas price for PureChain
                **kwargs
            })
            
            # Sign transaction
            signed_tx = account.sign_transaction(transaction)
            
            # Send transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx['rawTransaction'])
            
            # Wait for receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt['status'] != 1:
                raise ContractException("Contract deployment failed")
            
            # Get deployed contract address
            contract_address = receipt['contractAddress']
            
            print(f"✅ Contract deployed at: {contract_address}")
            print(f"   Transaction hash: {receipt['transactionHash'].hex()}")
            print(f"   Block number: {receipt['blockNumber']}")
            print(f"   Gas used: 0 (PureChain - Zero gas!)")
            
            # Return Contract instance
            return Contract(contract_address, self.abi, self.web3)
            
        except Exception as e:
            raise ContractException(f"Failed to deploy contract: {str(e)}")
    
    def at(self, address: str) -> Contract:
        """
        Create Contract instance for existing deployed contract
        
        Args:
            address: Contract address
            
        Returns:
            Contract instance
        """
        return Contract(address, self.abi, self.web3)