# !/usr/bin/python3
# coding: utf-8

# Default device url and port
DEFAULT_URL = "http://localhost"
DEFAULT_PORT = 6790

# Default pack config
DEFAULT_JAR_FILENAME = "uia2.jar"
DEFAULT_PUSH_PATH = f"/data/local/tmp/udt/{DEFAULT_JAR_FILENAME}"
DEFAULT_PACK_NAME = "com.wetest.uia2.Main"
BUSYBOX_PUSH_PATH = "/data/local/tmp"
BUSYBOX_NAME = "busybox"

DEFAULT_RUNNER_TIMEOUT = 30

# Logger tags
GET_TAG = "[GET]"
POST_TAG = "[POST]"
INIT_TAG = "[INIT]"
FIND_TAG = "[FIND]"

# API args value restrictions
ALL_ORIENTATION = ["LANDSCAPE", "PORTRAIT"]
ALL_ROTATION = [0, 90, 180, 270]
ALL_FLING = ["UP", "DOWN", "LEFT", "RIGHT"]

# Available element identifiers
LEGACY_WEB_ELEMENT_IDENTIFIER = "ELEMENT"
WEB_ELEMENT_IDENTIFIER = "element-6066-11e4-a52e-4f735466cecf"

# Android shell contents
ANDORID_SDK_IMCOMPATIBLE_VERSION = 25
ALPHAS, NUMS, TIMES = "[a-zA-Z0-9_]*", "[0-9]*", "[0-9][0-9]:[0-9][0-9]:[0-9][0-9]"
PROCESS_PATTERN = f"({ALPHAS})[ ]*({NUMS})[ ]*({NUMS})[ ]*({NUMS})[ ]*({TIMES})(.*)({TIMES})[ ]*(.*)"
PROCESS_PATTERN_LOW_VER = (
    f"({ALPHAS})[ ]*({NUMS})[ ]*({NUMS})[ ]*({NUMS})[ ]*({NUMS})[ ]*({ALPHAS})[ ]*({NUMS})[ ]*[a-ZA-Z]*[ ]*(.*)"
)
PROCESS_PATTERN_BUSYBOX = f"({NUMS})[ ]*({NUMS})[ ]*({NUMS}:{NUMS})[ ]*(.*)"
PROCESS_KEYS = ["uid", "pid", "ppid", "c", "stime", "tty", "time", "name"]
PROCESS_KEYS_LOW_VER = ["user", "pid", "ppid", "vsize", "rss", "wchan", "pc", "name"]
PROCESS_KEYS_BUSYBOX = ["pid", "user", "time", "name"]
LSOF_PATTERN = f"({ALPHAS})[ ]*({NUMS})[ ]*(.*)"
SERVER_START_NOTICE = "[AppiumUiAutomator2Server] Starting Server"

# Server runner message
APPIUM_SERVER_READY = "---------------- Appium Server is Ready -----------------"
APPIUM_SERVER_FAILS = "-------------- Appium Server Starts Failed --------------"

# Request header
HEADER_KEY, HEADER_VAL = "Content-Type", "application/json"

# OPPO install consts
WETEST_TMP_FOLDER_NAME = "00000_wetest"
OPPO_TOGGLE_RISK_VERSION = 33
OPPO_FILE_MANAGER_NAME = "com.coloros.filemanager"
OPPO_LAUNCH_FILE_MANAGER = f"monkey -p {OPPO_FILE_MANAGER_NAME} -c android.intent.category.LAUNCHER 1"
OPPO_APK_PUSH_PATH = f"/sdcard/{WETEST_TMP_FOLDER_NAME}"
OPPO_NEWOS_TOGGLE_RISK_BUTTON_ID = "com.oplus.appdetail:id/safe_guard_checkbox"
OPPO_NEWOS_COMFIRM_BUTTON_ID = "com.oplus.appdetail:id/view_bottom_guide_continue_install_btn"
OPPO_SOME_FILE_MANAGER_TAG_NAMES = [
    "所有文件",
    "All Files",
]
