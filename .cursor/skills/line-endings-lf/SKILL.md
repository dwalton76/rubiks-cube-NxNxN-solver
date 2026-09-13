---
name: line-endings-lf
description: Enforces LF newlines on every file in the rubiks-cube solver and lookup-tables repos. Use when creating or editing any file, committing, reviewing diffs, or when the user mentions CRLF, line endings, or LF.
---

# Line endings

never use CRLF, always use LF

## Instructions

- Write and save every text file with Unix LF (`\n`) only. Never emit `\r\n`.
- When editing on Windows, do not let the editor or git convert to CRLF.
- After writing files from Windows tools, check with `file` or `grep -l $'\r'` and convert: `sed -i 's/\r$//' <file>`.
- Keep `.gitattributes` as `* text=auto eol=lf` plus binary exceptions for tables (`*.bin`, `*.ef`, `*.gz`, images).
- Reject or rewrite patches that introduce CRLF. `git diff` showing `^M` is a bug.
