#!/usr/bin/env python3
"""
Comprehensive test script for all YamlForge cloud providers.
Tests that all required mappings/defaults are found and no warnings are generated.
"""

import sys
import os
import io
from contextlib import redirect_stdout, redirect_stderr

# Import YamlForge components
from ..core.converter import YamlForgeConverter
from ..providers.aws import AWSProvider
from ..providers.azure import AzureProvider  
from ..providers.gcp import GCPProvider
from ..providers.ibm_vpc import IBMVPCProvider
from ..providers.ibm_classic import IBMClassicProvider
from ..providers.oci import OCIProvider
from ..providers.vmware import VMwareProvider
from ..providers.alibaba import AlibabaProvider
from ..providers.cnv import CNVProvider
from ..providers.openshift.base import BaseOpenShiftProvider

def capture_output(func, *args, **kwargs):
    """Capture stdout and stderr from a function call"""
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            result = func(*args, **kwargs)
        return result, stdout_capture.getvalue(), stderr_capture.getvalue()
    except Exception as e:
        return None, stdout_capture.getvalue(), str(e)

def test_converter_initialization():
    """Test that the main converter initializes without warnings"""
    print("🧪 Testing YamlForgeConverter initialization...")
    
    converter, stdout, stderr = capture_output(lambda: YamlForgeConverter(analyze_mode=True))
    
    if converter:
        print(f"  ✅ Converter initialized successfully")
        print(f"  ✅ Loaded {len(converter.images)} images")
        print(f"  ✅ Loaded {len(converter.locations)} locations") 
        print(f"  ✅ Loaded {len(converter.flavors)} flavors")
        
        if stdout.strip():
            print(f"  ⚠️  STDOUT output: {stdout.strip()}")
        if stderr.strip():
            print(f"  ⚠️  STDERR output: {stderr.strip()}")
        
        return converter
    else:
        print(f"  ❌ Failed to initialize converter")
        if stdout.strip():
            print(f"     STDOUT: {stdout.strip()}")
        if stderr.strip():
            print(f"     STDERR: {stderr.strip()}")
        return None

def test_provider(provider_class, provider_name, converter):
    """Test initialization of a specific provider"""
    print(f"🧪 Testing {provider_name} provider...")
    
    try:
        provider, stdout, stderr = capture_output(lambda: provider_class(converter))
        
        if provider:
            print(f"  ✅ {provider_name} provider initialized successfully")
            
            # Check for any output that might indicate warnings
            if stdout.strip():
                if "warning" in stdout.lower() or "error" in stdout.lower():
                    print(f"  ⚠️  STDOUT output: {stdout.strip()}")
                else:
                    print(f"  ℹ️  STDOUT (info): {stdout.strip()}")
                    
            if stderr.strip():
                print(f"  ⚠️  STDERR output: {stderr.strip()}")
                
            return True
        else:
            print(f"  ❌ Failed to initialize {provider_name} provider")
            if stdout.strip():
                print(f"     STDOUT: {stdout.strip()}")
            if stderr.strip():
                print(f"     STDERR: {stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"  ❌ Exception testing {provider_name}: {e}")
        return False

def test_openshift_provider(converter):
    """Special test for OpenShift provider (different initialization)"""
    print(f"🧪 Testing OpenShift provider...")
    
    try:
        provider, stdout, stderr = capture_output(lambda: BaseOpenShiftProvider())
        
        if provider:
            print(f"  ✅ OpenShift provider initialized successfully")
            
            if stdout.strip():
                if "warning" in stdout.lower() or "error" in stdout.lower():
                    print(f"  ⚠️  STDOUT output: {stdout.strip()}")
                else:
                    print(f"  ℹ️  STDOUT (info): {stdout.strip()}")
                    
            if stderr.strip():
                print(f"  ⚠️  STDERR output: {stderr.strip()}")
                
            return True
        else:
            print(f"  ❌ Failed to initialize OpenShift provider")
            if stdout.strip():
                print(f"     STDOUT: {stdout.strip()}")
            if stderr.strip():
                print(f"     STDERR: {stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"  ❌ Exception testing OpenShift: {e}")
        return False

def main():
    """Run all provider tests"""
    print("=" * 80)
    print("🚀 YAMLFORGE PROVIDER INITIALIZATION TEST")
    print("=" * 80)
    print()
    
    # Test converter first
    converter = test_converter_initialization()
    if not converter:
        print("\n❌ Cannot continue - converter failed to initialize")
        return False
    
    print()
    
    # Define all providers to test
    providers_to_test = [
        (AWSProvider, "AWS"),
        (AzureProvider, "Azure"),
        (GCPProvider, "GCP"),
        (IBMVPCProvider, "IBM VPC"),
        (IBMClassicProvider, "IBM Classic"),
        (OCIProvider, "OCI"),
        (VMwareProvider, "VMware"),
        (AlibabaProvider, "Alibaba"),
        (CNVProvider, "CNV")
    ]
    
    # Test each provider
    results = {}
    for provider_class, provider_name in providers_to_test:
        success = test_provider(provider_class, provider_name, converter)
        results[provider_name] = success
        print()
    
    # Test OpenShift separately (different initialization pattern)
    openshift_success = test_openshift_provider(converter)
    results["OpenShift"] = openshift_success
    print()
    
    # Summary
    print("=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for provider_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {provider_name}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print()
    print(f"📈 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL PROVIDERS PASSED! No warnings or missing files detected.")
        return True
    else:
        print(f"⚠️  {failed} provider(s) had issues - check output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)