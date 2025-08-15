# ==============================================================================
#
# Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# All Rights Reserved.
# Confidential and Proprietary - Qualcomm Technologies, Inc.
#
# ==============================================================================
"""Electron launcher"""

import platform
import subprocess
from typing import List

from qairt_visualizer.core.launchers.base_ui_launcher_context import BaseUILauncherContext
from qairt_visualizer.core.launchers.models.process_attributes import ProcessAttributes
from qairt_visualizer.helpers.ui_helpers import find_ui_path_to


class ElectronLauncherContext(BaseUILauncherContext):
    """
    Concrete launcher class responsible for launching the Electron Visualization application.
    """

    def __init__(self):
        super().__init__()
        self.application_name = "qairt_visualizer"

    def _get_electron_path(self, caller_platform: str) -> str:
        app_extension = ""
        if caller_platform == "windows":
            app_extension = ".exe"
        elif caller_platform == "darwin":
            app_extension = ".app"
        return find_ui_path_to(f"dist/{self.application_name}{app_extension}")

    def is_same_process(self, process_attrs: ProcessAttributes, process_name: str) -> bool:
        return process_attrs.proc_name == process_name

    def launch(self) -> int:
        """Launches application in background at given port"""
        port = self.detect_port(5555)
        self._launch(["--port", f"{port}"])
        return port

    def launch_standalone(self) -> None:
        """Launches full application"""
        self._launch([])

    def _launch(self, extra_args: List[str]) -> None:
        p = platform.system().lower()
        if p == "darwin":
            extra_args = ["--args"] + extra_args if extra_args else extra_args
            command_line_args = ["open", "-a", self._get_electron_path(p)] + extra_args
        else:
            command_line_args = [self._get_electron_path(p)] + extra_args

        self.logger.debug("Launching Visualizer application.")
        self.logger.debug("Launch command: %s", command_line_args)
        proc = subprocess.Popen(  # pylint: disable=consider-using-with
            command_line_args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        self.set_pid(proc.pid)

    def extract_port_from_process(self, process_attrs: ProcessAttributes) -> int:
        app_extension = ""
        process_name = self.application_name

        if platform.system().lower() == "windows":
            app_extension = ".exe"

        process_name = process_name + app_extension
        cmdline = process_attrs.cmdline
        if self.is_same_process(process_attrs, process_name):
            if cmdline and "--port" in cmdline:
                port_index = cmdline.index("--port") + 1
                if port_index < len(cmdline):
                    port = cmdline[port_index]
                    return int(port)
            self.logger.debug("Couldn't extract port argument. CMD line args: %s", cmdline)
        return -1

    def get_ui_process_search_command_for_windows(self, process_name: str) -> str:
        return f"""
            Get-CimInstance Win32_Process | `
            Where-Object {{ $_.Name -match '{process_name}' }} | `
            Select-Object -First 1 ProcessId, Name, CommandLine | `
            ConvertTo-Json
        """

    async def after_launch_tasks(self, port: int) -> None:
        pass
