import platform
import subprocess
import time
import math

_WINDOWS_IMPORTS_AVAILABLE = False
if platform.system() == 'Windows':
    try:
        import ctypes
        from ctypes import wintypes
        import win32con
        import win32gui
        import win32api
        _WINDOWS_IMPORTS_AVAILABLE = True
    except ImportError:
        pass

# ===== DWM (via Visible Frame Bounds) =====
if _WINDOWS_IMPORTS_AVAILABLE:
    DWMWA_EXTENDED_FRAME_BOUNDS = 9
    _dwmapi = ctypes.windll.dwmapi

    class RECT(ctypes.Structure):
        _fields_ = [('left', ctypes.c_long),
                    ('top', ctypes.c_long),
                    ('right', ctypes.c_long),
                    ('bottom', ctypes.c_long)]


def execute_os(mac_command, win_command):

    os_name = platform.system()

    if os_name == 'Darwin':
        return mac_command
    elif os_name == 'Windows': 
        return win_command
    else:
        print("Unsupported Operating System (Not MacOS or Windows)")
        return False


def check_fullscreen_mac() -> bool:

    script = r'''
    try
      tell application "System Events"
        set frontProc to first application process whose frontmost is true
        tell frontProc
          -- Prefer the actually focused window
          set targetWin to missing value
          try
            set targetWin to value of attribute "AXFocusedWindow"
          end try
          -- Fall back to a standard window, then any window
          if targetWin is missing value then
            set stdWins to every window whose subrole is "AXStandardWindow"
            if stdWins is not {} then set targetWin to item 1 of stdWins
          end if
          if targetWin is missing value then
            if (count of windows) > 0 then set targetWin to window 1
          end if

          if targetWin is missing value then return false

          if exists attribute "AXFullScreen" of targetWin then
            return (value of attribute "AXFullScreen" of targetWin)
          else
            return false
          end if
        end tell
      end tell
    on error
      return false
    end try
    '''

    try:
        r = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, check=True) 
        return r.stdout.strip().lower() == 'true' # Fullscreen = True, Otherwise = False
    except subprocess.CalledProcessError:
        return False


def exit_fullscreen_mac():

    script = '''
    tell application "System Events"
        key code 3 using {command down, control down}
    end tell
    '''

    subprocess.run(['osascript', '-e', script], check=True) # Exit Fullscreen via (CMD + CTRL + F)
    return True


def check_exit_fullscreen_win(hwnd):
    """Restore if Window is Maximized so it can be Resized/Moved."""
    placement = win32gui.GetWindowPlacement(hwnd)
    if placement[1] == win32con.SW_SHOWMAXIMIZED:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)


def set_dpi_aware_win():
    """Ensure Coordinates Match Physical Pixels on High-DPI Displays."""
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def get_effective_dimension_win(hwnd):
    """(L, T, R, B) for the Monitor Containing hwnd, Excluding Taskbar."""
    monitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
    mi = win32api.GetMonitorInfo(monitor)  # Keys: "Monitor" & "Work"
    return mi['Work']


def get_visible_frame_win(hwnd):
    """
    (L, T, R, B) of the Visible Window Frame (Excludes Drop Shadow).
    Falls back to GetWindowRect if DWM Call Fails.
    """
    rect = RECT()
    hr = _dwmapi.DwmGetWindowAttribute(
        wintypes.HWND(hwnd),
        ctypes.c_uint(DWMWA_EXTENDED_FRAME_BOUNDS),
        ctypes.byref(rect),
        ctypes.sizeof(rect),
    )
    if hr == 0:
        return rect.left, rect.top, rect.right, rect.bottom
    return win32gui.GetWindowRect(hwnd)


