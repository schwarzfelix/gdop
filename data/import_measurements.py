from pathlib import Path
import io
import pandas as pd
from typing import List
import logging

_LOG = logging.getLogger(__name__)

def _clean_col(name: str) -> str:
    """Normalize column names (remove angle brackets, whitespace)."""
    return name.strip().lstrip("<").rstrip(">").strip().replace(" ", "_").lower()

def _read_csv_with_hash_header(path: Path) -> pd.DataFrame:
    """
    Read a CSV file that may contain lines starting with '//' (comments)
    and a header line starting with '#'. Returns a pandas DataFrame.
    """
    text = path.read_text(encoding="utf-8")
    lines: List[str] = text.splitlines()
    cleaned_lines: List[str] = []
    header_found = False

    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if s.startswith("//"):
            # skip tooling/filepath comments
            continue
        if s.startswith("#"):
            # header line - strip leading '#'
            cleaned_lines.append(s.lstrip("#").strip())
            header_found = True
        else:
            cleaned_lines.append(ln)

    # Fallback: if no '#' header found, try to use first non-empty line as header
    if not header_found and cleaned_lines:
        # assume first line currently is header already, keep as-is
        pass

    csv_text = "\n".join(cleaned_lines)
    if not csv_text.strip():
        return pd.DataFrame()

    df = pd.read_csv(io.StringIO(csv_text), sep=",", skipinitialspace=True)
    df.columns = [_clean_col(c) for c in df.columns]
    return df

def read_workspace_csvs(workspace_dir: str = "workspace") -> pd.DataFrame:
    """
    Recursively read CSV measurement files under workspace_dir.
    Each subfolder is treated as a 'scenario' name; each CSV is read and
    annotated with 'scenario' and 'source_file' columns.

    Returns a single concatenated pandas.DataFrame (empty DataFrame if none).
    """
    base = Path(workspace_dir)
    if not base.exists():
        raise FileNotFoundError(f"workspace directory not found: {workspace_dir}")

    dfs = []
    # look one level deep: workspace/<scenario>/*.csv
    for scenario_dir in base.iterdir():
        if not scenario_dir.is_dir():
            continue
        for csv_path in scenario_dir.glob("*.csv"):
            try:
                df = _read_csv_with_hash_header(csv_path)
                if df.empty:
                    continue
                df["scenario"] = scenario_dir.name
                df["source_file"] = str(csv_path)
                dfs.append(df)
            except Exception as e:
                # keep function robust: skip problematic files but log
                _LOG.warning("Failed to read %s: %s", csv_path, e)

    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)
# ...existing code...