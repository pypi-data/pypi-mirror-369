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
    
    # Performance Testing Functions
    
    async def testTPS(self, duration: int = 30, target_tps: int = 100) -> Dict:
        """
        Test Transactions Per Second (TPS) performance
        
        Args:
            duration: Test duration in seconds (default: 30)
            target_tps: Target TPS to achieve (default: 100)
            
        Returns:
            Dictionary with TPS results
        """
        if not self.signer:
            raise Exception("No signer available. Call connect() first.")
        
        print(f"🚀 Starting TPS test for {duration} seconds...")
        print(f"🎯 Target TPS: {target_tps}")
        
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
        
        # Send transactions at target rate
        while time.time() < end_time:
            batch_start = time.time()
            batch_size = min(10, target_tps // 10)  # Send in small batches
            
            # Send batch of transactions
            for _ in range(batch_size):
                try:
                    tx_start = time.time()
                    tx_hash = await self.execute(contract, 'increment')
                    tx_end = time.time()
                    
                    latency = (tx_end - tx_start) * 1000  # Convert to ms
                    latencies.append(latency)
                    successful_txs += 1
                    
                except Exception as e:
                    failed_txs += 1
                    print(f"❌ Transaction failed: {e}")
            
            # Rate limiting to maintain target TPS
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
            'avg_latency_ms': round(statistics.mean(latencies) if latencies else 0, 2),
            'min_latency_ms': round(min(latencies) if latencies else 0, 2),
            'max_latency_ms': round(max(latencies) if latencies else 0, 2),
            'contract_address': contract.address
        }
        
        print(f"\n📊 TPS Test Results:")
        print(f"Duration: {results['duration']}s")
        print(f"Successful Transactions: {results['successful_transactions']}")
        print(f"Failed Transactions: {results['failed_transactions']}")
        print(f"Actual TPS: {results['actual_tps']}")
        print(f"Target TPS: {results['target_tps']}")
        print(f"Efficiency: {results['efficiency']}%")
        print(f"Average Latency: {results['avg_latency_ms']}ms")
        
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
        Benchmark overall network throughput
        
        Args:
            test_duration: Test duration in seconds (default: 60)
            
        Returns:
            Dictionary with throughput metrics
        """
        if not self.signer:
            raise Exception("No signer available. Call connect() first.")
        
        print(f"⚡ Running throughput benchmark for {test_duration} seconds...")
        
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
        
        operations_count = 0
        bytes_transferred = 0
        successful_ops = 0
        failed_ops = 0
        
        print("🚀 Starting throughput test...")
        
        while time.time() < end_time:
            try:
                # Mix of different operations
                operation_type = operations_count % 4
                
                if operation_type == 0:
                    # Single increment
                    await self.execute(contract, 'incrementUser')
                    bytes_transferred += 100  # Approximate transaction size
                    
                elif operation_type == 1:
                    # Batch increment
                    await self.execute(contract, 'batchIncrement', 5)
                    bytes_transferred += 150
                    
                elif operation_type == 2:
                    # Read operation
                    await self.call(contract, 'getUserCounter', self.signer.address)
                    bytes_transferred += 50
                    
                else:
                    # Check total operations
                    await self.call(contract, 'totalOperations')
                    bytes_transferred += 50
                
                operations_count += 1
                successful_ops += 1
                
            except Exception as e:
                failed_ops += 1
                print(f"❌ Operation failed: {e}")
        
        actual_duration = time.time() - start_time
        
        # Get final contract state
        final_user_counter = await self.call(contract, 'getUserCounter', self.signer.address)
        final_total_ops = await self.call(contract, 'totalOperations')
        
        # Calculate metrics
        ops_per_second = successful_ops / actual_duration
        bytes_per_second = bytes_transferred / actual_duration
        mb_per_second = bytes_per_second / (1024 * 1024)
        
        results = {
            'duration': round(actual_duration, 2),
            'total_operations': operations_count,
            'successful_operations': successful_ops,
            'failed_operations': failed_ops,
            'operations_per_second': round(ops_per_second, 2),
            'bytes_transferred': bytes_transferred,
            'bytes_per_second': round(bytes_per_second, 2),
            'mb_per_second': round(mb_per_second, 4),
            'success_rate': round((successful_ops / operations_count) * 100, 2),
            'final_user_counter': int(final_user_counter),
            'final_total_operations': int(final_total_ops),
            'contract_address': contract.address
        }
        
        print(f"\n⚡ Throughput Benchmark Results:")
        print(f"Duration: {results['duration']}s")
        print(f"Operations/sec: {results['operations_per_second']}")
        print(f"Throughput: {results['mb_per_second']} MB/s")
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
            results['tps'] = await self.testTPS(tps_duration, 50)
            
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
            print(f"Throughput: {results['throughput']['mb_per_second']} MB/s")
            print(f"Network: {results['network']['networkName']}")
            
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            results['error'] = str(e)
        
        return results