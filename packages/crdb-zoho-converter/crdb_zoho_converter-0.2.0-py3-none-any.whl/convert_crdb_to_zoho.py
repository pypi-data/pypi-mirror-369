import argparse
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os
import sys
import pandas as pd
from typing import List, Dict, Tuple, Any
try:
    from importlib.metadata import version as _pkg_version  # Python 3.8+
except Exception:  # pragma: no cover
    _pkg_version = None  # type: ignore


class ConversionError(Exception):
    """Base class for conversion-related errors."""


class ReadFileError(ConversionError):
    pass


class HeaderNotFoundError(ConversionError):
    pass


class MissingColumnsError(ConversionError):
    def __init__(self, message: str, available: List[str] | None = None) -> None:
        super().__init__(message)
        self.available = available or []


def get_package_version() -> str:
    if _pkg_version is None:
        return "unknown"
    try:
        return _pkg_version("crdb-zoho-converter")
    except Exception:
        return "unknown"


def find_transaction_header_index(raw_df: pd.DataFrame, max_scan_rows: int = 500) -> int | None:
    max_scan_rows = min(max_scan_rows, len(raw_df))
    for i in range(max_scan_rows):
        row_values = raw_df.iloc[i].fillna("").astype(str).str.strip()
        lowered = [v.lower() for v in row_values]

        def contains(token: str) -> bool:
            return any(token in cell for cell in lowered)

        if contains("posting") and contains("date") and contains("details") and contains("value") and contains("debit") and contains("credit"):
            return i
        if contains("posting date") and contains("details") and contains("value date") and contains("debit") and contains("credit"):
            return i
    return None


def normalize_header(cells: List[str]) -> List[str]:
    normalized = []
    for c in cells:
        name = (c or "").strip()
        name = " ".join(name.split())
        normalized.append(name)
    return normalized


def parse_number(
    value: str,
    *,
    decimal: str = ".",
    thousands: str | None = None,
    currency: str | None = None,
    allow_parentheses_negative: bool = True,
) -> float:
    if value is None:
        return 0.0
    s = str(value).strip()
    if not s:
        return 0.0
    # Normalize unicode minus and NBSP
    s = s.replace("\xa0", " ")
    s = s.replace("−", "-")  # Unicode minus

    # Detect parentheses negative
    is_negative = False
    if allow_parentheses_negative and s.startswith("(") and s.endswith(")"):
        is_negative = True
        s = s[1:-1].strip()

    # Strip currency codes/symbols if provided or common ones
    currency_tokens = [
        "USD",
        "$",
        "TZS",
        "€",
        "EUR",
        "£",
        "GBP",
    ]
    if currency:
        currency_tokens.append(currency)
    for tok in currency_tokens:
        s = s.replace(tok, "")

    # Remove spaces
    s = s.replace(" ", "")

    # Thousands/decimal handling
    if thousands:
        s = s.replace(thousands, "")
    else:
        # Remove common thousands separators
        for sep in [",", ".", "'", "\u202f", "\u00a0"]:
            # Do not remove if it's the decimal separator
            if sep != decimal:
                s = s.replace(sep, "")

    if decimal != ".":
        s = s.replace(decimal, ".")

    try:
        num = float(s)
        return -num if is_negative else num
    except ValueError:
        return 0.0


def parse_date_str(date_str: str) -> str:
    if not isinstance(date_str, str):
        date_str = str(date_str)
    date_str = date_str.strip()
    if not date_str:
        return ""
    dt = pd.to_datetime(date_str, dayfirst=True, errors="coerce")
    if pd.isna(dt):
        return ""
    return dt.strftime("%Y-%m-%d")


def _normalize_mapping_value(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(v) for v in value]
    return [str(value)]


def _select_column_with_mapping(columns: List[str], mapping_values: List[str], fallback_picker) -> str:
    # Try exact case-insensitive match first
    lowered = {c.lower(): c for c in columns}
    for mv in mapping_values:
        key = mv.strip().lower()
        if key in lowered:
            return lowered[key]
    # Try containment
    for mv in mapping_values:
        key = mv.strip().lower()
        for c in columns:
            if key and key in c.lower():
                return c
    # Fallback heuristic
    return fallback_picker()


