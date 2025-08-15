# 🚀 PyPI Publishing Commands - edaflow v0.15.0

## ✅ **Ready for Publishing!**

All preparation complete:
- ✅ Version updated to 0.15.0 in all files
- ✅ CHANGELOG.md updated with critical fixes  
- ✅ README.md updated with release highlights
- ✅ Package built successfully
- ✅ Distribution files ready in `dist/`

## 📦 **Files Ready for Upload**
```
dist/edaflow-0.15.0-py3-none-any.whl  (130,061 bytes)
dist/edaflow-0.15.0.tar.gz           (421,078 bytes)
```

## 🧪 **Step 1: Test Upload (RECOMMENDED FIRST)**

Upload to TestPyPI to verify everything works:

```powershell
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/edaflow-0.15.0*

# Test installation (in a new environment)
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ edaflow==0.15.0

# Quick test
python -c "import edaflow; print(f'✅ edaflow {edaflow.__version__} works!')"
```

## 🚀 **Step 2: Production Upload**

After TestPyPI verification passes:

```powershell
# Upload to PyPI
python -m twine upload dist/edaflow-0.15.0*

# Verify installation
pip install edaflow==0.15.0

# Test
python -c "import edaflow; print(f'🎉 edaflow {edaflow.__version__} published!')"
```

## 🔐 **Authentication Required**

Make sure you have PyPI credentials:
- API token for PyPI in `~/.pypirc`, OR
- Use `--username __token__` with your API token when prompted

## ⚠️ **Important Notes**

1. **TestPyPI First**: Always test on TestPyPI before production upload
2. **Clean Upload**: Only upload the v0.15.0 files (specified in commands above)
3. **Verification**: Test installation after upload to ensure it works
4. **Documentation**: README will automatically appear on PyPI project page

## 📋 **Post-Upload Verification Checklist**

After successful upload:

### **PyPI Verification**:
- ⏳ Check project page: https://pypi.org/project/edaflow/0.15.0/
- ⏳ Verify README displays correctly
- ⏳ Check download stats appear

### **Installation Test**:
```powershell
# Fresh environment test
pip install edaflow==0.15.0
python -c "import edaflow; import edaflow.ml; print('✅ All modules work')"
```

### **Documentation Links**:
- ⏳ Ensure documentation links work
- ⏳ Check badge links in README

## 🎯 **Release Summary**

**What's in this release**:
- 🚨 **CRITICAL**: Fixed ML workflow documentation bugs
- ✅ **Model Fitting**: Added missing training steps 
- ✅ **Function Parameters**: Corrected all function signatures
- ✅ **User Experience**: Enhanced warnings and guidance

**Why this matters**:
- Users were getting "not fitted" errors following docs
- All ML workflow examples now work perfectly
- No breaking changes to API
- Significantly improved user experience

---

## 🎉 **Ready to Publish!**

Execute the commands above to publish edaflow v0.15.0 with critical ML workflow documentation fixes.

**Expected Timeline**:
- TestPyPI upload: ~1-2 minutes
- Production upload: ~1-2 minutes  
- Package availability: ~5-10 minutes
- Index updates: ~15-30 minutes
