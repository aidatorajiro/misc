import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

tmp = [1,3,9,2,8]

for i in range(20):
    tmp = np.convolve(tmp, np.floor(np.random.rand(5)*10))

x = 0
for i in range(len(tmp)):
    x += i * tmp[i]

mean = x/tmp.sum()

x = 0
for i in range(len(tmp)):
    x += (i-mean)**2 * tmp[i]

std = np.sqrt(x/tmp.sum())

tmp_fix_y = tmp/tmp.sum()

norm_x = np.arange(0.0, len(tmp), 0.1)

norm_y = stats.norm.pdf(norm_x, mean, std)

plt.plot(norm_x, norm_y)

plt.plot(range(len(tmp_fix_y)), tmp_fix_y)

# requires pyobjc
import AppKit
import Foundation
import ctypes
import objc
import Cocoa

win = plt.gcf().canvas.manager

winobj = ctypes.py_object(win)

winobj_addr = ctypes.addressof(winobj)

winobj_addr_resolve = ctypes.cast(winobj_addr, ctypes.POINTER(ctypes.c_void_p)).contents

class WinStruct(ctypes.Structure):
    _fields_ = [("pyobj", ctypes.c_void_p), ("unknown", ctypes.c_void_p), ("win_ptr", ctypes.c_void_p)]

nswindow_ptr = ctypes.cast(winobj_addr_resolve.value, ctypes.POINTER(WinStruct)).contents.win_ptr

nswindow = objc.objc_object(c_void_p=ctypes.c_void_p(nswindow_ptr))

nswindow.setAlphaValue_(0.5)

"""

view = plt.gcf().canvas

viewobj = ctypes.py_object(view)

viewobj_addr = ctypes.addressof(viewobj)

viewobj_addr_resolve = ctypes.cast(viewobj_addr, ctypes.POINTER(ctypes.c_void_p)).contents

class ViewStruct(ctypes.Structure):
    _fields_ = [("pyobj", ctypes.c_void_p), ("unknown", ctypes.c_void_p), ("view_ptr", ctypes.c_void_p)]

nsview_ptr = ctypes.cast(viewobj_addr_resolve.value, ctypes.POINTER(ViewStruct)).contents.view_ptr

nsview = objc.objc_object(c_void_p=ctypes.c_void_p(nsview_ptr))

"""

plt.show()
