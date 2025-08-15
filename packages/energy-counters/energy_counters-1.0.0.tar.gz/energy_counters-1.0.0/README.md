# Energy Counters Library

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://pypi.org/project/nemotek-counters/)
[![Maintained](https://img.shields.io/badge/maintained-yes%2C%202025-success.svg)](https://github.com/Nemotek-GTC/counters)


![Carlo Gavazzi](https://img.shields.io/badge/support-Carlo%20Gavazzi-lightgrey.svg)
![Lovato](https://img.shields.io/badge/support-Lovato-lightgrey.svg)
![Diris](https://img.shields.io/badge/support-Diris-lightgrey.svg)
![RedZ](https://img.shields.io/badge/support-RedZ-lightgrey.svg)
![Contrel](https://img.shields.io/badge/support-Contrel-lightgrey.svg)
![Schneider](https://img.shields.io/badge/support-Schneider-lightgrey.svg)




A Python library for reading data from various electrical energy counters including Carlo Gavazzi, Contrel, Diris, Lovato, RedZ, and Schneider devices.

## Features

- **Multiple Communication Protocols**: Support for both Modbus RTU (serial) and Modbus TCP connections
- **Automatic Fallback**: Intelligent switching between TCP and RTU when both are configured
- **Comprehensive Data Collection**: Read voltage, current, power, energy, and frequency measurements
- **Easy Configuration**: Simple dataclass-based configuration for counters and connections
- **Detailed Logging**: Built-in logging for debugging and monitoring
- **Modern Python**: Written for Python 3.8+ with type hints and dataclasses
- **Extensible Design**: Easy to add support for new counter models

## Installation

```bash
pip install energy-counters
```

Or for development:
```bash
pip install -e .
```

## Usage

### Import the library

```python
import energy_counters
from src.energy_counters import carlo_gavazzi
from energy_counters.carlo_gavazzi import em530
```

### Carlo Gavazzi EM530 Example

#### RTU (Serial) Connection

```python
from src.energy_counters.carlo_gavazzi import (
    CounterConfiguration,
    ModbusRTUConfiguration,
    EM530DataCollector
)

# Configure the counter
counter_config = CounterConfiguration(
    counter_id=167,
    unit_id=100,  # Modbus address
    counter_name="TestCounter",
    company_id="MyCompany"
)

# Configure Modbus RTU connection
rtu_config = ModbusRTUConfiguration(
    port="/dev/ttyNS0",  # Adjust according to your system
    baudrate=9600
)

# Create collector
collector = EM530DataCollector(counter_config, modbus_rtu_config=rtu_config)

# Connect and read data
if collector.connect():
    data = collector.collect_data()
    if data:
        print(f"Voltage L1: {data['voltageL1']}V")
        print(f"Current L1: {data['currentL1']}A")
        print(f"Active Power: {data['activePower']}kW")
    collector.disconnect()
```

#### TCP Connection

```python
from src.energy_counters.carlo_gavazzi import (
    CounterConfiguration,
    ModbusTCPConfiguration,
    EM530DataCollector
)

# Configure the counter
counter_config = CounterConfiguration(
    counter_id=167,
    unit_id=100,  # Modbus address
    counter_name="TestCounter",
    company_id="MyCompany"
)

# Configure Modbus TCP connection
tcp_config = ModbusTCPConfiguration(
    host="192.162.10.10",  # IP address of the counter
    port=502
)

# Create collector
collector = EM530DataCollector(counter_config, modbus_tcp_config=tcp_config)

# Connect and read data
if collector.connect():
    data = collector.collect_data()
    if data:
        print(f"Voltage L1: {data['voltageL1']}V")
        print(f"Current L1: {data['currentL1']}A")
        print(f"Active Power: {data['activePower']}kW")
    collector.disconnect()
```

#### TCP with RTU Fallback

```python
from src.energy_counters.carlo_gavazzi import (
    CounterConfiguration,
    ModbusTCPConfiguration,
    ModbusRTUConfiguration,
    EM530DataCollector
)

counter_config = CounterConfiguration(167, 100, "TestCounter", "MyCompany")
tcp_config = ModbusTCPConfiguration("192.162.10.10", 502)
rtu_config = ModbusRTUConfiguration("/dev/ttyNS0", 9600)

# Create collector with both configurations (tries TCP first, then RTU)
collector = EM530DataCollector(counter_config,
                               modbus_tcp_config=tcp_config,
                               modbus_rtu_config=rtu_config)

if collector.connect():
    data = collector.collect_data()
    if data:
        print(f"Voltage L1: {data['voltageL1']}V")
    collector.disconnect()
```

### Lovato DMG210 Example

```python
from src.energy_counters.lovato import (
    CounterConfiguration,
    ModbusTCPConfiguration,
    ModbusRTUConfiguration,
    DMG210DataCollector
)

# Configure the counter  
counter_config = CounterConfiguration(
    counter_id=115,
    unit_id=81,  # Modbus address
    counter_name="General #115",
    company_id="MyCompany"
)

# Configure Modbus TCP (primary)
tcp_config = ModbusTCPConfiguration(
    host="172.16.5.11",
    port=502
)

# Configure Modbus RTU (fallback)
rtu_config = ModbusRTUConfiguration(
    port="/dev/ttyNS0",
    baudrate=9600
)

# Create collector with both TCP and RTU support
collector = DMG210DataCollector(counter_config, tcp_config, rtu_config)

# Connect and read data (tries TCP first, RTU as fallback)
if collector.connect():
    data = collector.collect_data()
    if data:
        print(f"Voltage L1: {data['vl1']}V")
        print(f"Current L1: {data['il1']}A")
        print(f"Power P1: {data['p1']}kW")
        print(f"Frequency: {data['freq']}Hz")
        print(f"Active Energy: {data['activeEnergy']}kWh")
    collector.disconnect()
```

### Diris A10 Example

```python
from src.energy_counters.diris import (
    CounterConfiguration,
    ModbusTCPConfiguration,
    A10DataCollector
)

# Configure the counter
counter_config = CounterConfiguration(
    counter_id=152,
    unit_id=97,  # Modbus address
    counter_name="Carregador_Carro",
    company_id="NEMOTEK"
)

# Configure Modbus TCP connection
tcp_config = ModbusTCPConfiguration(
    host="172.16.5.11",
    port=502,
    timeout=4.0
)

# Create collector
collector = A10DataCollector(counter_config, modbus_tcp_config=tcp_config)

# Connect and read data
if collector.connect():
    data = collector.collect_data()
    if data:
        print(f"Voltage L1: {data['vl1']}V")
        print(f"Line-to-line voltage L12: {data['vl12']}V")
        print(f"Current L1: {data['il1']}A")
        print(f"Phase power L1: {data['pl1']}W")
        print(f"Total active power: {data['paeq']}W")
        print(f"Frequency: {data['freq']}Hz")
        print(f"Power factor: {data['pfeq']}")
        print(f"THD Voltage L1: {data['thdV1']}%")
        print(f"THD Current L1: {data['thdIL1']}%")
        print(f"Active Energy: {data['energyActive']}Wh")
    collector.disconnect()
```

### RedZ LKM144 Example

```python
from src.energy_counters.redz import (
    CounterConfiguration,
    ModbusRTUConfiguration,
    ModbusTCPConfiguration,
    LKM144DataCollector
)

# Configure the counter (matching Node-RED Red Z#10 setup)
counter_config = CounterConfiguration(
    counter_id=200,
    unit_id=1,  # Modbus address
    counter_name="e-Redes",
    company_id="MyCompany"
)

# Configure Modbus RTU connection (primary for LKM144)
rtu_config = ModbusRTUConfiguration(
    port="/dev/ttyNS0",
    baudrate=9600
)

# Optional TCP configuration (fallback)
tcp_config = ModbusTCPConfiguration(
    host="192.162.10.10",
    port=502
)

# Create collector with RTU primary, TCP fallback
collector = LKM144DataCollector(
    counter_config,
    modbus_tcp_config=tcp_config,
    modbus_rtu_config=rtu_config
)

# Connect and read data
if collector.connect():
    data = collector.collect_data()
    if data:
        print(f"Counter: {data['counterName']}")
        print(f"Voltage L1: {data['voltageL1']}")
        print(f"Current L1: {data['currentL1']}")
        print(f"Instantaneous Power: {data['instantaneousPower']}")
        print(f"Active Energy: {data['energyActive']}")
        print(f"Reactive Energy: {data['energyReactive']}")
        print(f"Power Factor: {data['powerFactor']}")
        print(f"Frequency: {data['frequency']}")
        print(f"Meter Number: {data['meterNumber']}")
    collector.disconnect()
```

### Contrel uD3h Example

```python
from src.energy_counters.contrel.ud3h import (
    CounterConfiguration,
    ModbusTCPConfiguration,
    ModbusRTUConfiguration,
    UD3hDataCollector
)

# Configure the counter
counter_config = CounterConfiguration(
    counter_id=175,
    unit_id=1,  # Modbus address
    counter_name="MainMeter",
    company_id="MyCompany"
)

# Configure Modbus TCP connection (primary)
tcp_config = ModbusTCPConfiguration(
    host="192.162.10.10",
    port=502,
    timeout=4.0
)

# Configure Modbus RTU connection (fallback)
rtu_config = ModbusRTUConfiguration(
    port="/dev/ttyNS0",
    baudrate=9600
)

# Create collector with both TCP and RTU support
collector = UD3hDataCollector(
    counter_config,
    modbus_tcp_config=tcp_config,
    modbus_rtu_config=rtu_config
)

# Connect and read data (tries TCP first, RTU as fallback)
if collector.connect():
    data = collector.collect_data()
    if data:
        print(f"Counter: {data['counterName']}")
        print(f"L-N Voltage L1: {data['vl1']}V")
        print(f"L-L Voltage L12: {data['vl12']}V")
        print(f"Current L1: {data['il1']}A")
        print(f"Phase Power L1: {data['pl1']}W")
        print(f"Total Active Power: {data['paeq']}W")
        print(f"Frequency: {data['freq']}Hz")
        print(f"Power Factor: {data['pfeq']}")
        print(f"Active Energy: {data['energyActive']}Wh")
    collector.disconnect()
```

## Supported Counters

| Brand | Model | Status | Modbus RTU | Modbus TCP | Features |
|-------|-------|--------|------------|------------|----------|
| **Carlo Gavazzi** | EM530 | **Implemented** | Yes | Yes | Full energy monitoring, fallback support |
| **Lovato** | DMG210 | **Implemented** | Yes | Yes | Complete energy data collection, dual communication |
| **Lovato** | DMG800 | **Planned** | - | - | Module structure ready |
| **Lovato** | DMG6 | **Planned** | - | - | Module structure ready |
| **Contrel** | uD3h | **Implemented** | Yes | Yes | Complete energy monitoring, dual communication |
| **Diris** | A10 | **Implemented** | Yes | Yes | Complete energy monitoring, THD analysis, dual communication |
| **RedZ** | LKM144 | **Implemented** | Yes | Yes | Complete energy monitoring, dual communication |
| **Schneider** | IEM3250 | **Planned** | - | - | Module structure ready |
| **Schneider** | IEM3155 | **Planned** | - | - | Module structure ready |

### Implementation Status Legend
- **Implemented**: Full functionality with comprehensive data collection
- **Planned**: Module structure exists, implementation pending
- **Modbus RTU/TCP**: Protocol supported
- **Fallback Support**: Automatic failover between TCP and RTU connections

## Requirements

- Python 3.8+
- pymodbus 3.0.0+
- pyserial 3.5+

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
