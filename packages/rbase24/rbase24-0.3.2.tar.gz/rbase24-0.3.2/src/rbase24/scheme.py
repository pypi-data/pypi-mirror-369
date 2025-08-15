from pathlib import Path
from typing import Generator

import yaml
import slugify
from rbase24.typedefs import ColorScheme, SchemeDB, Palette


def load_scheme(scheme_file: Path) -> ColorScheme:
    with open(scheme_file, "r") as fp:
        data = yaml.load(fp.read(-1), yaml.SafeLoader)

        palette_data = data.get("palette", None)
        if palette_data is None:
            raise ValueError(
                f"Scheme file {scheme_file} must contain a 'palette' entry"
            )

        palette: Palette = {k: v.lower() for k, v in palette_data.items()}  # type: ignore

        system = data.get("system", None)
        if system is None:
            if len(palette) == 16:
                system = "base16"
            else:
                system = "base24"

        slug = data.get("slug", None)
        if slug is None:
            slug = slugify.slugify(scheme_file.stem)

        description = data.get("description", "")
        variant = data.get("variant", "unknown")

        return ColorScheme(
            name=data["name"],
            author=data["author"],
            system=system,
            slug=slug,
            description=description,
            variant=variant,
            palette=palette,
        )


def get_schemes(scheme_dir: Path, file_spec: str = "*") -> Generator[Path, None, None]:
    if "*" not in file_spec:
        fs = file_spec + "*"
    else:
        fs = file_spec

    if not fs.endswith(".yaml"):
        fs = fs + ".yaml"

    if not fs.startswith("**/"):
        fs = "**/" + fs

    return scheme_dir.glob(fs)


def list_schemes(scheme_dir: Path, file_spec: str = "*"):
    return tuple(get_schemes(scheme_dir, file_spec))


def load_schemes(scheme_dir: Path, file_spec: str = "*") -> SchemeDB:
    if not scheme_dir.exists():
        return {}

    return {
        scheme_file.name: load_scheme(scheme_file)
        for scheme_file in get_schemes(scheme_dir, file_spec)
    }