def apply_effective_bounds_win(hwnd, target_ltrb):
    """
    Move/Resize so the Visible Frame Aligns with the Target Rect.
    1) Set Outer Bounds Roughly, 2) Measure Insets, 3) Correct.
    """
    L, T, R, B = target_ltrb
    W = max(1, R - L)
    H = max(1, B - T)

    win32gui.SetWindowPos(
        hwnd, 0, L, T, W, H,
        win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW
    )

    visL, visT, visR, visB = get_visible_frame_win(hwnd)
    outL, outT, outR, outB = win32gui.GetWindowRect(hwnd)

    inset_left   = visL - outL
    inset_top    = visT - outT
    inset_right  = outR - visR
    inset_bottom = outB - visB

    corrL = L - inset_left
    corrT = T - inset_top
    corrW = W + inset_left + inset_right
    corrH = H + inset_top + inset_bottom

    corrL = int(round(corrL))
    corrT = int(round(corrT))
    corrW = max(1, int(round(corrW)))
    corrH = max(1, int(round(corrH)))

    win32gui.SetWindowPos(
        hwnd, 0, corrL, corrT, corrW, corrH,
        win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW
    )


def apply_window_fraction_win(rx, ry, rw, rh):
    """
    Snap the Foreground Window to a Rectangle Expressed as Fractions
    of the Monitor Work Area: (rx, ry, rw, rh) in [0..1].
    """
    set_dpi_aware_win()
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd or not win32gui.IsWindowVisible(hwnd):
        raise RuntimeError("No visible foreground window found.")

    check_exit_fullscreen_win(hwnd)

    waL, waT, waR, waB = get_effective_dimension_win(hwnd)
    waW = waR - waL
    waH = waB - waT

    L = waL + int(math.floor(waW * rx))
    T = waT + int(math.floor(waH * ry))
    R = waL + int(math.floor(waW * (rx + rw)))
    B = waT + int(math.floor(waH * (ry + rh)))

    R = max(R, L + 1)
    B = max(B, T + 1)

    apply_effective_bounds_win(hwnd, (L, T, R, B))


# Tool 01 - Minimise Window
def minimise_window():
    run = execute_os(minimise_window_mac, minimise_window_win)
    return run()


