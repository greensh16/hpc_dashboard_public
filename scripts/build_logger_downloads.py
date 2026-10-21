#!/usr/bin/env python3
"""Mirror the current logger-rs release into the Pages artifact and fill its download page."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen

RELEASE_API = "https://api.github.com/repos/greensh16/logger-rs/releases/latest"
ARCHIVE_PATTERN = re.compile(r"logger-rs-(\d+\.\d+\.\d+)-x86_64-linux-musl\.tar\.gz")


def fetch(url: str) -> bytes:
    headers = {"User-Agent": "hpc-dashboard-pages", "Accept": "application/vnd.github+json"}
    if url == RELEASE_API and os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    request = Request(url, headers=headers)
    with urlopen(request, timeout=30) as response:
        return response.read()


def build(site: Path) -> None:
    release = json.loads(fetch(RELEASE_API))
    tag = release["tag_name"]
    assets = {asset["name"]: asset["browser_download_url"] for asset in release["assets"]}
    archives = [(name, ARCHIVE_PATTERN.fullmatch(name)) for name in assets]
    archives = [(name, match) for name, match in archives if match and tag == f"v{match.group(1)}"]
    if len(archives) != 1:
        raise ValueError(f"Expected one matching Linux archive in release {tag}")
    archive_name, match = archives[0]
    checksum_name = archive_name + ".sha256"
    if checksum_name not in assets:
        raise ValueError(f"Missing checksum for {archive_name}")
    archive = fetch(assets[archive_name])
    checksum = fetch(assets[checksum_name])
    checksum_parts = checksum.decode("utf-8").strip().split()
    if len(checksum_parts) != 2 or checksum_parts[1].lstrip("*") != archive_name:
        raise ValueError(f"Unexpected checksum format for {archive_name}")
    if hashlib.sha256(archive).hexdigest() != checksum_parts[0]:
        raise ValueError(f"Checksum mismatch for {archive_name}")

    downloads = site / "logger-rs" / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    (downloads / archive_name).write_bytes(archive)
    (downloads / checksum_name).write_bytes(checksum)

    page = site / "logger-rs" / "index.html"
    content = page.read_text(encoding="utf-8")
    replacements = {
        "{{LOGGER_VERSION}}": match.group(1),
        "{{LOGGER_ARCHIVE}}": f"/logger-rs/downloads/{archive_name}",
        "{{LOGGER_CHECKSUM}}": f"/logger-rs/downloads/{checksum_name}",
        "{{LOGGER_SIZE}}": f"{len(archive) / 1024:.0f} KB",
    }
    for placeholder, value in replacements.items():
        if placeholder not in content:
            raise ValueError(f"Missing placeholder {placeholder} in logger-rs page")
        content = content.replace(placeholder, value)
    page.write_text(content, encoding="utf-8")
    print(f"Mirrored logger-rs {tag} ({len(archive)} bytes, SHA256 verified)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: build_logger_downloads.py SITE_OUTPUT")
    build(Path(sys.argv[1]))
