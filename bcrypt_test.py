#!/usr/bin/env python3
"""
Test bcrypt functionality to identify the password length issue
"""

from passlib.context import CryptContext
import os
import sys

# Initialize the same context as the backend
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_bcrypt_functionality():
    print("🔍 Testing bcrypt functionality...")
    
    # Test 1: Normal password
    try:
        normal_password = "password123"
        print(f"✅ Test 1: Normal password ({len(normal_password)} chars)")
        hashed = pwd_context.hash(normal_password)
        verified = pwd_context.verify(normal_password, hashed)
        print(f"   Hash: {hashed[:50]}...")
        print(f"   Verify: {verified}")
    except Exception as e:
        print(f"❌ Test 1 failed: {str(e)}")
    
    # Test 2: Long password (72 bytes)
    try:
        long_password = "a" * 72
        print(f"✅ Test 2: 72-byte password ({len(long_password)} chars)")
        hashed = pwd_context.hash(long_password)
        verified = pwd_context.verify(long_password, hashed)
        print(f"   Hash: {hashed[:50]}...")
        print(f"   Verify: {verified}")
    except Exception as e:
        print(f"❌ Test 2 failed: {str(e)}")
    
    # Test 3: Too long password (73+ bytes)
    try:
        too_long_password = "a" * 73
        print(f"❌ Test 3: 73-byte password ({len(too_long_password)} chars) - Should fail")
        hashed = pwd_context.hash(too_long_password)
        verified = pwd_context.verify(too_long_password, hashed)
        print(f"   Hash: {hashed[:50]}...")
        print(f"   Verify: {verified}")
    except Exception as e:
        print(f"✅ Test 3 correctly failed: {str(e)}")
    
    # Test 4: Test with a realistic long password
    try:
        realistic_long = "ThisIsAVeryLongPasswordThatMightExceedThe72ByteLimitForBcryptHashing123!"
        print(f"🔍 Test 4: Realistic long password ({len(realistic_long)} chars, {len(realistic_long.encode('utf-8'))} bytes)")
        if len(realistic_long.encode('utf-8')) > 72:
            print("   ⚠️ This password exceeds 72 bytes - will cause bcrypt error")
            # Truncate to 72 bytes
            truncated = realistic_long.encode('utf-8')[:72].decode('utf-8', errors='ignore')
            print(f"   🔧 Truncated version: {truncated} ({len(truncated)} chars)")
            hashed = pwd_context.hash(truncated)
            verified = pwd_context.verify(truncated, hashed)
            print(f"   ✅ Truncated version works: {verified}")
        else:
            hashed = pwd_context.hash(realistic_long)
            verified = pwd_context.verify(realistic_long, hashed)
            print(f"   ✅ Password works: {verified}")
    except Exception as e:
        print(f"❌ Test 4 failed: {str(e)}")

if __name__ == "__main__":
    test_bcrypt_functionality()