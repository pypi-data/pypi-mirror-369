"""
Solidity compiler integration for PureChain
Handles compilation of Solidity source code and files
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import aiofiles
import solcx
from semantic_version import Version

from purechainlib.exceptions import CompilerException


class CompiledContract:
    """Represents a compiled Solidity contract"""
    
    def __init__(self, name: str, abi: List[Dict], bytecode: str, metadata: Optional[Dict] = None):
        """
        Initialize compiled contract
        
        Args:
            name: Contract name
            abi: Contract ABI
            bytecode: Contract bytecode
            metadata: Additional metadata
        """
        self.name = name
        self.abi = abi
        self.bytecode = bytecode
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "abi": self.abi,
            "bytecode": self.bytecode,
            "metadata": self.metadata
        }


class SolidityCompiler:
    """
    Solidity compiler wrapper for PureChain
    Uses py-solc-x for compilation
    """
    
    def __init__(self, version: str = "0.8.19"):
        """
        Initialize compiler
        
        Args:
            version: Solidity compiler version
        """
        self.version = version
        self._ensure_compiler_installed()
    
    def _ensure_compiler_installed(self) -> None:
        """Ensure the specified compiler version is installed"""
        try:
            installed_versions = solcx.get_installed_solc_versions()
            target_version = Version(self.version)
            
            if target_version not in installed_versions:
                print(f"Installing Solidity compiler v{self.version}...")
                solcx.install_solc(self.version)
                print(f"Solidity compiler v{self.version} installed successfully")
        except Exception as e:
            raise CompilerException(f"Failed to install Solidity compiler: {str(e)}")
    
    def compile_source(self, source: str, optimize: bool = True) -> Dict[str, CompiledContract]:
        """
        Compile Solidity source code
        
        Args:
            source: Solidity source code
            optimize: Enable optimizer
            
        Returns:
            Dictionary of contract name -> CompiledContract
        """
        try:
            # Set compiler version
            solcx.set_solc_version(self.version)
            
            # Compile source
            compiled = solcx.compile_source(
                source,
                output_values=['abi', 'bin', 'bin-runtime', 'metadata'],
                optimize=optimize,
                optimize_runs=200 if optimize else None
            )
            
            # Parse compiled contracts
            contracts = {}
            for contract_id, contract_data in compiled.items():
                # Extract contract name from ID (format: <source>:<contractName>)
                contract_name = contract_id.split(':')[-1]
                
                contracts[contract_name] = CompiledContract(
                    name=contract_name,
                    abi=contract_data['abi'],
                    bytecode=contract_data['bin'],
                    metadata={
                        'runtime_bytecode': contract_data.get('bin-runtime', ''),
                        'metadata': contract_data.get('metadata', {})
                    }
                )
            
            return contracts
        except Exception as e:
            raise CompilerException(f"Compilation failed: {str(e)}")
    
    async def compile_file(self, file_path: Union[str, Path], optimize: bool = True) -> Dict[str, CompiledContract]:
        """
        Compile Solidity file
        
        Args:
            file_path: Path to Solidity file
            optimize: Enable optimizer
            
        Returns:
            Dictionary of contract name -> CompiledContract
        """
        try:
            file_path = Path(file_path)
            
            # Check if file exists
            if not file_path.exists():
                raise CompilerException(f"File not found: {file_path}")
            
            # Read file content asynchronously
            async with aiofiles.open(file_path, 'r') as f:
                source = await f.read()
            
            # Handle imports (basic support)
            source = await self._resolve_imports(source, file_path.parent)
            
            # Compile source
            return self.compile_source(source, optimize)
        except CompilerException:
            raise
        except Exception as e:
            raise CompilerException(f"Failed to compile file: {str(e)}")
    
    async def _resolve_imports(self, source: str, base_path: Path) -> str:
        """
        Resolve import statements in Solidity source
        
        Args:
            source: Solidity source code
            base_path: Base directory for relative imports
            
        Returns:
            Source code with imports resolved
        """
        # Find all import statements
        import_pattern = r'import\s+["\'](.+?)["\'];'
        imports = re.findall(import_pattern, source)
        
        for import_path in imports:
            # Handle relative imports
            if import_path.startswith('./') or import_path.startswith('../'):
                full_path = base_path / import_path
                
                if full_path.exists():
                    # Read imported file
                    async with aiofiles.open(full_path, 'r') as f:
                        imported_source = await f.read()
                    
                    # Replace import with actual source
                    # This is a simplified approach - production should use proper import resolution
                    source = source.replace(f'import "{import_path}";', imported_source)
                    source = source.replace(f"import '{import_path}';", imported_source)
            
            # Handle OpenZeppelin and other common imports
            elif import_path.startswith('@openzeppelin/'):
                # For now, skip OpenZeppelin imports (would need to be installed)
                # In production, you'd resolve these from node_modules or a package manager
                pass
        
        return source
    
    def compile_standard_json(self, input_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compile using Solidity standard JSON input/output
        
        Args:
            input_json: Standard JSON input
            
        Returns:
            Standard JSON output
        """
        try:
            solcx.set_solc_version(self.version)
            return solcx.compile_standard(input_json)
        except Exception as e:
            raise CompilerException(f"Standard JSON compilation failed: {str(e)}")
    
    def get_contract_from_compiled(self, compiled: Dict[str, CompiledContract], name: str) -> CompiledContract:
        """
        Get specific contract from compiled output
        
        Args:
            compiled: Dictionary of compiled contracts
            name: Contract name to retrieve
            
        Returns:
            CompiledContract instance
            
        Raises:
            CompilerException: If contract not found
        """
        if name not in compiled:
            available = list(compiled.keys())
            raise CompilerException(f"Contract '{name}' not found. Available: {available}")
        
        return compiled[name]
    
    @staticmethod
    def install_solc_version(version: str) -> None:
        """
        Install a specific Solidity compiler version
        
        Args:
            version: Version to install
        """
        try:
            solcx.install_solc(version)
            print(f"Installed Solidity compiler v{version}")
        except Exception as e:
            raise CompilerException(f"Failed to install Solidity v{version}: {str(e)}")
    
    @staticmethod
    def get_available_versions() -> List[str]:
        """
        Get list of available Solidity compiler versions
        
        Returns:
            List of version strings
        """
        return [str(v) for v in solcx.get_installable_solc_versions()]
    
    @staticmethod
    def get_installed_versions() -> List[str]:
        """
        Get list of installed Solidity compiler versions
        
        Returns:
            List of version strings
        """
        return [str(v) for v in solcx.get_installed_solc_versions()]