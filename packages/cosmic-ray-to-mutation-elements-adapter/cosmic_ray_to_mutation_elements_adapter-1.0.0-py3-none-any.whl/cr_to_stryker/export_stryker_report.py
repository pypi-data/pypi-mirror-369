import enum
import json
import os
import sqlite3
from typing import Any, Dict, Optional
import argparse

from cr_to_stryker.constants.html_report_template import HTML_PAGE_TEMPLATE

DB_PATH = os.path.join(os.path.dirname(__file__), "mutation_session.sqlite")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "stryker-report.json")
WORKSPACE_PATH = os.getcwd()

class StrEnum(str, enum.Enum):
    "An Enum subclass with str values."

class TestOutcome(StrEnum):
    """A enum of the possible outcomes for any mutant test run."""

    SURVIVED = "survived"
    KILLED = "killed"
    INCOMPETENT = "incompetent"




def map_status(test_outcome:str) -> str:
    # Stryker MutantStatus enum: ["Killed","Survived","NoCoverage","CompileError","RuntimeError","Timeout","Ignored","Pending"]
    # Map to stryker status
    print("Test outcome: ", test_outcome)
    print("Is Killed: ", test_outcome == TestOutcome.KILLED)
    if test_outcome.strip().upper() == TestOutcome.KILLED.value.upper():
        return "Killed"
    if test_outcome.strip().upper() == TestOutcome.SURVIVED.value.upper():
        return "Survived"
    if test_outcome.strip().upper() == TestOutcome.INCOMPETENT.value.upper():
        return "RuntimeError"

    # Unknown mapping, mark as pending
    return "Pending"


def safe_json_loads(value: Optional[str]) -> Optional[Any]:
    if value is None:
        return None
    try:
        return json.loads(value)
    except Exception:
        return None


def normalize_start_position(line_value: Optional[int], file_text: Optional[str]) -> Dict[str, int]:
    if line_value is None:
        return {"line": 0, "column": 0}

    # Ensure line_value is at least 1
    line_value = max(1, line_value)

    if file_text is None:
        return {"line": line_value, "column": 0}

    # Get the actual line from the file text
    lines = file_text.splitlines()
    if line_value - 1 < len(lines):
        line_text = lines[line_value - 1]
        # Find the first non-whitespace character
        first_non_whitespace_index = next((i for i, c in enumerate(line_text) if not c.isspace()), len(line_text))
        column_value = max(1, first_non_whitespace_index + 1)  # Convert to 1-based index

    return {"line": line_value, "column": column_value}   

def normalize_end_position(line_value: Optional[int], file_text: Optional[str]) -> Dict[str, int]:
    if line_value is None:
        return {"line": 0, "column": 0}

    # Ensure line_value is at least 1
    line_value = max(1, line_value)

    if file_text is None:
        return {"line": line_value, "column": 0}

    # Get the actual line from the file text
    lines = file_text.splitlines()
    if line_value - 1 < len(lines):
        line_text = lines[line_value - 1]
        last_character_index = len(line_text)
        column_value = max(1, last_character_index)  # Convert to 1-based index

    return {"line": line_value, "column": column_value+1}

def getNewDiffLine(diff: Optional[str]) -> Optional[str]:
    """
        Diff is in the format of regular git diff output.
        For example, if we have diff as following:

        ```
        --- mutation diff ---
        --- aapp\service\friend_service.py
        +++ bapp\service\friend_service.py
        @@ -14,7 +14,7 @@
                    raise Exception("Failed to fetch user data: Invalid response format")
                    
                    # Then check if results is empty
        -            if len(data['results']) == 0:
        +            if len(data['results']) != 0:
                    raise Exception("Failed to fetch user data: Empty response")
                    
                return data['results'][0]
        ```

        We need to return just `if len(data['results']) != 0:`
    """
    if not diff:
        return None
    lines = diff.splitlines()
    # Find the line that starts with "+" followed by whitespaces
    for line in lines:
        if line.startswith("+ ") and len(line) > 2:
            return line[2:].strip()
    # No line starts with "+" followed by whitespace, so there are only deletions    
    return " "


