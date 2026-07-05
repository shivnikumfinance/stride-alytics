"""
Utility to package the app directory into a deployable zip file.
"""

import os
import zipfile
from pathlib import Path


def make_zip(output_name: str = "app.zip") -> str:
    """
    Create a zip archive of the app directory.

    Parameters
    ----------
    output_name : str
        Name of the output zip file.

    Returns
    -------
    str
        Path to the created zip file.
    """
    base_dir = Path(__file__).parent
    output_path = base_dir.parent / output_name

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith(".py") or file.endswith(".sql"):
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, base_dir.parent)
                    zf.write(file_path, arcname)

    return str(output_path)


if __name__ == "__main__":
    path = make_zip()
    print(f"Created: {path}")
