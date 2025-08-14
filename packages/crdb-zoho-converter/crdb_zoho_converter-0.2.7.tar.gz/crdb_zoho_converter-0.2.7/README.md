## CRDB → ZOHO Books Converter

Converts CRDB bank statements (XLS/XLSX) into the CSV format that can be imported into Zoho Books.

### Why this tool exists

**CRDB Bank Tanzania** is one of Tanzania's leading commercial banks, but unfortunately they don't provide APIs or direct integration interfaces for accounting software. However, they do allow customers to download bank statements from their web portal in XLS (Excel) format.

This script bridges that gap by converting these downloaded XLS files into a CSV format that can be directly imported into **Zoho Books** as bank statements, eliminating the need for manual data entry and ensuring accurate financial records.

### Contents
- `convert_crdb_to_zoho.py`: CLI script for conversion
- `_inspect_xls.py`: small helper script to analyze new/changed XLS layouts
- `files/`: workspace for input/output files (ignored via `.gitignore`)

### Requirements
- Python 3.11 (or compatible)
- Windows PowerShell (examples below use PowerShell paths)
- Linux/macOS shells are supported (examples provided)
 - Dependencies: see `requirements.txt` (includes `pandas`, `xlrd`, `openpyxl`)

### Quick start
Linux/macOS (bash/zsh):
```bash
git clone https://github.com/lkasdorf/CRDB_con_2025.git && cd CRDB_con_2025
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Batch conversion (recommended)
crdb-convert --source source --dest converted

# Single file
crdb-convert -i source/statement.xlsx -o converted/statement.csv

# With mapping and per-row diagnostics
crdb-convert --source source --dest converted --map-file mapping.json --report-dir converted/reports
```

Windows (PowerShell):
```powershell
git clone https://github.com/lkasdorf/CRDB_con_2025.git
Set-Location .\CRDB_con_2025
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .

# Batch conversion (recommended)
crdb-convert --source source --dest converted

# Single file
crdb-convert -i source\statement.xlsx -o converted\statement.csv

# With mapping and per-row diagnostics
crdb-convert --source source --dest converted --map-file mapping.json --report-dir converted\reports
```

Alternative (global install via pipx):
```bash
pip install pipx && pipx ensurepath
pipx install .
crdb-convert --help
```

## 🗑️ Uninstallation & Cleanup

**💡 Quick Cleanup:** Use the provided cleanup scripts for complete removal:
- **Windows:** `cleanup-windows.ps1` (run as Administrator)
- **Linux/macOS:** `cleanup-linux.sh` (make executable with `chmod +x`)

### Remove pipx Installation (Linux/macOS/Windows)
```bash
# Remove the package
pipx uninstall crdb-zoho-converter

# Remove pipx completely (optional)
pip uninstall pipx
```

### Remove Virtual Environment Installation
```bash
# Simply delete the virtual environment directory
rm -rf .venv/                    # Linux/macOS
Remove-Item -Recurse -Force .venv  # Windows PowerShell
```

### Remove Windows EXE Files
If you built standalone executables with PyInstaller:
```powershell
# Remove the dist/ directory containing EXEs
Remove-Item -Recurse -Force dist\

# Remove build artifacts
Remove-Item -Recurse -Force build\
Remove-Item -Recurse -Force *.spec
```

### Remove Windows Inno Setup Installer
If you installed via the professional installer:
```powershell
# Method 1: Control Panel (recommended)
# Go to Control Panel → Programs → Programs and Features
# Find "CRDB Zoho Converter" and click "Uninstall"

# Method 2: Command line (requires admin)
# The installer should have created an uninstaller at:
# C:\Program Files\CRDB Zoho Converter\unins000.exe
# Run: "C:\Program Files\CRDB Zoho Converter\unins000.exe"

# Method 3: Manual cleanup (if uninstaller fails)
# Remove from PATH manually:
# - User PATH: Edit Environment Variables → User variables → Path
# - System PATH: Edit Environment Variables → System variables → Path
# Remove: C:\Program Files\CRDB Zoho Converter

# Remove installation directory
Remove-Item -Recurse -Force "C:\Program Files\CRDB Zoho Converter"
```

### Remove from Windows PATH
If you manually added to PATH:
```powershell
# Check current PATH
$env:PATH -split ';'

# Remove specific directory from PATH
$oldPath = [Environment]::GetEnvironmentVariable("Path", "User")
$newPath = ($oldPath -split ';' | Where-Object { $_ -notlike "*CRDB*" }) -join ';'
[Environment]::SetEnvironmentVariable("Path", $newPath, "User")

# For system PATH (requires admin):
$oldPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$newPath = ($oldPath -split ';' | Where-Object { $_ -notlike "*CRDB*" }) -join ';'
[Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
```

