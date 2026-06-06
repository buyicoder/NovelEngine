"""Project backup and archive management."""

import os
import zipfile
from datetime import datetime


def create_backup(project_root, backup_dir=None):
    if backup_dir is None:
        backup_dir = os.path.join(project_root, ".novel", "backups")
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_name = os.path.basename(project_root.rstrip("/\\"))
    zip_name = f"{project_name}_{timestamp}.zip"
    zip_path = os.path.join(backup_dir, zip_name)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(project_root):
            dirs[:] = [d for d in dirs if d not in ("backups", "tmp")]
            for f in files:
                filepath = os.path.join(root, f)
                arcname = os.path.relpath(filepath, project_root)
                zf.write(filepath, arcname)
    return zip_path


def list_backups(project_root):
    backup_dir = os.path.join(project_root, ".novel", "backups")
    if not os.path.isdir(backup_dir):
        return []
    return sorted([f for f in os.listdir(backup_dir) if f.endswith(".zip")], reverse=True)
