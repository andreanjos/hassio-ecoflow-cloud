#!/usr/bin/env python3
"""
Simple test to verify River 3 Plus files exist and can be imported.
"""

import os
import sys

def test_files_exist():
    """Test that the River 3 Plus files exist."""
    print("Testing River 3 Plus file structure...")
    
    base_path = "custom_components/ecoflow_cloud/devices"
    
    # Check internal file
    internal_file = os.path.join(base_path, "internal", "river3_plus.py")
    if os.path.exists(internal_file):
        print(f"✅ {internal_file} exists")
    else:
        print(f"❌ {internal_file} not found")
        return False
    
    # Check public file
    public_file = os.path.join(base_path, "public", "river3_plus.py")
    if os.path.exists(public_file):
        print(f"✅ {public_file} exists")
    else:
        print(f"❌ {public_file} not found")
        return False
    
    # Check registry file
    registry_file = os.path.join(base_path, "registry.py")
    if os.path.exists(registry_file):
        print(f"✅ {registry_file} exists")
        
        # Check if River 3 Plus is mentioned in registry
        with open(registry_file, 'r') as f:
            content = f.read()
            if "river3_plus" in content:
                print("✅ River 3 Plus imports found in registry")
            else:
                print("❌ River 3 Plus imports not found in registry")
                return False
            
            if "RIVER_3_PLUS" in content:
                print("✅ RIVER_3_PLUS found in devices registry")
            else:
                print("❌ RIVER_3_PLUS not found in devices registry")
                return False
                
            if "RIVER 3 Plus" in content:
                print("✅ 'RIVER 3 Plus' found in device_by_product registry")
            else:
                print("❌ 'RIVER 3 Plus' not found in device_by_product registry")
                return False
    else:
        print(f"❌ {registry_file} not found")
        return False
    
    return True

if __name__ == "__main__":
    print("EcoFlow Integration - River 3 Plus File Structure Test")
    print("=" * 60)
    
    success = test_files_exist()
    
    if success:
        print("\n🎉 River 3 Plus files are properly structured!")
        print("\nNext steps:")
        print("1. Copy the custom_components/ecoflow_cloud directory to your Home Assistant")
        print("2. Restart Home Assistant")
        print("3. Add the EcoFlow integration and configure your River 3 Plus devices")
    else:
        print("\n❌ River 3 Plus file structure test failed!")
        sys.exit(1)


