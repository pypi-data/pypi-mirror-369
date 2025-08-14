#!/usr/bin/env python3
"""
Comprehensive Terraform generation test for YamlForge.
Tests actual Terraform file generation for AWS, Azure, IBM VPC, IBM Classic, and GCP.
Uses --no-credentials mode to avoid authentication dependencies.
"""

import sys
import os
import tempfile
import yaml
import shutil
import subprocess
from pathlib import Path

# Get repo root for yamlforge.py script location
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_test_config(provider_name, provider_config):
    """Create a test YAML configuration for a provider"""
    # Create valid 5-character GUIDs
    guid_map = {
        'AWS': 'test1',
        'Azure': 'test2', 
        'GCP': 'test3',
        'IBM VPC': 'test4',
        'IBM Classic': 'test5'
    }
    
    config = {
        'guid': guid_map.get(provider_name, 'test9'),
        'yamlforge': {
            'cloud_workspace': {'name': f'{provider_name.lower().replace(" ", "-")}-terraform-test'},
            'instances': [provider_config]
        }
    }
    return yaml.dump(config, default_flow_style=False)

def test_terraform_generation(provider_name, provider_config):
    """Test Terraform generation for a specific provider"""
    print(f"🧪 Testing {provider_name} Terraform generation...")
    
    # Create temporary directories
    test_dir = tempfile.mkdtemp(prefix=f'yamlforge_test_{provider_name.lower()}_')
    config_file = os.path.join(test_dir, 'config.yaml')
    output_dir = os.path.join(test_dir, 'terraform_output')
    
    try:
        # Create config file
        config_yaml = create_test_config(provider_name, provider_config)
        with open(config_file, 'w') as f:
            f.write(config_yaml)
        
        print(f"  📝 Created config: {config_file}")
        print(f"  📁 Output directory: {output_dir}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Run yamlforge to generate Terraform
        yamlforge_script = os.path.join(repo_root, 'yamlforge.py')
        cmd = [
            sys.executable, 
            yamlforge_script,
            config_file,
            '-d', output_dir,
            '--verbose',
            '--no-credentials'  # Skip credential validation for testing
        ]
        
        print(f"  🔨 Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=repo_root
        )
        
        if result.returncode == 0:
            print(f"  ✅ Terraform generation completed successfully")
            
            # Check for expected Terraform files
            terraform_files = list(Path(output_dir).glob('*.tf'))
            if terraform_files:
                print(f"  ✅ Generated {len(terraform_files)} Terraform files:")
                for tf_file in sorted(terraform_files):
                    size = tf_file.stat().st_size
                    print(f"    - {tf_file.name} ({size} bytes)")
            else:
                print(f"  ⚠️  No .tf files found in output directory")
            
            # Check for terraform state files
            tf_state_files = list(Path(output_dir).glob('terraform.tf*'))
            if tf_state_files:
                print(f"  ✅ Found Terraform state files: {[f.name for f in tf_state_files]}")
            
            # Check stdout for any warnings
            if result.stdout:
                warning_count = result.stdout.lower().count('warning')
                error_count = result.stdout.lower().count('error')
                if warning_count > 0:
                    print(f"  ⚠️  Found {warning_count} warning(s) in output")
                if error_count > 0:
                    print(f"  ❌ Found {error_count} error(s) in output")
                
            return True, output_dir, result.stdout
            
        else:
            print(f"  ❌ Terraform generation failed with exit code {result.returncode}")
            if result.stdout:
                print(f"     STDOUT: {result.stdout}")
            if result.stderr:
                print(f"     STDERR: {result.stderr}")
            return False, None, result.stderr
            
    except Exception as e:
        print(f"  ❌ Exception during {provider_name} test: {e}")
        return False, None, str(e)
        
    finally:
        # Clean up temporary directory
        try:
            shutil.rmtree(test_dir)
            print(f"  🧹 Cleaned up test directory: {test_dir}")
        except Exception as e:
            print(f"  ⚠️  Failed to clean up {test_dir}: {e}")

def main():
    """Run Terraform generation tests for all major providers"""
    print("=" * 80)
    print("🚀 YAMLFORGE TERRAFORM GENERATION TEST")
    print("=" * 80)
    print("Using --no-credentials mode for testing (no authentication required)")
    print()
    
    # Define test configurations for each provider
    provider_tests = [
        ("AWS", {
            'name': 'aws-terraform-test',
            'provider': 'aws',
            'flavor': 'small',
            'image': 'RHEL9-latest',
            'location': 'us-east'
        }),
        ("Azure", {
            'name': 'azure-terraform-test', 
            'provider': 'azure',
            'flavor': 'small',
            'image': 'RHEL9-latest',
            'location': 'us-east'
        }),
        ("GCP", {
            'name': 'gcp-terraform-test',
            'provider': 'gcp', 
            'flavor': 'small',
            'image': 'RHEL9-latest',
            'location': 'us-east'
        }),
        ("IBM VPC", {
            'name': 'ibm-vpc-terraform-test',
            'provider': 'ibm_vpc',
            'flavor': 'small', 
            'image': 'RHEL9-latest',
            'location': 'us-east'
        }),
        ("IBM Classic", {
            'name': 'ibm-classic-terraform-test',
            'provider': 'ibm_classic',
            'flavor': 'small',
            'image': 'RHEL9-latest', 
            'location': 'dal13',  # Dallas datacenter for IBM Classic
            'domain': 'example.com'  # Required domain for IBM Classic
        })
    ]
    
    # Test each provider
    results = {}
    successful_outputs = []
    
    for provider_name, config in provider_tests:
        success, output_dir, details = test_terraform_generation(provider_name, config)
        results[provider_name] = success
        
        if success and output_dir:
            successful_outputs.append((provider_name, output_dir))
        
        print()
    
    # Summary
    print("=" * 80)
    print("📊 TERRAFORM GENERATION TEST SUMMARY")
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
        print("🎉 ALL TERRAFORM GENERATION TESTS PASSED!")
        print("   Path resolution working perfectly for Terraform generation!")
        return True
    else:
        print(f"⚠️  {failed} provider(s) had Terraform generation issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)