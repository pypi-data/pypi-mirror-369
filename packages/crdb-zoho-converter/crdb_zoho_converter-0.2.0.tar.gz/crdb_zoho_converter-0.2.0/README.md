## CRDB → ZOHO Books Converter

Converts CRDB bank statements (XLS/XLSX) into the CSV format that can be imported into Zoho Books.

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

### Setup (recommended with virtual environment)
Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
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
if (-Not (Test-Path "$env:USERPROFILE\bin")) { New-Item -ItemType Directory $env:USERPROFILE\bin | Out-Null }
Invoke-WebRequest -Uri https://github.com/lkasdorf/CRDB_con_2025/releases/download/vX.Y.Z/crdb-convert.exe -OutFile $env:USERPROFILE\bin\crdb-convert.exe
# Make it available on PATH for future sessions:
setx PATH "$env:PATH;$env:USERPROFILE\bin"
crdb-convert.exe --help

# Optional inspector tool
Invoke-WebRequest -Uri https://github.com/lkasdorf/CRDB_con_2025/releases/download/vX.Y.Z/crdb-inspect.exe -OutFile $env:USERPROFILE\bin\crdb-inspect.exe
```

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