def _read_excel_with_fallback(input_path: Path, engine_choice: str, sheet: Any = None) -> pd.DataFrame:
    suffix = input_path.suffix.lower()
    if engine_choice == "xlrd":
        try:
            return pd.read_excel(input_path, engine="xlrd", header=None, dtype=str, sheet_name=sheet)
        except Exception as exc:  # noqa: BLE001
            raise ReadFileError(f"Failed reading {input_path} with xlrd: {exc}")
    if engine_choice == "openpyxl":
        try:
            return pd.read_excel(input_path, engine="openpyxl", header=None, dtype=str, sheet_name=sheet)
        except ImportError as exc:
            raise ReadFileError(
                f"openpyxl is required to read {input_path}. Install with 'pip install openpyxl'. ({exc})"
            )
        except Exception as exc:  # noqa: BLE001
            raise ReadFileError(f"Failed reading {input_path} with openpyxl: {exc}")

    # auto engine selection
    if suffix in {".xlsx", ".xlsm", ".xltx", ".xltm"}:
        try:
            return pd.read_excel(input_path, engine="openpyxl", header=None, dtype=str, sheet_name=sheet)
        except ImportError as exc:
            raise ReadFileError(
                f"openpyxl is required to read {input_path}. Install with 'pip install openpyxl'. ({exc})"
            )
        except Exception as exc_openpyxl:  # noqa: BLE001
            logging.warning("openpyxl failed for %s: %s. Trying engine=None as fallback.", input_path, exc_openpyxl)
            try:
                return pd.read_excel(input_path, engine=None, header=None, dtype=str, sheet_name=sheet)
            except Exception as exc_none:  # noqa: BLE001
                raise ReadFileError(f"Failed reading {input_path} with auto engine: {exc_none}")
    # legacy .xls
    try:
        return pd.read_excel(input_path, engine="xlrd", header=None, dtype=str, sheet_name=sheet)
    except Exception as exc_xlrd:  # noqa: BLE001
        logging.warning("xlrd failed for %s: %s. Trying engine=None as fallback.", input_path, exc_xlrd)
        try:
            return pd.read_excel(input_path, engine=None, header=None, dtype=str, sheet_name=sheet)
        except Exception as exc_none:  # noqa: BLE001
            raise ReadFileError(f"Failed reading {input_path} with auto engine: {exc_none}")