def minimise_window_mac():

    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
        end tell
        tell application frontApp
            activate
        end tell
        tell application "System Events"
            tell process frontApp
                set frontWindow to window 1
                set value of attribute "AXMinimized" of frontWindow to true
            end tell
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error Minimising Window: {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def minimise_window_win():

    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        result = ctypes.windll.user32.ShowWindow(hwnd, 6)

        if result:
            return True
        else:
            print("Failed to Minimise Window")
            return False
 
    except Exception as e:
        print(f"Error Minimising Window: {e}")
        return False


# Tool 02 - Maximise Window
def maximise_window():
    run = execute_os(maximise_window_mac, maximise_window_win)
    return run()


def maximise_window_mac():
  
    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = r'''
        use framework "AppKit"
        use scripting additions

        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            -- Get main screen's visible frame (excludes menu bar & Dock)
            set scr to current application's NSScreen's mainScreen()
            set vFrame to scr's visibleFrame()
            set sFrame to scr's frame()

            set visX to (current application's NSMinX(vFrame)) as integer
            set visW to (current application's NSWidth(vFrame)) as integer
            set visYBottom to (current application's NSMinY(vFrame)) as integer
            set visH to (current application's NSHeight(vFrame)) as integer
            set screenH to (current application's NSHeight(sFrame)) as integer

            -- Convert Cocoa bottom-left origin to AppleScript's top-left
            set visTopY to (screenH - (visYBottom + visH))

            tell frontProc
              -- Prefer focused window; fall back to a standard window, then any
              set targetWin to missing value
              try
                set targetWin to value of attribute "AXFocusedWindow"
              end try
              if targetWin is missing value then
                set stdWins to every window whose subrole is "AXStandardWindow"
                if stdWins is not {} then set targetWin to item 1 of stdWins
              end if
              if targetWin is missing value then
                if (count of windows) > 0 then set targetWin to window 1
              end if

              if targetWin is not missing value then
                set canResize to true
                try
                  set canResize to (value of attribute "AXResizable" of targetWin)
                end try

                if canResize then
                  set position of targetWin to {visX, visTopY}
                  set size of targetWin to {visW, visH}
                end if
              end if
            end tell
          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error Maximising Window: {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def maximise_window_win():
    """Put the Foreground Window into the OS 'Maximize/Bordered Fullscreen' State (Bordered, Taskbar Visible)."""
    set_dpi_aware_win()
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd or not win32gui.IsWindowVisible(hwnd):
        raise RuntimeError("No visible foreground window found.")
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)


# Tool 03 - Fullscreen Window
def fullscreen_window():
    run = execute_os(fullscreen_window_mac, fullscreen_window_win)
    return run()


def fullscreen_window_mac():

    try:
        script = '''
        tell application "System Events"
            tell process (name of first application process whose frontmost is true)
                set frontWindow to window 1
                set value of attribute "AXFullScreen" of frontWindow to true
            end tell
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error to Fullscreen Window: {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def fullscreen_window_win():
    """Put the Foreground Window into the OS 'Maximize/Bordered Fullscreen' State (Bordered, Taskbar Visible)."""
    set_dpi_aware_win()
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd or not win32gui.IsWindowVisible(hwnd):
        raise RuntimeError("No visible foreground window found.")
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)


# Tool 04 - Left 1/2 Screen
def left_half_window():
    run = execute_os(left_half_window_mac, left_half_window_win)
    return run()


def left_half_window_mac():

    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)
        
    try:
        script = r'''
        use framework "AppKit"
        use scripting additions
        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            set scr to current application's NSScreen's mainScreen()
            set vFrame to scr's visibleFrame()
            set sFrame to scr's frame()

            set visX to (current application's NSMinX(vFrame)) as integer
            set visW to (current application's NSWidth(vFrame)) as integer
            set visYBottom to (current application's NSMinY(vFrame)) as integer
            set visH to (current application's NSHeight(vFrame)) as integer
            set screenH to (current application's NSHeight(sFrame)) as integer

            set visTopY to (screenH - (visYBottom + visH))
            set halfW to (round (visW / 2))

            tell frontProc
              set targetWin to missing value
              try
                set targetWin to value of attribute "AXFocusedWindow"
              end try
              if targetWin is missing value then
                set stdWins to every window whose subrole is "AXStandardWindow"
                if stdWins is not {} then set targetWin to item 1 of stdWins
              end if
              if targetWin is missing value then
                if (count of windows) > 0 then set targetWin to window 1
              end if

              if targetWin is not missing value then
                set canResize to true
                try
                  set canResize to (value of attribute "AXResizable" of targetWin)
                end try
                if canResize then
                  set position of targetWin to {visX, visTopY}
                  set size of targetWin to {halfW, visH}
                end if
              end if
            end tell
          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (left half): {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def left_half_window_win():
    apply_window_fraction_win(0.0, 0.0, 0.5, 1.0)


# Tool 05 - Right 1/2 Screen
def right_half_window():
    run = execute_os(right_half_window_mac, right_half_window_win)
    return run()


def right_half_window_mac():

    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = r'''
        use framework "AppKit"
        use scripting additions
        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            set scr to current application's NSScreen's mainScreen()
            set vFrame to scr's visibleFrame()
            set sFrame to scr's frame()

            set visX to (current application's NSMinX(vFrame)) as integer
            set visW to (current application's NSWidth(vFrame)) as integer
            set visYBottom to (current application's NSMinY(vFrame)) as integer
            set visH to (current application's NSHeight(vFrame)) as integer
            set screenH to (current application's NSHeight(sFrame)) as integer

            set visTopY to (screenH - (visYBottom + visH))
            set halfW to (round (visW / 2))

            tell frontProc
              set targetWin to missing value
              try
                set targetWin to value of attribute "AXFocusedWindow"
              end try
              if targetWin is missing value then
                set stdWins to every window whose subrole is "AXStandardWindow"
                if stdWins is not {} then set targetWin to item 1 of stdWins
              end if
              if targetWin is missing value then
                if (count of windows) > 0 then set targetWin to window 1
              end if

              if targetWin is not missing value then
                set canResize to true
                try
                  set canResize to (value of attribute "AXResizable" of targetWin)
                end try
                if canResize then
                  set position of targetWin to {visX + halfW, visTopY}
                  set size of targetWin to {visW - halfW, visH}
                end if
              end if
            end tell
          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (right half): {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def right_half_window_win():
    apply_window_fraction_win(0.5, 0.0, 0.5, 1.0)


# Tool 06 - Left 1/3 Screen
def left_third_window():
    run = execute_os(left_third_window_mac, left_third_window_win)
    return run()


def left_third_window_mac():

    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)
        
    try:
        script = r'''
        use framework "AppKit"
        use scripting additions
        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            set scr to current application's NSScreen's mainScreen()
            set vFrame to scr's visibleFrame()
            set sFrame to scr's frame()

            set visX to (current application's NSMinX(vFrame)) as integer
            set visW to (current application's NSWidth(vFrame)) as integer
            set visYBottom to (current application's NSMinY(vFrame)) as integer
            set visH to (current application's NSHeight(vFrame)) as integer
            set screenH to (current application's NSHeight(sFrame)) as integer
            set visTopY to (screenH - (visYBottom + visH))

            -- third boundaries (rounded so thirds tile perfectly)
            set b0 to round (visW * 0.0 / 3.0)
            set b1 to round (visW * 1.0 / 3.0)
            set x0 to visX + b0
            set x1 to visX + b1
            set sliceW to (x1 - x0)

            tell frontProc
              set targetWin to missing value
              try
                set targetWin to value of attribute "AXFocusedWindow"
              end try
              if targetWin is missing value then
                set stdWins to every window whose subrole is "AXStandardWindow"
                if stdWins is not {} then set targetWin to item 1 of stdWins
              end if
              if targetWin is missing value then if (count of windows) > 0 then set targetWin to window 1

              if targetWin is not missing value then
                set canResize to true
                try
                  set canResize to (value of attribute "AXResizable" of targetWin)
                end try
                if canResize then
                  set position of targetWin to {x0, visTopY}
                  set size of targetWin to {sliceW, visH}
                end if
              end if
            end tell
          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (left third): {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def left_third_window_win():
    apply_window_fraction_win(0.0, 0.0, 1.0/3.0, 1.0)


# Tool 07 - Middle 1/3 Screen
def middle_third_window():
    run = execute_os(middle_third_window_mac, middle_third_window_win)
    return run()


def middle_third_window_mac():

    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = r'''
        use framework "AppKit"
        use scripting additions
        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            set scr to current application's NSScreen's mainScreen()
            set vFrame to scr's visibleFrame()
            set sFrame to scr's frame()

            set visX to (current application's NSMinX(vFrame)) as integer
            set visW to (current application's NSWidth(vFrame)) as integer
            set visYBottom to (current application's NSMinY(vFrame)) as integer
            set visH to (current application's NSHeight(vFrame)) as integer
            set screenH to (current application's NSHeight(sFrame)) as integer
            set visTopY to (screenH - (visYBottom + visH))

            set b1 to round (visW * 1.0 / 3.0)
            set b2 to round (visW * 2.0 / 3.0)
            set x0 to visX + b1
            set x1 to visX + b2
            set sliceW to (x1 - x0)

            tell frontProc
              set targetWin to missing value
              try
                set targetWin to value of attribute "AXFocusedWindow"
              end try
              if targetWin is missing value then
                set stdWins to every window whose subrole is "AXStandardWindow"
                if stdWins is not {} then set targetWin to item 1 of stdWins
              end if
              if targetWin is missing value then if (count of windows) > 0 then set targetWin to window 1

              if targetWin is not missing value then
                set canResize to true
                try
                  set canResize to (value of attribute "AXResizable" of targetWin)
                end try
                if canResize then
                  set position of targetWin to {x0, visTopY}
                  set size of targetWin to {sliceW, visH}
                end if
              end if
            end tell
          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (middle third): {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def middle_third_window_win():
    apply_window_fraction_win(1.0/3.0, 0.0, 1.0/3.0, 1.0)


# Tool 08 - Right 1/3 Screen
def right_third_window():
    run = execute_os(right_third_window_mac, right_third_window_win)
    return run()


def right_third_window_mac():

    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = r'''
        use framework "AppKit"
        use scripting additions
        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            set scr to current application's NSScreen's mainScreen()
            set vFrame to scr's visibleFrame()
            set sFrame to scr's frame()

            set visX to (current application's NSMinX(vFrame)) as integer
            set visW to (current application's NSWidth(vFrame)) as integer
            set visYBottom to (current application's NSMinY(vFrame)) as integer
            set visH to (current application's NSHeight(vFrame)) as integer
            set screenH to (current application's NSHeight(sFrame)) as integer
            set visTopY to (screenH - (visYBottom + visH))

            set b2 to round (visW * 2.0 / 3.0)
            set x0 to visX + b2
            set x1 to visX + visW
            set sliceW to (x1 - x0)

            tell frontProc
              set targetWin to missing value
              try
                set targetWin to value of attribute "AXFocusedWindow"
              end try
              if targetWin is missing value then
                set stdWins to every window whose subrole is "AXStandardWindow"
                if stdWins is not {} then set targetWin to item 1 of stdWins
              end if
              if targetWin is missing value then if (count of windows) > 0 then set targetWin to window 1

              if targetWin is not missing value then
                set canResize to true
                try
                  set canResize to (value of attribute "AXResizable" of targetWin)
                end try
                if canResize then
                  set position of targetWin to {x0, visTopY}
                  set size of targetWin to {sliceW, visH}
                end if
              end if
            end tell
          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (right third): {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def right_third_window_win():
    apply_window_fraction_win(2.0/3.0, 0.0, 1.0/3.0, 1.0)


# Tool 09 - Top 1/2 Screen
def top_half_window():
    run = execute_os(top_half_window_mac, top_half_window_win)
    return run()


def top_half_window_mac():

    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = r'''
        use framework "AppKit"
        use scripting additions

        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            -- Visible frame (excludes menu bar & Dock) in Cocoa coords (origin = bottom-left)
            set scr to current application's NSScreen's mainScreen()
            set vFrame to scr's visibleFrame()
            set sFrame to scr's frame()

            set visX to (current application's NSMinX(vFrame)) as integer
            set visW to (current application's NSWidth(vFrame)) as integer
            set visYBottom to (current application's NSMinY(vFrame)) as integer
            set visH to (current application's NSHeight(vFrame)) as integer
            set screenH to (current application's NSHeight(sFrame)) as integer

            -- Convert Cocoa bottom-left Y to AppleScript's top-left Y
            set visTopY to (screenH - (visYBottom + visH))
            set halfH to (round (visH / 2))

            tell frontProc
              -- Prefer focused window; fall back to standard window, then any
              set targetWin to missing value
              try
                set targetWin to value of attribute "AXFocusedWindow"
              end try
              if targetWin is missing value then
                set stdWins to every window whose subrole is "AXStandardWindow"
                if stdWins is not {} then set targetWin to item 1 of stdWins
              end if
              if targetWin is missing value then
                if (count of windows) > 0 then set targetWin to window 1
              end if

              if targetWin is not missing value then
                set canResize to true
                try
                  set canResize to (value of attribute "AXResizable" of targetWin)
                end try
                if canResize then
                  set position of targetWin to {visX, visTopY}
                  set size of targetWin to {visW, halfH}
                end if
              end if
            end tell
          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error Resizing Window via Top Half: {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def top_half_window_win():
    apply_window_fraction_win(0.0, 0.0, 1.0, 0.5)


# Tool 10 - Bottom 1/2 Screen
def bottom_half_window():
    run = execute_os(bottom_half_window_mac, bottom_half_window_win)
    return run()


def bottom_half_window_mac():

    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = r'''
        use framework "AppKit"
        use scripting additions

        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            -- Visible frame (excludes menu bar & Dock) in Cocoa coords (origin = bottom-left)
            set scr to current application's NSScreen's mainScreen()
            set vFrame to scr's visibleFrame()
            set sFrame to scr's frame()

            set visX to (current application's NSMinX(vFrame)) as integer
            set visW to (current application's NSWidth(vFrame)) as integer
            set visYBottom to (current application's NSMinY(vFrame)) as integer
            set visH to (current application's NSHeight(vFrame)) as integer
            set screenH to (current application's NSHeight(sFrame)) as integer

            -- Convert Cocoa bottom-left Y to AppleScript's top-left Y
            set visTopY to (screenH - (visYBottom + visH))
            set halfH to (round (visH / 2))

            tell frontProc
              -- Prefer focused window; fall back to standard window, then any
              set targetWin to missing value
              try
                set targetWin to value of attribute "AXFocusedWindow"
              end try
              if targetWin is missing value then
                set stdWins to every window whose subrole is "AXStandardWindow"
                if stdWins is not {} then set targetWin to item 1 of stdWins
              end if
              if targetWin is missing value then
                if (count of windows) > 0 then set targetWin to window 1
              end if

              if targetWin is not missing value then
                set canResize to true
                try
                  set canResize to (value of attribute "AXResizable" of targetWin)
                end try
                if canResize then
                  -- y = top of visible area + half its height
                  set position of targetWin to {visX, visTopY + halfH}
                  -- height = remaining half of visible area
                  set size of targetWin to {visW, visH - halfH}
                end if
              end if
            end tell
          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error Resizing Window via Bottom Half: {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def bottom_half_window_win():
    apply_window_fraction_win(0.0, 0.5, 1.0, 0.5)


# Tool 11 - Top Left 1/4 Screen
def top_left_quadrant_window():
    run = execute_os(top_left_quadrant_window_mac, top_left_quadrant_window_win)
    return run()


def top_left_quadrant_window_mac():

    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = r'''
        use framework "AppKit"
        use scripting additions
        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            set scr to current application's NSScreen's mainScreen()
            set vFrame to scr's visibleFrame()
            set sFrame to scr's frame()

            set visX to (current application's NSMinX(vFrame)) as integer
            set visW to (current application's NSWidth(vFrame)) as integer
            set visYBottom to (current application's NSMinY(vFrame)) as integer
            set visH to (current application's NSHeight(vFrame)) as integer
            set screenH to (current application's NSHeight(sFrame)) as integer

            set visTopY to (screenH - (visYBottom + visH))
            set halfW to (round (visW / 2))
            set halfH to (round (visH / 2))

            tell frontProc
              set targetWin to missing value
              try
                set targetWin to value of attribute "AXFocusedWindow"
              end try
              if targetWin is missing value then
                set stdWins to every window whose subrole is "AXStandardWindow"
                if stdWins is not {} then set targetWin to item 1 of stdWins
              end if
              if targetWin is missing value then
                if (count of windows) > 0 then set targetWin to window 1
              end if
              if targetWin is not missing value then
                set canResize to true
                try
                  set canResize to (value of attribute "AXResizable" of targetWin)
                end try
                if canResize then
                  set position of targetWin to {visX, visTopY}
                  set size of targetWin to {halfW, halfH}
                end if
              end if
            end tell
          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (top-left quadrant): {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def top_left_quadrant_window_win():
    apply_window_fraction_win(0.0, 0.0, 0.5, 0.5)


# Tool 12 - Top Right 1/4 Screen
def top_right_quadrant_window():
    run = execute_os(top_right_quadrant_window_mac, top_right_quadrant_window_win)
    return run()


def top_right_quadrant_window_mac():
    if check_fullscreen_mac():
        exit_fullscreen_mac(); time.sleep(0.4)
    try:
        script = r'''
        use framework "AppKit"
        use scripting additions
        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            set scr to current application's NSScreen's mainScreen()
            set vFrame to scr's visibleFrame()
            set sFrame to scr's frame()

            set visX to (current application's NSMinX(vFrame)) as integer
            set visW to (current application's NSWidth(vFrame)) as integer
            set visYBottom to (current application's NSMinY(vFrame)) as integer
            set visH to (current application's NSHeight(vFrame)) as integer
            set screenH to (current application's NSHeight(sFrame)) as integer

            set visTopY to (screenH - (visYBottom + visH))
            set halfW to (round (visW / 2))
            set halfH to (round (visH / 2))

            tell frontProc
              set targetWin to missing value
              try
                set targetWin to value of attribute "AXFocusedWindow"
              end try
              if targetWin is missing value then
                set stdWins to every window whose subrole is "AXStandardWindow"
                if stdWins is not {} then set targetWin to item 1 of stdWins
              end if
              if targetWin is missing value then
                if (count of windows) > 0 then set targetWin to window 1
              end if
              if targetWin is not missing value then
                set canResize to true
                try
                  set canResize to (value of attribute "AXResizable" of targetWin)
                end try
                if canResize then
                  set position of targetWin to {visX + halfW, visTopY}
                  set size of targetWin to {visW - halfW, halfH}
                end if
              end if
            end tell
          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (top-right quadrant): {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def top_right_quadrant_window_win():
    apply_window_fraction_win(0.5, 0.0, 0.5, 0.5)


# Tool 13 - Bottom Left 1/4 Screen
def bottom_left_quadrant_window():
    run = execute_os(bottom_left_quadrant_window_mac, bottom_left_quadrant_window_win)
    return run()


def bottom_left_quadrant_window_mac():

    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)

    try:
        script = r'''
        use framework "AppKit"
        use scripting additions
        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            set scr to current application's NSScreen's mainScreen()
            set vFrame to scr's visibleFrame()
            set sFrame to scr's frame()

            set visX to (current application's NSMinX(vFrame)) as integer
            set visW to (current application's NSWidth(vFrame)) as integer
            set visYBottom to (current application's NSMinY(vFrame)) as integer
            set visH to (current application's NSHeight(vFrame)) as integer
            set screenH to (current application's NSHeight(sFrame)) as integer

            set visTopY to (screenH - (visYBottom + visH))
            set halfW to (round (visW / 2))
            set halfH to (round (visH / 2))

            tell frontProc
              set targetWin to missing value
              try
                set targetWin to value of attribute "AXFocusedWindow"
              end try
              if targetWin is missing value then
                set stdWins to every window whose subrole is "AXStandardWindow"
                if stdWins is not {} then set targetWin to item 1 of stdWins
              end if
              if targetWin is missing value then
                if (count of windows) > 0 then set targetWin to window 1
              end if
              if targetWin is not missing value then
                set canResize to true
                try
                  set canResize to (value of attribute "AXResizable" of targetWin)
                end try
                if canResize then
                  set position of targetWin to {visX, visTopY + halfH}
                  set size of targetWin to {halfW, visH - halfH}
                end if
              end if
            end tell
          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (bottom-left quadrant): {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def bottom_left_quadrant_window_win():
    apply_window_fraction_win(0.0, 0.5, 0.5, 0.5)


# Tool 14 - Bottom Right 1/4 Screen
def bottom_right_quadrant_window():
    run = execute_os(bottom_right_quadrant_window_mac, bottom_right_quadrant_window_win)
    return run()


def bottom_right_quadrant_window_mac():

    if check_fullscreen_mac():
        exit_fullscreen_mac()
        time.sleep(0.4)
        
    try:
        script = r'''
        use framework "AppKit"
        use scripting additions
        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            set scr to current application's NSScreen's mainScreen()
            set vFrame to scr's visibleFrame()
            set sFrame to scr's frame()

            set visX to (current application's NSMinX(vFrame)) as integer
            set visW to (current application's NSWidth(vFrame)) as integer
            set visYBottom to (current application's NSMinY(vFrame)) as integer
            set visH to (current application's NSHeight(vFrame)) as integer
            set screenH to (current application's NSHeight(sFrame)) as integer

            set visTopY to (screenH - (visYBottom + visH))
            set halfW to (round (visW / 2))
            set halfH to (round (visH / 2))

            tell frontProc
              set targetWin to missing value
              try
                set targetWin to value of attribute "AXFocusedWindow"
              end try
              if targetWin is missing value then
                set stdWins to every window whose subrole is "AXStandardWindow"
                if stdWins is not {} then set targetWin to item 1 of stdWins
              end if
              if targetWin is missing value then
                if (count of windows) > 0 then set targetWin to window 1
              end if
              if targetWin is not missing value then
                set canResize to true
                try
                  set canResize to (value of attribute "AXResizable" of targetWin)
                end try
                if canResize then
                  set position of targetWin to {visX + halfW, visTopY + halfH}
                  set size of targetWin to {visW - halfW, visH - halfH}
                end if
              end if
            end tell
          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (bottom-right quadrant): {e}")
        return False
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return False


def bottom_right_quadrant_window_win():
    apply_window_fraction_win(0.5, 0.5, 0.5, 0.5)


# Tool 15 - Left 2/3 Screen
def left_two_thirds_window():
    run = execute_os(left_two_thirds_window_mac, left_two_thirds_window_win)
    return run()


def left_two_thirds_window_mac():

    if check_fullscreen_mac():
        exit_fullscreen_mac(); time.sleep(0.4)

    try:
        script = r'''
        use framework "AppKit"
        use scripting additions
        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            -- Visible frame (excludes menu bar & Dock)
            set scr to current application's NSScreen's mainScreen()
            set vFrame to scr's visibleFrame()
            set sFrame to scr's frame()

            set visX to (current application's NSMinX(vFrame)) as integer
            set visW to (current application's NSWidth(vFrame)) as integer
            set visYBottom to (current application's NSMinY(vFrame)) as integer
            set visH to (current application's NSHeight(vFrame)) as integer
            set screenH to (current application's NSHeight(sFrame)) as integer
            set visTopY to (screenH - (vyBottom + visH)) of {vyBottom:visYBottom}

            -- boundaries in thirds (rounded so all slices tile perfectly)
            set b2 to round (visW * 2.0 / 3.0)
            set x0 to visX
            set x1 to visX + b2
            set sliceW to (x1 - x0)

            tell frontProc
              -- pick a good target window
              set targetWin to missing value
              try
                set targetWin to value of attribute "AXFocusedWindow"
              end try
              if targetWin is missing value then
                set stdWins to every window whose subrole is "AXStandardWindow"
                if stdWins is not {} then set targetWin to item 1 of stdWins
              end if
              if targetWin is missing value then if (count of windows) > 0 then set targetWin to window 1

              if targetWin is not missing value then
                set canResize to true
                try
                  set canResize to (value of attribute "AXResizable" of targetWin)
                end try
                if canResize then
                  set position of targetWin to {x0, visTopY}
                  set size of targetWin to {sliceW, visH}
                end if
              end if
            end tell
          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript','-e',script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (left 2/3): {e}"); return False
    except Exception as e:
        print(f"Unexpected Error: {e}"); return False


def left_two_thirds_window_win():
    apply_window_fraction_win(0.0, 0.0, 2.0/3.0, 1.0)


# Tool 16 - Right 2/3 Screen
def right_two_thirds_window():
    run = execute_os(right_two_thirds_window_mac, right_two_thirds_window_win)
    return run()


def right_two_thirds_window_mac():
    if check_fullscreen_mac():
        exit_fullscreen_mac(); time.sleep(0.4)
    try:
        script = r'''
        use framework "AppKit"
        use scripting additions
        tell application "System Events"
          set frontProc to first application process whose frontmost is true
          try
            -- Visible frame (excludes menu bar & Dock)
            set scr to current application's NSScreen's mainScreen()
            set vFrame to scr's visibleFrame()
            set sFrame to scr's frame()

            set visX to (current application's NSMinX(vFrame)) as integer
            set visW to (current application's NSWidth(vFrame)) as integer
            set visYBottom to (current application's NSMinY(vFrame)) as integer
            set visH to (current application's NSHeight(vFrame)) as integer
            set screenH to (current application's NSHeight(sFrame)) as integer
            set visTopY to (screenH - (vyBottom + visH)) of {vyBottom:visYBottom}

            -- boundaries in thirds (rounded so all slices tile perfectly)
            set b1 to round (visW * 1.0 / 3.0)
            set x0 to visX + b1
            set x1 to visX + visW
            set sliceW to (x1 - x0)

            tell frontProc
              -- pick a good target window
              set targetWin to missing value
              try
                set targetWin to value of attribute "AXFocusedWindow"
              end try
              if targetWin is missing value then
                set stdWins to every window whose subrole is "AXStandardWindow"
                if stdWins is not {} then set targetWin to item 1 of stdWins
              end if
              if targetWin is missing value then if (count of windows) > 0 then set targetWin to window 1

              if targetWin is not missing value then
                set canResize to true
                try
                  set canResize to (value of attribute "AXResizable" of targetWin)
                end try
                if canResize then
                  set position of targetWin to {x0, visTopY}
                  set size of targetWin to {sliceW, visH}
                end if
              end if
            end tell
          on error errMsg number errNum
            error "UI scripting failed: " & errNum & " — " & errMsg
          end try
        end tell
        '''
        subprocess.run(['osascript','-e',script], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error (right 2/3): {e}"); return False
    except Exception as e:
        print(f"Unexpected Error: {e}"); return False


def right_two_thirds_window_win():
    apply_window_fraction_win(1.0/3.0, 0.0, 2.0/3.0, 1.0)
