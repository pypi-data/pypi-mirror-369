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
import time
import asyncio
import statistics
from .carbon_tracker import CarbonFootprintTracker
from .security_auditor import SecurityAuditor, SecurityTool

class ContractFactory:
    """Contract factory for deploying contracts (matches npm library)"""
    
    def __init__(self, abi: List, bytecode: str, web3: Web3, signer: Optional[EthAccount] = None, purechain_instance: Optional['PureChain'] = None):
        self.abi = abi
        self.bytecode = bytecode
        self.web3 = web3
        self.signer = signer
        self.purechain = purechain_instance
    
    async def deploy(self, *args, track_carbon: bool = False, audit_security: bool = False, security_tool: Optional[SecurityTool] = None, **kwargs) -> Contract:
        """
        Deploy contract with zero gas fees
        
        Args:
            *args: Constructor arguments
            track_carbon: Include carbon footprint tracking
            **kwargs: Additional arguments
            
        Returns:
            Deployed contract instance
        """
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
        
        # Calculate carbon footprint if requested
        carbon_data = None
        if (track_carbon or (self.purechain and self.purechain.track_carbon)) and self.purechain and self.purechain.carbon_tracker:
            bytecode_size = len(self.bytecode) // 2 if isinstance(self.bytecode, str) else len(self.bytecode)
            carbon_data = self.purechain.carbon_tracker.calculate_contract_deployment(bytecode_size)
        
        tx_hash = self.web3.eth.send_raw_transaction(raw_tx)
        
        # Wait for deployment
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Add carbon data to receipt if calculated
        if carbon_data:
            receipt['carbon_footprint'] = carbon_data
            print(f"🌱 Carbon footprint: {carbon_data['carbon']['gCO2']} gCO2 (99.99%+ less than Ethereum)")
        
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
    
    def _setup_middleware(self):
        """Setup Web3 middleware with compatibility for all versions"""
        try:
            # First try Web3 v6+ with geth_poa_middleware
            from web3.middleware import geth_poa_middleware
            self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            return
        except (ImportError, AttributeError):
            pass
        
        try:
            # Try alternative import path for geth_poa_middleware
            from web3.middleware.geth_poa import geth_poa_middleware
            self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            return
        except (ImportError, AttributeError):
            pass
        
        try:
            # Some versions have it as extradata_to_poa_middleware
            from web3.middleware import extradata_to_poa_middleware
            self.web3.middleware_onion.inject(extradata_to_poa_middleware, layer=0)
            return
        except (ImportError, AttributeError):
            pass
        
        try:
            # Try creating a compatibility layer
            import web3.middleware
            
            # Check if any POA-related middleware exists
            if hasattr(web3.middleware, 'geth_poa_middleware'):
                self.web3.middleware_onion.inject(web3.middleware.geth_poa_middleware, layer=0)
            elif hasattr(web3.middleware, 'extradata_to_poa_middleware'):
                self.web3.middleware_onion.inject(web3.middleware.extradata_to_poa_middleware, layer=0)
            else:
                # Create a no-op middleware if POA support isn't available
                # PureChain should work without POA middleware in most cases
                pass
        except Exception:
            # If all fails, PureChain may work without POA middleware
            # This is OK for PureChain as it doesn't strictly require POA middleware
            pass
    
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
        
        # Add POA middleware for PureChain - handle all Web3 versions
        self._setup_middleware()
        
        self.signer = None
        if private_key:
            self.connect(private_key)
        
        # Initialize carbon footprint tracker
        self.carbon_tracker = None
        self.track_carbon = False
        
        # Initialize security auditor
        self.security_auditor = SecurityAuditor()
        self.auto_audit = False  # Auto-audit before deployment
        self.security_logs = []  # Store all security audit logs
        
        # Initialize help system (easter egg)
        self.help = self._Help(self)
    
    class _Help:
        """Hidden help system - Easter egg for power users"""
        def __init__(self, parent):
            self.parent = parent
        
        def islarpee(self):
            """
            🎉 Secret command discovered! Welcome, power user!
            This comprehensive guide shows ALL available functions and instructions.
            """
            guide = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 PURECHAIN PYTHON SDK - COMPLETE GUIDE                   ║
║                           Created by islarpee 🎯                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎊 Congratulations! You found the secret command! Here's EVERYTHING you can do:

═══════════════════════════════════════════════════════════════════════════════
                              📚 QUICK START
═══════════════════════════════════════════════════════════════════════════════

from purechainlib import PureChain
import asyncio

async def main():
    # Initialize
    pc = PureChain('testnet')  # or 'mainnet', 'local'
    
    # Connect wallet
    pc.connect('your_private_key_here')  # No 0x prefix needed
    
    # Check balance
    balance = await pc.balance()
    print(f"Balance: {balance} PURE")

asyncio.run(main())

═══════════════════════════════════════════════════════════════════════════════
                         🔧 ALL AVAILABLE FUNCTIONS
═══════════════════════════════════════════════════════════════════════════════

🔐 ACCOUNT & WALLET
├── pc.connect(private_key)           Connect wallet
├── pc.account()                      Create new account
├── pc.getSigner()                    Get current signer
├── pc.getProvider()                  Get Web3 provider
└── pc.network()                      Get network info

💰 BALANCES & TRANSACTIONS  
├── await pc.balance(address?)        Check balance (FREE!)
├── await pc.bal(address?)            Balance shorthand
├── await pc.send(to, value?)         Send PURE tokens (FREE!)
├── await pc.gasPrice()               Get gas price (always 0!)
└── await pc.transaction(hash)        Get transaction details

📄 SMART CONTRACTS
├── await pc.contract(source)         Compile contract from source
├── await factory.deploy(*args)       Deploy contract (FREE!)
├── factory.attach(address)           Attach to existing contract
├── await pc.call(contract, method, *args)     Read from contract
├── await pc.execute(contract, method, *args)  Write to contract
└── await pc.isContract(address)      Check if address is contract

