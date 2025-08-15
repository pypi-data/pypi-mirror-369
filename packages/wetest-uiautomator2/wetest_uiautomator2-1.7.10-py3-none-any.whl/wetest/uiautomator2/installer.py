# !/usr/bin/python3
# coding: utf-8

import os
import time
import subprocess

from multiprocessing import Process

from .core._const import *
from .core._utils import execute

from .android_driver import AndroidDriver
from .server_runner import ServerRunner


class Installer:
    def __init__(self, runner: ServerRunner, driver: AndroidDriver) -> None:
        """
        Init Installer.

        Args:
            runner (ServerRunner): A ServerRunner instance.
            driver (AndroidDriver): An AndroidDriver instance.
        """
        self.runner = runner
        self.driver = driver

    def install(self, apk_path: str, package_name: str):
        """
        An complex apk installer with strategies that are compatible with different phone manufactures.

        Args:
            apk_path (str): The path of the package to be installed.
            package_name (str): The name (com.company.id) of the package to be installed.
        """
        self.runner.d.uninstall(package_name)
        brand, version = self.runner._brand.upper(), self.runner._version
        if brand == "OPPO":
            """
            OPPO phone with OS older than Android 13 requires OPPO account's password when installing apks
            Therefore push apk files to sdcard, then use automation to install and click pop-ups

            However, OPPO phone with newer OS will not trigger the password popup during adb installation
            Instead, a confirm page with a toggle button that reads "已知悉风险" will pop up
            Thus use adbinstall + AndroidDriver to dismiss the pop-up instead.
            """
            if version >= OPPO_TOGGLE_RISK_VERSION:
                self._oppo_install_target_new(apk_path)
            else:
                self._oppo_install_target_old(apk_path)
        elif brand == "VIVO":
            """
            VIVO Phone need a special installer to perform shadow installation.
            """
            self._vivo_install_target(apk_path)
        elif brand == "REDMI" or brand == "XIAOMI":
            """
            Using abd install on MIUI will trigger a pop-up window from the bottom of the screen
            The pop-up counts down 10 seconds before dismissing itself
            """
            self._xiaomi_install_target(apk_path)
        else:
            p = Process(target=self.runner.d.install, args=(apk_path,))
            p.start()
            p.join()
        time.sleep(5)
        self.runner.shell(f"am force-stop {package_name}")
        time.sleep(1)
        self.runner.expect().set_permission(package_name).readwrite()
        self.runner.shell(f"monkey -p {package_name} 1")
        time.sleep(5)

    """ ===========================================================================
        NOTE: strategies HERE
        ===========================================================================
    """

    def _vivo_install_target(self, apk_path: str):
        """
        NOTE:
            The resource/vivo-* files are NOT INCLUDED in the source code, but in the Pypi wheel source.
            Download these binary files from: FIXME <links to be added>
        """
        print(f"vivo installing {apk_path}...")
        tool = ""
        if "MACOS" in self.runner.platform():
            tool = "resource/vivo-mac"
        elif "LINUX" in self.runner.platform():
            tool = "resource/vivo-linux-x86"
        elif "WINDOWS" in self.runner.platform():
            tool = "resource/vivo-win.exe"
        else:
            raise ValueError(f"Unknown platform: {self.runner.platform()}")
        path = os.path.join(os.path.dirname(__file__), tool)
        execute(f"{path} -s {self.runner.d.serial} -i {apk_path}")

    def _oppo_install_target_old(self, apk_path: str):
        # Push apk file
        self.runner.shell(f"am force-stop {OPPO_FILE_MANAGER_NAME}")
        self.runner.shell(f"mkdir {OPPO_APK_PUSH_PATH}")
        self.runner.push_file(apk_path, f"{OPPO_APK_PUSH_PATH}/{apk_path.split('/')[-1]}")
        # Open file browser;'
        self.runner.shell(OPPO_LAUNCH_FILE_MANAGER)
        time.sleep(5)
        # Automated clicks in file browser
        self.driver.expect().find(id="com.coloros.filemanager:id/action_file_browser", retry=10, interval=1000).click()
        if self.driver.inspect(text=OPPO_SOME_FILE_MANAGER_TAG_NAMES, timeout=2500, interval=500):
            self.driver.expect().find(text=OPPO_SOME_FILE_MANAGER_TAG_NAMES, retry=10, interval=1000).click()
        self.driver.expect().find(text=WETEST_TMP_FOLDER_NAME, retry=10, interval=1000).click()
        self.driver.expect().find(text=apk_path.split("/")[-1], retry=10, interval=1000).click()

        """
        FIXME: Wait for appium server click install fix. 
        Expected:
            self.driver.inspect(text="安装", timeout=-1)
            self.driver.find(text="安装", retry=10, interval=1000).click()
        Temporary:
            Hardcoded tap for now.
        """
        time.sleep(15)  # Wait for '安全检查'
        size = self.driver.window_size()
        brand, version = self.runner._brand.upper(), self.runner._version
        if brand == "OPPO" and version == 28:
            self.driver.tap(x=size.width * 0.75, y=size.height * 0.85)
        else:
            self.driver.tap(x=size.width * 0.75, y=size.height * 0.95)

        # Wait for installation finished and remove pushed file
        self.driver.inspect(text=["完成", "Done"], timeout=30000)
        self.driver.expect(show_log=True).find(text=["完成", "Done"], retry=10, interval=1000).click()
        self.runner.shell(f"rm -rf {OPPO_APK_PUSH_PATH}")

    def _oppo_install_target_new(self, apk_path: str):
        # Install app with a new thread
        p = Process(target=self.runner.d.install, args=(apk_path,))
        p.start()
        self.driver.inspect(id=OPPO_NEWOS_COMFIRM_BUTTON_ID, timeout=30000)
        # Skip pop-ups on OPPO Android 13 OS ("已知悉风险" and "继续安装")
        self.driver.expect().find(
            id=OPPO_NEWOS_TOGGLE_RISK_BUTTON_ID,
            retry=10,
            interval=1000,
        ).click()
        self.driver.expect().find(
            id=OPPO_NEWOS_COMFIRM_BUTTON_ID,
            retry=10,
            interval=1000,
        ).click()
        p.join()

    def _xiaomi_install_target(self, apk_path: str):
        p = Process(
            target=execute,
            args=(f"adb -s {self.runner.serial} install {apk_path}",),
        )
        p.start()
        self.driver.inspect(id="android:id/button2", interval=500, timeout=30000)
        self.driver.expect().find(id="android:id/button2", retry=10, interval=1000).click()  # Use Id selector
        p.join()
