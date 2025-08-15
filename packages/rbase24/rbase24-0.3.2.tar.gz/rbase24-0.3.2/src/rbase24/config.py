import os
from pathlib import Path
from configparser import ConfigParser


class Base24ViewerConfig:
    def __init__(self, config_file: Path | None = None):
        self.config_file = config_file
        self._scheme_dir: Path | None = None

    @property
    def scheme_dir(self):
        if self._scheme_dir is None:
            self._scheme_dir = self._get_scheme_dir(self.config_file)
        return self._scheme_dir

    def _get_scheme_dir(self, config_file: Path | None = None) -> Path | None:
        scheme_dir = os.environ.get("BASE24_SCHEME_DIR", None)
        if scheme_dir is not None:
            return Path(scheme_dir)

        if config_file is None:
            config_file = Base24ViewerConfig.default_config_path()

        try:
            cfg = self._read_config(config_file)
        except IOError:
            cfg = None

        if cfg is None:
            return Base24ViewerConfig.default_scheme_dir()

        scheme_dir = cfg.get("rbase24", "scheme_dir")
        if scheme_dir is not None:
            return Path(scheme_dir)
        return None

    def _read_config(self, config_file: Path | None = None) -> ConfigParser:
        if config_file is None:
            cf = Base24ViewerConfig.default_config_path()
        else:
            cf = config_file

        if not cf.exists():
            raise IOError(f"Unable to find config file {cf}")

        cp = ConfigParser()
        cp.read(cf)
        return cp

    @staticmethod
    def default_scheme_dir() -> Path:
        xdg_data_home = Path(
            os.environ.get("XDG_DATA_HOME", "~/.local/share/")
        ).expanduser()
        return xdg_data_home / "tinted-themeing" / "schemes"

    @staticmethod
    def default_config_path() -> Path:
        xdg_config = os.environ.get("XDG_CONFIG_HOME", "~/.config")
        xdg_config_dir = Path(xdg_config).expanduser()

        config_dir = xdg_config_dir / "rbase24"
        config_file = config_dir / "config.ini"
        return config_file

    @staticmethod
    def default_config():
        return dict(scheme_dir=Base24ViewerConfig.default_scheme_dir())
