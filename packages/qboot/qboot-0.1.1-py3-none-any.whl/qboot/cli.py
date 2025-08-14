#!/usr/bin/env python3
"""
py-init-bootstrap.py
--------------------
Create a fully-initialized Python project with a virtual environment and sensible defaults.

Features
- Cross-platform (Windows/macOS/Linux)
- Creates `.venv` virtual environment
- Upgrades pip & setuptools
- Installs dev tooling: black, ruff, isort, mypy, pytest, pre-commit, pip-tools, ipykernel, python-dotenv
- Writes config files: pyproject.toml, mypy.ini, .pre-commit-config.yaml, .editorconfig, .gitignore, .env.example
- Creates basic package layout under src/
- Compiles requirements with pip-compile (requirements.txt + requirements-dev.txt)
- Initializes git repo and installs pre-commit hook (if git is present)

Usage
  python py-init-bootstrap.py my_project [--python 3.11] [--no-mypy] [--no-precommit] [--no-piptools]
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

TOOLS = [
    "black",
    "ruff",
    "isort",
    "mypy",
    "pytest",
    "pre-commit",
    "pip-tools",
    "ipykernel",
    "python-dotenv",
    "build",
    "twine",
]

DEV_ONLY = [
    "black",
    "ruff",
    "isort",
    "mypy",
    "pytest",
    "pre-commit",
    "pip-tools",
    "ipykernel",
]

def run(cmd, **kwargs):
    """Run a command, raising on error, streaming output."""
    print("$", " ".join(map(str, cmd)))
    subprocess.check_call(cmd, **kwargs)

def venv_python(venv_dir: Path) -> Path:
    if platform.system() == "Windows":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"

def ensure_git(project_dir: Path):
    if shutil.which("git") is None:
        print("git not found; skipping git init.")
        return
    run(["git", "init"], cwd=project_dir)
    run(["git", "add", "-A"], cwd=project_dir)
    run(["git", "commit", "-m", "chore: bootstrap project"], cwd=project_dir)

def make_files(project_dir: Path, pkg_name: str, enable_mypy: bool, enable_precommit: bool):
    (project_dir / "src" / pkg_name).mkdir(parents=True, exist_ok=True)
    (project_dir / "tests").mkdir(parents=True, exist_ok=True)

    # Basic package file
    (project_dir / "src" / pkg_name / "__init__.py").write_text("__all__ = []\n")

    # Readme
    (project_dir / "README.md").write_text(dedent(f"""
    # {pkg_name}

    Bootstrapped Python project. Common tasks:

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
    pip install -r requirements-dev.txt
    pre-commit install
    pytest -q
    ```
    """).strip() + "\n")

    # .gitignore
    (project_dir / ".gitignore").write_text(dedent(r"""
    # Byte-compiled / optimized / DLL files
    __pycache__/
    *.py[cod]
    *$py.class

    # Virtual environment
    .venv/

    # Distribution / packaging
    build/
    dist/
    *.egg-info/

    # Test & coverage
    .pytest_cache/
    .coverage*
    htmlcov/

    # IDE
    .idea/
    .vscode/

    # OS
    .DS_Store

    # Python
    .mypy_cache/
    .ruff_cache/
    .ipynb_checkpoints/
    """).lstrip())

    # .editorconfig
    (project_dir / ".editorconfig").write_text(dedent(r"""
    root = true

    [*]
    charset = utf-8
    end_of_line = lf
    indent_style = space
    indent_size = 4
    insert_final_newline = true
    trim_trailing_whitespace = true
    """).lstrip())

    # VS Code recommended settings
    (project_dir / ".vscode").mkdir(exist_ok=True)
    (project_dir / ".vscode" / "settings.json").write_text(dedent(r"""
    {
      "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
      "python.testing.pytestEnabled": true,
      "python.testing.unittestEnabled": false,
      "editor.formatOnSave": true
    }
    """).lstrip())

    # Tests
    (project_dir / "tests" / "test_smoke.py").write_text(dedent(f"""
    def test_smoke_import():
        import {pkg_name}  # noqa: F401
    """).lstrip())

    # .env.example
    (project_dir / ".env.example").write_text("EXAMPLE_API_KEY=\n")

    # pre-commit config
    if enable_precommit:
        (project_dir / ".pre-commit-config.yaml").write_text(dedent(r"""
        repos:
          - repo: https://github.com/psf/black
            rev: 24.4.2
            hooks:
              - id: black
          - repo: https://github.com/charliermarsh/ruff-pre-commit
            rev: v0.5.6
            hooks:
              - id: ruff
                args: [--fix]
              - id: ruff-format
          - repo: https://github.com/pre-commit/mirrors-isort
            rev: v5.13.2
            hooks:
              - id: isort
        """).strip() + "\n")

    # mypy.ini
    if enable_mypy:
        (project_dir / "mypy.ini").write_text(dedent(f"""
        [mypy]
        python_version = {sys.version_info.major}.{sys.version_info.minor}
        strict = True
        warn_unused_ignores = True
        warn_redundant_casts = True
        warn_unused_configs = True
        namespace_packages = True
        explicit_package_bases = True
        mypy_path = src
        """).lstrip())

    # pyproject.toml
    (project_dir / "pyproject.toml").write_text(dedent(f"""
    [build-system]
    requires = ["setuptools>=68", "wheel"]
    build-backend = "setuptools.build_meta"

    [project]
    name = "{pkg_name.replace('_','-')}"
    version = "0.1.0"
    description = "Bootstrapped Python project"
    readme = "README.md"
    requires-python = ">=3.9"
    authors = [{{name = "Your Name"}}]
    dependencies = []

    [tool.black]
    line-length = 100
    target-version = ["py311", "py310", "py39"]

    [tool.isort]
    profile = "black"
    line_length = 100
    float_to_top = true
    src_paths = ["src"]

    [tool.ruff]
    target-version = "py311"
    line-length = 100
    src = ["src", "tests"]
    extend-exclude = ["build", "dist", ".venv"]
    lint.select = ["E", "F", "I", "UP", "B", "SIM"]
    lint.ignore = ["E501"]
    format.quote-style = "double"

    [tool.pytest.ini_options]
    minversion = "7.0"
    addopts = "-q"
    testpaths = ["tests"]
    """).lstrip())

    # requirements.in / dev.in
    (project_dir / "requirements.in").write_text("# Add your runtime dependencies here\n")
    (project_dir / "requirements-dev.in").write_text(dedent("\n".join(DEV_ONLY)).lstrip())

def pip_install(python_exec: Path, packages: list[str]):
    run([str(python_exec), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    if packages:
        run([str(python_exec), "-m", "pip", "install", *packages])

def compile_requirements(python_exec: Path, project_dir: Path):
    # Compile base and dev requirements if pip-tools exists
    try:
        run([str(python_exec), "-m", "piptools", "--version"])
    except subprocess.CalledProcessError:
        print("pip-tools not installed; skipping compilation.")
        return

    base_in = project_dir / "requirements.in"
    dev_in = project_dir / "requirements-dev.in"
    base_txt = project_dir / "requirements.txt"
    dev_txt = project_dir / "requirements-dev.txt"

    run([str(python_exec), "-m", "piptools", "compile", str(base_in), "--output-file", str(base_txt)])
    run([str(python_exec), "-m", "piptools", "compile", str(dev_in), "--extra", "dev", "--output-file", str(dev_txt)])
    # Install dev requirements by default
    run([str(python_exec), "-m", "pip", "install", "-r", str(dev_txt)])

def install_precommit(python_exec: Path, project_dir: Path):
    if not (project_dir / ".pre-commit-config.yaml").exists():
        return
    try:
        run([str(python_exec), "-m", "pre_commit", "install"], cwd=project_dir)
    except subprocess.CalledProcessError:
        print("pre-commit installation failed (non-fatal).")

def main():
    parser = argparse.ArgumentParser(description="Bootstrap a Python project with venv and tooling.")
    parser.add_argument("project_name", help="Project/package name (e.g., awesome_project)")
    parser.add_argument("--python", help="Python executable to use for venv (default: current)")
    parser.add_argument("--dir", dest="directory", help="Target directory (default: ./<project_name>)")
    parser.add_argument("--no-mypy", action="store_true", help="Skip mypy")
    parser.add_argument("--no-precommit", action="store_true", help="Skip pre-commit setup")
    parser.add_argument("--no-piptools", action="store_true", help="Skip pip-tools and compilation")
    args = parser.parse_args()

    pkg_name = args.project_name.replace("-", "_")
    target_dir = Path(args.directory) if args.directory else Path.cwd() / args.project_name
    target_dir.mkdir(parents=True, exist_ok=True)

    venv_dir = target_dir / ".venv"
    if venv_dir.exists():
        print(f"Virtual env already exists at {venv_dir}. Reusing it.")
    else:
        py = args.python or sys.executable
        run([py, "-m", "venv", str(venv_dir)])

    py_exec = venv_python(venv_dir)

    # Install base tooling
    base_tools = TOOLS.copy()
    if args.no_mypy and "mypy" in base_tools:
        base_tools.remove("mypy")
    if args.no_precommit and "pre-commit" in base_tools:
        base_tools.remove("pre-commit")
    if args.no_piptools and "pip-tools" in base_tools:
        base_tools.remove("pip-tools")

    pip_install(py_exec, base_tools)

    # Scaffold files
    make_files(target_dir, pkg_name, enable_mypy=not args.no_mypy, enable_precommit=not args.no_precommit)

    # Optionally compile requirements
    if not args.no_piptools:
        compile_requirements(py_exec, target_dir)

    # Git + pre-commit
    ensure_git(target_dir)
    if not args.no_precommit:
        install_precommit(py_exec, target_dir)

    print("\nDone! Next steps:")
    print(f"  cd {target_dir}")
    if platform.system() == "Windows":
        print(r"  .venv\Scripts\activate")
    else:
        print(r"  source .venv/bin/activate")
    print("  pytest -q")

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"\nERROR running command: {e}")
        sys.exit(1)