### Complete Cleanup Script (Windows PowerShell)
```powershell
# Run as Administrator for complete cleanup
Write-Host "Cleaning up CRDB Zoho Converter..." -ForegroundColor Yellow

# Remove from PATH
$paths = @("User", "Machine")
foreach ($scope in $paths) {
    try {
        $oldPath = [Environment]::GetEnvironmentVariable("Path", $scope)
        $newPath = ($oldPath -split ';' | Where-Object { $_ -notlike "*CRDB*" -and $_ -notlike "*crdb*" }) -join ';'
        [Environment]::SetEnvironmentVariable("Path", $newPath, $scope)
        Write-Host "Cleaned PATH for $scope scope" -ForegroundColor Green
    } catch {
        Write-Host "Could not clean PATH for $scope scope (may require admin)" -ForegroundColor Red
    }
}

# Remove installation directory
$installPath = "C:\Program Files\CRDB Zoho Converter"
if (Test-Path $installPath) {
    Remove-Item -Recurse -Force $installPath
    Write-Host "Removed installation directory" -ForegroundColor Green
}

# Remove user-specific files
$userBin = "$env:USERPROFILE\bin\crdb-convert.exe"
if (Test-Path $userBin) {
    Remove-Item -Force $userBin
    Write-Host "Removed user bin file" -ForegroundColor Green
}

# Remove build artifacts
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
    Write-Host "Removed build artifacts" -ForegroundColor Green
}

Write-Host "Cleanup complete!" -ForegroundColor Green
```

### Complete Cleanup Scripts

**Windows PowerShell (Recommended):**
```powershell
# Run the comprehensive cleanup script
.\cleanup-windows.ps1

# Or with options:
.\cleanup-windows.ps1 -Force -Verbose
```

**Linux/macOS:**
```bash
# Make executable and run
chmod +x cleanup-linux.sh
./cleanup-linux.sh

# Or with options:
./cleanup-linux.sh --force --verbose
```

**Manual Cleanup (if scripts fail):**
```bash
#!/bin/bash
echo "Cleaning up CRDB Zoho Converter..."

# Remove pipx installation
if command -v pipx &> /dev/null; then
    pipx uninstall crdb-zoho-converter 2>/dev/null
    echo "Removed pipx installation"
fi

# Remove virtual environment
if [ -d ".venv" ]; then
    rm -rf .venv
    echo "Removed virtual environment"
fi

# Remove build artifacts
if [ -d "dist" ]; then
    rm -rf dist
    echo "Removed build artifacts"
fi

if [ -d "build" ]; then
    rm -rf build
    echo "Removed build directory"
fi

# Remove spec files
rm -f *.spec
echo "Removed spec files"

echo "Cleanup complete!"
```

### Setup (recommended with virtual environment)
Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**⚠️ Windows PowerShell Execution Policy Issue:**
If you encounter the error "cannot be loaded because running scripts is disabled on this system", run this command first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Alternative (if Execution Policy can't be changed):**
Use the virtual environment directly without activation:
```powershell
.\.venv\Scripts\python.exe convert_crdb_to_zoho.py
```

Linux/macOS (bash/zsh):
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

### Usage
Windows (PowerShell):
1) Place the CRDB source file (e.g., `crdb_input.xls`) into `source/` for batch mode, or `files/` for single-file mode.
2) Batch conversion (recommended):
```powershell
.\.venv\Scripts\python.exe convert_crdb_to_zoho.py --source source --dest converted
```
3) Force re-run even if targets exist:
```powershell
.\.venv\Scripts\python.exe convert_crdb_to_zoho.py --source source --dest converted --force
```
4) Single-file conversion (optional):
```powershell
.\.venv\Scripts\python.exe convert_crdb_to_zoho.py -i files\crdb_input.xls -o converted\crdb_input.csv
```

**💡 Pro Tip:** For batch processing of multiple XLS files from any directory:
```powershell
.\.venv\Scripts\python.exe convert_crdb_to_zoho.py --source "C:\path\to\xls\files" --dest "C:\path\to\output"
```

Linux/macOS (bash/zsh):
1) Place the CRDB source file (e.g., `crdb_input.xls`) into `source/` for batch mode, or `files/` for single-file mode.
2) Batch conversion (recommended):
```bash
python3 convert_crdb_to_zoho.py --source source --dest converted
```
3) Force re-run even if targets exist:
```bash
python3 convert_crdb_to_zoho.py --source source --dest converted --force
```
4) Single-file conversion (optional):
```bash
python3 convert_crdb_to_zoho.py -i files/crdb_input.xls -o converted/crdb_input.csv
```
5) Import the generated CSV(s) from `converted/` into Zoho Books.

