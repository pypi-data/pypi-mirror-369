import textwrap
from pathlib import Path
from typing import Any

import jinja2

from pbi_core.logging import get_logger
from pbi_core.pydantic import BaseValidation

logger = get_logger()

PACKAGE_DIR = Path(__file__).parents[2]
assert PACKAGE_DIR.name == "pbi_core"


class PbiCoreStartupConfig(BaseValidation):
    cert_dir: Path
    msmdsrv_ini: Path
    msmdsrv_exe: Path
    workspace_dir: Path

    def model_post_init(self, __context: Any, /) -> None:
        if not self.cert_dir.is_absolute():
            self.cert_dir = PACKAGE_DIR / self.cert_dir
        if not self.msmdsrv_ini.is_absolute():
            self.msmdsrv_ini = PACKAGE_DIR / self.msmdsrv_ini
        if not self.msmdsrv_exe.is_absolute():
            self.msmdsrv_exe = PACKAGE_DIR / self.msmdsrv_exe
        if not self.workspace_dir.is_absolute():
            self.workspace_dir = PACKAGE_DIR / self.workspace_dir

    def msmdsrv_ini_template(self) -> jinja2.Template:
        return jinja2.Template(self.msmdsrv_ini.read_text())


def get_startup_config() -> PbiCoreStartupConfig:
    try:
        with (PACKAGE_DIR / "local" / "settings.json").open("r") as f:
            return PbiCoreStartupConfig.model_validate_json(f.read())
    except FileNotFoundError as e:
        msg = textwrap.dedent("""

        When loading a pbix file with pbi_core, the package needs one of the following:
            1. The package needs to be initialized once with "python -m pbi_core setup" to find the necessary SSAS
               files (currently broken)
            2. To be run while PowerBI Desktop is currently running, so that the SSAS server set up by PowerBI Desktop
               can be used
            3. The load_pbix function can be called with the `load_ssas=False` argument, which will not load the SSAS
               model and therefore not require the SSAS server to be set up.
        """)
        raise FileNotFoundError(msg) from e
