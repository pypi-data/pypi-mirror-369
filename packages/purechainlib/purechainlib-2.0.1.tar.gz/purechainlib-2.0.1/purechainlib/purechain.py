"""
PureChain Python Library - Final Version
Matches npm library API exactly
"""

from typing import Any, Dict, List, Optional, Union, Tuple
from web3 import Web3, HTTPProvider
from web3.contract import Contract
from eth_account import Account as EthAccount
import json
import os

class ContractFactory:
    """Contract factory for deploying contracts (matches npm library)"""
    
    def __init__(self, abi: List, bytecode: str, web3: Web3, signer: Optional[EthAccount] = None):
        self.abi = abi
        self.bytecode = bytecode
        self.web3 = web3
        self.signer = signer
    
    async def deploy(self, *args, **kwargs) -> Contract:
        """Deploy contract with zero gas fees"""
        if not self.signer:
            raise Exception("No signer available for deployment")
        
        contract = self.web3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        
        # Build deployment transaction with zero gas
        tx = contract.constructor(*args).build_transaction({
            'from': self.signer.address,
            'nonce': self.web3.eth.get_transaction_count(self.signer.address),
            'gas': 8000000,  # Optimal for PureChain (matches npm)
            'gasPrice': 0,   # ZERO GAS!
            'chainId': 900520900520
        })
        
        # Sign and send
        signed = self.signer.sign_transaction(tx)
        raw_tx = signed.raw_transaction if hasattr(signed, 'raw_transaction') else signed.rawTransaction
        tx_hash = self.web3.eth.send_raw_transaction(raw_tx)
        
        # Wait for deployment
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Return deployed contract
        return self.web3.eth.contract(address=receipt.contractAddress, abi=self.abi)
    
    def attach(self, address: str) -> Contract:
        """Attach to existing contract"""
        return self.web3.eth.contract(address=Web3.to_checksum_address(address), abi=self.abi)
    
    def getABI(self) -> List:
        """Get contract ABI"""
        return self.abi
    
    def getBytecode(self) -> str:
        """Get contract bytecode"""
        return self.bytecode


