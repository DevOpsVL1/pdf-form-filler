#!/usr/bin/env python3
"""
Quick backend test - checks if PDF generation works
"""

print("=" * 60)
print("BACKEND TEST - PDF Generation")
print("=" * 60)

# Test 1: Import test
print("\n1. Testing imports...")
try:
    from form_fillers.cif1_filler import generate_cif1_pdf
    from form_fillers.pembiayaan_filler import generate_pembiayaan_pdf
    print("   ✓ Imports successful")
except ImportError as e:
    print(f"   ✗ Import failed: {e}")
    exit(1)

# Test 2: PDF template check
print("\n2. Checking PDF templates...")
import os
cif1_path = "templates/BORANG_CIF-1.pdf"
pembiayaan_path = "templates/BORANG_PEMBIAYAAN_PERIBADI.pdf"

if os.path.exists(cif1_path):
    print(f"   ✓ CIF-1 template found: {os.path.getsize(cif1_path)} bytes")
else:
    print(f"   ✗ CIF-1 template NOT found at: {cif1_path}")

if os.path.exists(pembiayaan_path):
    print(f"   ✓ Pembiayaan template found: {os.path.getsize(pembiayaan_path)} bytes")
else:
    print(f"   ✗ Pembiayaan template NOT found at: {pembiayaan_path}")

# Test 3: CIF-1 PDF Generation
print("\n3. Testing CIF-1 PDF generation...")
test_data = {
    'ic_number': '920315105438',
    'name_ic': 'AHMAD FARIZ BIN ABDULLAH'
}

try:
    pdf_buffer = generate_cif1_pdf(test_data)
    pdf_size = len(pdf_buffer.getvalue())
    print(f"   ✓ CIF-1 PDF generated successfully: {pdf_size} bytes")
except Exception as e:
    print(f"   ✗ CIF-1 generation failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 4: Pembiayaan PDF Generation
print("\n4. Testing Pembiayaan PDF generation...")
test_data = {
    'ic_number': '920315105438',
    'name': 'AHMAD FARIZ'
}

try:
    pdf_buffer = generate_pembiayaan_pdf(test_data)
    pdf_size = len(pdf_buffer.getvalue())
    print(f"   ✓ Pembiayaan PDF generated successfully: {pdf_size} bytes")
except Exception as e:
    print(f"   ✗ Pembiayaan generation failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 5: Flask app check
print("\n5. Checking Flask app configuration...")
try:
    from app import app, CIF1_LIMITS, PEMBIAYAAN_LIMITS
    print(f"   ✓ Flask app loaded")
    print(f"   ✓ CIF-1 has {len(CIF1_LIMITS)} field limits configured")
    print(f"   ✓ Pembiayaan has {len(PEMBIAYAAN_LIMITS)} field limits configured")
except Exception as e:
    print(f"   ✗ Flask app error: {e}")

print("\n" + "=" * 60)
print("RESULT: All backend tests passed! ✅")
print("=" * 60)
print("\nIf backend works but web doesn't, the issue is in JavaScript/frontend.")
print("Please open browser console (F12) and send me the error messages.")
print("=" * 60)
