"""
Network configuration for PureChain
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class NetworkConfig(BaseModel):
    """Network configuration model"""
    
    name: str = Field(..., description="Network name")
    chain_id: int = Field(..., description="Chain ID")
    rpc_url: str = Field(..., description="RPC endpoint URL")
    explorer_url: Optional[str] = Field(None, description="Block explorer URL")
    ws_url: Optional[str] = Field(None, description="WebSocket URL")
    
    class Config:
        frozen = True  # Make immutable


# Predefined network configurations
NETWORKS: Dict[str, NetworkConfig] = {
    "mainnet": NetworkConfig(
        name="PureChain Mainnet",
        chain_id=900520900520,
        rpc_url="https://purechainnode.com:8547",
        explorer_url="https://nsllab-kit.onrender.com/explorer",
        ws_url="wss://purechainnode.com:8548"
    ),
    "testnet": NetworkConfig(
        name="PureChain Testnet",
        chain_id=900520900520,
        rpc_url="https://purechainnode.com:8547",
        explorer_url="https://nsllab-kit.onrender.com/explorer",
        ws_url="wss://purechainnode.com:8548"
    ),
    "local": NetworkConfig(
        name="Local Development",
        chain_id=1337,
        rpc_url="http://localhost:8545",
        explorer_url=None,
        ws_url="ws://localhost:8546"
    )
}


def get_network_config(network: str) -> NetworkConfig:
    """
    Get network configuration by name
    
    Args:
        network: Network name (mainnet, testnet, local)
        
    Returns:
        NetworkConfig object
        
    Raises:
        ValueError: If network is not found
    """
    if network not in NETWORKS:
        raise ValueError(f"Unknown network: {network}. Available: {list(NETWORKS.keys())}")
    return NETWORKS[network]


def create_custom_network(name: str, chain_id: int, rpc_url: str, **kwargs) -> NetworkConfig:
    """
    Create a custom network configuration
    
    Args:
        name: Network name
        chain_id: Chain ID
        rpc_url: RPC endpoint URL
        **kwargs: Additional optional parameters
        
    Returns:
        NetworkConfig object
    """
    return NetworkConfig(
        name=name,
        chain_id=chain_id,
        rpc_url=rpc_url,
        **kwargs
    )