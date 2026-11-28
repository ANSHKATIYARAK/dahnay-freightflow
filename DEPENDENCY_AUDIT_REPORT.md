# Dependency Audit Report: DahNAY FreightFlow

**Generated:** 2026-11-28  
**Python Version:** 3.12 (venv)  
**Scope:** `/home/hud/dahnay-freightflow/requirements.txt` + installed packages + codebase imports

---

## Summary Table

| Package | Required (req.txt) | Latest PyPI | Outdated? | CVE Count | Python Requires | Yanked Latest? | Notes |
|---------|-------------------|-------------|-----------|-----------|-----------------|----------------|-------|
| **fastapi** | `>=0.110.0` | 0.165.0 | ✅ Yes (55 versions behind) | 3 | >=3.11 | No | Core framework; latest requires Python 3.11+ ✓ |
| **uvicorn** | `>=0.28.0` | 0.54.0 | ✅ Yes (26 versions behind) | 4 | >=3.10 | No (0.17.0 yanked) | ASGI server; compatible |
| **pydantic** | `>=2.7.0` | 2.14.4 | ✅ Yes (7 minor behind) | 4 | >=3.10 | No (2.12.1, 1.10.3 yanked) | Data validation; latest compatible |
| **python-multipart** | `>=0.0.9` | 0.0.34 | ✅ Yes (25 versions behind) | **18** | >=3.11 | No (0.0.13, 0.0.14 yanked) | **HIGH RISK** - 18 DoS/ReDoS CVEs |
| **openpyxl** | `>=3.1.2` | 3.1.5 | ✅ Yes (3 versions behind) | 2 | >=3.8 | No (3.2.0b1 yanked) | Excel parsing; compatible |
| **pyyaml** | `>=6.0.1` | 6.0.4 | ✅ Yes (3 versions behind) | **8** | >=3.10 | No (6.0.2rc1 yanked) | **HIGH RISK** - unsafe deserialization CVEs |
| **httpx** | `>=0.27.0` | 0.29.0 | ✅ Yes (2 versions behind) | 2 | >=3.10 | No | **UNUSED** in codebase |
| **jinja2** | `>=3.1.3` | 3.1.6 | ✅ Yes (3 versions behind) | **20** | >=3.7 | No | **UNUSED** - **HIGH RISK** sandbox escapes |
| **requests** | `>=2.31.0` | 2.34.2 | ✅ Yes (3 versions behind) | 16 | >=3.10 | No (2.32.0, 2.32.1 yanked) | **UNUSED** in codebase |
| **rapidfuzz** | `>=3.6.0` | 3.14.6 | ✅ Yes (8 versions behind) | 0 | >=3.11 | No (3.14.0, 3.14.4 yanked) | Fuzzy matching; compatible, no CVEs |

---

## Critical Findings

### 🔴 HIGH SEVERITY: Unused Dependencies with Critical CVEs

| Package | CVEs | Risk | Action |
|---------|------|------|--------|
| **jinja2** | 20 | Sandbox escapes, arbitrary code execution, RCE via template injection | **REMOVE** - not imported anywhere in codebase |
| **requests** | 16 | Credential leaks, session fixation, proxy auth leaks | **REMOVE** - not imported anywhere in codebase |
| **httpx** | 2 | Input validation issues | **REMOVE** - not imported anywhere in codebase |

### 🟠 HIGH SEVERITY: Used Dependencies with Many CVEs

| Package | CVEs | Details |
|---------|------|---------|
| **python-multipart** | 18 | Multiple DoS/ReDoS via Content-Type header, boundary parsing, semicolon separators, preamble/epilogue, negative Content-Length. Arbitrary file write via non-default config. |
| **pyyaml** | 8 | Unsafe deserialization (arbitrary code execution via `yaml.load`), multiple input validation flaws. **Must use `yaml.safe_load`** - codebase does this correctly in `template_engine.py:35`. |

### 🟡 MEDIUM: All Pinned Versions Are Outdated

Every package in `requirements.txt` uses `>=X.Y.Z` lower bounds, meaning `pip install` will pull latest. However, the lower bounds are significantly behind current releases. Consider pinning to known-good versions or updating lower bounds.

### 🔵 INFO: Missing Dependency

