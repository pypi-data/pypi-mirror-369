# Real-Time Energy Monitoring Implementation Plan
## Software-Based Measurement for PureChain SDK

### Executive Summary
This document outlines the plan to implement actual energy consumption monitoring in the PureChain Python SDK using software-based approaches, without requiring external hardware.

---

## 1. Python Libraries for Energy Monitoring

### 1.1 CPU Energy Monitoring

#### **pyRAPL** (Recommended)
```python
# pip install pyRAPL
```
- **Purpose**: Direct access to Intel RAPL (Running Average Power Limit) counters
- **Platforms**: Linux with Intel CPUs (Sandy Bridge+)
- **Capabilities**: 
  - Real-time CPU package power (Watts)
  - DRAM power consumption
  - Per-core energy measurements
- **Pros**: Most accurate software-based measurement
- **Cons**: Intel-only, requires root on some systems

**Example Usage**:
```python
import pyRAPL
pyRAPL.setup()
meter = pyRAPL.Measurement('transaction')
meter.begin()
# ... perform blockchain operation ...
meter.end()
energy_used = meter.result.pkg[0]  # Joules
```

#### **py-rapl** (Alternative)
```python
# pip install py-rapl
```
- Similar to pyRAPL but simpler API
- Less documentation but lighter weight

#### **pynvml** (For NVIDIA GPUs)
```python
# pip install nvidia-ml-py
```
- Monitor GPU power consumption if using GPU acceleration
- Access to NVIDIA Management Library

### 1.2 System Resource Monitoring

#### **psutil** (Essential)
```python
# pip install psutil
```
- **Purpose**: Cross-platform system and process monitoring
- **Capabilities**:
  - CPU usage percentage
  - Memory consumption (RSS, VMS)
  - Network I/O statistics
  - Disk I/O operations
  - Process-specific measurements
- **Pros**: Works on all platforms (Windows, Linux, macOS)
- **Cons**: No direct energy measurements

**Example Usage**:
```python
import psutil
import os

process = psutil.Process(os.getpid())

# Before operation
cpu_before = process.cpu_percent()
mem_before = process.memory_info().rss
net_before = psutil.net_io_counters()

# ... perform operation ...

# After operation
cpu_after = process.cpu_percent()
mem_after = process.memory_info().rss
net_after = psutil.net_io_counters()

# Calculate deltas
cpu_usage = cpu_after - cpu_before
memory_delta = mem_after - mem_before
network_bytes = (net_after.bytes_sent - net_before.bytes_sent + 
                 net_after.bytes_recv - net_before.bytes_recv)
```

#### **py-cpuinfo** (Hardware Detection)
```python
# pip install py-cpuinfo
```
- Detect CPU model and specifications
- Get TDP (Thermal Design Power) for energy estimation
- Cross-platform CPU information

### 1.3 Power Estimation Libraries

#### **codecarbon** (Comprehensive)
```python
# pip install codecarbon
```
- **Purpose**: Track carbon emissions from computing
- **Capabilities**:
  - Automatic energy tracking
  - Cloud provider detection
  - Regional carbon intensity
  - Hardware-specific models
- **Pros**: Full-featured, includes carbon calculations
- **Cons**: May be overkill for our needs

**Example Usage**:
```python
from codecarbon import EmissionsTracker

tracker = EmissionsTracker()
tracker.start()
# ... blockchain operations ...
emissions = tracker.stop()  # Returns CO2 emissions
```

#### **energyusage** (Simple)
```python
# pip install energyusage
```
- Lightweight energy estimation
- Based on CPU models and usage

### 1.4 Platform-Specific Tools

