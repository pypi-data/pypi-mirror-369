import ctypes
import json
import os
from platform import machine
from sys import platform

if platform == 'darwin':
    file_ext = '-arm64.dylib' if machine() == "arm64" else '-x86.dylib'
elif platform in ('win32', 'cygwin'):
    file_ext = '-win64.dll' if 8 == ctypes.sizeof(ctypes.c_voidp) else '-win32.dll'
else:
    if machine() == "aarch64":
        file_ext = '-arm64.so'
    elif "x86" in machine():
        file_ext = '-x86.so'
    else:
        file_ext = '-amd64.so'


root_dir = os.path.abspath(os.path.dirname(__file__))
library = ctypes.cdll.LoadLibrary(f'{root_dir}/lib/libparser{file_ext}')

parse = library.parse
parse.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
parse.restype = ctypes.c_char_p

freeMemory = library.freeMemory
freeMemory.argtypes = [ctypes.c_char_p]

def readablity_go_parse(html_content, url="https://example.com"):
    if not url:
        url = "https://example.com"
    result = parse(html_content.encode('utf-8'), url.encode('utf-8'))
    if result:
        data = json.loads(ctypes.c_char_p(result).value.decode('utf-8'))
        freeMemory(data["id"].encode('utf-8'))
        return data
    return None