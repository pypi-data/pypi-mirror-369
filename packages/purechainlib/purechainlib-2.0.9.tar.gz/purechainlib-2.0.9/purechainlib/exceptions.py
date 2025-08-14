"""
Custom exceptions for PureChainLib
"""


class PureChainException(Exception):
    """Base exception for all PureChain errors"""
    pass


class AccountException(PureChainException):
    """Exception raised for account-related errors"""
    pass


class CompilerException(PureChainException):
    """Exception raised for Solidity compilation errors"""
    pass


class ContractException(PureChainException):
    """Exception raised for contract deployment/interaction errors"""
    pass


class TransactionException(PureChainException):
    """Exception raised for transaction-related errors"""
    pass


class NetworkException(PureChainException):
    """Exception raised for network connection errors"""
    pass


class ValidationException(PureChainException):
    """Exception raised for input validation errors"""
    pass