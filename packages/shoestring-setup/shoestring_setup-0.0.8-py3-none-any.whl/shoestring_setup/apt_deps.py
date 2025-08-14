from shoestring_setup import display
from shoestring_setup import operations as ops

class InstallAptDependencies:
    def __init__(self, os_env, force):
        self.os_env = os_env
        self.force = force

    def install(self):
        self._do_install()

    def _do_install(self):
        display.print_header("APT dependencies ...")

        ops.subprocess_exec(
            "Refreshed package index",
            ["sudo", "apt-get", "-qq", "update"],
        )

        ops.subprocess_exec(
            "Ensured emoji fonts are installed",
            ["sudo", "apt-get", "-qq", "install", "fonts-noto-color-emoji"],
        )

        ops.subprocess_exec(
            "Ensured git is installed",
            ["sudo", "apt-get", "-qq", "install", "git"],
        )

        ops.subprocess_exec(
            "Ensured pipx is installed",
            ["sudo", "apt-get", "-qq", "install", "pipx"],
        )

    def update(self):
        self._do_install()