Inspector (optional):
```bash
crdb-inspect --help
crdb-inspect --input files/crdb_input.xls --engine auto --sheet 0 --max-scan-rows 500
```

### Installation (local/standalone)

Option A: Install into a virtual environment (recommended)
- Windows (PowerShell): see "Setup" above. Then:
```powershell
pip install -e .
```
- Linux/macOS:
```bash
pip install -e .
```
After this, the commands `crdb-convert` and `crdb-inspect` are available on your PATH.

Option B: System-wide via pipx (clean, isolated)
- Prerequisite: install `pipx` (`pip install pipx` and then `pipx ensurepath`).
```bash
pipx install .
```
You can now use the tools globally: `crdb-convert --help`.

Option C: Run directly with Python (no installation)
```bash
python3 convert_crdb_to_zoho.py --source source --dest converted
```

Optional: Build standalone binaries (no Python required on target system)
- Install PyInstaller and build binaries:
```bash
pip install pyinstaller
pyinstaller --onefile --name crdb-convert convert_crdb_to_zoho.py
pyinstaller --onefile --name crdb-inspect _inspect_xls.py
```
The generated binaries are in `dist/` (`crdb-convert`, `crdb-inspect`). They are OS/arch specific.

**Windows EXE Build (PowerShell):**
```powershell
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller --onefile --name crdb-convert convert_crdb_to_zoho.py

# The EXE file will be created in dist/crdb-convert.exe
```

**Make Windows EXE available everywhere (add to PATH):**

**Option 1: User-specific PATH (recommended)**
```powershell
# Create a bin directory in your user profile
if (-Not (Test-Path "$env:USERPROFILE\bin")) { 
    New-Item -ItemType Directory "$env:USERPROFILE\bin" | Out-Null 
}

# Copy the EXE to your bin directory
Copy-Item "dist\crdb-convert.exe" "$env:USERPROFILE\bin\"

# Add to PATH permanently
setx PATH "$env:PATH;$env:USERPROFILE\bin"

# Restart PowerShell or run this to update current session
$env:PATH = "$env:PATH;$env:USERPROFILE\bin"

# Test it
crdb-convert.exe --help
```

**Option 2: System-wide PATH (requires admin)**
```powershell
# Copy to Windows System32 (requires admin rights)
Copy-Item "dist\crdb-convert.exe" "C:\Windows\System32\"

# Now available everywhere without PATH changes
crdb-convert.exe --help
```

**Option 3: Custom directory and add to PATH**
```powershell
# Create a custom directory
New-Item -ItemType Directory "C:\Tools\crdb-converter" -Force

# Copy the EXE
Copy-Item "dist\crdb-convert.exe" "C:\Tools\crdb-converter\"

# Add to system PATH (requires admin)
setx PATH "$env:PATH;C:\Tools\crdb-converter" /M

# Test it
crdb-convert.exe --help
```

**Option 4: Professional Windows Installer (Recommended for Distribution)**
```powershell
# Build the installer (requires Inno Setup)
cd installer
.\build-installer.ps1

# The installer will be created in dist/crdb-converter-setup-0.2.7.exe
# It automatically handles PATH modification and creates Start Menu shortcuts
```

After installing/building:
- Show help: `crdb-convert --help`
- See examples under "Usage" and "CLI options".

### Install from PyPI (recommended for end users)
Using pipx (global, isolated; auto PATH integration):
```bash
pip install pipx && pipx ensurepath
pipx install crdb-zoho-converter
crdb-convert --help
```

Alternative with pip --user:
```bash
pip install --user crdb-zoho-converter
# Ensure ~/.local/bin (Linux/macOS) or the Windows user Scripts folder is on PATH
```

### Download prebuilt binaries (GitHub Releases)
Linux/macOS (download and add to PATH):
```bash
curl -L -o /usr/local/bin/crdb-convert \
  https://github.com/lkasdorf/CRDB_con_2025/releases/download/vX.Y.Z/crdb-convert
chmod +x /usr/local/bin/crdb-convert
crdb-convert --help

# Optional inspector tool
sudo curl -L -o /usr/local/bin/crdb-inspect \
  https://github.com/lkasdorf/CRDB_con_2025/releases/download/vX.Y.Z/crdb-inspect
sudo chmod +x /usr/local/bin/crdb-inspect
```