class PureChain:
    """
    Main PureChain class - matches npm library API
    
    Example:
        pc = PureChain('testnet')
        pc.connect('private_key')
        
        # Deploy contract
        factory = await pc.contract('Token.sol')
        contract = await factory.deploy()
        
        # Send transaction
        await pc.send('0x...', '1.0')
        
        # Call contract
        result = await pc.call(contract, 'balanceOf', address)
    """
    
    def __init__(self, network: str = 'testnet', private_key: Optional[str] = None):
        """Initialize PureChain SDK"""
        # Network configurations
        networks = {
            'mainnet': {
                'rpc': 'https://purechainnode.com:8547',
                'chainId': 900520900520,
                'name': 'PureChain Mainnet'
            },
            'testnet': {
                'rpc': 'https://purechainnode.com:8547',
                'chainId': 900520900520,
                'name': 'PureChain Testnet'
            },
            'local': {
                'rpc': 'http://localhost:8545',
                'chainId': 1337,
                'name': 'Local Development'
            }
        }
        
        self.network_config = networks.get(network, networks['testnet'])
        self.web3 = Web3(HTTPProvider(self.network_config['rpc']))
        
        # Add POA middleware for PureChain
        from web3.middleware import ExtraDataToPOAMiddleware
        self.web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        
        self.signer = None
        if private_key:
            self.connect(private_key)
    
    def connect(self, private_key_or_mnemonic: str) -> 'PureChain':
        """Connect with private key or mnemonic"""
        if ' ' in private_key_or_mnemonic:
            # It's a mnemonic - not implemented yet in eth_account
            raise NotImplementedError("Mnemonic support coming soon")
        else:
            # It's a private key
            if not private_key_or_mnemonic.startswith('0x'):
                private_key_or_mnemonic = '0x' + private_key_or_mnemonic
            self.signer = EthAccount.from_key(private_key_or_mnemonic)
        return self
    
    async def contract(self, path_or_source: str) -> ContractFactory:
        """
        Load and compile Solidity contract
        Returns ContractFactory for deployment
        """
        # Check if it's a file path
        if os.path.exists(path_or_source) or path_or_source.endswith('.sol'):
            # Read file
            if os.path.exists(path_or_source):
                with open(path_or_source, 'r') as f:
                    source = f.read()
            else:
                raise FileNotFoundError(f"Contract file not found: {path_or_source}")
        else:
            # It's source code
            source = path_or_source
        
        # Compile contract
        from purechainlib.compiler import SolidityCompiler
        compiler = SolidityCompiler()
        compiled = compiler.compile_source(source)
        
        # Get main contract
        contract_name = list(compiled.keys())[0]
        contract_data = compiled[contract_name]
        
        # Return factory
        return ContractFactory(
            abi=contract_data.abi,
            bytecode=contract_data.bytecode,
            web3=self.web3,
            signer=self.signer
        )
    
    def compile(self, sources: Union[str, Dict[str, str]]) -> Dict:
        """Compile Solidity source(s)"""
        from purechainlib.compiler import SolidityCompiler
        compiler = SolidityCompiler()
        
        if isinstance(sources, str):
            # Single source
            compiled = compiler.compile_source(sources)
        else:
            # Multiple sources - not implemented yet
            raise NotImplementedError("Multiple source compilation coming soon")
        
        # Return in format matching npm
        result = {}
        for name, contract in compiled.items():
            result[name] = {
                'abi': contract.abi,
                'bytecode': contract.bytecode
            }
        return result
    
    async def balance(self, address: Optional[str] = None) -> str:
        """Get account balance in PURE"""
        addr = address or (self.signer.address if self.signer else None)
        if not addr:
            raise Exception("No address provided and no signer connected")
        
        balance_wei = self.web3.eth.get_balance(addr)
        return str(self.web3.from_wei(balance_wei, 'ether'))
    
    async def send(self, to: Union[str, Dict], value: Optional[str] = None) -> Dict:
        """Send transaction with zero gas fees"""
        if not self.signer:
            raise Exception("No signer connected. Use connect() first.")
        
        if isinstance(to, str):
            # Simple send
            tx = {
                'to': Web3.to_checksum_address(to),
                'value': self.web3.to_wei(float(value or 0), 'ether'),
                'from': self.signer.address,
                'nonce': self.web3.eth.get_transaction_count(self.signer.address),
                'gas': 1000000,
                'gasPrice': 0,  # ZERO GAS!
                'chainId': self.network_config['chainId']
            }
        else:
            # Transaction object
            tx = to
            tx['from'] = self.signer.address
            tx['nonce'] = self.web3.eth.get_transaction_count(self.signer.address)
            tx['gasPrice'] = 0  # ZERO GAS!
            tx['gas'] = tx.get('gas', 1000000)
            tx['chainId'] = self.network_config['chainId']
            
            if 'value' in tx and isinstance(tx['value'], str):
                tx['value'] = self.web3.to_wei(float(tx['value']), 'ether')
        
        # Sign and send
        signed = self.signer.sign_transaction(tx)
        raw_tx = signed.raw_transaction if hasattr(signed, 'raw_transaction') else signed.rawTransaction
        tx_hash = self.web3.eth.send_raw_transaction(raw_tx)
        
        # Wait for receipt
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt
    
    async def call(self, contract: Union[str, Contract], method: str, *args) -> Any:
        """Call contract method (read-only)"""
        if isinstance(contract, str):
            # Need to create contract instance - but we need ABI
            raise Exception("Contract ABI required for calls. Use contract instance instead.")
        
        # Call method
        return contract.functions[method](*args).call()
    
    async def execute(self, contract: Union[str, Contract], method: str, *args) -> Dict:
        """Execute contract method (state-changing)"""
        if not self.signer:
            raise Exception("No signer connected. Use connect() first.")
        
        if isinstance(contract, str):
            raise Exception("Contract ABI required for execution. Use contract instance instead.")
        
        # Build transaction
        tx = contract.functions[method](*args).build_transaction({
            'from': self.signer.address,
            'nonce': self.web3.eth.get_transaction_count(self.signer.address),
            'gas': 1000000,
            'gasPrice': 0,  # ZERO GAS!
            'chainId': self.network_config['chainId']
        })
        
        # Sign and send
        signed = self.signer.sign_transaction(tx)
        raw_tx = signed.raw_transaction if hasattr(signed, 'raw_transaction') else signed.rawTransaction
        tx_hash = self.web3.eth.send_raw_transaction(raw_tx)
        
        # Wait for receipt
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt
    
    def account(self) -> Dict[str, str]:
        """Create new account"""
        new_account = EthAccount.create()
        return {
            'address': new_account.address,
            'privateKey': new_account.key.hex()
        }
    
    def network(self) -> Dict:
        """Get network configuration"""
        return self.network_config
    
    def getProvider(self) -> Web3:
        """Get Web3 provider"""
        return self.web3
    
    def getSigner(self) -> Optional[EthAccount]:
        """Get current signer"""
        return self.signer
    
    async def block(self, block_number: Union[int, str] = 'latest') -> Dict:
        """Get block information"""
        block = self.web3.eth.get_block(block_number)
        return dict(block)
    
    async def transaction(self, tx_hash: str) -> Dict:
        """Get transaction information"""
        tx = self.web3.eth.get_transaction(tx_hash)
        return dict(tx) if tx else None
    
    async def gasPrice(self) -> int:
        """Get gas price (always 0 for PureChain)"""
        return 0
    
    # Pythonic style methods (short names)
    
    async def tx(self, hash: Optional[str] = None) -> Dict:
        """Get transaction details"""
        if not hash:
            raise Exception("Transaction hash required")
        return await self.transaction(hash)
    
    async def address(self, addr: Optional[str] = None) -> Dict:
        """Get address details"""
        address = addr or (self.signer.address if self.signer else None)
        if not address:
            raise Exception("No address provided")
        
        balance = await self.balance(address)
        nonce = self.web3.eth.get_transaction_count(address)
        is_contract = len(self.web3.eth.get_code(address)) > 0
        
        return {
            'address': address,
            'balance': balance,
            'nonce': nonce,
            'isContract': is_contract
        }
    
    async def bal(self, address: Optional[str] = None) -> str:
        """Quick balance check"""
        return await self.balance(address)
    
    async def isContract(self, address: str) -> bool:
        """Check if address is contract"""
        code = self.web3.eth.get_code(address)
        return len(code) > 0
    
    async def events(self, contract: str, blocks: int = 0) -> List:
        """Get contract events"""
        if blocks == 0:
            # Latest block only
            from_block = to_block = 'latest'
        else:
            latest = self.web3.eth.block_number
            from_block = max(0, latest - blocks)
            to_block = latest
        
        # Get logs
        logs = self.web3.eth.get_logs({
            'address': contract,
            'fromBlock': from_block,
            'toBlock': to_block
        })
        
        return logs
    
    async def status(self) -> Dict:
        """Get network status"""
        return {
            'chainId': self.network_config['chainId'],
            'networkName': self.network_config['name'],
            'blockNumber': self.web3.eth.block_number,
            'gasPrice': 0,  # Always 0
            'connected': self.web3.is_connected()
        }