🔍 BLOCKCHAIN INFO
├── await pc.block(number?)           Get block information
├── await pc.status()                 Network status
├── await pc.address(addr?)           Address information
├── await pc.events(contract, blocks?) Get contract events
└── await pc.tx(hash?)                Transaction info (alias)

⚡ PERFORMANCE TESTING
├── await pc.testTPS(duration?, target?, mode?)
│   └── Modes: 'full', 'send', 'parallel'
├── await pc.measureLatency(operations?)
├── await pc.benchmarkThroughput(duration?)
└── await pc.runPerformanceTest(quick?)

🌱 CARBON TRACKING
├── pc.enableCarbonTracking(region?)
│   └── Regions: 'global', 'us', 'eu', 'asia', 'renewable'
├── pc.disableCarbonTracking()
├── await pc.getCarbonReport()
├── await pc.getCarbonESGMetrics()
└── await pc.exportCarbonReport()

🔒 SECURITY AUDITING (NEW!)
├── await pc.audit(contract_source, tool?)
│   └── Tools: 'slither', 'mythril', 'manticore', 'solhint'
├── await pc.auditWithAllTools(contract_source)
├── await pc.auditAndDeploy(source, require_pass?)
├── await pcl.audit(source)                    # One-liner!
└── SecuritySetup.check_and_install_tools()    # Auto-install

═══════════════════════════════════════════════════════════════════════════════
                          💡 COMPLETE EXAMPLES
═══════════════════════════════════════════════════════════════════════════════

1️⃣ DEPLOY & INTERACT WITH TOKEN CONTRACT
----------------------------------------
async def deploy_token():
    pc = PureChain('testnet')
    pc.connect('your_private_key')
    
    contract_source = '''
    pragma solidity ^0.8.19;
    contract Token {
        mapping(address => uint256) public balances;
        
        function mint(uint256 amount) public {
            balances[msg.sender] += amount;
        }
        
        function transfer(address to, uint256 amount) public {
            require(balances[msg.sender] >= amount);
            balances[msg.sender] -= amount;
            balances[to] += amount;
        }
    }
    '''
    
    # Deploy (FREE!)
    factory = await pc.contract(contract_source)
    token = await factory.deploy()
    print(f"Token deployed: {token.address}")
    
    # Interact (FREE!)
    await pc.execute(token, 'mint', 1000000)
    balance = await pc.call(token, 'balances', pc.signer.address)
    print(f"Your balance: {balance}")

2️⃣ PERFORMANCE TESTING
-----------------------
async def test_performance():
    pc = PureChain('testnet')
    pc.connect('your_private_key')
    
    # Test TPS with different modes
    results = await pc.testTPS(
        duration=30,      # Test for 30 seconds
        target_tps=100,   # Target 100 TPS
        measure_mode='parallel'  # Use parallel mode
    )
    print(f"Achieved TPS: {results['actual_tps']}")
    print(f"Efficiency: {results['efficiency']}%")
    
    # Measure latency
    latency = await pc.measureLatency(100)
    print(f"Avg latency: {latency['balance_check']['avg_ms']}ms")

3️⃣ CARBON TRACKING
------------------
async def track_carbon():
    pc = PureChain('testnet')
    pc.connect('your_private_key')
    
    # Enable tracking for your region
    pc.enableCarbonTracking('asia')  # or 'us', 'eu', etc.
    
    # Send transaction with carbon data
    result = await pc.send(
        '0xRecipientAddress',
        '1.0',
        include_carbon=True
    )
    print(f"CO2 emitted: {result['carbon_footprint']['carbon']['gCO2']} gCO2")
    
    # Get ESG report
    esg = await pc.getCarbonESGMetrics()
    print(f"Total emissions: {esg['environmental']['total_emissions_kg_co2']} kg")

4️⃣ SECURITY AUDITING (NEW!)
----------------------------
async def secure_deploy():
    pc = PureChain('testnet')
    pc.connect('your_private_key')
    
    vulnerable_contract = '''
    pragma solidity ^0.8.0;
    contract Vulnerable {
        mapping(address => uint256) balances;
        function withdraw() public {
            uint256 amount = balances[msg.sender];
            msg.sender.call{value: amount}("");  // Reentrancy bug!
            balances[msg.sender] = 0;
        }
    }
    '''
    
    # Quick audit (one-liner!)
    import purechainlib as pcl
    result = await pcl.audit(vulnerable_contract)
    print(f"Issues found: {result['issues_count']}")
    
    # Full audit with PureChain instance
    audit = await pc.audit(vulnerable_contract)
    for issue in audit['issues']:
        print(f"⚠️ {issue['severity']}: {issue['title']}")
    
    # Safe deploy (only if audit passes)
    safe_contract = await pc.auditAndDeploy(
        vulnerable_contract,
        require_pass=True  # Will refuse to deploy!
    )
    if not safe_contract:
        print("❌ Contract too risky to deploy!")

5️⃣ BATCH OPERATIONS
--------------------
async def batch_operations():
    pc = PureChain('testnet')
    pc.connect('your_private_key')
    
    # Create multiple accounts
    accounts = [pc.account() for _ in range(5)]
    
    # Fund them all (FREE!)
    for i, acc in enumerate(accounts):
        await pc.send(acc['address'], f"{i+1}.0")
        print(f"Sent {i+1} PURE to {acc['address']}")
    
    # Check all balances concurrently
    import asyncio
    balances = await asyncio.gather(*[
        pc.balance(acc['address']) for acc in accounts
    ])
    for bal, acc in zip(balances, accounts):
        print(f"{acc['address']}: {bal} PURE")

═══════════════════════════════════════════════════════════════════════════════
                           🎯 PRO TIPS & TRICKS
═══════════════════════════════════════════════════════════════════════════════

🔥 OPTIMIZATION TIPS:
• Use asyncio.gather() for concurrent operations
• Cache frequently accessed data (blocks, balances)
• Use 'parallel' mode for maximum TPS
• Batch similar operations together

