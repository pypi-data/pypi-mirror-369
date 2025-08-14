"""
PureChain Python Library - Zero Gas EVM Network SDK
Matches npm library API exactly
"""

__version__ = "2.1.3"
__author__ = "PureChain Team"

# Main exports - matching npm library
from purechainlib.purechain import PureChain, ContractFactory

# One-liner security audit function
async def audit(contract_code: str, tool: str = "slither") -> dict:
    """
    One-liner security audit
    
    Usage:
        import purechainlib as pcl
        result = await pcl.audit("contract code here")
    """
    pc = PureChain('testnet')
    result = await pc.audit(contract_code, tool=tool)
    
    # Fix the display issue: map 'findings' to 'issues' for backward compatibility
    if 'findings' in result and 'issues' not in result:
        result['issues'] = result['findings']
        result['issues_count'] = len(result['findings'])
    
    # Ensure success flag is set based on evaluation
    if 'summary' in result:
        result['success'] = (result['summary'].get('critical', 0) == 0 and 
                           result['summary'].get('high', 0) == 0)
    
    return result

# Utility exports
from purechainlib.account import Account
from purechainlib.compiler import SolidityCompiler
from purechainlib.carbon_tracker import CarbonFootprintTracker
from purechainlib.security_auditor import SecurityAuditor, SecurityTool, SeverityLevel
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
    "SecurityAuditor",
    "SecurityTool",
    "SeverityLevel",
    "PureChainException",
    "NetworkException",
    "CompilerException", 
    "TransactionException"
]