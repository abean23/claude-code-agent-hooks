"""Generate run manifest for determinism and reproducibility."""

import json
import sys
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime


def get_git_info():
    """Get git commit hash if in a git repository."""
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2
        )
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2
        )
        dirty = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=2
        )

        return {
            "commit": commit.stdout.strip() if commit.returncode == 0 else None,
            "branch": branch.stdout.strip() if branch.returncode == 0 else None,
            "dirty": bool(dirty.stdout.strip()) if dirty.returncode == 0 else None
        }
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {"commit": None, "branch": None, "dirty": None}


def get_tool_versions():
    """Get versions of key tools."""
    versions = {}

    try:
        python_version = subprocess.run(
            [sys.executable, "--version"],
            capture_output=True,
            text=True,
            timeout=2
        )
        versions["python"] = python_version.stdout.strip()
    except:
        versions["python"] = None

    # Get package versions
    try:
        import pytest
        versions["pytest"] = pytest.__version__
    except ImportError:
        versions["pytest"] = None

    try:
        import jsonschema
        versions["jsonschema"] = jsonschema.__version__
    except ImportError:
        versions["jsonschema"] = None

    try:
        import black
        versions["black"] = black.__version__
    except ImportError:
        versions["black"] = None

    return versions


def compute_file_checksum(file_path: Path) -> str:
    """Compute SHA256 checksum of a file."""
    if not file_path.exists():
        return None

    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def generate_manifest(project_dir: Path, output_path: Path):
    """Generate run manifest with all reproducibility metadata."""

    manifest = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "git": get_git_info(),
        "versions": get_tool_versions(),
        "environment": {
            "python_executable": sys.executable,
            "platform": sys.platform
        },
        "files": {
            "ir_json": compute_file_checksum(project_dir / "ir.json"),
            "division_py": compute_file_checksum(project_dir / "division.py"),
            "generated_tests_py": compute_file_checksum(project_dir / "generated_tests.py"),
            "ir_schema_json": compute_file_checksum(project_dir / "ir_schema.json")
        },
        "config": {
            "random_seed": None,  # Placeholder for future use
            "model_name": "claude-sonnet-4-5-20250929"  # Could be parameterized
        },
        "traceability": {
            "agent_used": "EdgeCaseAgent",
            "agent_config": str(project_dir / ".claude" / "agents" / "edge_case_agent.md"),
            "prompt_summary": "Analyze code for edge cases and generate structured IR",
            "note": "Full agent prompt available in agent_config file"
        }
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"✓ Generated run manifest: {output_path}")
    return manifest


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manifest_generator.py <project_dir> [output_path]")
        sys.exit(1)

    project_dir = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else project_dir / "reports" / "run.meta.json"

    generate_manifest(project_dir, output_path)