"""
SurakshaVision AI - Production Packaging Script
Creates a standalone, clean surakshavision-ai.zip excluding caches and temporary files.
"""

import os
import zipfile
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parent
ZIP_PATH = SOURCE_DIR / "surakshavision-ai.zip"

EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".git", ".idea", ".vscode"}
EXCLUDE_EXTS = {".pyc", ".pyo"}

def create_zip():
    print(f"Packaging {SOURCE_DIR} into {ZIP_PATH}...")
    file_count = 0
    total_bytes = 0

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(SOURCE_DIR):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in EXCLUDE_EXTS:
                    continue

                full_path = Path(root) / file
                rel_path = full_path.relative_to(SOURCE_DIR)

                zipf.write(full_path, rel_path)
                file_count += 1
                total_bytes += full_path.stat().st_size

    zip_size_mb = ZIP_PATH.stat().st_size / (1024 * 1024)
    print(f" Successfully packaged {file_count} files ({total_bytes / (1024*1024):.2f} MB uncompressed) into:")
    print(f"   --> {ZIP_PATH} ({zip_size_mb:.2f} MB)")

if __name__ == "__main__":
    create_zip()
