#!/usr/bin/env python3
"""
Example: Creating and using multiple accounts with PureChain's zero gas fees
This shows the CORRECT way to handle accounts without checking balance for gas
"""

import asyncio
from purechainlib import PureChain

async def multi_account_example():
    """
    Demonstrate multiple account creation and usage with zero gas fees.
    This corrects the common mistake of checking balance before operations.
    """
    
    print("🚀 PureChain Zero-Gas Multi-Account Example")
    print("=" * 60)
    
    # Initialize PureChain
    pc = PureChain('testnet')
    
    # Connect with your main account
    # For testing, you can use a new account or your existing key
    main_account = pc.account()  # Create new account for demo
    pc.connect(main_account['privateKey'])
    
    print(f"Main account: {pc.signer.address}")
    
    # Check balance (for information only, NOT for validation!)
    balance = await pc.balance()
    print(f"Main account balance: {balance} PURE")
    
    # Create multiple new accounts
    print("\n📝 Creating 3 new accounts:")
    accounts = []
    for i in range(3):
        account = pc.account()
        accounts.append(account)
        print(f"Account {i+1}: {account['address']}")
    
    # IMPORTANT: With zero gas fees, we can send transactions regardless of balance!
    # We only need balance if we're sending VALUE, not for gas
    
    print("\n💡 Sending transactions (0 PURE value):")
    print("Note: These work even with 0 balance because gas is FREE!")
    
    for i, account in enumerate(accounts):
        try:
            # Send 0 PURE - this should work even with 0 balance!
            # We're not sending value, just creating a transaction
            result = await pc.send(account['address'], '0')
            print(f"✅ Sent to Account {i+1} - tx: {result.get('transactionHash', 'pending')}")
        except Exception as e:
            # If this fails, it's a network issue, not gas-related
            print(f"⚠️ Account {i+1} transaction failed: {e}")
    
    # Check balances of new accounts
    print("\n📊 Checking new account balances:")
    for i, account in enumerate(accounts):
        try:
            balance = await pc.balance(account['address'])
            print(f"Account {i+1} balance: {balance} PURE")
        except Exception as e:
            print(f"Account {i+1} balance check failed: {e}")
    
    # Deploy a simple contract (works with 0 balance for gas!)
    print("\n📄 Deploying contract with zero gas fees:")
    contract_source = """
    pragma solidity ^0.8.19;
    contract MultiAccountTest {
        mapping(address => bool) public registered;
        
        function register() public {
            registered[msg.sender] = true;
        }
    }
    """
    
    try:
        factory = await pc.contract(contract_source)
        contract = await factory.deploy()
        print(f"✅ Contract deployed at: {contract.address}")
        
        # Register each account (0 gas cost!)
        print("\n🔄 Registering accounts with contract:")
        for i, account in enumerate(accounts):
            # Switch to each account
            pc.connect(account['privateKey'])
            try:
                result = await pc.execute(contract, 'register')
                print(f"✅ Account {i+1} registered")
            except Exception as e:
                print(f"⚠️ Account {i+1} registration failed: {e}")
        
    except Exception as e:
        print(f"⚠️ Contract operations failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Key Takeaways:")
    print("1. No balance needed for gas (it's always 0)")
    print("2. Balance only needed for sending VALUE")
    print("3. Contract deployment costs 0 gas")
    print("4. Contract execution costs 0 gas")
    print("5. Account creation is always free")
    
    print("\n⚠️ Common Mistakes to Avoid:")
    print("❌ DON'T check balance before operations for gas")
    print("❌ DON'T skip operations due to low balance")
    print("✅ DO send 0-value transactions freely")
    print("✅ DO deploy and interact with contracts freely")

async def main():
    """Main function with error handling"""
    try:
        await multi_account_example()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nThis example requires connection to PureChain network.")
        print("Make sure you're using the correct RPC endpoint.")

if __name__ == "__main__":
    asyncio.run(main())