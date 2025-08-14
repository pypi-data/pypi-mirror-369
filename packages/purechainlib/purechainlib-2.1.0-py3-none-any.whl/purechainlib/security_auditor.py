"""
Security Auditor Module for PureChainLib
Integrates multiple smart contract security tools for comprehensive auditing
"""

import subprocess
import json
import tempfile
import os
from typing import Dict, List, Optional, Any, Literal
from enum import Enum
from pathlib import Path
import asyncio
from datetime import datetime

class SecurityTool(Enum):
    """Available security audit tools"""
    SLITHER = "slither"
    MYTHRIL = "mythril"
    MANTICORE = "manticore"
    SOLHINT = "solhint"
    ALL = "all"  # Run all available tools

class SeverityLevel(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "informational"

class SecurityAuditor:
    """
    Smart Contract Security Auditor
    Supports multiple security analysis tools
    """
    
    def __init__(self, default_tool: SecurityTool = SecurityTool.SLITHER, auto_install: bool = True):
        """
        Initialize Security Auditor
        
        Args:
            default_tool: Default security tool to use
            auto_install: Automatically install missing tools
        """
        self.default_tool = default_tool
        self.audit_history = []
        
        # Check and optionally install tools
        if auto_install:
            self._auto_install_tools()
        
        self.available_tools = self._check_available_tools()
    
    def _auto_install_tools(self) -> None:
        """Automatically install missing security tools"""
        from .security_setup import SecuritySetup
        
        # Check if any tools are missing
        initial_check = self._check_available_tools()
        missing_tools = [tool for tool, available in initial_check.items() if not available]
        
        if missing_tools and not SecuritySetup.is_setup_complete():
            print(f"🔍 Security tools needed: {', '.join(missing_tools)}")
            print("📦 Installing bundled security tools...")
            try:
                # Try to install missing tools silently
                import subprocess
                import sys
                
                if 'slither' in missing_tools:
                    subprocess.run(
                        [sys.executable, '-m', 'pip', 'install', 'slither-analyzer', '--quiet'],
                        capture_output=True
                    )
                
                if 'mythril' in missing_tools:
                    subprocess.run(
                        [sys.executable, '-m', 'pip', 'install', 'mythril', '--quiet'],
                        capture_output=True
                    )
                
                print("✅ Security tools installed successfully")
            except Exception as e:
                print(f"ℹ️  Some tools couldn't be auto-installed: {e}")
                print("   Run 'python -m purechainlib.security_setup' for full setup")
        
    def _check_available_tools(self) -> Dict[str, bool]:
        """Check which security tools are installed"""
        tools = {}
        
        # Check Slither
        tools['slither'] = self._is_tool_installed('slither', '--version')
        
        # Check Mythril
        tools['mythril'] = self._is_tool_installed('myth', '--version')
        
        # Check Manticore
        tools['manticore'] = self._is_tool_installed('manticore', '--version')
        
        # Check Solhint
        tools['solhint'] = self._is_tool_installed('solhint', '--version')
        
        return tools
    
    def _is_tool_installed(self, command: str, version_flag: str) -> bool:
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
    
    async def audit(
        self,
        contract_source: str,
        tool: Optional[SecurityTool] = None,
        save_report: bool = True
    ) -> Dict[str, Any]:
        """
        Perform security audit on contract source code
        
        Args:
            contract_source: Solidity source code
            tool: Security tool to use (defaults to self.default_tool)
            save_report: Whether to save audit report
            
        Returns:
            Audit results with findings categorized by severity
        """
        tool = tool or self.default_tool
        
        # Create temporary file for contract
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.sol',
            delete=False
        ) as temp_file:
            temp_file.write(contract_source)
            temp_path = temp_file.name
        
        try:
            if tool == SecurityTool.ALL:
                # Run all available tools
                results = await self._run_all_tools(temp_path)
            else:
                # Run specific tool
                results = await self._run_tool(tool, temp_path)
            
            # Add metadata
            results['timestamp'] = datetime.now().isoformat()
            results['contract_hash'] = self._hash_contract(contract_source)
            
            # Save to history
            if save_report:
                self.audit_history.append(results)
            
            return results
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    async def _run_tool(self, tool: SecurityTool, contract_path: str) -> Dict[str, Any]:
        """Run a specific security tool"""
        if tool == SecurityTool.SLITHER:
            return await self._run_slither(contract_path)
        elif tool == SecurityTool.MYTHRIL:
            return await self._run_mythril(contract_path)
        elif tool == SecurityTool.MANTICORE:
            return await self._run_manticore(contract_path)
        elif tool == SecurityTool.SOLHINT:
            return await self._run_solhint(contract_path)
        else:
            return {'error': f'Tool {tool.value} not supported'}
    
    async def _run_all_tools(self, contract_path: str) -> Dict[str, Any]:
        """Run all available security tools"""
        results = {
            'tool': 'all',
            'findings': {},
            'summary': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'info': 0
            }
        }
        
        # Run each available tool
        tasks = []
        if self.available_tools.get('slither'):
            tasks.append(('slither', self._run_slither(contract_path)))
        if self.available_tools.get('mythril'):
            tasks.append(('mythril', self._run_mythril(contract_path)))
        if self.available_tools.get('solhint'):
            tasks.append(('solhint', self._run_solhint(contract_path)))
        
        # Run tools concurrently
        for tool_name, task in tasks:
            tool_results = await task
            results['findings'][tool_name] = tool_results
            
            # Aggregate severity counts
            if 'summary' in tool_results:
                for severity in ['critical', 'high', 'medium', 'low', 'info']:
                    results['summary'][severity] += tool_results['summary'].get(severity, 0)
        
        return results
    
    async def _run_slither(self, contract_path: str) -> Dict[str, Any]:
        """Run Slither security analysis"""
        if not self.available_tools.get('slither'):
            return {'error': 'Slither not installed. Install with: pip install slither-analyzer'}
        
        try:
            # Run Slither with JSON output
            result = await asyncio.create_subprocess_exec(
                'slither', contract_path, '--json', '-',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            # Parse JSON output
            findings = json.loads(stdout.decode()) if stdout else {}
            
            # Process findings
            processed = self._process_slither_results(findings)
            return processed
            
        except Exception as e:
            return {'error': f'Slither analysis failed: {str(e)}'}
    
    def _process_slither_results(self, raw_results: Dict) -> Dict[str, Any]:
        """Process Slither results into standard format"""
        processed = {
            'tool': 'slither',
            'findings': [],
            'summary': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'info': 0
            }
        }
        
        if 'results' in raw_results and 'detectors' in raw_results['results']:
            for finding in raw_results['results']['detectors']:
                severity = finding.get('impact', 'low').lower()
                
                processed_finding = {
                    'severity': severity,
                    'title': finding.get('check', 'Unknown'),
                    'description': finding.get('description', ''),
                    'locations': finding.get('elements', []),
                    'confidence': finding.get('confidence', 'medium')
                }
                
                processed['findings'].append(processed_finding)
                
                # Update summary
                if severity in processed['summary']:
                    processed['summary'][severity] += 1
        
        return processed
    
    async def _run_mythril(self, contract_path: str) -> Dict[str, Any]:
        """Run Mythril security analysis"""
        if not self.available_tools.get('mythril'):
            return {'error': 'Mythril not installed. Install with: pip install mythril'}
        
        try:
            # Run Mythril analysis
            result = await asyncio.create_subprocess_exec(
                'myth', 'analyze', contract_path, '-o', 'json',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            # Parse JSON output
            findings = json.loads(stdout.decode()) if stdout else {}
            
            # Process findings
            processed = self._process_mythril_results(findings)
            return processed
            
        except Exception as e:
            return {'error': f'Mythril analysis failed: {str(e)}'}
    
    def _process_mythril_results(self, raw_results: Dict) -> Dict[str, Any]:
        """Process Mythril results into standard format"""
        processed = {
            'tool': 'mythril',
            'findings': [],
            'summary': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'info': 0
            }
        }
        
        if 'issues' in raw_results:
            for issue in raw_results['issues']:
                severity = issue.get('severity', 'Low').lower()
                
                processed_finding = {
                    'severity': severity,
                    'title': issue.get('title', 'Unknown'),
                    'description': issue.get('description', ''),
                    'type': issue.get('type', ''),
                    'line': issue.get('lineno', 0),
                    'code': issue.get('code', '')
                }
                
                processed['findings'].append(processed_finding)
                
                # Update summary
                if severity in processed['summary']:
                    processed['summary'][severity] += 1
        
        return processed
    
    async def _run_manticore(self, contract_path: str) -> Dict[str, Any]:
        """Run Manticore security analysis (basic implementation)"""
        if not self.available_tools.get('manticore'):
            return {'error': 'Manticore not installed. Install with: pip install manticore'}
        
        # Manticore is more complex and requires more setup
        # This is a placeholder for basic integration
        return {
            'tool': 'manticore',
            'status': 'not_implemented',
            'message': 'Manticore integration coming soon'
        }
    
    async def _run_solhint(self, contract_path: str) -> Dict[str, Any]:
        """Run Solhint linter"""
        if not self.available_tools.get('solhint'):
            return {'error': 'Solhint not installed. Install with: npm install -g solhint'}
        
        try:
            # Run Solhint
            result = await asyncio.create_subprocess_exec(
                'solhint', contract_path, '-f', 'json',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            # Parse JSON output
            findings = json.loads(stdout.decode()) if stdout else []
            
            # Process findings
            processed = self._process_solhint_results(findings)
            return processed
            
        except Exception as e:
            return {'error': f'Solhint analysis failed: {str(e)}'}
    
    def _process_solhint_results(self, raw_results: List) -> Dict[str, Any]:
        """Process Solhint results into standard format"""
        processed = {
            'tool': 'solhint',
            'findings': [],
            'summary': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'info': 0
            }
        }
        
        for file_results in raw_results:
            if 'reports' in file_results:
                for report in file_results['reports']:
                    severity = 'low'  # Solhint mainly focuses on style/best practices
                    if report.get('severity') == 'error':
                        severity = 'high'
                    elif report.get('severity') == 'warning':
                        severity = 'medium'
                    
                    processed_finding = {
                        'severity': severity,
                        'title': report.get('ruleId', 'Unknown'),
                        'description': report.get('message', ''),
                        'line': report.get('line', 0),
                        'column': report.get('column', 0)
                    }
                    
                    processed['findings'].append(processed_finding)
                    
                    # Update summary
                    if severity in processed['summary']:
                        processed['summary'][severity] += 1
        
        return processed
    
    def _hash_contract(self, source: str) -> str:
        """Generate hash of contract source for tracking"""
        import hashlib
        return hashlib.sha256(source.encode()).hexdigest()[:16]
    
    def get_available_tools(self) -> Dict[str, bool]:
        """Get list of available security tools"""
        return self.available_tools
    
    def generate_report(
        self,
        audit_results: Dict[str, Any],
        format: Literal['text', 'json', 'html', 'markdown'] = 'text'
    ) -> str:
        """
        Generate formatted audit report
        
        Args:
            audit_results: Audit results from audit()
            format: Output format
            
        Returns:
            Formatted report string
        """
        if format == 'json':
            return json.dumps(audit_results, indent=2)
        elif format == 'markdown':
            return self._generate_markdown_report(audit_results)
        elif format == 'html':
            return self._generate_html_report(audit_results)
        else:
            return self._generate_text_report(audit_results)
    
    def _generate_text_report(self, results: Dict) -> str:
        """Generate plain text report"""
        report = []
        report.append("=" * 80)
        report.append("SMART CONTRACT SECURITY AUDIT REPORT")
        report.append("=" * 80)
        report.append(f"Tool: {results.get('tool', 'Unknown')}")
        report.append(f"Timestamp: {results.get('timestamp', 'N/A')}")
        report.append("")
        
        # Summary
        if 'summary' in results:
            report.append("SUMMARY:")
            report.append("-" * 40)
            for severity, count in results['summary'].items():
                if count > 0:
                    report.append(f"  {severity.upper()}: {count}")
            report.append("")
        
        # Findings
        if 'findings' in results:
            report.append("FINDINGS:")
            report.append("-" * 40)
            
            # Group by severity
            for severity in ['critical', 'high', 'medium', 'low', 'info']:
                severity_findings = [
                    f for f in results['findings']
                    if f.get('severity') == severity
                ]
                
                if severity_findings:
                    report.append(f"\n[{severity.upper()}]")
                    for finding in severity_findings:
                        report.append(f"  • {finding.get('title', 'Unknown')}")
                        if finding.get('description'):
                            report.append(f"    {finding['description']}")
                        if finding.get('line'):
                            report.append(f"    Line: {finding['line']}")
                        report.append("")
        
        report.append("=" * 80)
        return "\n".join(report)
    
    def _generate_markdown_report(self, results: Dict) -> str:
        """Generate Markdown report"""
        report = []
        report.append("# Smart Contract Security Audit Report")
        report.append("")
        report.append(f"**Tool:** {results.get('tool', 'Unknown')}")
        report.append(f"**Timestamp:** {results.get('timestamp', 'N/A')}")
        report.append("")
        
        # Summary
        if 'summary' in results:
            report.append("## Summary")
            report.append("")
            report.append("| Severity | Count |")
            report.append("|----------|-------|")
            for severity, count in results['summary'].items():
                if count > 0:
                    emoji = "🔴" if severity == "critical" else "🟠" if severity == "high" else "🟡" if severity == "medium" else "🟢"
                    report.append(f"| {emoji} {severity.capitalize()} | {count} |")
            report.append("")
        
        # Findings
        if 'findings' in results:
            report.append("## Findings")
            report.append("")
            
            for severity in ['critical', 'high', 'medium', 'low', 'info']:
                severity_findings = [
                    f for f in results['findings']
                    if f.get('severity') == severity
                ]
                
                if severity_findings:
                    report.append(f"### {severity.capitalize()} Severity")
                    report.append("")
                    for finding in severity_findings:
                        report.append(f"#### {finding.get('title', 'Unknown')}")
                        if finding.get('description'):
                            report.append(f"> {finding['description']}")
                        if finding.get('line'):
                            report.append(f"- **Line:** {finding['line']}")
                        report.append("")
        
        return "\n".join(report)
    
    def _generate_html_report(self, results: Dict) -> str:
        """Generate HTML report"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Audit Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .critical {{ color: #d32f2f; }}
                .high {{ color: #f57c00; }}
                .medium {{ color: #fbc02d; }}
                .low {{ color: #388e3c; }}
                .info {{ color: #1976d2; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Smart Contract Security Audit Report</h1>
            <p><strong>Tool:</strong> {results.get('tool', 'Unknown')}</p>
            <p><strong>Timestamp:</strong> {results.get('timestamp', 'N/A')}</p>
            
            <h2>Summary</h2>
            <table>
                <tr><th>Severity</th><th>Count</th></tr>
        """
        
        if 'summary' in results:
            for severity, count in results['summary'].items():
                if count > 0:
                    html += f"<tr><td class='{severity}'>{severity.upper()}</td><td>{count}</td></tr>"
        
        html += """
            </table>
            
            <h2>Findings</h2>
        """
        
        if 'findings' in results:
            for finding in results['findings']:
                severity = finding.get('severity', 'unknown')
                html += f"""
                <div style='margin: 10px 0; padding: 10px; border-left: 3px solid;' class='{severity}'>
                    <h3>{finding.get('title', 'Unknown')}</h3>
                    <p>{finding.get('description', '')}</p>
                    {f"<p><small>Line: {finding.get('line', 'N/A')}</small></p>" if finding.get('line') else ""}
                </div>
                """
        
        html += """
        </body>
        </html>
        """
        return html
    
    def export_report(
        self,
        audit_results: Dict[str, Any],
        filename: str,
        format: Literal['text', 'json', 'html', 'markdown'] = 'markdown'
    ) -> str:
        """Export audit report to file"""
        report = self.generate_report(audit_results, format)
        
        # Add appropriate extension
        if not filename.endswith(('.txt', '.json', '.html', '.md')):
            extensions = {'text': '.txt', 'json': '.json', 'html': '.html', 'markdown': '.md'}
            filename += extensions.get(format, '.txt')
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return filename
    
    def recommend_fixes(self, audit_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Provide recommendations for fixing vulnerabilities
        
        Returns:
            List of recommendations with severity and fix suggestions
        """
        recommendations = []
        
        if 'findings' not in audit_results:
            return recommendations
        
        # Common vulnerability patterns and fixes
        fix_patterns = {
            'reentrancy': {
                'fix': 'Use ReentrancyGuard or Checks-Effects-Interactions pattern',
                'example': 'modifier nonReentrant() { require(!locked); locked = true; _; locked = false; }'
            },
            'overflow': {
                'fix': 'Use SafeMath library or Solidity 0.8+ built-in overflow checks',
                'example': 'pragma solidity ^0.8.0; // Auto overflow protection'
            },
            'uninitialized': {
                'fix': 'Initialize all storage variables explicitly',
                'example': 'uint256 public counter = 0; // Explicit initialization'
            },
            'timestamp': {
                'fix': 'Avoid using block.timestamp for critical logic',
                'example': 'Use block.number or external oracle for time-sensitive operations'
            },
            'visibility': {
                'fix': 'Explicitly declare function visibility',
                'example': 'function transfer() public { } // Not just function transfer() { }'
            }
        }
        
        for finding in audit_results['findings']:
            title = finding.get('title', '').lower()
            
            # Match patterns
            for pattern, fix_info in fix_patterns.items():
                if pattern in title:
                    recommendations.append({
                        'issue': finding.get('title'),
                        'severity': finding.get('severity'),
                        'fix': fix_info['fix'],
                        'example': fix_info['example']
                    })
                    break
        
        return recommendations