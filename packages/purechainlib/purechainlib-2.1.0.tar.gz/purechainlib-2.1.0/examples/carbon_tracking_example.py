#!/usr/bin/env python3
"""
PureChain Carbon Footprint Tracking Example
Demonstrates environmental impact measurement and ESG reporting
"""

import asyncio
import json
from purechainlib import PureChain

async def carbon_tracking_demo():
    """
    Complete demonstration of carbon tracking features
    """
    
    print("🌱 PureChain Carbon Footprint Tracking Demo")
    print("=" * 60)
    
    # Initialize PureChain
    pc = PureChain('testnet')
    
    # Connect with a test account
    test_account = pc.account()
    pc.connect(test_account['privateKey'])
    
    print(f"📍 Connected as: {test_account['address']}")
    
    # Enable carbon tracking for US region
    pc.enableCarbonTracking('us')
    print("✅ Carbon tracking enabled (US grid intensity)")
    
    print("\n" + "=" * 60)
    print("1️⃣ TRANSACTION WITH CARBON TRACKING")
    print("=" * 60)
    
    # Create recipient
    recipient = pc.account()
    
    # Send transaction with carbon tracking
    try:
        result = await pc.send(
            recipient['address'], 
            '0',  # Zero value (just for demo)
            include_carbon=True
        )
        
        if 'carbon_footprint' in result:
            carbon = result['carbon_footprint']
            print(f"✅ Transaction sent!")
            print(f"📊 Carbon Footprint:")
            print(f"   - Energy: {carbon['energy']['joules']} Joules")
            print(f"   - Carbon: {carbon['carbon']['gCO2']} gCO2")
            print(f"   - vs Ethereum: {carbon['comparison']['vs_ethereum']}")
            print(f"   - Savings: {carbon['comparison']['savings_vs_eth_kg']} kg CO2")
    except Exception as e:
        print(f"⚠️ Transaction failed (expected in test environment): {e}")
    
    print("\n" + "=" * 60)
    print("2️⃣ CONTRACT DEPLOYMENT WITH CARBON TRACKING")
    print("=" * 60)
    
    # Simple contract for testing
    contract_source = """
    pragma solidity ^0.8.19;
    contract CarbonTest {
        uint256 public value = 42;
        mapping(address => uint256) public balances;
        
        function setValue(uint256 _value) public {
            value = _value;
        }
        
        function deposit() public payable {
            balances[msg.sender] += msg.value;
        }
    }
    """
    
    try:
        # Compile contract
        factory = await pc.contract(contract_source)
        print("✅ Contract compiled")
        
        # Deploy with carbon tracking
        contract = await factory.deploy(track_carbon=True)
        print(f"✅ Contract deployed at: {contract.address}")
        
        # The receipt would include carbon_footprint if deployment succeeded
        print("📊 Deployment carbon footprint tracked")
        
    except Exception as e:
        print(f"⚠️ Deployment failed (expected in test environment): {e}")
    
    print("\n" + "=" * 60)
    print("3️⃣ CARBON FOOTPRINT REPORT")
    print("=" * 60)
    
    # Get carbon report
    report = await pc.getCarbonReport()
    print("📊 Carbon Report:")
    print(json.dumps(report, indent=2))
    
    print("\n" + "=" * 60)
    print("4️⃣ ESG COMPLIANCE METRICS")
    print("=" * 60)
    
    # Get ESG metrics
    esg_metrics = await pc.getCarbonESGMetrics()
    print("🌍 ESG Metrics:")
    print(json.dumps(esg_metrics, indent=2))
    
    print("\n" + "=" * 60)
    print("5️⃣ COMPARING DIFFERENT REGIONS")
    print("=" * 60)
    
    regions = ['us', 'eu', 'asia', 'renewable']
    
    for region in regions:
        # Create new instance for each region
        regional_pc = PureChain('testnet')
        regional_pc.enableCarbonTracking(region)
        
        # Simulate a transaction
        from purechainlib.carbon_tracker import CarbonFootprintTracker
        tracker = CarbonFootprintTracker(region)
        result = tracker.calculate_transaction(250)
        
        print(f"\n📍 Region: {region.upper()}")
        print(f"   Carbon per tx: {result['carbon']['gCO2']} gCO2")
        print(f"   Grid multiplier: {result['efficiency']['grid_multiplier']}")
    
    print("\n" + "=" * 60)
    print("6️⃣ SCIENTIFIC MEASUREMENTS")
    print("=" * 60)
    
    # Use scientific carbon tracker for detailed measurements
    from purechainlib.carbon_tracker_v2 import ScientificCarbonTracker
    
    sci_tracker = ScientificCarbonTracker('us_average', 'aws_us_east')
    
    # Measure different operations
    measurements = {
        'transaction': sci_tracker.measure_transaction(250, 1, 1),
        'contract_deploy': sci_tracker.measure_contract_deployment(5000, 200),
        'contract_execute': sci_tracker.measure_contract_execution(100, 2, 1)
    }
    
    print("🔬 Scientific Measurements:")
    for op_type, measurement in measurements.items():
        print(f"\n{op_type.replace('_', ' ').title()}:")
        print(f"   Energy: {measurement['energy']['joules']:.6f} J")
        print(f"   Power: {measurement['energy'].get('watts_for_1_second', measurement['energy']['joules']):.6f} W")
        print(f"   Carbon: {measurement['carbon']['gCO2']:.9f} gCO2")
        print(f"   vs Bitcoin: {measurement['comparisons']['vs_bitcoin']['times_more_efficient']:,}x more efficient")
    
    # Generate scientific report
    sci_report = sci_tracker.get_scientific_report()
    
    print("\n📈 Scientific Report Summary:")
    print(f"   Total operations: {sci_report['summary']['total_operations']}")
    print(f"   Total energy: {sci_report['summary']['total_energy']['joules']:.6f} J")
    print(f"   Total carbon: {sci_report['summary']['total_carbon']['kgCO2']:.9f} kg CO2")
    print(f"   Methodology: {sci_report['methodology']['measurement_approach']}")
    
    print("\n" + "=" * 60)
    print("7️⃣ EXPORT CARBON REPORT")
    print("=" * 60)
    
    # Export full report as JSON
    json_report = await pc.exportCarbonReport()
    
    # Save to file (optional)
    with open('carbon_report.json', 'w') as f:
        f.write(json_report)
    
    print("✅ Carbon report exported to carbon_report.json")
    
    # Parse and show summary
    report_data = json.loads(json_report)
    if 'error' not in report_data:
        print(f"📊 Report contains {len(report_data.get('history', []))} tracked operations")
    
    print("\n" + "=" * 60)
    print("✅ CARBON TRACKING DEMO COMPLETE")
    print("=" * 60)
    
    print("""
Key Takeaways:
1. PureChain uses ~0.000003 gCO2 per transaction
2. This is 99.99999% less than Ethereum
3. Carbon tracking helps with ESG compliance
4. Regional grid intensity affects carbon calculations
5. All measurements based on scientific methodology
    """)

async def main():
    """Main function with error handling"""
    try:
        await carbon_tracking_demo()
    except Exception as e:
        print(f"❌ Demo error: {e}")
        print("\nNote: Some operations may fail without network connection")
        print("But carbon calculations and tracking features are demonstrated")

if __name__ == "__main__":
    print("Note: This demo shows carbon tracking features.")
    print("Some operations may fail without actual network connection.\n")
    asyncio.run(main())