Windows (PowerShell):
```powershell
# Create bin directory in user profile
if (-Not (Test-Path "$env:USERPROFILE\bin")) { 
    New-Item -ItemType Directory "$env:USERPROFILE\bin" | Out-Null 
}

# Download the EXE from GitHub Releases
Invoke-WebRequest -Uri https://github.com/lkasdorf/CRDB_con_2025/releases/download/vX.Y.Z/crdb-convert.exe -OutFile "$env:USERPROFILE\bin\crdb-convert.exe"

# Make it available on PATH for future sessions
setx PATH "$env:PATH;$env:USERPROFILE\bin"

# Test it
crdb-convert.exe --help

# Optional inspector tool
Invoke-WebRequest -Uri https://github.com/lkasdorf/CRDB_con_2025/releases/download/vX.Y.Z/crdb-inspect.exe -OutFile "$env:USERPROFILE\bin\crdb-inspect.exe"
```

**💡 Pro Tip:** Replace `vX.Y.Z` with the actual release version (e.g., `v0.2.6`) from the GitHub Releases page.

### GitHub Release Assets
Each release includes:
- **Source code** (`.tar.gz`, `.zip`)
- **Windows EXE** (`crdb-convert.exe`) - standalone, no Python required
- **Linux/macOS binaries** (`crdb-convert`) - standalone, no Python required
- **Release notes** with changelog and installation instructions

