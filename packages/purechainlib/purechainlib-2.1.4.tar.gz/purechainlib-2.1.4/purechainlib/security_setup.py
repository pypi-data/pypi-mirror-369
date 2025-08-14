"""
Security Tools Setup Helper
Automatically installs and configures security audit tools
"""

import subprocess
import sys
import os
from typing import Dict, List, Tuple
import platform

class SecuritySetup:
    """
    Automatic setup for security audit tools
    Bundled with PureChainLib SDK
    """
    
    @staticmethod
    def check_and_install_tools() -> Dict[str, bool]:
        """
        Check and automatically install missing security tools
        
        Returns:
            Dictionary of tool installation status
        """
        print("🔧 PureChain Security Tools Setup")
        print("="*50)
        
        results = {}
        
        # Check Python tools
        python_tools = [
            ('slither-analyzer', 'slither', '--version'),
            ('mythril', 'myth', '--version'),
        ]
        
        for package, command, version_flag in python_tools:
            if SecuritySetup._check_tool(command, version_flag):
                print(f"✅ {package} already installed")
                results[package] = True
            else:
                print(f"📦 Installing {package}...")
                success = SecuritySetup._install_python_package(package)
                results[package] = success
                if success:
                    print(f"✅ {package} installed successfully")
                else:
                    print(f"⚠️  {package} installation failed (optional)")
        
        # Check Node.js tools (Solhint)
        if SecuritySetup._check_nodejs():
            if SecuritySetup._check_tool('solhint', '--version'):
                print("✅ solhint already installed")
                results['solhint'] = True
            else:
                print("📦 Installing solhint...")
                success = SecuritySetup._install_npm_package('solhint')
                results['solhint'] = success
                if success:
                    print("✅ solhint installed successfully")
                else:
                    print("⚠️  solhint installation failed (optional)")
        else:
            print("ℹ️  Node.js not found - skipping solhint")
            results['solhint'] = False
        
        print("="*50)
        return results
    
    @staticmethod
    def _check_tool(command: str, version_flag: str) -> bool:
        """Check if a tool is installed"""
        try:
            result = subprocess.run(
                [command, version_flag],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    @staticmethod
    def _check_nodejs() -> bool:
        """Check if Node.js is installed"""
        return SecuritySetup._check_tool('node', '--version')
    
    @staticmethod
    def _install_python_package(package: str) -> bool:
        """Install a Python package using pip"""
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    @staticmethod
    def _install_npm_package(package: str) -> bool:
        """Install a Node.js package globally using npm"""
        try:
            subprocess.check_call(
                ['npm', 'install', '-g', package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    @staticmethod
    def setup_solc_versions() -> None:
        """Setup common Solidity compiler versions"""
        print("\n📚 Setting up Solidity compilers...")
        
        from solcx import install_solc, get_installed_solc_versions
        
        common_versions = ['0.8.19', '0.8.20', '0.8.21']
        installed = get_installed_solc_versions()
        
        for version in common_versions:
            if version not in [str(v) for v in installed]:
                try:
                    print(f"  Installing solc {version}...")
                    install_solc(version)
                    print(f"  ✅ solc {version} installed")
                except Exception as e:
                    print(f"  ⚠️  Failed to install solc {version}: {e}")
            else:
                print(f"  ✅ solc {version} already installed")
    
    @staticmethod
    def verify_installation() -> Dict[str, str]:
        """
        Verify all security tools are properly installed
        
        Returns:
            Dictionary with tool versions
        """
        versions = {}
        
        # Check Slither
        try:
            result = subprocess.run(
                ['slither', '--version'],
                capture_output=True,
                text=True
            )
            versions['slither'] = result.stdout.strip() if result.returncode == 0 else 'Not installed'
        except:
            versions['slither'] = 'Not installed'
        
        # Check Mythril
        try:
            result = subprocess.run(
                ['myth', '--version'],
                capture_output=True,
                text=True
            )
            versions['mythril'] = result.stdout.strip() if result.returncode == 0 else 'Not installed'
        except:
            versions['mythril'] = 'Not installed'
        
        # Check Solhint
        try:
            result = subprocess.run(
                ['solhint', '--version'],
                capture_output=True,
                text=True
            )
            versions['solhint'] = result.stdout.strip() if result.returncode == 0 else 'Not installed'
        except:
            versions['solhint'] = 'Not installed'
        
        return versions
    
    @staticmethod
    def quick_setup() -> None:
        """
        One-command setup for all security tools
        Call this when PureChainLib is first imported
        """
        print("\n🚀 PureChain Security Quick Setup")
        print("This will install security audit tools bundled with the SDK")
        print("-"*50)
        
        # Install tools
        results = SecuritySetup.check_and_install_tools()
        
        # Setup Solidity compilers
        SecuritySetup.setup_solc_versions()
        
        # Verify installation
        print("\n✅ Verification:")
        versions = SecuritySetup.verify_installation()
        for tool, version in versions.items():
            status = "✅" if version != "Not installed" else "❌"
            print(f"  {status} {tool}: {version}")
        
        print("\n🎉 Security setup complete!")
        
        # Save setup status
        setup_file = os.path.join(os.path.expanduser('~'), '.purechain_security_setup')
        with open(setup_file, 'w') as f:
            f.write('completed')
    
    @staticmethod
    def is_setup_complete() -> bool:
        """Check if security setup has been completed"""
        setup_file = os.path.join(os.path.expanduser('~'), '.purechain_security_setup')
        return os.path.exists(setup_file)


# Auto-setup function to call on first use
def auto_setup_security():
    """
    Automatically setup security tools on first use
    This is called when security features are first accessed
    """
    if not SecuritySetup.is_setup_complete():
        print("\n🔒 First-time security setup detected...")
        print("Would you like to install security audit tools? (y/n): ", end='')
        
        try:
            response = input().strip().lower()
            if response == 'y':
                SecuritySetup.quick_setup()
            else:
                print("ℹ️  Skipping security setup. You can run it later with:")
                print("    from purechainlib.security_setup import SecuritySetup")
                print("    SecuritySetup.quick_setup()")
        except:
            # If running non-interactively, skip
            print("ℹ️  Running non-interactively, skipping security setup")


# CLI command for manual setup
def main():
    """CLI entry point for security setup"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PureChain Security Tools Setup')
    parser.add_argument('--check', action='store_true', help='Check installation status')
    parser.add_argument('--install', action='store_true', help='Install missing tools')
    parser.add_argument('--verify', action='store_true', help='Verify tool versions')
    
    args = parser.parse_args()
    
    if args.check:
        versions = SecuritySetup.verify_installation()
        print("Security Tools Status:")
        for tool, version in versions.items():
            print(f"  {tool}: {version}")
    
    elif args.install:
        SecuritySetup.quick_setup()
    
    elif args.verify:
        versions = SecuritySetup.verify_installation()
        all_installed = all(v != "Not installed" for v in versions.values())
        if all_installed:
            print("✅ All security tools are installed!")
        else:
            print("⚠️  Some tools are missing. Run with --install to setup.")
    
    else:
        # Default action
        SecuritySetup.quick_setup()


if __name__ == "__main__":
    main()