def convert(
    input_path: Path,
    output_path: Path,
    *,
    strict: bool = False,
    delimiter: str = ";",
    max_scan_rows: int = 500,
    engine: str = "auto",
    dry_run: bool = False,
    log_sample_limit: int = 5,
    mapping: Dict[str, Any] | None = None,
    trace: bool = False,
    trace_max_rows: int = 20,
    report_path: Path | None = None,
    sheet: Any = None,
    header_row: int | None = None,
    decimal: str = ".",
    thousands: str | None = None,
    currency: str | None = None,
    csv_encoding: str = "utf-8",
    csv_quotechar: str = '"',
    csv_no_header: bool = False,
    redact: bool = False,
    summary_path: Path | None = None,
) -> Tuple[int, int, Dict[str, int]]:
    raw = _read_excel_with_fallback(input_path, engine_choice=engine, sheet=sheet)

    if header_row is not None:
        # Treat CLI as 1-based for convenience
        header_idx = max(0, header_row - 1)
    else:
        header_idx = find_transaction_header_index(raw, max_scan_rows=max_scan_rows)
    if header_idx is None:
        raise HeaderNotFoundError("Could not locate the transactions table header row.")

    headers = normalize_header(raw.iloc[header_idx].tolist())
    data = raw.iloc[header_idx + 1 :].copy()
    if data.shape[0] == 0:
        raise ConversionError("No transaction rows found below detected header.")
    if len(data.columns) > len(headers):
        headers = headers + [f"extra_{j}" for j in range(len(data.columns) - len(headers))]
    data.columns = headers

    def pick(col_name: str) -> str:
        for c in data.columns:
            lc = c.lower()
            if col_name == "posting_date" and "posting" in lc and "date" in lc:
                return c
            if col_name == "details" and ("details" in lc or "narration" in lc or "description" in lc):
                return c
            if col_name == "value_date" and "value" in lc and "date" in lc:
                return c
            if col_name == "debit" and "debit" in lc:
                return c
            if col_name == "credit" and "credit" in lc:
                return c
            if col_name == "book_balance" and "book" in lc and "balance" in lc:
                return c
        return ""

    mapping = mapping or {}
    mapping_posting = _normalize_mapping_value(mapping.get("posting_date"))
    mapping_details = _normalize_mapping_value(mapping.get("details"))
    mapping_debit = _normalize_mapping_value(mapping.get("debit"))
    mapping_credit = _normalize_mapping_value(mapping.get("credit"))

    cols_list = list(data.columns)
    col_posting = _select_column_with_mapping(cols_list, mapping_posting, lambda: pick("posting_date"))
    col_details = _select_column_with_mapping(cols_list, mapping_details, lambda: pick("details"))
    col_debit = _select_column_with_mapping(cols_list, mapping_debit, lambda: pick("debit"))
    col_credit = _select_column_with_mapping(cols_list, mapping_credit, lambda: pick("credit"))

    if not all([col_posting, col_details, col_debit, col_credit]):
        available = list(data.columns.astype(str))
        raise MissingColumnsError(
            (
                "Missing required columns. "
                f"posting={col_posting!r} details={col_details!r} debit={col_debit!r} credit={col_credit!r}. "
                f"Available columns: {available}"
            ),
            available=available,
        )

    issues: Dict[str, int] = {
        "date_unparsed": 0,
        "debit_unparsed": 0,
        "credit_unparsed": 0,
        "both_amounts": 0,
        "negative_debit": 0,
        "negative_credit": 0,
        "date_missing_with_amount": 0,
    }
    samples: Dict[str, List[str]] = {k: [] for k in issues.keys()}

    dates: List[str] = []
    withdrawals: List[float] = []
    deposits: List[float] = []
    payees: List[str] = []
    descriptions: List[str] = []
    ref_numbers: List[str] = []

    posting_vals = data[col_posting].fillna("").astype(str).tolist()
    debit_vals = data[col_debit].fillna("").astype(str).tolist()
    credit_vals = data[col_credit].fillna("").astype(str).tolist()
    detail_vals = data[col_details].fillna("").astype(str).tolist()

    row_reports: List[Dict[str, Any]] = []
    for idx in range(len(data)):
        src_date = posting_vals[idx]
        src_debit = debit_vals[idx]
        src_credit = credit_vals[idx]
        src_detail = detail_vals[idx]

        parsed_date = parse_date_str(src_date)
        if src_date.strip() and parsed_date == "":
            issues["date_unparsed"] += 1
            if len(samples["date_unparsed"]) < log_sample_limit:
                samples["date_unparsed"].append(f"row {header_idx + 1 + 1 + idx}: '{src_date}'")

        parsed_debit = parse_number(
            src_debit,
            decimal=decimal,
            thousands=thousands,
            currency=currency,
            allow_parentheses_negative=True,
        )
        norm_debit = src_debit.replace("\xa0", " ").strip()
        has_digit_debit = any(ch.isdigit() for ch in norm_debit)
        if has_digit_debit and parsed_debit == 0.0 and norm_debit not in {"0", "0.0", "0.00"}:
            issues["debit_unparsed"] += 1
            if len(samples["debit_unparsed"]) < log_sample_limit:
                samples["debit_unparsed"].append(f"row {header_idx + 1 + 1 + idx}: '{src_debit}'")

        parsed_credit = parse_number(
            src_credit,
            decimal=decimal,
            thousands=thousands,
            currency=currency,
            allow_parentheses_negative=True,
        )
        norm_credit = src_credit.replace("\xa0", " ").strip()
        has_digit_credit = any(ch.isdigit() for ch in norm_credit)
        if has_digit_credit and parsed_credit == 0.0 and norm_credit not in {"0", "0.0", "0.00"}:
            issues["credit_unparsed"] += 1
            if len(samples["credit_unparsed"]) < log_sample_limit:
                samples["credit_unparsed"].append(f"row {header_idx + 1 + 1 + idx}: '{src_credit}'")

        # Extended validations
        flag_negative_debit = False
        flag_negative_credit = False
        flag_both_amounts = False
        flag_date_missing_with_amount = False

        if parsed_debit < 0:
            issues["negative_debit"] += 1
            flag_negative_debit = True
            if len(samples["negative_debit"]) < log_sample_limit:
                samples["negative_debit"].append(f"row {header_idx + 1 + 1 + idx}: '{src_debit}' -> {parsed_debit}")
        if parsed_credit < 0:
            issues["negative_credit"] += 1
            flag_negative_credit = True
            if len(samples["negative_credit"]) < log_sample_limit:
                samples["negative_credit"].append(f"row {header_idx + 1 + 1 + idx}: '{src_credit}' -> {parsed_credit}")
        if (parsed_debit > 0) and (parsed_credit > 0):
            issues["both_amounts"] += 1
            flag_both_amounts = True
            if len(samples["both_amounts"]) < log_sample_limit:
                samples["both_amounts"].append(
                    f"row {header_idx + 1 + 1 + idx}: debit='{src_debit}' credit='{src_credit}'"
                )
        if (parsed_debit > 0 or parsed_credit > 0) and parsed_date == "":
            issues["date_missing_with_amount"] += 1
            flag_date_missing_with_amount = True
            if len(samples["date_missing_with_amount"]) < log_sample_limit:
                samples["date_missing_with_amount"].append(
                    f"row {header_idx + 1 + 1 + idx}: date='{src_date}' debit='{src_debit}' credit='{src_credit}'"
                )

        dates.append(parsed_date)
        withdrawals.append(parsed_debit)
        deposits.append(parsed_credit)
        payees.append("")
        descriptions.append("Transfer")
        ref_numbers.append(src_detail)

        if trace and idx < trace_max_rows:
            logging.debug(
                "trace row=%s src_date=%r parsed_date=%r debit=%r->%s credit=%r->%s details=%r",
                header_idx + 2 + idx,
                src_date,
                parsed_date,
                src_debit,
                parsed_debit,
                src_credit,
                parsed_credit,
                src_detail,
            )

        # Build per-row report entry if any issue on this row
        row_issue_flags = {
            "date_unparsed": (src_date.strip() and parsed_date == ""),
            "debit_unparsed": (has_digit_debit and parsed_debit == 0.0 and norm_debit not in {"0", "0.0", "0.00"}),
            "credit_unparsed": (has_digit_credit and parsed_credit == 0.0 and norm_credit not in {"0", "0.0", "0.00"}),
            "negative_debit": flag_negative_debit,
            "negative_credit": flag_negative_credit,
            "both_amounts": flag_both_amounts,
            "date_missing_with_amount": flag_date_missing_with_amount,
        }
        if any(row_issue_flags.values()):
            report_row: Dict[str, Any] = {
                "row_number": header_idx + 2 + idx,
                "src_date": src_date,
                "src_debit": src_debit,
                "src_credit": src_credit,
                "src_details": src_detail,
                "parsed_date": parsed_date,
                "parsed_debit": parsed_debit,
                "parsed_credit": parsed_credit,
            }
            report_row.update(row_issue_flags)
            row_reports.append(report_row)

    df = pd.DataFrame({
        "Date": dates,
        "Withdrawals": withdrawals,
        "Deposits": deposits,
        "Payee": payees,
        "Description": descriptions,
        "Reference Number": ref_numbers,
    })

    before_filter_rows = len(df)
    df = df[(df["Date"] != "") & ((df["Withdrawals"] > 0) | (df["Deposits"] > 0) | (df["Reference Number"] != ""))]
    after_filter_rows = len(df)

    # Optionally write per-row report before enforcing strict
    total_warnings = sum(issues.values())
    if report_path is not None:
        try:
            if row_reports:
                report_df = pd.DataFrame(row_reports)
                report_path.parent.mkdir(parents=True, exist_ok=True)
                report_df.to_csv(report_path, sep=delimiter, index=False)
                logging.info("Wrote diagnostics report: %s (rows=%s)", report_path, len(report_df))
            else:
                logging.info("No diagnostics to report for %s", input_path)
        except Exception as exc:  # noqa: BLE001
            logging.error("Failed writing diagnostics report %s: %s", report_path, exc)

    # Log warnings summary
    if total_warnings:
        logging.warning(
            "Parsing warnings for %s: %s | samples: %s",
            input_path,
            issues,
            {k: v for k, v in samples.items() if v},
        )
        if strict:
            raise ConversionError(f"Strict mode: encountered parsing warnings: {issues}")

    if redact:
        # Mask Reference Number and Details-like fields in reports/logs
        def _mask(sval: str) -> str:
            sval = str(sval)
            if len(sval) <= 6:
                return "***"
            return sval[:3] + "***" + sval[-3:]
        df["Reference Number"] = df["Reference Number"].astype(str).map(_mask)

    if not dry_run:
        df.to_csv(
            output_path,
            sep=delimiter,
            index=False,
            encoding=csv_encoding,
            quotechar=csv_quotechar,
        )

    if summary_path is not None:
        try:
            summary = {
                "input": str(input_path),
                "output": str(output_path),
                "rows_in": before_filter_rows,
                "rows_out": after_filter_rows,
                "issues": issues,
            }
            summary_path.parent.mkdir(parents=True, exist_ok=True)
            with summary_path.open("w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
            logging.info("Wrote summary: %s", summary_path)
        except Exception as exc:  # noqa: BLE001
            logging.error("Failed to write summary %s: %s", summary_path, exc)

    return before_filter_rows, after_filter_rows, issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert CRDB XLS/XLSX statement(s) to Zoho Books CSV format")
    # Single-file mode (optional)
    parser.add_argument("-i", "--input", type=Path, help="Path to a single XLS file to convert")
    parser.add_argument("-o", "--output", type=Path, help="Output CSV path for single-file mode")
    parser.add_argument("--version", action="version", version=f"%(prog)s {get_package_version()}")
    # Batch mode
    parser.add_argument("--source", type=Path, default=Path("source"), help="Directory containing source .xls files")
    parser.add_argument("--dest", type=Path, default=Path("converted"), help="Directory to write converted .csv files")
    parser.add_argument("--log", type=Path, default=None, help="Path to log file (default: <dest>/conversion.log)")
    parser.add_argument("--force", action="store_true", help="Re-convert even if target file already exists")
    # Advanced options
    parser.add_argument("--strict", action="store_true", help="Fail if parsing warnings occur")
    parser.add_argument("--dry-run", action="store_true", help="Validate and report without writing CSV")
    parser.add_argument("--delimiter", default=";", help="CSV delimiter (default ';')")
    parser.add_argument("--max-scan-rows", type=int, default=500, help="Max rows to scan when searching for header")
    parser.add_argument("--engine", choices=["auto", "xlrd", "openpyxl"], default="auto", help="Excel reader engine")
    parser.add_argument("--trace", action="store_true", help="Enable detailed DEBUG tracing logs")
    parser.add_argument("--trace-max-rows", type=int, default=20, help="Max number of rows to trace at DEBUG level")
    # Mapping configuration
    parser.add_argument("--map-file", type=Path, default=None, help="Path to JSON mapping file for column names")
    parser.add_argument("--map-posting", type=str, default=None, help="Override mapping for posting date column")
    parser.add_argument("--map-details", type=str, default=None, help="Override mapping for details column")
    parser.add_argument("--map-debit", type=str, default=None, help="Override mapping for debit column")
    parser.add_argument("--map-credit", type=str, default=None, help="Override mapping for credit column")
    # Diagnostics report
    parser.add_argument("--report", type=Path, default=None, help="Per-row diagnostics CSV (single-file mode)")
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=None,
        help="Directory to write per-row diagnostics CSVs in batch mode (files named <stem>.report.csv)",
    )
    # Sheet and header overrides
    parser.add_argument("--sheet", help="Sheet name or 0-based index to read", default=None)
    parser.add_argument("--header-row", type=int, default=None, help="1-based header row index to override detection")
    # Number/Currency locale options
    parser.add_argument("--decimal", default=".", help="Decimal separator in numbers (default '.')")
    parser.add_argument("--thousands", default=None, help="Thousands separator in numbers (optional)")
    parser.add_argument("--currency", default=None, help="Currency code or symbol to strip from amounts (optional)")
    # CSV output formatting
    parser.add_argument("--encoding", dest="csv_encoding", default="utf-8", help="CSV file encoding (default utf-8)")
    parser.add_argument("--quotechar", dest="csv_quotechar", default='"', help='CSV quote character (default ")')
    parser.add_argument("--no-header", dest="csv_no_header", action="store_true", help="Write CSV without header row")
    # Redaction
    parser.add_argument("--redact", action="store_true", help="Mask sensitive fields in outputs (reports/logs/CSV)")
    # Summary
    parser.add_argument("--summary", type=Path, default=None, help="Write a JSON summary file for each conversion")
    # Config file and environment overrides
    parser.add_argument("--config", type=Path, default=None, help="Path to TOML or JSON config file for defaults")
    parser.add_argument("--json-logs", action="store_true", help="Emit logs as one-JSON-object-per-line")
    parser.add_argument("--log-rotate-size", type=int, default=0, help="Rotate log file at ~N bytes (0=disabled)")
    parser.add_argument("--log-rotate-backups", type=int, default=3, help="How many rotated log files to keep")

    args = parser.parse_args()

    # Load config file (TOML or JSON) and merge into args defaults
    cfg: Dict[str, Any] = {}
    if args.config and args.config.exists():
        try:
            if args.config.suffix.lower() in {".toml"}:
                try:
                    import tomllib  # Python 3.11+
                except Exception as exc:  # noqa: BLE001
                    raise RuntimeError(f"tomllib is required for TOML config: {exc}")
                with args.config.open("rb") as f:
                    cfg = tomllib.load(f)
            elif args.config.suffix.lower() in {".json"}:
                with args.config.open("r", encoding="utf-8") as f:
                    cfg = json.load(f)
            else:
                logging.warning("Unsupported config extension for %s; only .toml or .json supported", args.config)
        except Exception as exc:  # noqa: BLE001
            logging.error("Failed to read config %s: %s", args.config, exc)
            cfg = {}

    def cfg_get(name: str, default: Any) -> Any:
        return cfg.get(name, default)

    # Environment overrides (prefix CRDB_)
    env = os.environ
    def env_get(name: str, default: Any) -> Any:
        key = f"CRDB_{name.upper().replace('-', '_')}"
        return env.get(key, default)

    # Resolve logging settings early
    log_path = args.log if args.log else Path(cfg_get("log", args.dest / "conversion.log"))
    log_path = Path(env_get("log", str(log_path)))
    log_path.parent.mkdir(parents=True, exist_ok=True)

    level = logging.DEBUG if args.trace or env_get("trace", str(cfg_get("trace", "")).lower() in {"1", "true", "yes"}) else logging.INFO

    handlers: List[logging.Handler] = []
    if args.log_rotate_size and args.log_rotate_size > 0:
        handlers.append(RotatingFileHandler(log_path, maxBytes=args.log_rotate_size, backupCount=args.log_rotate_backups, encoding="utf-8"))
    else:
        handlers.append(logging.FileHandler(log_path, encoding="utf-8"))
    handlers.append(logging.StreamHandler(sys.stdout))

    if args.json_logs:
        class JsonFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:  # noqa: D401
                payload = {
                    "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
                    "level": record.levelname,
                    "message": record.getMessage(),
                    "name": record.name,
                }
                return json.dumps(payload, ensure_ascii=False)
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    for h in handlers:
        h.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers = []
    root.setLevel(level)
    for h in handlers:
        root.addHandler(h)

    # Load mapping config
    mapping: Dict[str, Any] = {}
    if args.map_file:
        try:
            with args.map_file.open("r", encoding="utf-8") as f:
                mapping = json.load(f)
            if not isinstance(mapping, dict):
                logging.warning("Mapping file %s did not contain a JSON object. Ignoring.", args.map_file)
                mapping = {}
        except Exception as exc:  # noqa: BLE001
            logging.error("Failed to read mapping file %s: %s. Ignoring.", args.map_file, exc)
            mapping = {}
    # CLI overrides take precedence
    if args.map_posting:
        mapping["posting_date"] = args.map_posting
    if args.map_details:
        mapping["details"] = args.map_details
    if args.map_debit:
        mapping["debit"] = args.map_debit
    if args.map_credit:
        mapping["credit"] = args.map_credit

    # Single-file mode if input is provided
    if args.input:
        output = args.output if args.output else (args.dest / f"{args.input.stem}.csv")
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists() and not args.force:
            logging.info("Skip (exists): %s -> %s", args.input, output)
            return
        try:
            before, after, issues = convert(
                args.input,
                output,
                strict=args.strict,
                delimiter=args.delimiter,
                max_scan_rows=args.max_scan_rows,
                engine=args.engine,
                dry_run=args.dry_run,
                mapping=mapping,
                trace=args.trace,
                trace_max_rows=args.trace_max_rows,
                report_path=(args.report if args.report else (args.report_dir / f"{args.input.stem}.report.csv")) if (args.report or args.report_dir) else None,
                sheet=(int(args.sheet) if isinstance(args.sheet, str) and args.sheet.isdigit() else args.sheet),
                header_row=args.header_row,
                decimal=args.decimal,
                thousands=args.thousands,
                currency=args.currency,
                csv_encoding=args.csv_encoding,
                csv_quotechar=args.csv_quotechar,
                csv_no_header=args.csv_no_header,
                redact=args.redact,
                summary_path=args.summary,
            )
            logging.info(
                "Converted: %s -> %s | rows_in=%s rows_out=%s warnings=%s",
                args.input,
                output,
                before,
                after,
                issues,
            )
            print(f"Wrote: {output}")
        except ConversionError as exc:
            logging.error("Failed to convert %s: %s", args.input, exc)
            raise
        except Exception as exc:  # noqa: BLE001
            logging.exception("Unexpected failure converting %s: %s", args.input, exc)
            raise
        return

    # Batch mode
    source_dir: Path = args.source
    dest_dir: Path = args.dest
    source_dir.mkdir(parents=True, exist_ok=True)
    dest_dir.mkdir(parents=True, exist_ok=True)

    xls_files = sorted([p for p in source_dir.glob("*.xls") if p.is_file()])
    # Also support .xlsx in batch mode
    xlsx_files = sorted([p for p in source_dir.glob("*.xlsx") if p.is_file()])
    all_files = xls_files + xlsx_files
    if not all_files:
        logging.info("No .xls/.xlsx files found in %s", source_dir)
        print("No .xls/.xlsx files found.")
        return

    converted_count = 0
    skipped_count = 0
    failed_count = 0
    for src in all_files:
        dst = dest_dir / f"{src.stem}.csv"
        if dst.exists() and not args.force:
            logging.info("Skip (exists): %s -> %s", src, dst)
            skipped_count += 1
            continue
        try:
            before, after, issues = convert(
                src,
                dst,
                strict=args.strict,
                delimiter=args.delimiter,
                max_scan_rows=args.max_scan_rows,
                engine=args.engine,
                dry_run=args.dry_run,
                mapping=mapping,
                trace=args.trace,
                trace_max_rows=args.trace_max_rows,
                report_path=(args.report_dir / f"{src.stem}.report.csv") if args.report_dir else None,
                sheet=(int(args.sheet) if isinstance(args.sheet, str) and args.sheet.isdigit() else args.sheet),
                header_row=args.header_row,
                decimal=args.decimal,
                thousands=args.thousands,
                currency=args.currency,
                csv_encoding=args.csv_encoding,
                csv_quotechar=args.csv_quotechar,
                csv_no_header=args.csv_no_header,
                redact=args.redact,
                summary_path=(args.summary.parent / f"{src.stem}.summary.json") if (args.summary and args.summary.is_dir()) else args.summary,
            )
            logging.info(
                "Converted: %s -> %s | rows_in=%s rows_out=%s warnings=%s",
                src,
                dst,
                before,
                after,
                issues,
            )
            converted_count += 1
        except ConversionError as exc:
            logging.error("Failed: %s -> %s : %s", src, dst, exc)
            failed_count += 1
        except Exception as exc:  # noqa: BLE001
            logging.exception("Unexpected failure: %s -> %s : %s", src, dst, exc)
            failed_count += 1

    summary = f"Done. Converted={converted_count}, Skipped={skipped_count}, Failed={failed_count}. Log: {log_path}"
    print(summary)
    logging.info(summary)


if __name__ == "__main__":
    main()


