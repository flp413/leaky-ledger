# Findings

From the CI run on commit `TODO`.

## Coverage: which tool caught which bug

| ID | Bug | Semgrep registry | My Semgrep rules | ZAP | My Nuclei templates | gitleaks | pip-audit / Trivy |
|----|-----|:-:|:-:|:-:|:-:|:-:|:-:|
| 01 | IDOR | | | | | | |
| 02 | SQL injection | | | | | | |
| 03 | Unverified JWT | | | | | | |
| 04 | Mass assignment | | | | | | |
| 05 | Race condition | | | | | | |
| 05b | No login rate limit | | | | | | |
| 06 | SSRF | | | | | | |
| 07 | Secrets / DEBUG | | | | | | |
| 08 | Reflected XSS | | | | | | |
| 09 | Vulnerable deps | | | | | | |
| 10 | BOLA by IBAN | | | | | | |
| 11 | FX rounding | | | | | | |
| 12 | Prompt injection (LedgerBot) | | | | | | |
| 12b | Excessive agency (LedgerBot) | | | | | | |

## Noise

Total findings per tool, and how many were false positives. TODO

## What no off-the-shelf tool caught, and why

TODO

## Triage of individual findings

For the interesting ones: what the tool said, whether it is real, severity, fix.

TODO

## What I would do differently in a real codebase

TODO
