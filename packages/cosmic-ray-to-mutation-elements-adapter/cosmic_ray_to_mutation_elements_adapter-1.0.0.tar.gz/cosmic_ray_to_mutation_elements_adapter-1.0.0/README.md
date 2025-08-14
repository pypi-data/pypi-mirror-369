

## Usage

```
usage: cr-to-stryker-report [-h] [-f {html,json}] [-o OUTPUT] [-w WORKSPACE]
                            sqlite_db_path

Convert Cosmic Ray mutation results to Stryker JSON report.

positional arguments:
  sqlite_db_path        Path to the Cosmic Ray mutation session SQLite database.

options:
  -h, --help            show this help message and exit
  -f {html,json}, --format {html,json}
                        Output format for the report.
  -o OUTPUT, --output OUTPUT
                        Path to output Stryker report file.
  -w WORKSPACE, --workspace WORKSPACE
                        Workspace root directory for resolving module paths.
```