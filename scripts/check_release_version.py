"""Check stable release versions without installing build dependencies."""

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys
from zipfile import BadZipFile, ZipFile


STABLE_VERSION = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")
# v0.45 is already public. A new version must outrank tag-based clients too.
LEGACY_RELEASE = (0, 45, 0)


def read_version(content, label):
    package = json.loads(content)
    version = package.get("version") if isinstance(package, dict) else None
    if not isinstance(version, str) or not STABLE_VERSION.fullmatch(version):
        raise ValueError(f"{label}: expected a stable X.Y.Z version, got {version!r}")
    return version


def check_version(package_json, tag=None, archive=None):
    version = read_version(Path(package_json).read_text(encoding="utf-8"), str(package_json))
    if tuple(map(int, version.split("."))) <= LEGACY_RELEASE:
        raise ValueError(f"{version} must be newer than historical v0.45 (0.45.0)")
    if tag and tag != f"v{version}":
        raise ValueError(f"release tag {tag!r} must be exactly 'v{version}'")

    if archive is not None:
        with ZipFile(archive) as zipped:
            # Decky install ZIPs contain one plugin folder. Ignore dependency
            # manifests further down the tree, but reject ambiguous plugin roots.
            manifests = [
                info for info in zipped.infolist()
                if len(PurePosixPath(info.filename).parts) == 2
                and PurePosixPath(info.filename).name == "package.json"
                and PurePosixPath(info.filename).parts[0] != ".."
                and not PurePosixPath(info.filename).is_absolute()
                and not info.is_dir()
            ]
            if len(manifests) != 1:
                raise ValueError(f"{archive}: expected exactly one plugin-folder/package.json")
            packaged = read_version(zipped.read(manifests[0]), str(archive))
            if packaged != version:
                raise ValueError(f"{archive}: ZIP version {packaged} differs from source {version}")
    return version


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-json", type=Path, default=Path("package.json"))
    parser.add_argument("--tag", help="expected release tag; omit for branch/PR builds")
    parser.add_argument("--archive", type=Path, help="installable Decky plugin ZIP")
    args = parser.parse_args()
    try:
        version = check_version(args.package_json, args.tag, args.archive)
    except (OSError, ValueError, BadZipFile) as error:
        print(f"Version check failed: {error}", file=sys.stderr)
        return 1
    print(f"Version check passed: {version}" + (f" / {args.tag}" if args.tag else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
