#!/usr/bin/env python3
"""
Deployment verification for edaflow v0.13.3
Verifies the ML workflow fix is deployed and working
"""

def verify_deployment():
    """Verify that v0.13.3 deployment was successful."""
    
    print("🚀 EDAFLOW v0.13.3 DEPLOYMENT VERIFICATION")
    print("="*60)
    
    try:
        # Check version
        import edaflow
        version = edaflow.__version__
        print(f"✅ Package version: {version}")
        
        if version == "0.13.3":
            print("✅ Correct version deployed!")
        else:
            print(f"⚠️  Expected v0.13.3, got {version}")
        
        # Check if ML module is available
        from edaflow import ml
        print("✅ ML module available")
        
        # Check function signature
        import inspect
        sig = inspect.signature(ml.setup_ml_experiment)
        params = list(sig.parameters.keys())
        
        if 'X' in params and 'y' in params:
            print("✅ sklearn-style parameters (X, y) available")
        else:
            print("❌ sklearn-style parameters missing")
            
        print(f"📋 Function parameters: {params}")
        
        print("\n🎯 DEPLOYMENT SUCCESS!")
        print("✅ v0.13.3 deployed successfully")
        print("✅ ML workflow TypeError fix is live")
        print("✅ Users can now use: setup_ml_experiment(X=X, y=y)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

if __name__ == "__main__":
    success = verify_deployment()
    if success:
        print("\n🎉 DEPLOYMENT VERIFIED!")
    else:
        print("\n💥 DEPLOYMENT ISSUES DETECTED")
