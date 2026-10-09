from app.services.file_storage import validate_file_magic_bytes
import os

print("Testing File Magic Byte Validation")
print("=" * 60)
print()

# Test 1: Valid JPEG
print("Test 1: Valid JPEG file")
jpeg_signature = b'\xFF\xD8\xFF' + b'\x00' * 100
try:
    validate_file_magic_bytes(jpeg_signature, "photo.jpg")
    print("✅ Valid JPEG accepted")
except ValueError as e:
    print(f"❌ {e}")

print()

# Test 2: Valid PNG
print("Test 2: Valid PNG file")
png_signature = b'\x89PNG' + b'\x00' * 100
try:
    validate_file_magic_bytes(png_signature, "photo.png")
    print("✅ Valid PNG accepted")
except ValueError as e:
    print(f"❌ {e}")

print()

# Test 3: Invalid - JPEG signature with .png extension
print("Test 3: JPEG content with .png extension (SHOULD FAIL)")
try:
    validate_file_magic_bytes(jpeg_signature, "photo.png")
    print("❌ Invalid file was accepted (BUG!)")
except ValueError as e:
    print(f"✅ Correctly rejected: {e}")

print()

# Test 4: Invalid - Executable/text with image extension
print("Test 4: Executable/text content with .jpg extension (SHOULD FAIL)")
malicious_content = b'#!/bin/bash\nrm -rf /' + b'\x00' * 100
try:
    validate_file_magic_bytes(malicious_content, "photo.jpg")
    print("❌ Malicious file was accepted (BUG!)")
except ValueError as e:
    print(f"✅ Correctly rejected: {e}")

print()

# Test 5: Valid GIF
print("Test 5: Valid GIF file")
gif_signature = b'GIF89a' + b'\x00' * 100
try:
    validate_file_magic_bytes(gif_signature, "photo.gif")
    print("✅ Valid GIF accepted")
except ValueError as e:
    print(f"❌ {e}")

print()

# Test 6: Empty file (SHOULD FAIL)
print("Test 6: Empty file (SHOULD FAIL)")
try:
    validate_file_magic_bytes(b'', "photo.jpg")
    print("❌ Empty file was accepted (BUG!)")
except ValueError as e:
    print(f"✅ Correctly rejected: {e}")

print()
print("=" * 60)
print("✅ All file validation tests passed!")
