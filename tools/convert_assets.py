#!/usr/bin/env python3

"""Convert 3D models to Panda3D formats and update assets.toml.

This utility converts source models (e.g. .obj, .blend) into Panda3D
friendly formats like .bam or .egg. Converted outputs are recorded in
``assets.toml`` with SHA256 hashes. Conversion results are cached in
``tools/convert_assets.cache.json`` to avoid redundant work.
"""

import json
import hashlib
import tomllib
import argparse
import subprocess

from pathlib import Path

ASSETS_TOML = Path("assets.toml")
CACHE_FILE = Path(__file__).with_suffix(".cache.json")
MODELS_DIR = Path("assets/models")


def sha256sum(path: Path) -> str:
    """Return the SHA256 hex digest of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest() -> dict:
    if ASSETS_TOML.exists():
        with ASSETS_TOML.open("rb") as f:
            return tomllib.load(f)
    return {"models": {}, "textures": {}, "audio": {}}


def save_manifest(manifest: dict) -> None:
    lines = []
    for section, items in manifest.items():
        lines.append(f"[{section}]")
        for key, value in items.items():
            path = value["path"]
            sha = value["sha256"]
            lines.append(f'{key} = {{ path = "{path}", sha256 = "{sha}" }}')
        lines.append("")
    ASSETS_TOML.write_text("\n".join(lines), encoding="utf-8")


def load_cache() -> dict:
    if CACHE_FILE.exists():
        with CACHE_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache: dict) -> None:
    with CACHE_FILE.open("w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def convert_obj(source: Path, dest: Path) -> None:
    """Convert a Wavefront OBJ file using obj2egg and egg2bam."""
    temp_egg = dest.with_suffix(".egg")
    subprocess.run(["obj2egg", str(source), str(temp_egg)], check=True)
    if dest.suffix == ".bam":
        subprocess.run(["egg2bam", str(temp_egg), "-o", str(dest)], check=True)
        temp_egg.unlink()


def convert_blend(source: Path, dest: Path) -> None:
    """Convert a Blender file using blend2bam."""
    subprocess.run(["blend2bam", str(source), str(dest)], check=True)


def convert(source: Path, fmt: str, manifest: dict, cache: dict) -> None:
    source = source.resolve()
    source_hash = sha256sum(source)
    cached = cache.get(str(source))
    if cached and cached.get("sha256") == source_hash and Path(cached["output"]).exists():
        print(f"{source.name} up to date; skipping")
        return

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    dest = MODELS_DIR / f"{source.stem}.{fmt}"
    if source.suffix == ".obj":
        convert_obj(source, dest)
    elif source.suffix == ".blend":
        convert_blend(source, dest)
    else:
        msg = f"Unsupported source format: {source.suffix}"
        raise ValueError(msg)

    output_hash = sha256sum(dest)
    manifest.setdefault("models", {})[source.stem] = {
        "path": str(dest.as_posix()),
        "sha256": output_hash,
    }
    cache[str(source)] = {"sha256": source_hash, "output": str(dest)}
    save_manifest(manifest)
    save_cache(cache)
    print(f"Converted {source} -> {dest}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="source model file (.obj or .blend)")
    parser.add_argument("--format", choices=["bam", "egg"], default="bam", help="output format")
    args = parser.parse_args()

    manifest = load_manifest()
    cache = load_cache()
    convert(args.source, args.format, manifest, cache)


if __name__ == "__main__":
    main()