| Package | Used In | Status |
|---------|---------|--------|
| **pdfplumber** | `dahnay_logistics/engine/normalizer.py:13` (optional, try/except) | **NOT INSTALLED** - PDF parsing will fall back to text extraction only. Add to requirements if PDF support needed. |

---

## CVE Details (Top Risks)

### python-multipart (18 vulnerabilities)
- **GHSA-2jv5-9r88-3w3p**: Content-Type Header ReDoS (CVSS 7.5)
- **GHSA-59g5-xgcq-4qw3**: DoS via deformed multipart boundary (CVSS 7.5)
- **GHSA-5rvq-cxj2-64vf**: Quadratic-time querystring parsing (CVSS 7.5)
- **GHSA-wp53-j4wj-2cfg**: Arbitrary File Write via Non-Default Config (CVSS 8.2)
- **GHSA-pp6c-gr5w-3c5g**: DoS via unbounded multipart part headers (CVSS 7.5)

> **Mitigation**: FastAPI uses python-multipart internally for form parsing. Ensure file upload size limits are configured. Update to >=0.0.34 (latest).

### pyyaml (8 vulnerabilities)
- **GHSA-3pqx-4fqf-j49f**: Deserialization of Untrusted Data (CVSS 9.8)
- **GHSA-rprw-h62v-c2w7**: Insecure deserialization leading to arbitrary code execution (CVSS 9.8)
- **GHSA-6757-jp84-gxfx**: Improper Input Validation (CVSS 9.8)

> **Mitigation**: Codebase uses `yaml.safe_load()` (line 35 in `template_engine.py`). **Do not use `yaml.load()`**. Update to >=6.0.4.

### jinja2 (20 vulnerabilities) — **UNUSED**
- **GHSA-462w-v97r-4m45**: Sandbox escape via string formatting (CVSS 9.1)
- **GHSA-gmj6-6f8f-6699**: Sandbox breakout through malicious filenames (CVSS 8.8)
- **GHSA-q2x7-8rv6-6q7h**: Sandbox breakout through indirect reference (CVSS 8.8)

> **Action**: Remove from requirements.txt immediately.

### requests (16 vulnerabilities) — **UNUSED**
- **GHSA-9hjg-9r4m-mvj7**: .netrc credentials leak via malicious URLs (CVSS 5.9)
- **GHSA-j8r2-6x86-q33q**: Proxy-Authorization header leak (CVSS 6.8)
- **GHSA-x84v-xcm2-53pg**: Insufficiently protected credentials (CVSS 7.5)

> **Action**: Remove from requirements.txt immediately.

---

## Python Version Compatibility

All latest package versions are compatible with **Python 3.12** (current venv):
- Minimum required: **Python 3.11** (for fastapi 0.165.0, python-multipart 0.0.34, rapidfuzz 3.14.6)
- Current: **Python 3.12** ✅

---

## Recommended Actions

### Immediate (Security)
1. **Remove unused packages** from `requirements.txt`:
   ```txt
   # REMOVE THESE LINES:
   httpx>=0.27.0
   jinja2>=3.1.3
   requests>=2.31.0
   ```

2. **Update lower bounds** to recent secure versions:
   ```txt
   fastapi>=0.115.0
   uvicorn>=0.30.0
   pydantic>=2.10.0
   python-multipart>=0.0.34
   openpyxl>=3.1.5
   pyyaml>=6.0.4
   rapidfuzz>=3.14.6
   ```

3. **Add missing optional dependency** if PDF parsing needed:
   ```txt
   pdfplumber>=0.11.0  # for PDF support in normalizer.py
   ```

### Short-term
- Pin exact versions in production (`==X.Y.Z`) after testing
- Add `pip-audit` or `safety` to CI pipeline
- Monitor OSV/GHSA for new advisories

### Code Verification
- ✅ `pyyaml`: Uses `yaml.safe_load()` correctly
- ✅ `python-multipart`: Used only via FastAPI's built-in form parsing (size limits recommended)
- ✅ No `eval()`, `exec()`, or unsafe deserialization patterns found

---

## Verification Sources

- PyPI JSON API: `https://pypi.org/pypi/<package>/json`
- OSV (Open Source Vulnerabilities): `https://api.osv.dev/v1/query`
- Codebase import scan: `grep -r "import\|from" --include="*.py" dahnay_logistics/ tests/ app.py main.py api/`

---

*Report generated by automated dependency audit. Manual review recommended before production deployment.*