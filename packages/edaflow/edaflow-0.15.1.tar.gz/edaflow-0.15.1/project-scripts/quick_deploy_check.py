import requests
import subprocess
import sys

def check_pypi_status():
    """Check what version is currently on PyPI."""
    try:
        url = "https://pypi.org/pypi/edaflow/json"
        response = requests.get(url, timeout=10)
        data = response.json()
        current_version = data['info']['version']
        print(f"Current PyPI version: {current_version}")
        
        # Check if 0.14.0 is available
        versions = list(data['releases'].keys())
        if "0.14.0" in versions:
            print("✅ Version 0.14.0 is available on PyPI!")
            return True
        else:
            print("⏳ Version 0.14.0 not yet available on PyPI")
            print(f"Latest available versions: {sorted(versions, reverse=True)[:5]}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking PyPI: {e}")
        return False

def check_local_version():
    """Check local installation version."""
    try:
        import edaflow
        print(f"Local version: {edaflow.__version__}")
        return edaflow.__version__ == "0.14.0"
    except Exception as e:
        print(f"❌ Error checking local version: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Quick Deployment Status Check")
    print("=" * 40)
    
    print("\n1. Local Version:")
    local_ok = check_local_version()
    
    print("\n2. PyPI Status:")
    pypi_ok = check_pypi_status()
    
    if local_ok and pypi_ok:
        print("\n🎉 Deployment successful!")
    elif local_ok:
        print("\n⏳ Local build ready, waiting for PyPI propagation...")
    else:
        print("\n❌ Issues detected")
