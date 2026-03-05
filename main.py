#!/usr/bin/env python3
"""Script para gestionar git worktrees del repositorio actual."""

import subprocess
import sys
from pathlib import Path

# ============================================================
# CONFIGURACION - Modifica estas variables segun tus necesidades
# ============================================================

# Worktrees a CREAR: lista de nombres de rama.
# Se creara un worktree por cada rama en la carpeta "trees/<nombre>".
WORKTREES_TO_CREATE: list[str] = [
    "feature/auth",
    "feature/api",
    "fix/login-bug",
    "holaa/prueba",
    "holaa/prueba2",
]

# Worktrees a ELIMINAR: lista de nombres de rama.
# Se eliminara el worktree y opcionalmente la rama asociada.
WORKTREES_TO_REMOVE: list[str] = [
    "feature/auth",
    "feature/api",
    "fix/login-bug",
    "holaa/prueba",
    "holaa/prueba2",
]

# Si True, tambien elimina la rama local al borrar un worktree.
DELETE_BRANCH_ON_REMOVE: bool = True

# Carpeta donde se crean los worktrees (relativa a la raiz del repo).
TREES_DIR: str = "trees"

# ============================================================


def get_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())


def branch_exists(branch: str) -> bool:
    result = subprocess.run(
        ["git", "branch", "--list", branch],
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


def worktree_list() -> list[str]:
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip().splitlines()


def create_worktree(branch: str, trees_path: Path) -> None:
    # Sanitizar nombre de rama para usarlo como nombre de carpeta
    folder_name = branch.replace("/", "-")
    worktree_path = trees_path / folder_name

    if worktree_path.exists():
        print(f"  [SKIP] Ya existe: {worktree_path}")
        return

    if branch_exists(branch):
        # La rama existe, crear worktree apuntando a ella
        subprocess.run(
            ["git", "worktree", "add", str(worktree_path), branch],
            check=True,
        )
    else:
        # Crear rama nueva con el worktree
        subprocess.run(
            ["git", "worktree", "add", "-b", branch, str(worktree_path)],
            check=True,
        )

    print(f"  [OK] Creado: {worktree_path} -> rama '{branch}'")


def remove_worktree(branch: str, trees_path: Path) -> None:
    folder_name = branch.replace("/", "-")
    worktree_path = trees_path / folder_name

    if not worktree_path.exists():
        print(f"  [SKIP] No existe: {worktree_path}")
        return

    subprocess.run(
        ["git", "worktree", "remove", str(worktree_path), "--force"],
        check=True,
    )
    print(f"  [OK] Eliminado worktree: {worktree_path}")

    if DELETE_BRANCH_ON_REMOVE and branch_exists(branch):
        subprocess.run(
            ["git", "branch", "-D", branch],
            check=True,
        )
        print(f"  [OK] Eliminada rama: '{branch}'")


def main() -> None:
    repo_root = get_repo_root()
    trees_path = repo_root / TREES_DIR
    trees_path.mkdir(exist_ok=True)

    if WORKTREES_TO_REMOVE:
        print(f"\n--- Eliminando {len(WORKTREES_TO_REMOVE)} worktree(s) ---")
        for branch in WORKTREES_TO_REMOVE:
            try:
                remove_worktree(branch, trees_path)
            except subprocess.CalledProcessError as e:
                print(f"  [ERROR] No se pudo eliminar '{branch}': {e}", file=sys.stderr)

    if WORKTREES_TO_CREATE:
        print(f"\n--- Creando {len(WORKTREES_TO_CREATE)} worktree(s) ---")
        for branch in WORKTREES_TO_CREATE:
            try:
                create_worktree(branch, trees_path)
            except subprocess.CalledProcessError as e:
                print(f"  [ERROR] No se pudo crear '{branch}': {e}", file=sys.stderr)

    # Mostrar estado actual
    print("\n--- Worktrees activos ---")
    subprocess.run(["git", "worktree", "list"])


if __name__ == "__main__":
    main()
