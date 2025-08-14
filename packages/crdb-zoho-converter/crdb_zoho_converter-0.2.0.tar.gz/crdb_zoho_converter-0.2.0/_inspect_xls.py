import pandas as pd
from pathlib import Path
from pprint import pprint
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect XLS/XLSX files for header candidates and sample rows")
    parser.add_argument("-i", "--input", type=Path, default=Path("files/crdb_input.xls"), help="Path to XLS/XLSX to inspect")
    parser.add_argument("--engine", choices=["auto", "xlrd", "openpyxl"], default="auto", help="Excel reader engine")
    parser.add_argument("--sheet", default=None, help="Sheet name or 0-based index")
    parser.add_argument("--max-scan-rows", type=int, default=500, help="Max rows to scan for headers")
    args = parser.parse_args()

    source_path = args.input
    print(f"Exists: {source_path.exists()}  Size: {source_path.stat().st_size if source_path.exists() else 'n/a'}")

    engine = None
    if args.engine == "xlrd":
        engine = "xlrd"
    elif args.engine == "openpyxl":
        engine = "openpyxl"

    # Read without header to scan for the real header row inside the sheet
    xl = pd.read_excel(source_path, engine=engine, header=None, dtype=str, sheet_name=args.sheet)
    print("Shape:", xl.shape)

    # Heuristics: look for typical header combinations
    candidate_indices: list[int] = []
    header_rows: list[list[str]] = []
    keywords_sets = [
        {"date", "withdrawals", "deposits"},
        {"date", "debit", "credit"},
        {"transaction date", "debit", "credit"},
    ]

    max_scan_rows = min(args.max_scan_rows, len(xl))
    for i in range(max_scan_rows):
        row = xl.iloc[i].fillna("").astype(str).str.strip()
        lowered = {cell.lower() for cell in row if cell}
        if any(ks.issubset(lowered) for ks in keywords_sets) or (
            ("date" in lowered) and ("details" in lowered or "description" in lowered or "narration" in lowered)
        ):
            candidate_indices.append(i)
            header_rows.append(list(row))

    print("Candidate header rows:", candidate_indices)
    if candidate_indices:
        idx = candidate_indices[0]
        header = header_rows[0]
        print("Chosen header idx:", idx)
        pprint(header)

        df = xl.iloc[idx + 1 :].copy()
        # Pad extra columns to avoid length mismatch
        if len(df.columns) > len(header):
            header = header + [f"extra_{j}" for j in range(len(df.columns) - len(header))]
        df.columns = header

        # Show a small sample under the header
        with pd.option_context("display.max_colwidth", 200):
            print("First 15 rows under header:")
            print(df.head(15).to_string(index=False))
    else:
        print("No header candidates found; showing rows 0..60:")
        with pd.option_context("display.max_colwidth", 200):
            print(xl.iloc[:60].to_string(index=False, header=False))


if __name__ == "__main__":
    main()


