"""
Quick Start Example for PureChainLib
Demonstrates basic usage patterns matching the JavaScript API
"""

import asyncio
from purechainlib import PureChain


async def main():
    """Quick start example showing main features"""
    
    print("🚀 PureChain Quick Start Example")
    print("=" * 50)
    
    # 1. Initialize PureChain
    purechain = PureChain('testnet')  # or 'mainnet', 'local'
    
    # Custom network example:
    # purechain = PureChain({
    #     'name': 'Custom Network',
    #     'chain_id': 1337,
    #     'rpc_url': 'http://localhost:8545'
    # })
    
    # 2. Account Management
    print("\n📝 Account Management:")
    
    # Create new account
    new_account = purechain.account()
    print(f"New account created: {new_account.address}")
    
    # Connect with private key
    # await purechain.connect('0x...')
    
    # Connect with mnemonic
    # await purechain.connect('word1 word2 word3...')
    
    # For this example, connect the new account
    await purechain.connect(new_account.private_key)
    
    # 3. Check Balance
    print("\n💰 Balance Check:")
    balance = await purechain.balance()
    print(f"Account balance: {balance} PURE")
    
    # Check another address balance
    # other_balance = await purechain.balance('0x...')
    
    # 4. Send Transaction (if account has balance)
    if balance > 0:
        print("\n📤 Sending Transaction:")
        recipient = purechain.account()  # Create recipient
        
        receipt = await purechain.send(recipient.address, 0.1)
        print(f"Sent 0.1 PURE to {recipient.address}")
        print(f"Transaction hash: {receipt['transactionHash']}")
        print(f"Gas used: {receipt['gasUsed']} (Always 0!)")
    
    # 5. Contract Deployment Example
    print("\n📄 Contract Example:")
    
    # Simple contract
    CONTRACT_CODE = """
    pragma solidity ^0.8.19;
    
    contract HelloWorld {
        string public message;
        
        constructor(string memory _message) {
            message = _message;
        }
        
        function setMessage(string memory _newMessage) public {
            message = _newMessage;
        }
        
        function getMessage() public view returns (string memory) {
            return message;
        }
    }
    """
    
    # Compile and deploy
    factory = await purechain.contract(CONTRACT_CODE)
    contract = await factory.deploy("Hello, PureChain!", account=new_account)
    
    print(f"Contract deployed at: {contract.address}")
    
    # Read from contract
    message = await purechain.call(contract, 'getMessage')
    print(f"Contract message: {message}")
    
    # Write to contract
    await purechain.execute(contract, 'setMessage', "Zero Gas is Amazing!")
    
    # Read updated message
    new_message = await purechain.call(contract, 'getMessage')
    print(f"Updated message: {new_message}")
    
    # 6. Deploy from file (example)
    # factory = await purechain.contract('contracts/MyToken.sol')
    # token = await factory.deploy("TokenName", "TKN", 1000000)
    
    print("\n" + "=" * 50)
    print("✅ Quick start completed!")
    print("💸 Total gas spent: 0 (Everything is free on PureChain!)")


if __name__ == "__main__":
    asyncio.run(main())