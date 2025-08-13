"""
PureChain Python Library - Zero Gas EVM Network SDK
Matches npm library API exactly
"""

__version__ = "2.0.6"
__author__ = "PureChain Team"

# Main exports - matching npm library
from purechainlib.purechain import PureChain, ContractFactory

# Utility exports
from purechainlib.account import Account
from purechainlib.compiler import SolidityCompiler
from purechainlib.carbon_tracker import CarbonFootprintTracker
from purechainlib.exceptions import (
    PureChainException,
    NetworkException,
    CompilerException,
    TransactionException
)

__all__ = [
    "PureChain",
    "ContractFactory", 
    "Account",
    "SolidityCompiler",
    "CarbonFootprintTracker",
    "PureChainException",
    "NetworkException",
    "CompilerException", 
    "TransactionException"
]