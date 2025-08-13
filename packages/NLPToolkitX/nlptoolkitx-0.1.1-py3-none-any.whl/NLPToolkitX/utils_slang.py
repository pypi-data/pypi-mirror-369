from typing import IO
import io

# Prefer modern importlib.resources on 3.9+, fall back to pkgutil for 3.7/3.8
try:
    from importlib.resources import files as _res_files

    def _open_pkg_text(pkg: str, name: str) -> IO[str]:
        return (_res_files(pkg) / name).open("r", encoding="utf-8")

except Exception:
    import pkgutil

    def _open_pkg_text(pkg: str, name: str) -> IO[str]:
        data = pkgutil.get_data(pkg, name)
        if data is None:
            return io.StringIO("")  # empty stream on failure
        return io.StringIO(data.decode("utf-8"))


def load_builtin_slang() -> dict:
    """
    Load NLPToolkitX/slang.txt that is included as package data.
    Lines: KEY=Replacement   (KEY is matched case-insensitively)
    Blank lines and lines starting with # are ignored.
    """
    mapping = {}
    try:
        with _open_pkg_text("NLPToolkitX", "slang.txt") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    mapping[k.strip().upper()] = v.strip()
    except Exception:
        return {}
    return mapping