def getFileContentsFromModulePath(modulePath: str) -> Optional[str]:
    file_path = os.path.join(WORKSPACE_PATH, modulePath)
    print(f"Looking for file: {file_path}")
    if os.path.exists(file_path):
        print(f"Found file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return None

def composeHtmlReport(json_report: Dict[str, Any]) -> str:
    # Basic HTML report structure
    html = HTML_PAGE_TEMPLATE
    html = html.replace("%JSON_REPORT%", json.dumps(json_report, indent=2))
    return html 

def main() -> None:

    parser = argparse.ArgumentParser(
        description="Convert Cosmic Ray mutation results to Stryker JSON report."
    )
    parser.add_argument(
        "-f", "--format",
        choices=["html", "json"],
        default="html",
        help="Output format for the report."
    )    
    parser.add_argument(
        "-o", "--output",
        default=os.path.join(os.getcwd(), "stryker-report.html"),
        help="Path to output Stryker report file."
    )
    parser.add_argument(
        "-w", "--workspace",
        default=os.getcwd(),
        help="Workspace root directory for resolving module paths."
    )    
    parser.add_argument(
        "sqlite_db_path",
        help="Path to the Cosmic Ray mutation session SQLite database."
    )

    args = parser.parse_args()


    OUTPUT_FORMAT = args.format
    WORKSPACE_PATH = args.workspace
    DB_PATH = args.sqlite_db_path
    OUTPUT_PATH = args.output

    if OUTPUT_FORMAT == "json":
        OUTPUT_PATH = OUTPUT_PATH.replace(".html", ".json")

    if not os.path.exists(DB_PATH):
        raise SystemExit(f"Database not found at: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Join the three tables on job_id; not all rows might have results yet, so left joins
    query = (
        "SELECT m.module_path, m.operator_name, m.operator_args, m.occurrence, "
        "m.start_pos_row, m.start_pos_col, m.end_pos_row, m.end_pos_col, m.job_id, "
        "wr.worker_outcome, wr.output, wr.test_outcome, wr.diff "
        "FROM mutation_specs m "
        "LEFT JOIN work_results wr ON wr.job_id = m.job_id "
    )

    rows = list(conn.execute(query))
    conn.close()

    files_dict = {}

    for row in rows:
        module_path = row["module_path"] or "<unknown>"
        file_content_from_module_path = getFileContentsFromModulePath(module_path)
        file_entry = files_dict.get(module_path)
        # print(f"File content from {module_path}: {file_content_from_module_path}")
        if not file_entry:
            file_entry = {
                "language": "python",
                # Source code is not available in the DB; leave it empty so UI can still render mutants
                "source": file_content_from_module_path,
                "mutants": [],
            }
            files_dict[module_path] = file_entry

        # Build mutant entry
        location = {
            "start": normalize_start_position(row["start_pos_row"], file_content_from_module_path),
            "end": normalize_end_position(row["end_pos_row"], file_content_from_module_path),
        }
        print(f"Test outcome in row: {row['test_outcome']}")
        status = map_status(row["test_outcome"])

        mutant: Dict[str, Any] = {
            "id": str(row["job_id"]),
            "mutatorName": str(row["operator_name"]) if row["operator_name"] is not None else "",
            "location": location,
            "status": status,
            "description": str(row["operator_name"]) if row["operator_name"] is not None else ""            
        }

        replacement = getNewDiffLine(row["diff"])
        if replacement is not None:
            mutant["replacement"] = replacement

        if status in {"Killed", "RuntimeError", "CompileError", "Timeout"}:
            status_reason = (row["output"] or "").strip()
            if row["diff"]:
                # Include a short hint that there is a diff
                if status_reason:
                    status_reason = status_reason + "\n--- diff available ---"
                else:
                    status_reason = "diff available"
            if status_reason:
                mutant["statusReason"] = status_reason[:10000]  # avoid excessively large blobs

        file_entry["mutants"].append(mutant)


    # Compose top-level Stryker report
    json_report: Dict[str, Any] = {
        "schemaVersion": "2.0",
        "thresholds": {"high": 80, "low": 60},
        "files": files_dict,
    }

    if OUTPUT_FORMAT == "json":
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(json_report, f, ensure_ascii=False)
    else:
        html_report = composeHtmlReport(json_report)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(html_report)


    print(f"Wrote Stryker report with {sum(len(f['mutants']) for f in files_dict.values())} mutants "
          f"across {len(files_dict)} files to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