🛡️ BEST PRACTICES:
• Never commit private keys to code
• Always handle exceptions in async functions
• Use carbon tracking for ESG compliance
• Test on testnet before mainnet

🎨 ADVANCED FEATURES:
• Custom RPC endpoints supported
• Full Web3.py compatibility
• Automatic gas optimization (always 0!)
• Built-in performance monitoring

💰 COST SAVINGS:
• ALL operations are FREE (0 gas)
• No need for test tokens
• No gas estimation needed
• Unlimited transactions

═══════════════════════════════════════════════════════════════════════════════
                          📊 NETWORK INFORMATION
═══════════════════════════════════════════════════════════════════════════════

Network: {{network}}
RPC URL: {{rpc}}
Chain ID: {{chainId}}
Gas Price: 0 (FREE!)
Connected: {{connected}}
Signer: {{signer}}

═══════════════════════════════════════════════════════════════════════════════
                          🌍 KOREAN DOCUMENTATION
═══════════════════════════════════════════════════════════════════════════════

한국어 문서를 보려면:
1. 패키지 설치 후 README_ko.md 파일 확인
2. 다음 코드 실행:

import purechainlib
import os
korean_readme = os.path.join(
    os.path.dirname(purechainlib.__file__), 
    '..', 
    'README_ko.md'
)
with open(korean_readme, 'r', encoding='utf-8') as f:
    print(f.read())

═══════════════════════════════════════════════════════════════════════════════
                           🎊 CONGRATULATIONS!
═══════════════════════════════════════════════════════════════════════════════

You're now a PureChain power user! This guide is your secret weapon.
Remember: With zero gas costs, the only limit is your imagination!

