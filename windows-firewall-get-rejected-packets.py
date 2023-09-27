# for outgoing packets
#  auditpol /set /subcategory:"{0CCE9226-69AE-11D9-BED3-505054503030}" /success:disable /failure:enable

# for incoming & outgoing packets (strangely it also catches certain established connection's packets...)
#  auditpol /set /subcategory:"{0CCE9225-69AE-11D9-BED3-505054503030}" /success:disable /failure:enable

#  auditpol /get /category:*

import subprocess

from ctypes import *

import xml.etree.ElementTree as ET

import signal

import sys

import re

winevt = CDLL("Wevtapi.dll")

secur32 = CDLL("Secur32.dll")

advapi32 = CDLL("Advapi32.dll")

k32 = CDLL("Kernel32.dll")

EVT_SUBSCRIBE_CALLBACK = CFUNCTYPE(c_uint, c_uint, c_void_p, c_ulonglong)

deny_log = []

def py_callback(code, ctx, ev_handle):
    buf_size = c_int(0)
    prop_vount = c_int(0)
    winevt.EvtRender(0, ev_handle, 1, 0, 0, pointer(buf_size), pointer(prop_vount))
    xml_data = create_unicode_buffer(buf_size.value)
    success = winevt.EvtRender(0, ev_handle, 1, buf_size, pointer(xml_data), pointer(buf_size), pointer(prop_vount))
    if not success:
        print_err_for_evt()
    else:
        xml = ET.fromstring(xml_data.value)
        ns = {"e": 'http://schemas.microsoft.com/win/2004/08/events/event'}
        evid = xml.find(".//e:EventID", ns).text
        if evid == '5157' or evid == '5152':
            app_info = {}

            def retrieve(x):
                query = xml.find(".//e:Data[@Name='%s']" % x, ns)
                if query is not None:
                    app_info[x] = query.text
            
            retrieve('Application')
            retrieve('SourceAddress')
            retrieve('DestAddress')
            retrieve('SourcePort')
            retrieve('DestPort')
            retrieve('ProcessId')

            # if the process is a service
            if isSvcHostService(app_info):
                services = enum_services()
                match_list = [(x.lpServiceName.contents.value, x.lpDisplayName.contents.value) for x in services if x.ServiceStatusProcess.dwProcessId == int(app_info['ProcessId'])]
                app_info['ServiceName'] = match_list[0][0]
                app_info['ServiceDisplayName'] = match_list[0][1]
                        
            deny_log.append(app_info)
    return 1

def isSvcHostService(app_info):
    return re.match(r'^\\device\\harddiskvolume\d+\\windows\\system32\\svchost.exe$', app_info['Application'])

def print_err_for_evt():
    e = k32.GetLastError()
    bufsize = c_int(1) # i think this is Windows bug somewhere...
    strdata = create_unicode_buffer('', bufsize.value)
    winevt.EvtGetExtendedStatus(bufsize.value, pointer(strdata), pointer(bufsize))
    strdata = create_unicode_buffer('', bufsize.value)
    winevt.EvtGetExtendedStatus(bufsize.value, pointer(strdata), pointer(bufsize))
    print("!!!ERROR!!!", "CODE", e, "MESSAGE", strdata.value)

def print_err_generic():
    e = k32.GetLastError()
    print("!!!ERROR!!!", "CODE", e)

def signal_handler(sig, frame):
    print()
    subprocess.run(['auditpol.exe', '/set', '/subcategory:{0CCE9225-69AE-11D9-BED3-505054503030}', '/success:disable', '/failure:disable'])
    sys.exit(0)

class SERVICE_STATUS_PROCESS(Structure):
    _fields_ = [
            ("dwServiceType", c_uint) , 
            ("dwCurrentState", c_uint) , 
            ("dwControlsAccepted", c_uint) , 
            ("dwWin32ExitCode", c_uint) , 
            ("dwServiceSpecificExitCode", c_uint) , 
            ("dwCheckPoint", c_uint) , 
            ("dwWaitHint", c_uint) , 
            ("dwProcessId", c_uint) , 
            ("dwServiceFlags", c_uint)]

class ENUM_SERVICE_STATUS_PROCESSW(Structure):
    _fields_ = [
            ("lpServiceName", POINTER(c_wchar * 256)),
            ("lpDisplayName", POINTER(c_wchar * 256)),
            ("ServiceStatusProcess", SERVICE_STATUS_PROCESS)]

def convert_type(value, totype):
    return cast(pointer(value), POINTER(totype)).contents

def enum_services():
    # maybe 0x3B? idk
    bufsize = c_int(0)
    entries = c_int(0)
    entry_start = c_int(0)
    success = advapi32.EnumServicesStatusExW(c_longlong(service_manager), 0, 0x30, 1, 0, 0, pointer(bufsize), pointer(entries), 0, 0)
    services_bytes = (c_char * bufsize.value)()
    success = advapi32.EnumServicesStatusExW(c_longlong(service_manager), 0, 0x30, 1, pointer(services_bytes), bufsize.value, pointer(bufsize), pointer(entries), pointer(entry_start), 0)

    if success == 0:
        print_err_generic()

    services_struct = convert_type(services_bytes, ENUM_SERVICE_STATUS_PROCESSW * entries.value)

    return services_struct

# ++++++
#  MAIN
# ++++++

if __name__ == '__main__':
    subprocess.run(['auditpol.exe', '/set', '/subcategory:{0CCE9225-69AE-11D9-BED3-505054503030}', '/success:disable', '/failure:enable'])

    callback = EVT_SUBSCRIBE_CALLBACK(lambda x, y, z: py_callback(x, y, z))

    winevt.EvtSubscribe.restype = c_ulonglong
    ev_handle_main = winevt.EvtSubscribe(None, None, r"Security", None, None, None, callback, 1)
    if ev_handle_main == 0:
        print_err_for_evt()

    database_name = create_unicode_buffer("ServicesActive")
    advapi32.OpenSCManagerW.restype = c_longlong
    service_manager = advapi32.OpenSCManagerW(0, pointer(database_name), 0x20014)
    if service_manager == 0:
        print_err_generic()

    signal.signal(signal.SIGINT, signal_handler)

    signal.signal(signal.SIGTERM, signal_handler)

    while True:
        x = input("> ").split()
        if len(x) > 0:
            match x[0]:
                case 'exit':
                    signal_handler(None, None)
                case 'help':
                    print('exit: Exit the application')
                    print('log: Print all packet drop log')
                    print('appset: List all denied applications path')
                    print('srvset: List all denied services name')
                    print('reset: reset logs')
                case 'log':
                    for x in deny_log:
                        print(x)
                case 'appset':
                    for x in set([x['Application'] for x in deny_log if 'Application' in x]):
                        print(x)
                case 'srvset':
                    for x in set([(x['ServiceName'], x['ServiceDisplayName']) for x in deny_log if 'ServiceName' in x]):
                        print(x)
                case 'reset':
                    deny_log = []

