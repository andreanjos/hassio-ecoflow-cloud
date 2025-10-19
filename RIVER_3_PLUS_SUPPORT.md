# River 3 Plus Support for EcoFlow Home Assistant Integration

This document describes the River 3 Plus device support that has been added to the EcoFlow Home Assistant integration.

## Overview

The River 3 Plus devices (serial numbers starting with "R631") are now supported in the EcoFlow Home Assistant integration. This support includes:

- **Sensors**: Battery level, charging state, power input/output, temperature, voltage, and more
- **Switches**: AC output, DC output, X-Boost, and other device controls
- **Numbers**: Charging power, battery levels, and other configurable parameters
- **Selects**: Charging modes, timeouts, and other device settings

## Files Added/Modified

### New Files
- `custom_components/ecoflow_cloud/devices/internal/river3_plus.py` - Internal device implementation
- `custom_components/ecoflow_cloud/devices/public/river3_plus.py` - Public API device implementation

### Modified Files
- `custom_components/ecoflow_cloud/devices/registry.py` - Added River 3 Plus to device registries

## Device Features

The River 3 Plus integration provides the following Home Assistant entities:

### Sensors
- **Battery Level** - Main battery state of charge (0-100%)
- **Battery Health** - State of health percentage
- **Combined Battery Level** - LCD display battery level
- **Charging State** - Current charging status
- **Total Input Power** - Total power being input to the device
- **Total Output Power** - Total power being output from the device
- **Solar Input Current/Voltage** - Solar panel input measurements
- **AC Input/Output Power** - AC power measurements
- **DC Output Power** - DC output power
- **USB Output Power** - USB output power
- **Type-C Output Power** - Type-C output power
- **Remaining Time** - Estimated time remaining for charge/discharge
- **Battery Temperature** - Battery temperature with min/max cell temps
- **Battery Voltage** - Battery voltage with min/max cell voltages
- **Cycles** - Battery charge/discharge cycles
- **Status** - Device operational status

### Switches
- **AC Enabled** - Enable/disable AC output
- **AC Always Enabled** - Auto-enable AC output based on battery level
- **X-Boost Enabled** - Enable X-Boost mode for higher power output
- **DC Enabled** - Enable/disable DC output
- **Backup Power Enabled** - Enable backup power mode

### Numbers (Sliders)
- **Max Charge Level** - Maximum battery charge level (50-100%)
- **Min Discharge Level** - Minimum battery discharge level (0-30%)
- **AC Charging Power** - AC charging power setting (50-660W)
- **Backup Reserve Level** - Backup power reserve level (5-100%)

### Selects (Dropdowns)
- **DC Charge Current** - DC charging current setting
- **DC Mode** - DC charging mode selection
- **Screen Timeout** - LCD screen timeout setting
- **Unit Timeout** - Device standby timeout setting
- **AC Timeout** - AC output timeout setting

## Installation

1. **Copy the integration files** to your Home Assistant:
   ```bash
   # Copy the entire custom_components directory to your Home Assistant
   cp -r custom_components/ecoflow_cloud /path/to/homeassistant/custom_components/
   ```

2. **Restart Home Assistant** to load the updated integration

3. **Add the EcoFlow integration**:
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "EcoFlow"
   - Follow the setup wizard

4. **Configure your River 3 Plus devices**:
   - The integration should automatically detect your River 3 Plus devices
   - Enter your EcoFlow account credentials
   - The devices will appear as separate entities in Home Assistant

## Device Detection

The integration will automatically detect River 3 Plus devices based on:
- **Serial Number Pattern**: Devices with serial numbers starting with "R631"
- **Product Name**: "RIVER 3 Plus" in the device registry
- **Device Type**: "RIVER_3_PLUS" in the internal device registry

## Configuration

No special configuration is required for River 3 Plus devices. The integration uses the same configuration as other EcoFlow devices:

- **Account Credentials**: Your EcoFlow account email and password
- **Device Selection**: Choose which devices to monitor
- **Update Interval**: How often to poll for device updates

## Troubleshooting

### Device Not Detected
- Ensure your River 3 Plus device is connected to the EcoFlow app
- Check that the device serial number starts with "R631"
- Verify your EcoFlow account credentials are correct

### Missing Entities
- Restart Home Assistant after adding the integration
- Check the Home Assistant logs for any error messages
- Ensure the device is online and connected to EcoFlow servers

### Performance Issues
- Adjust the update interval in the integration settings
- Consider reducing the number of monitored devices if experiencing slowdowns

## Technical Details

The River 3 Plus implementation is based on the River 2 Max device structure, as they share similar hardware and capabilities. The integration uses:

- **Internal API**: Direct MQTT communication with EcoFlow servers
- **Public API**: REST API calls for device configuration
- **Data Bridge**: Converts between internal and public API formats

## Contributing

If you encounter issues with River 3 Plus support or want to add additional features:

1. Check the existing device implementations for reference
2. Test your changes with a real River 3 Plus device
3. Submit a pull request with your improvements

## Support

For issues with the River 3 Plus integration:
- Check the Home Assistant logs for error messages
- Verify your device is supported (serial starts with "R631")
- Ensure you're using the latest version of the integration
- Report issues on the GitHub repository with device details and logs


