"""
Account management for PureChain
Handles wallet creation, key management, and transaction signing
"""

import secrets
from typing import Optional, Dict, Any, Union
from eth_account import Account as EthAccount
from eth_account.messages import encode_defunct
from eth_utils import to_checksum_address
from mnemonic import Mnemonic
from web3 import Web3
from coincurve import PrivateKey

from purechainlib.exceptions import AccountException


class Account:
    """
    Account management for PureChain
    Provides wallet creation, key management, and transaction signing
    """
    
    def __init__(self, private_key: Optional[str] = None):
        """
        Initialize an account
        
        Args:
            private_key: Private key in hex format (optional)
        """
        if private_key:
            self._load_from_key(private_key)
        else:
            self._create_new()
    
    def _load_from_key(self, private_key: str) -> None:
        """Load account from private key"""
        try:
            # Remove 0x prefix if present
            if private_key.startswith('0x'):
                private_key = private_key[2:]
            
            # Validate and create account
            self._private_key = private_key
            self._account = EthAccount.from_key(f"0x{private_key}")
            self._address = self._account.address
        except Exception as e:
            raise AccountException(f"Invalid private key: {str(e)}")
    
    def _create_new(self) -> None:
        """Create a new account with random private key"""
        # Generate secure random private key using coincurve for performance
        private_key_bytes = secrets.token_bytes(32)
        private_key = PrivateKey(private_key_bytes)
        
        # Create account from private key
        self._private_key = private_key_bytes.hex()
        self._account = EthAccount.from_key(private_key_bytes)
        self._address = self._account.address
    
    @classmethod
    def from_key(cls, private_key: str) -> 'Account':
        """
        Create account from private key
        
        Args:
            private_key: Private key in hex format
            
        Returns:
            Account instance
        """
        return cls(private_key)
    
    @classmethod
    def from_mnemonic(cls, mnemonic: str, path: str = "m/44'/60'/0'/0/0") -> 'Account':
        """
        Create account from mnemonic phrase
        
        Args:
            mnemonic: BIP39 mnemonic phrase
            path: Derivation path (default: Ethereum path)
            
        Returns:
            Account instance
        """
        try:
            # Validate mnemonic
            mnemo = Mnemonic("english")
            if not mnemo.check(mnemonic):
                raise AccountException("Invalid mnemonic phrase")
            
            # Generate seed and derive key
            seed = mnemo.to_seed(mnemonic)
            account = EthAccount.from_mnemonic(mnemonic, account_path=path)
            
            return cls(account.key.hex())
        except Exception as e:
            raise AccountException(f"Failed to create account from mnemonic: {str(e)}")
    
    @classmethod
    def create(cls) -> 'Account':
        """
        Create a new random account
        
        Returns:
            Account instance with new keys
        """
        return cls()
    
    @classmethod
    def create_with_mnemonic(cls, strength: int = 128) -> tuple['Account', str]:
        """
        Create a new account with mnemonic phrase
        
        Args:
            strength: Mnemonic strength in bits (128, 160, 192, 224, 256)
            
        Returns:
            Tuple of (Account instance, mnemonic phrase)
        """
        try:
            # Generate mnemonic
            mnemo = Mnemonic("english")
            mnemonic = mnemo.generate(strength=strength)
            
            # Create account from mnemonic
            account = cls.from_mnemonic(mnemonic)
            
            return account, mnemonic
        except Exception as e:
            raise AccountException(f"Failed to create account with mnemonic: {str(e)}")
    
    @property
    def address(self) -> str:
        """Get account address (checksummed)"""
        return self._address
    
    @property
    def private_key(self) -> str:
        """Get private key in hex format (with 0x prefix)"""
        return f"0x{self._private_key}"
    
    def sign_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sign a transaction
        
        Args:
            transaction: Transaction dictionary
            
        Returns:
            Signed transaction dictionary
        """
        try:
            # Ensure zero gas for PureChain
            transaction['gas'] = 0
            transaction['gasPrice'] = 0
            transaction['maxFeePerGas'] = 0
            transaction['maxPriorityFeePerGas'] = 0
            
            # Sign transaction
            signed = self._account.sign_transaction(transaction)
            
            return {
                'rawTransaction': signed.rawTransaction.hex(),
                'hash': signed.hash.hex(),
                'r': signed.r,
                's': signed.s,
                'v': signed.v
            }
        except Exception as e:
            raise AccountException(f"Failed to sign transaction: {str(e)}")
    
    def sign_message(self, message: Union[str, bytes]) -> str:
        """
        Sign a message
        
        Args:
            message: Message to sign
            
        Returns:
            Signature in hex format
        """
        try:
            # Convert string to bytes if needed
            if isinstance(message, str):
                message = message.encode('utf-8')
            
            # Create signable message
            signable_message = encode_defunct(message)
            
            # Sign message
            signed = self._account.sign_message(signable_message)
            
            return signed.signature.hex()
        except Exception as e:
            raise AccountException(f"Failed to sign message: {str(e)}")
    
    def encrypt(self, password: str) -> Dict[str, Any]:
        """
        Encrypt private key with password (create keystore)
        
        Args:
            password: Password for encryption
            
        Returns:
            Encrypted keystore dictionary
        """
        try:
            return self._account.encrypt(password)
        except Exception as e:
            raise AccountException(f"Failed to encrypt account: {str(e)}")
    
    @classmethod
    def decrypt(cls, keystore: Dict[str, Any], password: str) -> 'Account':
        """
        Decrypt keystore with password
        
        Args:
            keystore: Encrypted keystore dictionary
            password: Password for decryption
            
        Returns:
            Account instance
        """
        try:
            private_key = EthAccount.decrypt(keystore, password)
            return cls(private_key.hex())
        except Exception as e:
            raise AccountException(f"Failed to decrypt keystore: {str(e)}")
    
    def __repr__(self) -> str:
        """String representation"""
        return f"<Account address='{self.address}'>"
    
    def __str__(self) -> str:
        """String conversion"""
        return self.address