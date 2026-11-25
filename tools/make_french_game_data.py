#!/usr/bin/env python3
"""Build albert_game_data_fr.zip from the French Windows installer.

Input: the Inno Setup installer of "L'Album secret de l'oncle Ernest"
(setup-02763-L_Album_secret_de_l_oncle_Ernest-PCWin.exe, French Windows
edition, mTropolis data album421.MPL / album422.MPX).

The script unpacks the installer with innoextract, keeps only the files the
ScummVM mTropolis engine needs, and writes them under ALBUM/DATA/ in a ZIP,
the same layout as the Greek albert_game_data.zip. The deploy workflow unpacks
this ZIP into web/data/albert_fr.

The ALBUM/DATA/ nesting matters for the web build: the Emscripten backend adds
/data to ScummVM's search paths two levels deep, so a flat layout makes the
engine see MTPLAY95.EXE twice and stop with "Found multiple mTropolis Player
executables".

Requirements: Python 3.8+ and innoextract 1.8+ on PATH
(Debian/Ubuntu: apt install innoextract, macOS: brew install innoextract).

Usage:
    python3 tools/make_french_game_data.py path/to/setup-...-PCWin.exe [-o albert_game_data_fr.zip]
"""

import argparse
import hashlib
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

# SHA-256 of the installer the French support was tested with.
KNOWN_INSTALLER_SHA256 = {
    "36a78a08a68db75924e2facb00a4bad724d3e9c0c0993991a493f2962a63dcf9":
        "setup-02763-L_Album_secret_de_l_oncle_Ernest-PCWin.exe (131,969,614 bytes)",
}

# MD5 of the first 5000 bytes, as used by ScummVM detection.
EXPECTED_MD5_5000 = {
    "album421.MPL": "2f3cc30f13ecc99e8e4818353cef1d34",
    "album422.MPX": "132db6e709ff40b49e5c702c6d14bd95",
}

ZIP_PREFIX = "ALBUM/DATA/"

# Files kept in the ZIP, relative to the installer's "app" directory.
# Left out on purpose:
#  - Boek.EXE and the Dutch autorun launcher: a second copy of the mTropolis
#    player makes ScummVM stop with "Found multiple mTropolis Player executables".
#  - sauve1 and photos1.dat: save slot 1 from a previous playthrough. Without
#    them every player starts from the "sauve" new-game template.
#  - QuickTime for Windows DLLs and codecs, icons and readme: not used by ScummVM.
REQUIRED_FILES = [
    "album421.MPL",
    "album422.MPX",
    "MTPLAY95.EXE",
    "sauve",
    "liste_pages",
    "textes_labo.dat",
    "RESOURCE/BASIC.X95",
    "RESOURCE/BITMAP.R95",
    "RESOURCE/CURSORS.C95",
    "RESOURCE/EXTRAS.R95",
    "RESOURCE/ROTATORK.R95",
] + [f"photo{i}/photo0" for i in range(1, 11)]


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def md5_of_head(path: Path, size: int = 5000) -> str:
    with path.open("rb") as f:
        return hashlib.md5(f.read(size)).hexdigest()


def find_app_dir(root: Path) -> Path:
    """Return the directory that holds album421.MPL (innoextract puts it under app/)."""
    for mpl in root.rglob("*"):
        if mpl.is_file() and mpl.name.lower() == "album421.mpl":
            return mpl.parent
    sys.exit("error: album421.MPL not found in the installer; is this the French edition?")


def resolve(app_dir: Path, rel: str) -> Path:
    """Find rel inside app_dir, ignoring case (installers differ in file name case)."""
    current = app_dir
    for part in rel.split("/"):
        match = next((p for p in current.iterdir() if p.name.lower() == part.lower()), None)
        if match is None:
            sys.exit(f"error: required file missing from installer: {rel}")
        current = match
    return current


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("installer", type=Path, help="French Windows installer (.exe)")
    parser.add_argument("-o", "--output", type=Path, default=Path("albert_game_data_fr.zip"),
                        help="output ZIP (default: albert_game_data_fr.zip)")
    args = parser.parse_args()

    if not args.installer.is_file():
        sys.exit(f"error: installer not found: {args.installer}")
    if shutil.which("innoextract") is None:
        sys.exit("error: innoextract not found on PATH (apt install innoextract / brew install innoextract)")

    print(f"Hashing {args.installer.name} ...")
    digest = sha256_of(args.installer)
    if digest in KNOWN_INSTALLER_SHA256:
        print(f"  known installer: {KNOWN_INSTALLER_SHA256[digest]}")
    else:
        print(f"  warning: unknown installer SHA-256 {digest}; continuing, data files are checked below")

    with tempfile.TemporaryDirectory(prefix="albert_fr_") as tmp:
        tmp_path = Path(tmp)
        print("Unpacking with innoextract ...")
        subprocess.run(["innoextract", "--silent", "--extract", "--output-dir", str(tmp_path), str(args.installer)],
                       check=True)
        app_dir = find_app_dir(tmp_path)

        for name, expected in EXPECTED_MD5_5000.items():
            actual = md5_of_head(resolve(app_dir, name))
            if actual != expected:
                sys.exit(f"error: {name} does not match the supported French release "
                         f"(md5 of first 5000 bytes {actual}, expected {expected})")
        print("  album421.MPL / album422.MPX match ScummVM's French albert1 entry")

        args.output.parent.mkdir(parents=True, exist_ok=True)
        tmp_zip = args.output.with_suffix(args.output.suffix + ".tmp")
        # ZIP_STORED: the MPX is already compressed media, and the workflow unzips it right away.
        with zipfile.ZipFile(tmp_zip, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as zf:
            for rel in REQUIRED_FILES:
                src = resolve(app_dir, rel)
                print(f"  + {ZIP_PREFIX}{rel} ({src.stat().st_size:,} bytes)")
                zf.write(src, arcname=ZIP_PREFIX + rel)
        tmp_zip.replace(args.output)

    print(f"Wrote {args.output} ({args.output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