#### **Linux-Specific**
- **powertop** Python bindings
- **/sys/class/powercap/** direct reading
- **perf** event counters via Python

#### **macOS-Specific**
- **powermetrics** wrapper
- **ioreg** for power statistics

#### **Windows-Specific**
- **WMI** (Windows Management Instrumentation)
```python
# pip install WMI
import wmi
c = wmi.WMI()
for processor in c.Win32_Processor():
    print(processor.CurrentVoltage, processor.CurrentClockSpeed)
```

---

## 2. Proposed Implementation Architecture

### 2.1 Multi-Tier Measurement System

```python
class EnergyMonitor:
    def __init__(self):
        self.monitors = []
        
        # Tier 1: Hardware counters (most accurate)
        if self._has_rapl():
            self.monitors.append(RAPLMonitor())
        
        # Tier 2: System metrics (good accuracy)
        self.monitors.append(PSUtilMonitor())
        
        # Tier 3: Model-based estimation (fallback)
        self.monitors.append(ModelBasedEstimator())
    
    def measure_operation(self, operation_func):
        """Measure energy consumption of an operation"""
        results = {}
        for monitor in self.monitors:
            if monitor.is_available():
                results[monitor.name] = monitor.measure(operation_func)
        return self._combine_results(results)
```

### 2.2 Data Collection Points

```python
class ComprehensiveMonitor:
    def collect_metrics(self):
        return {
            'energy': {
                'cpu_joules': self._get_cpu_energy(),      # Via RAPL
                'estimated_joules': self._estimate_energy() # Via model
            },
            'resources': {
                'cpu_percent': psutil.cpu_percent(),
                'memory_mb': psutil.Process().memory_info().rss / 1024 / 1024,
                'network_kb': self._get_network_delta() / 1024,
                'disk_io_kb': self._get_disk_io() / 1024
            },
            'hardware': {
                'cpu_model': cpuinfo.get_cpu_info()['brand_raw'],
                'cpu_freq_mhz': psutil.cpu_freq().current,
                'cpu_cores': psutil.cpu_count(),
                'cpu_temp': self._get_cpu_temp()  # If available
            },
            'timing': {
                'operation_ms': self.operation_duration * 1000,
                'timestamp': time.time()
            }
        }
```

---

## 3. Integration with PureChain SDK

### 3.1 New API Methods

```python
class PureChain:
    def enableRealTimeMonitoring(self, level='auto'):
        """
        Enable real-time energy monitoring
        
        Levels:
        - 'hardware': Use hardware counters (RAPL) if available
        - 'system': Use system metrics (psutil)
        - 'estimate': Use model-based estimation
        - 'auto': Best available method (default)
        """
        self.energy_monitor = EnergyMonitor(level)
    
    async def measureTransaction(self, to, value):
        """Send transaction with real-time measurements"""
        monitor = self.energy_monitor.start_measurement()
        
        # Perform transaction
        result = await self.send(to, value)
        
        # Stop measurement
        measurements = monitor.stop()
        
        result['measurements'] = {
            'energy_joules': measurements.energy_joules,
            'cpu_usage_percent': measurements.cpu_percent,
            'memory_mb': measurements.memory_mb,
            'duration_ms': measurements.duration_ms,
            'measurement_method': measurements.method  # 'rapl', 'psutil', or 'model'
        }
        
        return result
    
    async def calibrateEnergyModel(self, iterations=100):
        """
        Calibrate energy model for current hardware
        Runs test operations to build hardware-specific model
        """
        calibration_data = []
        
        for i in range(iterations):
            measurement = await self._run_calibration_operation()
            calibration_data.append(measurement)
        
        # Build regression model
        self.energy_model = self._build_energy_model(calibration_data)
        return {
            'hardware_profile': self._get_hardware_profile(),
            'calibration_accuracy': self.energy_model.accuracy,
            'samples_collected': iterations
        }
```

### 3.2 Measurement Storage

```python
class MeasurementDatabase:
    """Store measurements for analysis and model improvement"""
    
    def __init__(self, db_path='~/.purechain/measurements.db'):
        self.db = sqlite3.connect(db_path)
        self._init_schema()
    
    def record_measurement(self, measurement):
        """Store measurement with hardware context"""
        self.db.execute("""
            INSERT INTO measurements 
            (timestamp, operation_type, energy_joules, cpu_percent, 
             memory_mb, network_bytes, cpu_model, measurement_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, measurement.to_tuple())
    
    def get_statistics(self, operation_type=None):
        """Get energy statistics for operations"""
        # Returns avg, min, max, std_dev for each metric
```

---

## 4. Fallback Strategies

### 4.1 When Hardware Counters Unavailable

```python
class ModelBasedEstimator:
    """Estimate energy when direct measurement unavailable"""
    
    def __init__(self):
        self.cpu_info = cpuinfo.get_cpu_info()
        self.tdp = self._get_cpu_tdp()  # Thermal Design Power
    
    def estimate_energy(self, cpu_time_seconds, cpu_percent):
        """
        Estimate energy consumption based on:
        - CPU time
        - CPU utilization
        - CPU TDP rating
        """
        # Simple model: Energy = TDP * CPU% * Time
        power_watts = self.tdp * (cpu_percent / 100) * 0.7  # 70% efficiency
        energy_joules = power_watts * cpu_time_seconds
        
        return {
            'energy_joules': energy_joules,
            'confidence': 'estimated',
            'model': 'tdp_based'
        }
```

### 4.2 Cross-Platform Compatibility

```python
class PlatformAdapter:
    @staticmethod
    def get_energy_monitor():
        system = platform.system()
        
        if system == 'Linux':
            # Try RAPL first
            if os.path.exists('/sys/class/powercap/intel-rapl'):
                return LinuxRAPLMonitor()
            else:
                return LinuxPerfMonitor()
        
        elif system == 'Darwin':  # macOS
            return MacOSPowerMetricsMonitor()
        
        elif system == 'Windows':
            return WindowsWMIMonitor()
        
        else:
            # Fallback to psutil-based estimation
            return PSUtilEstimator()
```

---

## 5. Implementation Phases

### Phase 1: Basic Integration (v2.1.0)
- Add `psutil` for resource monitoring
- Implement basic CPU/memory tracking
- Add `measureTransaction()` method
- Store measurements locally

### Phase 2: Hardware Counters (v2.2.0)
- Integrate `pyRAPL` for Intel RAPL
- Add GPU monitoring with `pynvml`
- Implement platform detection
- Add calibration system

### Phase 3: Advanced Features (v2.3.0)
- Machine learning model for estimation
- Historical data analysis
- Comparative benchmarking
- Energy optimization suggestions

---

## 6. Example Usage (Future API)

```python
from purechainlib import PureChain

# Initialize with monitoring
pc = PureChain('testnet')
pc.connect('private_key')

# Enable real-time monitoring
pc.enableRealTimeMonitoring('auto')

# Calibrate for current hardware (one-time)
calibration = await pc.calibrateEnergyModel()
print(f"Calibrated for: {calibration['hardware_profile']['cpu']}")

# Send transaction with measurements
result = await pc.measureTransaction(
    to='0x...',
    value='1.0'
)

print(f"Transaction used {result['measurements']['energy_joules']} J")
print(f"CPU usage: {result['measurements']['cpu_usage_percent']}%")
print(f"Measurement method: {result['measurements']['measurement_method']}")

# Get energy report with real measurements
report = await pc.getEnergyReport()
print(f"Total measured energy: {report['total_energy_joules']} J")
print(f"Average per transaction: {report['avg_energy_per_tx']} J")
print(f"Measurement confidence: {report['confidence_level']}")
```

---

## 7. Dependencies to Add

```python
# requirements.txt additions
psutil>=5.9.0           # System monitoring (required)
py-cpuinfo>=9.0.0       # CPU detection (required)
pyRAPL>=0.2.3.1        # Intel RAPL (optional, Linux)
nvidia-ml-py>=12.535.0  # NVIDIA GPU (optional)
codecarbon>=2.3.0      # Comprehensive tracking (optional)
```

---

## 8. Benefits of This Approach

1. **No External Hardware Required**: Pure software solution
2. **Progressive Enhancement**: Works better with better hardware support
3. **Cross-Platform**: Falls back gracefully on all systems
4. **Scientific Accuracy**: Real measurements when possible
5. **User Transparency**: Shows measurement method and confidence
6. **Hardware Calibration**: Adapts to specific user hardware
7. **Historical Learning**: Improves estimates over time

---

## 9. Technical Challenges & Solutions

### Challenge 1: Root/Admin Requirements
- **Issue**: RAPL may require root access
- **Solution**: Graceful fallback to psutil-based estimation

### Challenge 2: Platform Differences
- **Issue**: Different OS have different APIs
- **Solution**: Platform adapter pattern with fallbacks

### Challenge 3: Measurement Overhead
- **Issue**: Monitoring itself uses energy
- **Solution**: Subtract monitoring overhead from measurements

### Challenge 4: Accuracy Validation
- **Issue**: How to verify measurements are correct
- **Solution**: Cross-validate between multiple methods when available

---

## 10. Next Steps

1. **Research Phase**: Test each library on different platforms
2. **Prototype**: Build proof-of-concept with psutil + pyRAPL
3. **Validation**: Compare measurements with external power meters
4. **Integration**: Add to PureChain SDK as opt-in feature
5. **Documentation**: Create user guide for energy monitoring
6. **Release**: Version 2.1.0 with basic monitoring

---

## Appendix: Library Comparison Matrix

| Library | Platform | Accuracy | Ease of Use | Dependencies | License |
|---------|----------|----------|-------------|--------------|---------|
| pyRAPL | Linux/Intel | High | Medium | None | MIT |
| psutil | All | Medium | High | None | BSD |
| codecarbon | All | Medium | High | Many | MIT |
| py-cpuinfo | All | N/A | High | None | MIT |
| nvidia-ml-py | All+NVIDIA | High | Medium | CUDA | BSD |
| WMI | Windows | Low | Medium | pywin32 | MIT |

---

## References

1. Intel RAPL Documentation: https://01.org/blogs/2014/running-average-power-limit-–-rapl
2. psutil Documentation: https://psutil.readthedocs.io/
3. CodeCarbon Paper: https://arxiv.org/abs/2007.03051
4. Energy Profiling Research: https://doi.org/10.1145/3524610
5. Python Power Measurement Survey: https://greenlab.di.uminho.pt/

---

*Document Version: 1.0*  
*Created: 2025-01-13*  
*Status: Planning Phase*