**Latest Release:** [v0.2.7](https://github.com/lkasdorf/CRDB_con_2025/releases/latest)

### Professional Windows Installer
For Windows users who prefer a traditional installer:
- **Automatic PATH modification** (system-wide or user-specific)
- **Start Menu shortcuts** and optional desktop icons
- **Uninstall capability** via Control Panel
- **Multi-language support** (English/German)

**Build the installer:**
```powershell
cd installer
.\build-installer.ps1
```

**Download:** [crdb-converter-setup-0.2.7.exe](https://github.com/lkasdorf/CRDB_con_2025/releases/latest)

### Add to PATH (so you can run `crdb-convert` from anywhere)

- Virtual environment (recommended): Activating the venv automatically adds its `Scripts` (Windows) or `bin` (Linux/macOS) folder to PATH.
  - Windows (PowerShell): `\.venv\Scripts\Activate.ps1`
  - Linux/macOS (bash/zsh): `source .venv/bin/activate`

- pipx (global, isolated): Run `pipx ensurepath` once and restart your shell.
  - Verify: `which crdb-convert` (Linux/macOS) or `where crdb-convert` (Windows)

- pip --user (if you use it): Ensure the user bin directory is on PATH.
  - Linux/macOS: `~/.local/bin` (add to `~/.bashrc`/`~/.zshrc` if needed)
    ```bash
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
    ```
  - Windows: Find your user base with `py -m site --user-base` or `python -m site --user-base`.
    Add its `Scripts` subfolder to PATH (e.g., `%USERPROFILE%\AppData\Roaming\Python\Python311\Scripts`).

- PyInstaller binaries: Put the files from `dist/` into a directory already on PATH, or extend PATH.
  - Linux/macOS (temporary for current session):
    ```bash
    export PATH="$(pwd)/dist:$PATH"
    ```
  - Linux/macOS (permanent): add the same line to `~/.bashrc`/`~/.zshrc`.
  - Windows (PowerShell, permanent): Control Panel → Environment Variables → PATH → add `...\dist`. Or (with care):
    ```powershell
    setx PATH "$env:PATH;$(Get-Location)\dist"
    ```

### CLI options
All flags are optional; defaults are chosen to work out-of-the-box with typical CRDB exports.

- `-i, --input PATH`: Single-file input (XLS/XLSX).
- `-o, --output PATH`: Output CSV path in single-file mode. Default: `<dest>/<input_stem>.csv`.
- `--source PATH`: Source directory for batch mode. Default: `source/`.
- `--dest PATH`: Output directory for batch mode. Default: `converted/`.
- `--log PATH`: Path to log file. Default: `<dest>/conversion.log`.
- `--force`: Overwrite existing target CSVs.

- `--strict`: Fail on parsing/validation warnings.
- `--dry-run`: Validate and report only; do not write CSV.
- `--delimiter ";"`: CSV delimiter (default `;`).
- `--max-scan-rows 500`: Max rows to scan while searching for the header.
- `--engine auto|xlrd|openpyxl`: Excel reader engine (default `auto`).
- `--trace`: Enable detailed DEBUG tracing in logs.
- `--trace-max-rows 20`: Number of rows to trace.
- `--sheet NAME|INDEX`: Select sheet by name or 0-based index.
- `--header-row N`: Override detected header row (1-based).

Mapping (column selection):
- `--map-file PATH`: JSON mapping configuration (see below).
- `--map-posting STR`: Override mapping for posting date column.
- `--map-details STR`: Override mapping for details/narration column.
- `--map-debit STR`: Override mapping for debit column.
- `--map-credit STR`: Override mapping for credit column.

Diagnostics reports:
- `--report PATH`: Per-row diagnostics CSV in single-file mode.
- `--report-dir PATH`: Directory for per-row diagnostics CSVs in batch mode (filename: `<stem>.report.csv`).

Notes:
- Supports `.xls` and `.xlsx`. For `.xlsx`, `openpyxl` is used.
- The log file is written to `<dest>/conversion.log` by default.
- Logging:
  - `--json-logs` to emit structured logs (one JSON per line)
  - `--log-rotate-size` and `--log-rotate-backups` for rotating log files

Numbers/locale:
- `--decimal .|,` decimal separator
- `--thousands .|,|'|space` thousands separator (optional)
- `--currency CODE|SYMBOL` currency code/symbol to strip (optional)

CSV formatting:
- `--encoding` output file encoding (default utf-8)
- `--quotechar` CSV quote character (default ")
- `--no-header` do not write CSV header row

Redaction:
- `--redact` masks sensitive fields in outputs (reports/logs/CSV)

Summary:
- `--summary PATH|DIR` write a JSON summary file (single-file) or to a directory (batch)

### Target format (CSV)
Semicolon-separated (;) with this header:
```
Date;Withdrawals;Deposits;Payee;Description;Reference Number
```

Notes:
- Dates are output as `YYYY-MM-DD`.
- Amounts are decimals with a dot (e.g., `212.40`).
- `Payee` remains empty, `Description` defaults to `Transfer`, `Reference Number` contains the CRDB details/narration.

### Mapping configuration
Mapping kann die Auswahl der Eingabespalten steuern. Beispiel `mapping.json`:
```json
{
  "posting_date": ["Posting Date", "Transaction Date"],
  "details": ["Details", "Narration", "Description"],
  "debit": ["Debit", "Withdrawal"],
  "credit": ["Credit", "Deposit"]
}
```

Anmerkungen:
- Werte können String oder Liste sein. Die Suche vergleicht case-insensitive, zuerst exakt, dann als Teilstring. Fallback-Heuristik bleibt aktiv.
- CLI-Overrides (`--map-*`) haben Vorrang vor der Datei.

### Diagnostics und Validierung
Der Konverter sammelt Validierungs- und Parsing-Warnungen und protokolliert Beispiele. Bei `--strict` wird mit Fehler abgebrochen.

Mögliche Issues je Zeile (wichtig für den Report):
- `date_unparsed`: Datum konnte nicht geparst werden.
- `debit_unparsed`, `credit_unparsed`: Beträge nicht interpretierbar, obwohl Ziffern vorhanden.
- `both_amounts`: Debit und Credit gleichzeitig > 0.
- `negative_debit`, `negative_credit`: Negative Beträge erkannt.
- `date_missing_with_amount`: Betrag vorhanden, aber Datum leer.

Per-Row-Diagnose kann optional als CSV erzeugt werden (`--report`/`--report-dir`).

### Helper script (optional)
Shows header candidate(s) and sample rows from the XLS file – useful if the CRDB layout changes:
```powershell
.\.venv\Scripts\python.exe _inspect_xls.py
```
```bash
python3 _inspect_xls.py
```

### Versioning
Semantic Versioning (MAJOR.MINOR.PATCH). Update the version in `pyproject.toml` under `[project].version`.

Examples:
- Stable release: `0.2.0` → `0.2.1`
- Next minor: `0.2.1` → `0.3.0`
- Development pre-release (editable installs and packaging will expose this): `0.3.0.dev1`, `0.3.0a1`, `0.3.0b1`.

Check installed version:
```bash
crdb-convert --version
```

Release checklist:
- Bump `[project].version` in `pyproject.toml`
- Commit and tag (optional): `git tag vX.Y.Z && git push --tags`
- Reinstall if using editable: `pip install -e .`

Repository notes:
- The `files/` directory is added to `.gitignore` and not versioned.
- The `source/` and `converted/` directories are versioned but kept empty in a fresh clone via `.gitkeep` files. Output CSVs and logs will appear in `converted/` after running the converter.

### License
See `LICENSE`.
