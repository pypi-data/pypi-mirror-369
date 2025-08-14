import argparse
import keyword
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


def normalize_package_name(raw_name: str) -> str:
    """
    Normalize a user-provided name to a valid Python package directory name.

    Rules:
    - lowercase
    - spaces and hyphens -> underscore
    - remove all non [a-z0-9_]
    - collapse multiple underscores
    - strip leading/trailing underscores
    - must not start with a digit; if so, prefix with 'api_'
    - must not be a Python keyword; if so, suffix with '_pkg'
    """
    name = raw_name.strip().lower()
    name = name.replace("-", "_").replace(" ", "_")
    name = re.sub(r"[^a-z0-9_]", "", name)
    name = re.sub(r"_+", "_", name).strip("_")
    if not name:
        name = "api_app"
    if name[0].isdigit():
        name = f"api_{name}"
    if keyword.iskeyword(name):
        name = f"{name}_pkg"
    return name


def project_has_pyproject(cwd: Path) -> bool:
    return (cwd / "pyproject.toml").exists()


def detect_package_manager() -> Tuple[str, List[str]]:
    """
    Detect an available Python package manager and return a tuple of:
    (manager_name, base_command_list)

    Preference order:
    - uv (uses 'uv add' if project, else 'uv pip install')
    - poetry (uses 'poetry add')
    - pipenv (uses 'pipenv install')
    - pip via current interpreter (uses 'python -m pip install')
    - pip3 (fallback)
    - pip (last resort)
    """
    cwd = Path.cwd()

    if shutil.which("uv") is not None:
        # We'll decide subcommand later based on presence of pyproject
        return ("uv", ["uv"]) 

    if shutil.which("poetry") is not None:
        return ("poetry", ["poetry", "add"]) 

    if shutil.which("pipenv") is not None:
        return ("pipenv", ["pipenv", "install"]) 

    # Prefer pip of the running interpreter
    return ("pip", [sys.executable, "-m", "pip", "install"]) 


def install_packages(packages: Iterable[str], ensure_upgrade: bool = True) -> None:
    manager, base = detect_package_manager()
    pkg_list = list(packages)

    try:
        if manager == "uv":
            args: List[str]
            if project_has_pyproject(Path.cwd()):
                # Add to project dependencies
                args = base + ["add"] + pkg_list
            else:
                # Install into current environment
                args = base + ["pip", "install"]
                if ensure_upgrade:
                    args.append("--upgrade")
                args += pkg_list
            subprocess.run(args, check=True)
            return

        if manager == "poetry":
            args = base + pkg_list
            subprocess.run(args, check=True)
            return

        if manager == "pipenv":
            args = base + pkg_list
            subprocess.run(args, check=True)
            return

        # pip (default)
        args = base.copy()
        if ensure_upgrade:
            args.append("--upgrade")
        args += pkg_list
        subprocess.run(args, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"Failed to install packages with {manager}: {exc}", file=sys.stderr)
        # Last-ditch fallback to 'pip' binary if available and not already used
        if manager != "pip" and shutil.which("pip") is not None:
            try:
                fallback = ["pip", "install"]
                if ensure_upgrade:
                    fallback.append("--upgrade")
                fallback += pkg_list
                subprocess.run(fallback, check=True)
            except subprocess.CalledProcessError as exc2:
                print(f"Fallback 'pip' install failed: {exc2}", file=sys.stderr)
                raise
        else:
            raise


def ensure_codename_available() -> None:
    try:
        import codename  # type: ignore # noqa: F401
    except Exception:
        install_packages(["codename"])  # install when name generation is needed


def generate_api_name(max_attempts: int = 5) -> str:
    ensure_codename_available()
    try:
        import codename  # type: ignore
        attempt = 0
        while attempt < max_attempts:
            base = normalize_package_name(codename.generate())
            if not base.endswith("_api"):
                base = f"{base}_api"
            if not Path(base).exists():
                return base
            attempt += 1
        # As a fallback, append numeric suffixes
        for i in range(1, 1000):
            candidate = f"api_{i}"
            if not Path(candidate).exists():
                return candidate
    except Exception:
        # Final fallback without codename
        return "api_app"


def copy_example_api_to(target_dir: Path) -> None:
    """Copy example FastAPI project from package resources into target_dir.

    - Copies contents of canonmap/_example_usage/app -> target_dir
    - Copies canonmap/_example_usage/.env.example -> CWD/.env.example if present
      If not present, generates a sensible template.
    """
    base = Path(__file__).resolve().parent
    example_root = base / "_example_usage"
    app_src = example_root / "app"
    if not app_src.exists():
        raise FileNotFoundError(f"Example app directory not found at {app_src}")

    # Copy app directory tree
    if target_dir.exists():
        raise FileExistsError(f"Target directory '{target_dir}' already exists")

    shutil.copytree(
        app_src,
        target_dir,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".DS_Store"),
        dirs_exist_ok=False,
    )

    # Copy or generate .env.example at project root
    env_src = example_root / ".env.example"
    env_dest = Path.cwd() / ".env.example"
    if env_src.exists():
        if not env_dest.exists():
            shutil.copy2(env_src, env_dest)
    else:
        # Generate a minimal template if not provided in package
        if not env_dest.exists():
            env_contents = (
                "# Example environment configuration for canonmap FastAPI app\n"
                "MYSQL_HOST=localhost\n"
                "MYSQL_USER=root\n"
                "MYSQL_PASSWORD=\n"
                "MYSQL_DATABASE=canonmap\n"
            )
            env_dest.write_text(env_contents, encoding="utf-8")


def handle_make_api(args: argparse.Namespace) -> None:
    # Ensure FastAPI and Uvicorn are installed
    required = ["fastapi", "uvicorn"]
    if args.name is None:
        required.append("codename")
    install_packages(required)

    if args.name:
        package_name = normalize_package_name(args.name)
        target = Path.cwd() / package_name
        if target.exists():
            print(
                f"Directory '{package_name}' already exists. Please choose a different name.",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        # Try up to 5 attempts to find an available directory name
        attempts = 0
        package_name = ""
        target = None  # type: ignore
        while attempts < 5:
            candidate = generate_api_name(max_attempts=1)
            target_path = Path.cwd() / candidate
            if not target_path.exists():
                package_name = candidate
                target = target_path
                break
            attempts += 1
        if not package_name:
            print("Failed to find an available directory name after 5 attempts.", file=sys.stderr)
            sys.exit(1)

    copy_example_api_to(target)  # type: ignore[arg-type]

    print(f"Copied example FastAPI app to '{package_name}'.")
    print(f".env.example written to project root if not present.")
    print(
        f"Run it with: uvicorn {package_name}.main:app --reload (or your preferred ASGI runner)"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cm", description="CanonMap CLI")
    subparsers = parser.add_subparsers(dest="command")

    # cm make ...
    make_parser = subparsers.add_parser("make", help="Scaffold helpers")
    make_sub = make_parser.add_subparsers(dest="make_command")

    # cm make api
    api_parser = make_sub.add_parser("api", help="Create a FastAPI app scaffold")
    api_parser.add_argument(
        "--name",
        type=str,
        default=None,
        help="Optional API package name (will be normalized to a valid Python package)",
    )
    api_parser.set_defaults(func=handle_make_api)

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


