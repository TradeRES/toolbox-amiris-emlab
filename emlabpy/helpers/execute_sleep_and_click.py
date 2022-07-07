import subprocess


SW_HIDE = 0
info = subprocess.STARTUPINFO()
info.dwFlags = subprocess.STARTF_USESHOWWINDOW
info.wShowWindow = SW_HIDE
subprocess.Popen(["python", "sleep_and_click.py"], creationflags=subprocess.CREATE_NEW_CONSOLE, startupinfo=info)
