"""
Simple test script to verify the backend setup
Run with: python test_setup.py
"""
import sys
import importlib.util

def check_module(module_name):
    """Check if a module can be imported"""
    spec = importlib.util.find_spec(module_name)
    return spec is not None

def main():
    print("=" * 60)
    print("Campus Security System - Setup Verification")
    print("=" * 60)
    
    # Check Python version
    print(f"\nPython Version: {sys.version}")
    if sys.version_info < (3, 9):
        print("⚠️  Warning: Python 3.9+ is recommended")
    else:
        print("✓ Python version OK")
    
    # Check required modules
    print("\nChecking dependencies...")
    dependencies = [
        "fastapi",
        "uvicorn",
        "sqlmodel",
        "sqlalchemy",
        "jose",
        "passlib",
        "pydantic"
    ]
    
    all_ok = True
    for dep in dependencies:
        if check_module(dep):
            print(f"✓ {dep}")
        else:
            print(f"✗ {dep} - NOT FOUND")
            all_ok = False
    
    if not all_ok:
        print("\n⚠️  Some dependencies are missing!")
        print("Run: pip install -r requirements.txt")
        return False
    
    # Try to import our modules
    print("\nChecking application modules...")
    try:
        import models
        print("✓ models.py")
    except Exception as e:
        print(f"✗ models.py - {e}")
        all_ok = False
    
    try:
        import database
        print("✓ database.py")
    except Exception as e:
        print(f"✗ database.py - {e}")
        all_ok = False
    
    try:
        import auth
        print("✓ auth.py")
    except Exception as e:
        print(f"✗ auth.py - {e}")
        all_ok = False
    
    try:
        import schemas
        print("✓ schemas.py")
    except Exception as e:
        print(f"✗ schemas.py - {e}")
        all_ok = False
    
    try:
        from routers import auth, scan, violations, visitors
        print("✓ routers/")
    except Exception as e:
        print(f"✗ routers/ - {e}")
        all_ok = False
    
    try:
        import main
        print("✓ main.py")
    except Exception as e:
        print(f"✗ main.py - {e}")
        all_ok = False
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✓ Setup verification PASSED!")
        print("\nYou can now start the server with:")
        print("  python main.py")
        print("or")
        print("  uvicorn main:app --reload")
        print("\nAPI will be available at:")
        print("  http://localhost:8000")
        print("  http://localhost:8000/docs (Interactive API docs)")
    else:
        print("✗ Setup verification FAILED!")
        print("\nPlease fix the errors above before running the server.")
    print("=" * 60)
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
