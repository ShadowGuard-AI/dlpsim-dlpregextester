![Banner](banner.png)

# dlpsim-DLPRegexTester
A command-line tool that takes a regular expression and a sample text file as input, and highlights matches in the text that would trigger a DLP rule based on the regex. It is a regex highlighter only: it generates no data, computes no detection rate, and makes no recommendations. Only the lines containing matches are printed, with each matched value highlighted; lines without matches are not printed, so values the pattern does not select are not echoed. With --redact, the middle of each matched value is masked, keeping only its first and last characters. A plain summary line is printed after the text, stating the matches found and the file bytes scanned. An empty file exits 1 with a plain line; a file with no matches prints a zero matches summary and exits 0. Useful for testing and refining DLP regular expression rules. - Focused on Tools to simulate data leakage scenarios and test the effectiveness of DLP solutions.

## Install
`git clone https://github.com/ShadowStrikeHQ/dlpsim-dlpregextester`

## Usage
`python main.py "\d{3}-\d{2}-\d{4}" test.txt`
`python main.py "\d{3}-\d{2}-\d{4}" test.txt --redact`

## Parameters
- `regex`: The regular expression to test.
- `file_path`: The path to the text file to scan.
- `-h`: Show help message and exit
- `-i`, `--ignore-case`: Perform case-insensitive matching.
- `-l`, `--log-level`: Set the logging level.
- `--redact`: Mask the middle of each matched value, keeping only its first and last characters.

## License
Copyright (c) ShadowStrikeHQ
