
import sys
import os

print(f"Python: {sys.version}")

found = False

try:
    print("Attempt 1: langchain.storage")
    from langchain.storage import EncoderBackedStore
    print("✅ Found in langchain.storage")
    found = True
except ImportError:
    print("❌ Not in langchain.storage")

if not found:
    try:
        print("Attempt 2: langchain.storage.encoder_backed")
        from langchain.storage.encoder_backed import EncoderBackedStore
        print("✅ Found in langchain.storage.encoder_backed")
        found = True
    except ImportError:
        print("❌ Not in langchain.storage.encoder_backed")

if not found:
    try:
        print("Attempt 3: langchain_classic.storage")
        from langchain_classic.storage import EncoderBackedStore
        print("✅ Found in langchain_classic.storage")
        found = True
    except ImportError:
        print("❌ Not in langchain_classic.storage")
