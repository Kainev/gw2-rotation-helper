import ctypes
import ctypes.wintypes
import threading

from typing import Callable

user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32

EVENT_SYSTEM_FOREGROUND = 0x0003
WINEVENT_OUTOFCONTEXT = 0x0000

WinEventProcType = ctypes.WINFUNCTYPE(
    None,
    ctypes.wintypes.HANDLE,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.HWND,
    ctypes.wintypes.LONG,
    ctypes.wintypes.LONG,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD
)


class FocusHook(object):
    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback

        self._hook = None
        self._current_window_title = ""

    def start(self):
        def callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
            length = user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            window_title = buff.value

            self.callback(window_title)

        WinEventProc = WinEventProcType(callback)

        ole32.CoInitialize(0)
        self._hook = user32.SetWinEventHook(
            EVENT_SYSTEM_FOREGROUND,
            EVENT_SYSTEM_FOREGROUND,
            0,
            WinEventProc,
            0,
            0,
            WINEVENT_OUTOFCONTEXT
        )
        if not self._hook:
            raise Exception("Failed to set hook")

        msg = ctypes.wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
            user32.TranslateMessage(msg)
            user32.DispatchMessage(msg)

        user32.UnhookWinEvent(self._hook)
        ole32.CoUninitialize()

    def stop(self):
        if self._hook:
            user32.UnhookWinEvent(self._hook)
            self._hook = None


if __name__ == "__main__":
    import time

    def window_focus_callback(window_title: str, focused):
        print(f"Window '{window_title}' focused", focused)

    focus_hook = FocusHook(["Guild Wars 2", "Notepad"], window_focus_callback)

    def run():
        focus_hook.start()

    hook_thread = threading.Thread(target=run)
    hook_thread.daemon = True
    hook_thread.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        focus_hook.stop()