Created with ❤️ by islarpee
Version: {{version}}
═══════════════════════════════════════════════════════════════════════════════
"""
            # Replace placeholders with actual values
            guide = guide.replace('{{network}}', self.parent.network_config['name'])
            guide = guide.replace('{{rpc}}', self.parent.network_config['rpc'])
            guide = guide.replace('{{chainId}}', str(self.parent.network_config['chainId']))
            guide = guide.replace('{{connected}}', str(self.parent.web3.is_connected()))
            guide = guide.replace('{{signer}}', self.parent.signer.address if self.parent.signer else 'Not connected')
            guide = guide.replace('{{version}}', '2.0.9')
            
            print(guide)
            return "🎉 Welcome to the secret club! Guide displayed above."
    
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
            signer=self.signer,
            purechain_instance=self
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
    
    async def send(self, to: Union[str, Dict], value: Optional[str] = None, include_carbon: bool = False) -> Dict:
        """
        Send transaction with zero gas fees
        
        Args:
            to: Recipient address or transaction dict
            value: Amount to send (in ether)
            include_carbon: Include carbon footprint data in response
            
        Returns:
            Transaction result with optional carbon data
        """
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
        
        # Calculate carbon footprint if requested
        carbon_data = None
        if include_carbon or self.track_carbon:
            if self.carbon_tracker:
                tx_size = len(raw_tx) if isinstance(raw_tx, bytes) else len(bytes(raw_tx))
                carbon_data = self.carbon_tracker.calculate_transaction(tx_size)
        
        tx_hash = self.web3.eth.send_raw_transaction(raw_tx)
        
        # Wait for receipt
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Add carbon data to receipt if calculated
        if carbon_data:
            receipt['carbon_footprint'] = carbon_data
        
        return receipt
    
    async def call(self, contract: Union[str, Contract], method: str, *args) -> Any:
        """Call contract method (read-only)"""
        if isinstance(contract, str):
            # Need to create contract instance - but we need ABI
            raise Exception("Contract ABI required for calls. Use contract instance instead.")
        
        # Call method
        return contract.functions[method](*args).call()
    
    async def execute(self, contract: Union[str, Contract], method: str, *args, include_carbon: bool = False) -> Dict:
        """
        Execute contract method (state-changing)
        
        Args:
            contract: Contract instance
            method: Method name to execute
            *args: Method arguments
            include_carbon: Include carbon footprint tracking
            
        Returns:
            Transaction receipt with optional carbon data
        """
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
        
        # Calculate carbon footprint if requested
        carbon_data = None
        if include_carbon or self.track_carbon:
            if self.carbon_tracker:
                carbon_data = self.carbon_tracker.calculate_contract_execution()
        
        tx_hash = self.web3.eth.send_raw_transaction(raw_tx)
        
        # Wait for receipt
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Add carbon data if calculated
        if carbon_data:
            receipt['carbon_footprint'] = carbon_data
        
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
    
    # Carbon Footprint Tracking Functions
    
    def enableCarbonTracking(self, region: str = 'global') -> 'PureChain':
        """
        Enable carbon footprint tracking for all operations
        
        Args:
            region: Geographic region for grid intensity ('global', 'us', 'eu', 'nordic', 'asia', 'renewable')
            
        Returns:
            Self for method chaining
        """
        self.carbon_tracker = CarbonFootprintTracker(region)
        self.track_carbon = True
        return self
    
    def disableCarbonTracking(self) -> 'PureChain':
        """
        Disable carbon footprint tracking
        
        Returns:
            Self for method chaining
        """
        self.track_carbon = False
        return self
    
    async def getCarbonReport(self) -> Dict:
        """
        Get carbon footprint report for all tracked operations
        
        Returns:
            Carbon footprint summary and details
        """
        if not self.carbon_tracker:
            return {'error': 'Carbon tracking not enabled. Call enableCarbonTracking() first.'}
        
        return self.carbon_tracker.get_summary()
    
    async def getCarbonESGMetrics(self) -> Dict:
        """
        Get ESG-compliant carbon metrics for reporting
        
        Returns:
            ESG metrics for environmental reporting
        """
        if not self.carbon_tracker:
            return {'error': 'Carbon tracking not enabled. Call enableCarbonTracking() first.'}
        
        return self.carbon_tracker.get_esg_metrics()
    
    async def exportCarbonReport(self) -> str:
        """
        Export full carbon footprint report as JSON
        
        Returns:
            JSON string of complete carbon report
        """
        if not self.carbon_tracker:
            return json.dumps({'error': 'Carbon tracking not enabled. Call enableCarbonTracking() first.'})
        
        return self.carbon_tracker.export_report()
    
    # Security Audit Functions
    
    def enableAutoAudit(self, tool: Optional[SecurityTool] = None) -> 'PureChain':
        """
        Enable automatic security auditing before contract deployment
        
        Args:
            tool: Preferred security tool (default: Slither)
            
        Returns:
            Self for method chaining
        """
        self.auto_audit = True
        if tool:
            self.security_auditor.default_tool = tool
        print(f"🔒 Auto-audit enabled with {self.security_auditor.default_tool.value}")
        return self
    
    def disableAutoAudit(self) -> 'PureChain':
        """Disable automatic security auditing"""
        self.auto_audit = False
        print("🔓 Auto-audit disabled")
        return self
    
    async def audit(self, contract_source: str, **kwargs) -> Dict[str, Any]:
        """
        Pythonic one-liner audit method
        
        Examples:
            result = await pc.audit(contract_code)
            result = await pc.audit("MyContract.sol", tool="mythril")
            result = await pc.audit(code, export=True)
        """
        # Handle string tool names for convenience
        if 'tool' in kwargs and isinstance(kwargs['tool'], str):
            kwargs['tool'] = SecurityTool[kwargs['tool'].upper()]
        
        return await self.auditContract(
            contract_source,
            tool=kwargs.get('tool'),
            export_report=kwargs.get('export', False),
            report_format=kwargs.get('format', 'markdown')
        )
    
    async def auditContract(
        self,
        contract_source: str,
        tool: Optional[SecurityTool] = None,
        export_report: bool = False,
        report_format: str = 'markdown'
    ) -> Dict[str, Any]:
        """
        Perform security audit on contract source code
        
        Args:
            contract_source: Solidity source code or file path
            tool: Security tool to use (None for default)
            export_report: Whether to export report to file
            report_format: Format for report export ('text', 'json', 'html', 'markdown')
            
        Returns:
            Comprehensive audit results with all findings
        """
        # Check if it's a file path
        if os.path.exists(contract_source) or contract_source.endswith('.sol'):
            if os.path.exists(contract_source):
                with open(contract_source, 'r') as f:
                    source = f.read()
            else:
                raise FileNotFoundError(f"Contract file not found: {contract_source}")
        else:
            source = contract_source
        
        # Run security audit
        print(f"🔍 Running security audit with {tool.value if tool else self.security_auditor.default_tool.value}...")
        audit_results = await self.security_auditor.audit(source, tool)
        
        # Add to security logs for tracking
        log_entry = {
            'timestamp': audit_results.get('timestamp'),
            'tool': audit_results.get('tool'),
            'summary': audit_results.get('summary'),
            'contract_hash': audit_results.get('contract_hash'),
            'passed': self._evaluate_audit_results(audit_results)
        }
        self.security_logs.append(log_entry)
        
        # Fix the display issue: ensure 'issues' and 'issues_count' are present
        if 'findings' in audit_results:
            audit_results['issues'] = audit_results['findings']
            audit_results['issues_count'] = len(audit_results['findings'])
        
        # Set success flag based on evaluation
        audit_results['success'] = self._evaluate_audit_results(audit_results)
        
        # Display summary
        self._display_audit_summary(audit_results)
        
        # Export report if requested
        if export_report:
            filename = f"audit_report_{audit_results.get('contract_hash', 'unknown')}_{int(time.time())}"
            exported_file = self.security_auditor.export_report(audit_results, filename, report_format)
            print(f"📄 Report exported to: {exported_file}")
            audit_results['report_file'] = exported_file
        
        return audit_results
    
    def _evaluate_audit_results(self, results: Dict) -> bool:
        """
        Evaluate if audit results pass security requirements
        
        Returns:
            True if no critical/high severity issues found
        """
        if 'summary' in results:
            return results['summary'].get('critical', 0) == 0 and results['summary'].get('high', 0) == 0
        return True
    
    def _display_audit_summary(self, results: Dict) -> None:
        """Display audit summary in console"""
        print("\n" + "="*60)
        print("🔒 SECURITY AUDIT SUMMARY")
        print("="*60)
        
        if 'summary' in results:
            summary = results['summary']
            total_issues = sum(summary.values())
            
            if total_issues == 0:
                print("✅ No security issues found!")
            else:
                if summary.get('critical', 0) > 0:
                    print(f"🔴 CRITICAL: {summary['critical']}")
                if summary.get('high', 0) > 0:
                    print(f"🟠 HIGH: {summary['high']}")
                if summary.get('medium', 0) > 0:
                    print(f"🟡 MEDIUM: {summary['medium']}")
                if summary.get('low', 0) > 0:
                    print(f"🟢 LOW: {summary['low']}")
                if summary.get('info', 0) > 0:
                    print(f"ℹ️  INFO: {summary['info']}")
            
            # Show pass/fail status
            if self._evaluate_audit_results(results):
                print("\n✅ AUDIT PASSED - Safe to deploy")
            else:
                print("\n❌ AUDIT FAILED - Critical/High severity issues found")
        
        print("="*60 + "\n")
    
    async def auditAndDeploy(
        self,
        contract_source: str,
        *constructor_args,
        security_tool: Optional[SecurityTool] = None,
        require_pass: bool = True,
        **kwargs
    ) -> Optional[Contract]:
        """
        Audit contract and deploy only if it passes security checks
        
        Args:
            contract_source: Solidity source code
            *constructor_args: Constructor arguments for deployment
            security_tool: Security tool to use for audit
            require_pass: Only deploy if audit passes (default: True)
            **kwargs: Additional deployment arguments
            
        Returns:
            Deployed contract if audit passes, None otherwise
        """
        # Run security audit
        audit_results = await self.auditContract(contract_source, security_tool)
        
        # Check if audit passed
        passed = self._evaluate_audit_results(audit_results)
        
        if not passed and require_pass:
            print("⚠️  Deployment cancelled due to security issues")
            print("💡 Fix the issues and try again, or set require_pass=False to deploy anyway")
            return None
        
        if not passed:
            print("⚠️  WARNING: Deploying contract with security issues!")
        
        # Compile and deploy
        print("📦 Compiling and deploying contract...")
        factory = await self.contract(contract_source)
        contract = await factory.deploy(*constructor_args, **kwargs)
        
        # Add audit results to contract metadata
        contract.security_audit = audit_results
        
        print(f"✅ Contract deployed at: {contract.address}")
        return contract
    
    def getSecurityLogs(self) -> List[Dict]:
        """
        Get all security audit logs from this session
        
        Returns:
            List of all security audit logs with timestamps and results
        """
        return self.security_logs
    
    def exportSecurityLogs(self, filename: str = 'security_logs.json') -> str:
        """
        Export all security logs to JSON file
        
        Args:
            filename: Output filename
            
        Returns:
            Path to exported file
        """
        with open(filename, 'w') as f:
            json.dump(self.security_logs, f, indent=2)
        print(f"📊 Security logs exported to: {filename}")
        return filename
    
    def getLastAuditReport(self) -> Optional[Dict]:
        """Get the most recent audit report"""
        if self.security_logs:
            return self.security_logs[-1]
        return None
    
    def checkSecurityTools(self) -> Dict[str, bool]:
        """
        Check which security tools are installed
        
        Returns:
            Dictionary of tool availability
        """
        tools = self.security_auditor.get_available_tools()
        print("🔧 Available Security Tools:")
        for tool, available in tools.items():
            status = "✅" if available else "❌"
            print(f"  {status} {tool}")
        return tools
    
    async def runSecurityLoop(
        self,
        contract_source: str,
        max_iterations: int = 5,
        auto_fix: bool = False
    ) -> Dict[str, Any]:
        """
        Run security audit in a loop until it passes or max iterations reached
        Perfect for LLM integration!
        
        Args:
            contract_source: Initial contract source code
            max_iterations: Maximum number of audit iterations
            auto_fix: Attempt automatic fixes (requires LLM integration)
            
        Returns:
            Final audit results with iteration history
        """
        iteration_results = []
        current_source = contract_source
        
        for iteration in range(max_iterations):
            print(f"\n🔄 Security Loop - Iteration {iteration + 1}/{max_iterations}")
            
            # Run audit
            audit_results = await self.auditContract(current_source)
            iteration_results.append(audit_results)
            
            # Check if passed
            if self._evaluate_audit_results(audit_results):
                print(f"✅ Security audit passed on iteration {iteration + 1}!")
                break
            
            # Get recommendations
            recommendations = self.security_auditor.recommend_fixes(audit_results)
            
            if auto_fix and recommendations:
                print("🔧 Attempting automatic fixes...")
                # This is where LLM integration would happen
                # For now, just log the recommendations
                for rec in recommendations:
                    print(f"  - {rec['issue']}: {rec['fix']}")
                
                # In a real implementation, you would:
                # 1. Pass recommendations to LLM
                # 2. Get fixed code
                # 3. Update current_source
                # 4. Continue loop
                
                print("💡 Auto-fix requires LLM integration. Please fix manually and retry.")
                break
            else:
                print("💡 Manual fixes required. Review recommendations above.")
                break
        
        return {
            'iterations': len(iteration_results),
            'passed': self._evaluate_audit_results(iteration_results[-1]),
            'history': iteration_results,
            'final_result': iteration_results[-1]
        }
    
    # Performance Testing Functions
    
    async def testTPS(self, duration: int = 30, target_tps: int = 100, measure_mode: str = 'full') -> Dict:
        """
        Test Transactions Per Second (TPS) performance
        
        Args:
            duration: Test duration in seconds (default: 30)
            target_tps: Target TPS to achieve (default: 100)
            measure_mode: What to measure - 'full' (send+confirm), 'send' (just sending), 'parallel' (concurrent) (default: 'full')
            
        Returns:
            Dictionary with TPS results
        """
        if not self.signer:
            raise Exception("No signer available. Call connect() first.")
        
        print(f"🚀 Starting TPS test for {duration} seconds...")
        print(f"🎯 Target TPS: {target_tps}")
        print(f"📊 Measurement Mode: {measure_mode}")
        
        transactions = []
        start_time = time.time()
        end_time = start_time + duration
        
        # Create a simple test contract for TPS testing
        test_contract_source = """
        pragma solidity ^0.8.19;
        contract TPSTest {
            uint256 public counter = 0;
            function increment() public {
                counter++;
            }
            function getCounter() public view returns (uint256) {
                return counter;
            }
        }
        """
        
        print("📄 Deploying TPS test contract...")
        factory = await self.contract(test_contract_source)
        contract = await factory.deploy()
        print(f"✅ Test contract deployed: {contract.address}")
        
        successful_txs = 0
        failed_txs = 0
        latencies = []
        send_times = []
        confirm_times = []
        pending_txs = []
        
        if measure_mode == 'parallel':
            # Parallel mode: Send many transactions concurrently
            print("⚡ Running in parallel mode...")
            tasks = []
            
            async def send_tx():
                try:
                    send_start = time.time()
                    
                    # Build transaction
                    tx = contract.functions.increment().build_transaction({
                        'from': self.signer.address,
                        'nonce': self.web3.eth.get_transaction_count(self.signer.address),
                        'gas': 1000000,
                        'gasPrice': 0,
                        'chainId': self.network_config['chainId']
                    })
                    
                    # Sign and send (measure just sending)
                    signed = self.signer.sign_transaction(tx)
                    raw_tx = signed.raw_transaction if hasattr(signed, 'raw_transaction') else signed.rawTransaction
                    tx_hash = self.web3.eth.send_raw_transaction(raw_tx)
                    send_end = time.time()
                    send_time = (send_end - send_start) * 1000
                    
                    # Wait for confirmation (measure confirmation time)
                    confirm_start = time.time()
                    receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
                    confirm_end = time.time()
                    confirm_time = (confirm_end - confirm_start) * 1000
                    
                    return True, send_time, confirm_time, send_time + confirm_time
                except Exception as e:
                    return False, 0, 0, 0
            
            # Send transactions in parallel batches
            while time.time() < end_time:
                batch_tasks = [send_tx() for _ in range(min(10, target_tps // 10))]
                results = await asyncio.gather(*batch_tasks)
                
                for success, send_time, confirm_time, total_time in results:
                    if success:
                        successful_txs += 1
                        send_times.append(send_time)
                        confirm_times.append(confirm_time)
                        latencies.append(total_time)
                    else:
                        failed_txs += 1
        
        elif measure_mode == 'send':
            # Send mode: Measure only sending time, don't wait for confirmation
            print("📤 Measuring send time only...")
            
            while time.time() < end_time:
                batch_start = time.time()
                batch_size = min(10, target_tps // 10)
                
                for _ in range(batch_size):
                    try:
                        send_start = time.time()
                        
                        # Build and send transaction
                        tx = contract.functions.increment().build_transaction({
                            'from': self.signer.address,
                            'nonce': self.web3.eth.get_transaction_count(self.signer.address),
                            'gas': 1000000,
                            'gasPrice': 0,
                            'chainId': self.network_config['chainId']
                        })
                        
                        signed = self.signer.sign_transaction(tx)
                        raw_tx = signed.raw_transaction if hasattr(signed, 'raw_transaction') else signed.rawTransaction
                        tx_hash = self.web3.eth.send_raw_transaction(raw_tx)
                        
                        send_end = time.time()
                        send_time = (send_end - send_start) * 1000
                        
                        send_times.append(send_time)
                        latencies.append(send_time)
                        pending_txs.append(tx_hash)
                        successful_txs += 1
                        
                    except Exception as e:
                        failed_txs += 1
                        print(f"❌ Transaction failed: {e}")
                
                # Rate limiting
                batch_duration = time.time() - batch_start
                target_batch_duration = batch_size / target_tps
                if batch_duration < target_batch_duration:
                    await asyncio.sleep(target_batch_duration - batch_duration)
            
            # Wait for all pending transactions at the end
            if pending_txs:
                print(f"⏳ Waiting for {len(pending_txs)} pending transactions...")
                for tx_hash in pending_txs:
                    try:
                        self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
                    except:
                        pass
        
        else:  # 'full' mode (default)
            # Full mode: Measure complete transaction lifecycle
            print("📊 Measuring full transaction lifecycle...")
            
            while time.time() < end_time:
                batch_start = time.time()
                batch_size = min(10, target_tps // 10)
                
                for _ in range(batch_size):
                    try:
                        tx_start = time.time()
                        
                        # Execute includes sending + waiting for confirmation
                        tx_hash = await self.execute(contract, 'increment')
                        
                        tx_end = time.time()
                        total_time = (tx_end - tx_start) * 1000
                        
                        latencies.append(total_time)
                        successful_txs += 1
                        
                    except Exception as e:
                        failed_txs += 1
                        print(f"❌ Transaction failed: {e}")
                
                # Rate limiting
                batch_duration = time.time() - batch_start
                target_batch_duration = batch_size / target_tps
                if batch_duration < target_batch_duration:
                    await asyncio.sleep(target_batch_duration - batch_duration)
        
        actual_duration = time.time() - start_time
        actual_tps = successful_txs / actual_duration
        
        # Get final counter value
        final_counter = await self.call(contract, 'getCounter')
        
        results = {
            'duration': round(actual_duration, 2),
            'successful_transactions': successful_txs,
            'failed_transactions': failed_txs,
            'actual_tps': round(actual_tps, 2),
            'target_tps': target_tps,
            'efficiency': round((actual_tps / target_tps) * 100, 2),
            'final_counter': int(final_counter),
            'measurement_mode': measure_mode,
            'contract_address': contract.address
        }
        
        # Add timing statistics based on mode
        if latencies:
            results['avg_latency_ms'] = round(statistics.mean(latencies), 2)
            results['min_latency_ms'] = round(min(latencies), 2)
            results['max_latency_ms'] = round(max(latencies), 2)
            results['median_latency_ms'] = round(statistics.median(latencies), 2)
        
        if send_times:
            results['avg_send_time_ms'] = round(statistics.mean(send_times), 2)
            results['min_send_time_ms'] = round(min(send_times), 2)
            results['max_send_time_ms'] = round(max(send_times), 2)
        
        if confirm_times:
            results['avg_confirm_time_ms'] = round(statistics.mean(confirm_times), 2)
            results['min_confirm_time_ms'] = round(min(confirm_times), 2)
            results['max_confirm_time_ms'] = round(max(confirm_times), 2)
        
        print(f"\n📊 TPS Test Results ({measure_mode} mode):")
        print(f"Duration: {results['duration']}s")
        print(f"Successful Transactions: {results['successful_transactions']}")
        print(f"Failed Transactions: {results['failed_transactions']}")
        print(f"Actual TPS: {results['actual_tps']}")
        print(f"Target TPS: {results['target_tps']}")
        print(f"Efficiency: {results['efficiency']}%")
        
        if 'avg_latency_ms' in results:
            print(f"Average Latency: {results['avg_latency_ms']}ms")
        if 'avg_send_time_ms' in results:
            print(f"Average Send Time: {results['avg_send_time_ms']}ms")
        if 'avg_confirm_time_ms' in results:
            print(f"Average Confirmation Time: {results['avg_confirm_time_ms']}ms")
        
        return results
    
    async def measureLatency(self, operations: int = 100) -> Dict:
        """
        Measure network latency for different operations
        
        Args:
            operations: Number of operations to test (default: 100)
            
        Returns:
            Dictionary with latency measurements
        """
        print(f"📊 Measuring latency for {operations} operations...")
        
        # Test different operation types
        latencies = {
            'balance_check': [],
            'block_fetch': [],
            'transaction_send': [],
            'contract_call': []
        }
        
        # Deploy a simple contract for testing
        test_contract = """
        pragma solidity ^0.8.19;
        contract LatencyTest {
            uint256 public value = 42;
            function getValue() public view returns (uint256) {
                return value;
            }
            function setValue(uint256 _value) public {
                value = _value;
            }
        }
        """
        
        print("📄 Deploying latency test contract...")
        factory = await self.contract(test_contract)
        contract = await factory.deploy()
        
        for i in range(operations):
            print(f"🔄 Running operation {i+1}/{operations}", end='\r')
            
            # Test balance check latency
            start = time.time()
            await self.balance()
            latencies['balance_check'].append((time.time() - start) * 1000)
            
            # Test block fetch latency
            start = time.time()
            await self.block()
            latencies['block_fetch'].append((time.time() - start) * 1000)
            
            # Test contract call latency (read operation)
            start = time.time()
            await self.call(contract, 'getValue')
            latencies['contract_call'].append((time.time() - start) * 1000)
            
            # Test transaction send latency (write operation) - every 10th iteration
            if i % 10 == 0 and self.signer:
                start = time.time()
                await self.execute(contract, 'setValue', i)
                latencies['transaction_send'].append((time.time() - start) * 1000)
        
        print("\n")
        
        # Calculate statistics
        results = {}
        for operation, times in latencies.items():
            if times:
                results[operation] = {
                    'operations': len(times),
                    'avg_ms': round(statistics.mean(times), 2),
                    'min_ms': round(min(times), 2),
                    'max_ms': round(max(times), 2),
                    'median_ms': round(statistics.median(times), 2),
                    'std_dev_ms': round(statistics.stdev(times) if len(times) > 1 else 0, 2)
                }
        
        print(f"📊 Latency Test Results:")
        for operation, stats in results.items():
            print(f"{operation}: {stats['avg_ms']}ms avg (min: {stats['min_ms']}, max: {stats['max_ms']})")
        
        return results
    
    async def benchmarkThroughput(self, test_duration: int = 60) -> Dict:
        """
        Benchmark blockchain throughput (TPS with mixed operations)
        
        Args:
            test_duration: Test duration in seconds (default: 60)
            
        Returns:
            Dictionary with throughput metrics (TPS, data transfer, success rates)
        """
        if not self.signer:
            raise Exception("No signer available. Call connect() first.")
        
        print(f"⚡ Running throughput benchmark for {test_duration} seconds...")
        print("📊 Testing mixed operations (writes + reads) for realistic TPS...")
        
        # Deploy benchmark contract
        benchmark_contract = """
        pragma solidity ^0.8.19;
        contract ThroughputTest {
            mapping(address => uint256) public userCounters;
            uint256 public totalOperations;
            
            function incrementUser() public {
                userCounters[msg.sender]++;
                totalOperations++;
            }
            
            function batchIncrement(uint256 times) public {
                for(uint256 i = 0; i < times; i++) {
                    userCounters[msg.sender]++;
                    totalOperations++;
                }
            }
            
            function getUserCounter(address user) public view returns (uint256) {
                return userCounters[user];
            }
        }
        """
        
        print("📄 Deploying throughput test contract...")
        factory = await self.contract(benchmark_contract)
        contract = await factory.deploy()
        
        start_time = time.time()
        end_time = start_time + test_duration
        
        # Track different operation types
        write_ops = 0
        read_ops = 0
        successful_writes = 0
        successful_reads = 0
        failed_ops = 0
        bytes_transferred = 0
        tx_sizes = []
        write_latencies = []
        read_latencies = []
        
        print("🚀 Starting throughput test...")
        
        while time.time() < end_time:
            try:
                # Mix of different operations
                total_ops = write_ops + read_ops
                operation_type = total_ops % 4
                
                if operation_type == 0:
                    # Single increment - write operation
                    op_start = time.time()
                    
                    tx = contract.functions.incrementUser().build_transaction({
                        'from': self.signer.address,
                        'nonce': self.web3.eth.get_transaction_count(self.signer.address),
                        'gas': 1000000,
                        'gasPrice': 0,
                        'chainId': self.network_config['chainId']
                    })
                    
                    signed = self.signer.sign_transaction(tx)
                    raw_tx = signed.raw_transaction if hasattr(signed, 'raw_transaction') else signed.rawTransaction
                    
                    # Actual transaction size in bytes
                    tx_size = len(raw_tx)
                    tx_sizes.append(tx_size)
                    bytes_transferred += tx_size
                    
                    # Send transaction
                    tx_hash = self.web3.eth.send_raw_transaction(raw_tx)
                    receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
                    
                    op_end = time.time()
                    write_latencies.append((op_end - op_start) * 1000)
                    write_ops += 1
                    successful_writes += 1
                    
                elif operation_type == 1:
                    # Batch increment - write operation
                    op_start = time.time()
                    
                    tx = contract.functions.batchIncrement(5).build_transaction({
                        'from': self.signer.address,
                        'nonce': self.web3.eth.get_transaction_count(self.signer.address),
                        'gas': 1000000,
                        'gasPrice': 0,
                        'chainId': self.network_config['chainId']
                    })
                    
                    signed = self.signer.sign_transaction(tx)
                    raw_tx = signed.raw_transaction if hasattr(signed, 'raw_transaction') else signed.rawTransaction
                    
                    tx_size = len(raw_tx)
                    tx_sizes.append(tx_size)
                    bytes_transferred += tx_size
                    
                    tx_hash = self.web3.eth.send_raw_transaction(raw_tx)
                    receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
                    
                    op_end = time.time()
                    write_latencies.append((op_end - op_start) * 1000)
                    write_ops += 1
                    successful_writes += 1
                    
                elif operation_type == 2:
                    # Read operation
                    op_start = time.time()
                    
                    # For read operations, estimate based on call data
                    call_data = contract.encode_abi('getUserCounter', [self.signer.address])
                    request_size = len(call_data) + 100  # Call data + JSON-RPC overhead
                    
                    result = await self.call(contract, 'getUserCounter', self.signer.address)
                    
                    op_end = time.time()
                    read_latencies.append((op_end - op_start) * 1000)
                    
                    # Response size (result + JSON-RPC overhead)
                    response_size = len(str(result)) + 100
                    total_size = request_size + response_size
                    
                    tx_sizes.append(total_size)
                    bytes_transferred += total_size
                    read_ops += 1
                    successful_reads += 1
                    
                else:
                    # Check total operations - read operation
                    op_start = time.time()
                    
                    call_data = contract.encode_abi('totalOperations', [])
                    request_size = len(call_data) + 100
                    
                    result = await self.call(contract, 'totalOperations')
                    
                    op_end = time.time()
                    read_latencies.append((op_end - op_start) * 1000)
                    
                    response_size = len(str(result)) + 100
                    total_size = request_size + response_size
                    
                    tx_sizes.append(total_size)
                    bytes_transferred += total_size
                    read_ops += 1
                    successful_reads += 1
                
            except Exception as e:
                failed_ops += 1
                print(f"❌ Operation failed: {e}")
        
        actual_duration = time.time() - start_time
        
        # Get final contract state
        final_user_counter = await self.call(contract, 'getUserCounter', self.signer.address)
        final_total_ops = await self.call(contract, 'totalOperations')
        
        # Calculate metrics
        total_operations = write_ops + read_ops
        successful_operations = successful_writes + successful_reads
        
        # Throughput in blockchain = TPS (Transactions Per Second)
        write_tps = successful_writes / actual_duration if actual_duration > 0 else 0
        read_tps = successful_reads / actual_duration if actual_duration > 0 else 0
        total_tps = successful_operations / actual_duration if actual_duration > 0 else 0
        
        # Data transfer metrics (secondary)
        bytes_per_second = bytes_transferred / actual_duration if actual_duration > 0 else 0
        kb_per_second = bytes_per_second / 1024
        
        results = {
            'duration': round(actual_duration, 2),
            'total_operations': total_operations,
            'write_operations': write_ops,
            'read_operations': read_ops,
            'successful_writes': successful_writes,
            'successful_reads': successful_reads,
            'failed_operations': failed_ops,
            
            # Primary metric: TPS (blockchain throughput)
            'throughput_tps': round(total_tps, 2),
            'write_tps': round(write_tps, 2),
            'read_tps': round(read_tps, 2),
            
            # Latencies
            'avg_write_latency_ms': round(statistics.mean(write_latencies), 2) if write_latencies else 0,
            'avg_read_latency_ms': round(statistics.mean(read_latencies), 2) if read_latencies else 0,
            
            # Data transfer (secondary metrics)
            'bytes_transferred': bytes_transferred,
            'kb_per_second': round(kb_per_second, 2),
            'avg_transaction_size': round(statistics.mean(tx_sizes), 2) if tx_sizes else 0,
            
            # Success rate
            'success_rate': round((successful_operations / total_operations) * 100, 2) if total_operations > 0 else 0,
            
            # Contract state
            'final_user_counter': int(final_user_counter),
            'final_total_operations': int(final_total_ops),
            'contract_address': contract.address
        }
        
        print(f"\n⚡ Throughput Benchmark Results:")
        print(f"Duration: {results['duration']}s")
        print(f"Total Throughput: {results['throughput_tps']} TPS")
        print(f"  - Write TPS: {results['write_tps']}")
        print(f"  - Read TPS: {results['read_tps']}")
        print(f"Average Latency: Write={results['avg_write_latency_ms']}ms, Read={results['avg_read_latency_ms']}ms")
        print(f"Data Transfer: {results['kb_per_second']} KB/s")
        print(f"Success Rate: {results['success_rate']}%")
        
        return results
    
    async def runPerformanceTest(self, quick: bool = False) -> Dict:
        """
        Run complete performance test suite
        
        Args:
            quick: Run quick test (shorter duration) if True
            
        Returns:
            Dictionary with all performance metrics
        """
        if not self.signer:
            raise Exception("No signer available. Call connect() first.")
        
        print("🎯 Starting Complete Performance Test Suite...")
        print("=" * 50)
        
        results = {}
        
        # Adjust durations based on quick flag
        tps_duration = 15 if quick else 30
        latency_ops = 50 if quick else 100
        throughput_duration = 30 if quick else 60
        
        try:
            # 1. Latency Test
            print("\n1️⃣ Running Latency Test...")
            results['latency'] = await self.measureLatency(latency_ops)
            
            # 2. TPS Test
            print(f"\n2️⃣ Running TPS Test...")
            results['tps'] = await self.testTPS(tps_duration, 50, 'full')
            
            # 3. Throughput Test
            print(f"\n3️⃣ Running Throughput Test...")
            results['throughput'] = await self.benchmarkThroughput(throughput_duration)
            
            # 4. Network Status
            print("\n4️⃣ Getting Network Status...")
            results['network'] = await self.status()
            
            # Overall summary
            print(f"\n🏆 Performance Test Summary:")
            print(f"Average Latency: {results['latency']['balance_check']['avg_ms']}ms")
            print(f"Achieved TPS: {results['tps']['actual_tps']}")
            print(f"Throughput: {results['throughput']['throughput_tps']} TPS (mixed operations)")
            print(f"Network: {results['network']['networkName']}")
            
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            results['error'] = str(e)
        
        return results