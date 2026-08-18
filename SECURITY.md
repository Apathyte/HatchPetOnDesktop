# Security Policy

## Supported Surface

Security fixes target the current root runtime on `main`. The `stable-v*`
directories are historical source snapshots and should not be treated as
separately supported releases.

## Reporting a Vulnerability

Use GitHub's private vulnerability reporting option for this repository when
it is available. If it is not visible, contact the repository owner through
their GitHub profile before sharing technical details.

Do not include credentials, personal information, confidential window titles,
or exploit material in a public issue. If a credential is ever committed,
revoke it first; deleting the file or commit is not sufficient.

## Runtime Privacy Boundary

The desktop runtime reads foreground application information locally to select
reactions. It does not transmit or persist that information. The status window
hides foreground window titles by default.
