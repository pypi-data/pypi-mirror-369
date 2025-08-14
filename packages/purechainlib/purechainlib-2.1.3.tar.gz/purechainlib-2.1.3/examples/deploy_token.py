"""
Example: Deploy an ERC20 token contract on PureChain
Demonstrates contract compilation, deployment, and interaction with ZERO gas costs
"""

import asyncio
from purechainlib import PureChain

# Simple ERC20 token contract
TOKEN_CONTRACT = """
pragma solidity ^0.8.19;

contract SimpleToken {
    string public name;
    string public symbol;
    uint8 public decimals = 18;
    uint256 public totalSupply;
    
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    
    constructor(string memory _name, string memory _symbol, uint256 _totalSupply) {
        name = _name;
        symbol = _symbol;
        totalSupply = _totalSupply * 10**uint256(decimals);
        balanceOf[msg.sender] = totalSupply;
        emit Transfer(address(0), msg.sender, totalSupply);
    }
    
    function transfer(address _to, uint256 _value) public returns (bool success) {
        require(balanceOf[msg.sender] >= _value, "Insufficient balance");
        balanceOf[msg.sender] -= _value;
        balanceOf[_to] += _value;
        emit Transfer(msg.sender, _to, _value);
        return true;
    }
    
    function approve(address _spender, uint256 _value) public returns (bool success) {
        allowance[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }
    
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success) {
        require(_value <= balanceOf[_from], "Insufficient balance");
        require(_value <= allowance[_from][msg.sender], "Insufficient allowance");
        balanceOf[_from] -= _value;
        balanceOf[_to] += _value;
        allowance[_from][msg.sender] -= _value;
        emit Transfer(_from, _to, _value);
        return true;
    }
}
"""


async def main():
    """Deploy and interact with a token contract"""
    
    print("=" * 60)
    print("PureChain Token Deployment Example")
    print("Zero Gas Cost Blockchain!")
    print("=" * 60)
    
    # Initialize PureChain
    purechain = PureChain('testnet')
    
    # Create or connect account
    print("\n1. Setting up account...")
    
    # Option 1: Create new account
    account = purechain.account()
    print(f"   Created new account: {account.address}")
    print(f"   Private key: {account.private_key}")
    print("   ⚠️  Save your private key securely!")
    
    # Option 2: Connect existing account (uncomment to use)
    # private_key = "0x..." # Your private key
    # account = await purechain.connect(private_key)
    
    # Connect the account for transactions
    await purechain.connect(account.private_key)
    
    # Check balance
    balance = await purechain.balance()
    print(f"   Account balance: {balance} PURE")
    
    # Compile contract
    print("\n2. Compiling token contract...")
    factory = await purechain.contract(TOKEN_CONTRACT)
    print("   ✅ Contract compiled successfully")
    
    # Deploy contract
    print("\n3. Deploying token contract...")
    print("   Token Name: MyToken")
    print("   Token Symbol: MTK")
    print("   Total Supply: 1,000,000")
    print("   Gas Cost: 0 (FREE!)")
    
    token = await factory.deploy(
        "MyToken",      # name
        "MTK",          # symbol
        1000000,        # totalSupply
        account=account
    )
    
    print(f"\n   🎉 Token deployed at: {token.address}")
    
    # Interact with deployed contract
    print("\n4. Interacting with token contract...")
    
    # Read token information
    name = await purechain.call(token, 'name')
    symbol = await purechain.call(token, 'symbol')
    decimals = await purechain.call(token, 'decimals')
    total_supply = await purechain.call(token, 'totalSupply')
    
    print(f"   Token Name: {name}")
    print(f"   Token Symbol: {symbol}")
    print(f"   Decimals: {decimals}")
    print(f"   Total Supply: {total_supply / 10**decimals:,.0f} {symbol}")
    
    # Check deployer balance
    deployer_balance = await purechain.call(token, 'balanceOf', account.address)
    print(f"   Deployer Balance: {deployer_balance / 10**decimals:,.0f} {symbol}")
    
    # Transfer tokens (if you have another account)
    print("\n5. Token Transfer Example...")
    
    # Create a recipient account
    recipient = purechain.account()
    print(f"   Recipient address: {recipient.address}")
    
    # Transfer 1000 tokens
    transfer_amount = 1000 * 10**decimals
    print(f"   Transferring 1,000 {symbol} to recipient...")
    
    receipt = await purechain.execute(
        token,
        'transfer',
        recipient.address,
        transfer_amount
    )
    
    print(f"   ✅ Transfer successful!")
    print(f"   Transaction hash: {receipt['transactionHash']}")
    print(f"   Gas used: {receipt['gasUsed']} (Always 0 on PureChain!)")
    
    # Check new balances
    sender_balance = await purechain.call(token, 'balanceOf', account.address)
    recipient_balance = await purechain.call(token, 'balanceOf', recipient.address)
    
    print(f"\n   Updated Balances:")
    print(f"   Sender: {sender_balance / 10**decimals:,.0f} {symbol}")
    print(f"   Recipient: {recipient_balance / 10**decimals:,.0f} {symbol}")
    
    print("\n" + "=" * 60)
    print("✨ Token deployment and interaction completed!")
    print("💸 Total gas cost: 0 PURE (Everything is free on PureChain!)")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())