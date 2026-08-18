#!/usr/bin/env python3
"""Fail CI when reachable history contains common secrets or private identities."""

from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


RULES = {
    "private key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "GitHub token": re.compile(rb"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b"),
    "AWS access key": re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "Slack token": re.compile(rb"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    "OpenAI key": re.compile(rb"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "connection string": re.compile(rb"(?i)\b(?:mongodb(?:\+srv)?|postgres(?:ql)?|mysql|redis|amqps?)://[^\s'\"]+"),
    "credential assignment": re.compile(
        rb"(?i)\b(?:password|passwd|pwd|secret|api[_-]?key|access[_-]?token|client[_-]?secret)\b"
        rb"\s*[:=]\s*['\"]?[^\s'\",;}{]{8,}"
    ),
}

SENSITIVE_NAMES = re.compile(
    r"(?i)(^|/)(?:\.env(?:\..*)?|credentials?(?:\..*)?|secrets?(?:\..*)?|"
    r"id_rsa|id_ed25519|.*\.(?:pem|pfx|p12|kdbx))$"
)


def scan_bytes(label, data, findings):
    if b"\x00" in data[:8192]:
        return
    for rule, pattern in RULES.items():
        if pattern.search(data):
            findings.add((rule, label))


def scan_worktree(findings):
    for raw_path in git("ls-files").decode().splitlines():
        if SENSITIVE_NAMES.search(raw_path):
            findings.add(("sensitive filename", raw_path))
        path = ROOT / raw_path
        if path.is_file():
            scan_bytes(raw_path, path.read_bytes(), findings)


def scan_history(findings):
    seen = set()
    for row in git("rev-list", "--objects", "--all").decode("utf-8", "replace").splitlines():
        oid, separator, path = row.partition(" ")
        if not separator or oid in seen:
            continue
        seen.add(oid)
        if SENSITIVE_NAMES.search(path):
            findings.add(("historical sensitive filename", path))
        if git("cat-file", "-t", oid).strip() != b"blob":
            continue
        scan_bytes(f"history:{path}", git("cat-file", "blob", oid), findings)


def scan_commit_identities(findings):
    values = git("log", "--all", "--format=%ae%n%ce").decode("utf-8", "replace").splitlines()
    for email in sorted(set(values)):
        normalized = email.strip().lower()
        if not normalized:
            continue
        if normalized == "noreply@github.com" or normalized.endswith("@users.noreply.github.com"):
            continue
        findings.add(("public commit identity", email))


def main():
    findings = set()
    scan_worktree(findings)
    scan_history(findings)
    scan_commit_identities(findings)
    if findings:
        for rule, location in sorted(findings):
            print(f"{rule}: {location}", file=sys.stderr)
        return 1
    print("Security scan passed: no recognized secrets, sensitive filenames, or private commit identities.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
