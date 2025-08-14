# PureChain RPC Configuration

## Network Details

PureChain provides direct RPC access for blockchain interaction with **ZERO GAS COSTS**.

### Official RPC Endpoints

| Network | RPC URL | Chain ID | WebSocket |
|---------|---------|----------|-----------|
| **Mainnet/Testnet** | `https://purechainnode.com:8547` | `900520900520` | `wss://purechainnode.com:8548` |
| **Local** | `http://localhost:8545` | `1337` | `ws://localhost:8546` |

### Connection Configuration

The library automatically connects to the testnet by default. You can customize the connection in several ways:

## 1. Using Default Networks

```python
from purechainlib import PureChain

# Connect to testnet (default)
pc = PureChain()

# Connect to mainnet
pc = PureChain(network='mainnet')

# Connect to local node
pc = PureChain(network='local')
```

## 2. Using Custom RPC

```python
# Custom RPC endpoint
pc = PureChain(rpc='https://purechainnode.com:8547')

# With custom chain ID
pc = PureChain(
    rpc='https://custom-node.com:8545',
    chain_id=900520900520
)
```

## 3. Configuration File

The library uses `purechain_config.json` for network settings:

```json
{
  "networks": {
    "testnet": {
      "name": "PureChain Testnet",
      "rpc_url": "https://purechainnode.com:8547",
      "ws_url": "wss://purechainnode.com:8548",
      "chain_id": 900520900520,
      "explorer": "https://nsllab-kit.onrender.com/explorer",
      "api_url": "https://nsllab-kit.onrender.com"
    }
  },
  "gas_settings": {
    "gas_price": 0,
    "comment": "PureChain uses gas for computation metering but gas price is always 0"
  }
}
```

## 4. Setup Wizard

Use the interactive setup wizard to configure your connection:

```bash
python setup_connection.py
```

This will guide you through:
1. Entering the RPC URL
2. Selecting network type
3. Testing the connection
4. Saving configuration

## Important Notes

### Gas Configuration
- **Gas Units**: Still used for computation metering
- **Gas Price**: Always 0 (zero cost!)
- **Gas Limit**: Default 3,000,000 for contracts, 21,000 for transfers

### Connection Testing

Test your connection with:

```python
from purechainlib import PureChain

pc = PureChain()
print(pc.status())
# Output: {
#   'connected': True,
#   'chain_id': 900520900520,
#   'account': None,
#   'balance': None,
#   'block': 12345,
#   'gas_price': 0
# }
```

### Direct RPC Access

For advanced users who need direct Web3 access:

```python
from purechainlib.direct_connection import PureChainDirect

# Direct connection with custom RPC
direct = PureChainDirect(rpc_url='https://purechainnode.com:8547')
direct.connect_account(private_key)

# Deploy contract
contract = direct.deploy_contract(abi, bytecode, *constructor_args)
```

## Troubleshooting

### Connection Issues

If you can't connect:

1. **Check RPC URL**: Ensure it's correct and accessible
   ```bash
   curl https://purechainnode.com:8547
   ```

2. **Check Network**: Verify you're on the right network
   ```python
   pc = PureChain()
   print(f"Connected: {pc.is_connected()}")
   print(f"Chain ID: {pc.chain_id}")
   ```

3. **Firewall/Proxy**: Ensure no firewall blocks the connection

4. **SSL/TLS**: For HTTPS endpoints, ensure certificates are valid

### Common Errors

| Error | Solution |
|-------|----------|
| `Connection refused` | Check if RPC URL is correct and service is running |
| `Invalid chain ID` | Verify chain ID matches network (900520900520) |
| `No account connected` | Call `pc.connect(private_key)` before transactions |
| `Insufficient funds` | Even with 0 gas cost, account needs PURE for value transfers |

## API Endpoints

Besides RPC, PureChain also provides REST API endpoints:

- **Explorer**: https://nsllab-kit.onrender.com/explorer
- **API Base**: https://nsllab-kit.onrender.com
- **Documentation**: https://nsllab-kit.onrender.com/docs

## Security Notes

1. **Never share your private key**
2. **Use environment variables for keys**:
   ```python
   import os
   private_key = os.getenv('PURECHAIN_PRIVATE_KEY')
   ```
3. **Use HTTPS/WSS for production**
4. **Validate contract addresses before interaction**

## Support

For issues or questions:
- GitHub Issues: [Report bugs or request features]
- Documentation: Check this guide and examples
- Network Status: Monitor at explorer URL