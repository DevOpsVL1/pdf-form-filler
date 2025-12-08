# ⚡ QUICK START GUIDE

## 🚀 **GET STARTED IN 3 STEPS**

### **Step 1: Install Dependencies**
```bash
cd PDF-FORM-PLATFORM-PERFECT
pip install -r requirements.txt
```

### **Step 2: Run the Platform**
```bash
python app.py
```

### **Step 3: Open in Browser**
```
http://localhost:5000
```

**That's it!** 🎉

---

## 🧪 **QUICK TEST**

### **Test Pembiayaan Form (All 49 fields):**

1. Go to: http://localhost:5000/pembiayaan

2. Fill in some test data:
   - **Top Section:**
     - Financing Amount: 50000
     - Tenure: 60
     - Membership Number: 7712345
   
   - **Section D (Spouse):**
     - Spouse Name: SITI NURHALIZA
     - IC New: 850805106789
   
   - **Section E (Reference):**
     - Reference Name: AHMAD BIN ALI
     - IC: 700101105678
   
   - **Section F (Financial) - NEW!:**
     - Monthly Salary: 5000
     - Spouse Income: 3000
     - Other Income: 500
     - Total Income: 8500
     - Cost of Living: 2000
     - Other Expenses: 500
     - **Bank 1:**
       - Name: Bank Rakyat
       - Type: Personal Loan
       - Account: 123456789
       - Monthly Payment: 500
       - Balance: 15000

3. Click "Generate PDF"

4. Download and check: **All 49 fields should appear perfectly!** ✅

---

### **Test CIF-1 Form (All 32 fields):**

1. Go to: http://localhost:5000/cif1

2. Fill in test data:
   - IC Number: 850805106789
   - Name: MUHAMMAD BIN AHMAD
   - Address: LOT 123, JALAN MERDEKA
   - Mobile: 0123456789
   - Employer: ABC COMPANY
   - Monthly Income: 5000

3. Click "Generate PDF"

4. Download and check: **All 32 fields should appear perfectly!** ✅

---

## 📂 **GENERATED PDFs**

All generated PDFs are saved in:
```
PDF-FORM-PLATFORM-PERFECT/outputs/
```

Files are named with timestamp:
- `CIF1_2025-12-03_17-30-45.pdf`
- `Pembiayaan_2025-12-03_17-30-45.pdf`

---

## 🎯 **KEY FEATURES TO TRY**

### **Automatic Uppercase:**
- Type: "siti nurhaliza" → Saves as: "SITI NURHALIZA"

### **IC Formatting:**
- Type: 850805106789 → PDF shows: 850805 10 6789

### **Decimal Formatting:**
- Type: 5000 → PDF shows: 5,000.00 (in proper boxes)

### **Right-to-Left Filling:**
- Financial fields fill from right, like calculators

### **Character Counting:**
- Real-time counter shows: "15 / 40 characters"

### **Bank Table:**
- 3 separate cards for up to 3 banks
- 5 fields per bank (Name, Type, Account, Payment, Balance)

---

## 🔧 **CONFIGURATION**

### **Change Port:**
Edit `app.py` line ~400:
```python
app.run(debug=True, port=5001)  # Change to 5001
```

### **Enable Debugging:**
Already enabled! Check `logs/` folder for errors.

### **Customize Styling:**
Edit `static/css/custom.css`

---

## ⚠️ **COMMON ISSUES**

### **"ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

### **"PDF Template Not Found"**
Make sure `BORANG PEMBIAYAAN PERIBADI-1.pdf` is in `static/` folder

### **"Port 5000 already in use"**
```bash
# Stop other process using port 5000, or change port in app.py
```

### **"Permission denied" (Windows)**
Run terminal as Administrator

---

## 📊 **WHAT YOU HAVE**

✅ **CIF-1 Form:** 32 fields, fully working
✅ **Pembiayaan Form:** 49 fields, Section F complete
✅ **Web Interface:** Professional, responsive
✅ **PDF Generation:** Accurate positioning
✅ **Total Fields:** 81 across 2 forms

---

## 🎉 **YOU'RE READY!**

Your platform is **COMPLETE** and **PRODUCTION-READY**!

Start using it for:
- ✅ Co-opbank Pertama CIF-1 forms
- ✅ Personal financing applications (Pembiayaan Peribadi)
- ✅ Automated form filling
- ✅ Batch processing (via API)

**Enjoy your perfect PDF form platform!** 🚀

---

## 📖 **MORE INFO**

- **Full Features:** See `COMPLETE_FEATURES.md`
- **Detailed Setup:** See `INSTALLATION_GUIDE.md`
- **Field Reference:** See `COMPLETE_FEATURES.md`
- **Main README:** See `README.md`
