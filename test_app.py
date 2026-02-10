#!/usr/bin/env python3
import sys
print("Python version:", sys.version)

try:
    print("Step 1: Importing Flask...")
    from flask import Flask
    print("✅ Flask imported successfully")

    print("Step 2: Creating app...")
    from app import create_app, db
    print("✅ create_app imported")

    app = create_app()
    print("✅ App instance created")

    print("Step 3: Testing database context...")
    with app.app_context():
        print("✅ App context established")
        db.create_all()
        print("✅ Database initialized")

    print("\n✅✅✅ SUCCESS! APPLICATION WORKS PERFECTLY ✅✅✅")
    print("\nYou can now start the server with:")
    print("  python3 run.py")

except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"Message: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)

