# Sqlite as FileSystem を作ろう！...とした形跡 (権限/CreationDisposition/TemplateFileなど多々未実装)

import sys
from ctypes import *

# constant definitions
MAX_MODULE_NAME32 = 255
MAX_PATH = 260

# class definitions
class MODULEENTRY32(Structure):
    _fields_ = [
        ("dwSize", c_ulong),
        ("th32ModuleID", c_ulong),
        ("th32ProcessID", c_ulong),
        ("GlblcntUsage", c_ulong),
        ("ProccntUsage", c_ulong),
        ("modBaseAddr", c_void_p),
        ("modBaseSize", c_ulong),
        ("hModule", c_ulong),
        ("szModule", c_char * MAX_MODULE_NAME32),
        ("szExePath", c_char * MAX_PATH)
    ]

class DUMMYUNIONNAME(Structure):
    _fields_ = [
        ("Characteristics", c_ulong),
        ("OriginalFirstThunk", c_ulong)
    ]

class IMAGE_IMPORT_DESCRIPTOR(Structure):
    _fields_ = [
        ("DummyUnionName", POINTER(DUMMYUNIONNAME)),
        ("TimeDateStamp", c_ulong),
        ("ForwarderChain", c_ulong),
        ("Name", c_ulong),
        ("FirstThunk", c_ulong)
    ]

# main overwrite func
def overwriteFunc(dllName, funcName, newFunc, funcArgTypes, funcResType):

    # get dll instances
    kernel32 = WinDLL("kernel32")
    dbghelp = WinDLL("dbghelp")
    
    # get original func address
    kernel32.GetModuleHandleA.restype = c_ulong
    kernel32.GetModuleHandleA.argtypes = (c_char_p, )
    handle = kernel32.GetModuleHandleA(dllName)
    
    kernel32.GetProcAddress.restype = c_void_p
    kernel32.GetProcAddress.argtypes = (c_ulong, c_char_p)
    orig_addr = kernel32.GetProcAddress(handle, funcName)
    
    # get process snapshot
    kernel32.GetCurrentProcessId.restype = c_ulong
    kernel32.GetCurrentProcessId.argtypes = ()
    pid = kernel32.GetCurrentProcessId()
    
    kernel32.CreateToolhelp32Snapshot.restype = c_ulong
    kernel32.CreateToolhelp32Snapshot.argtypes = (c_ulong, c_ulong)
    snap = kernel32.CreateToolhelp32Snapshot(8, pid)
    
    # convert python function to address
    TYPE_CREATEFILEW = CFUNCTYPE(funcResType, *funcArgTypes)
    new_addr = cast(TYPE_CREATEFILEW(newFunc), c_void_p).value # 今回のここすごポイント python is awesome!!!!
    
    # 
    dbghelp.ImageDirectoryEntryToData.restype = POINTER(IMAGE_IMPORT_DESCRIPTOR)
    dbghelp.ImageDirectoryEntryToData.argtypes = (c_ulong, c_bool, c_short, POINTER(c_ulong))
    
    # get module entries for process
    me = MODULEENTRY32()
    
    me.dwSize = sizeof(me)
    
    kernel32.Module32First.restype = c_bool
    kernel32.Module32First.argtypes = (c_ulong, c_void_p)
    kernel32.Module32Next.restype = c_bool
    kernel32.Module32Next.argtypes = (c_ulong, c_void_p)
    
    result = kernel32.Module32First(snap, byref(me))
    
    def overwrite():
        # get import descriptor for each module
        ulSize = c_ulong(0)
        pImportDesc = dbghelp.ImageDirectoryEntryToData(me.hModule, True, 1, pointer(ulSize))
        
        if not pImportDesc:
            return
        
        # find target dll in the module
        ind = 0
        while pImportDesc[ind].Name != 0:
            name = c_char_p(pImportDesc[ind].Name + me.hModule).value
            if name == b"kernel32.dll" or name == b"KERNEL32.dll":
                break
            ind += 1
        
        if pImportDesc.contents.Name == 0:
            return
        
        print("found target dll. overwriting...")
        
        # get module's metadata, then find target function
        
        pThunk = cast(me.hModule + pImportDesc.contents.FirstThunk, POINTER(c_ulong))
        
        old_flag = c_ulong(0)
        
        ind = 0
        while pThunk[ind]:
            if pThunk[ind] == orig_addr:
                print("found target function. overwriting...")
                # overwrite with calculated python func's address
                kernel32.VirtualProtect(pThunk[ind], 4, 0x4, pointer(old_flag))
                pThunk[ind] = new_addr
                kernel32.VirtualProtect(pThunk[ind], 4, old_flag, None)
            ind += 1
    
    while result:
        overwrite()
        result = kernel32.Module32Next(snap, byref(me))

handles = [None]

storage = {}

def cfw(lpFileName, dwDesiredAccess, dwShareMode, lpSecurityAttributes, dwCreationDisposition, dwFlagsAndAttributes, hTemplateFile):
    print("File open: %s, %X, %s, %s, %s, %s, %s" % (lpFileName, dwDesiredAccess, dwShareMode, lpSecurityAttributes, dwCreationDisposition, dwFlagsAndAttributes, hTemplateFile))
    handles.push((lpFileName, dwDesiredAccess, dwShareMode, lpSecurityAttributes, dwCreationDisposition, dwFlagsAndAttributes, hTemplateFile))
    return len(handles)

def wf(hFile, lpBuffer, nNumberOfBytesToWrite, lpNumberOfBytesWritten, lpOverlapped):
    info = handles[hFile]
    # ... plz do some security things ...
    storage[hFile] = lpBuffer[0:lpNumberOfBytesWritten[0]]
    return True

overwriteFunc(b'c:\\windows\\system32\\kernel32.dll', b'CreateFileW', cfw, (c_wchar_p, c_ulong, c_ulong, c_ulong, c_ulong, c_ulong, c_ulong), c_ulong)
overwriteFunc(b'c:\\windows\\system32\\kernel32.dll', b'WriteFile', wf, (c_ulong, c_char_p, c_ulong, POINTER(c_ulong), POINTER(c_ulong)), c_bool)

with open("testes.txt", "w") as f:
  f.write("AAAAA!")