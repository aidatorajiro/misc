import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

def drawsomething(tmp=[1,3,9], len_conv=3, itr=20, amp=40, offset=0.01):
    for i in range(itr):
        tmp = np.convolve(tmp, np.floor(np.random.rand(len_conv)*amp) + offset)
    
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
import ctypes
import objc

win = plt.gcf().canvas.manager
winobj = ctypes.py_object(win)
winobj_addr = ctypes.addressof(winobj)
winobj_addr_resolve = ctypes.cast(winobj_addr, ctypes.POINTER(ctypes.c_void_p)).contents
class WinStruct(ctypes.Structure):
    _fields_ = [("pyobj", ctypes.c_void_p), ("manager", ctypes.c_void_p), ("win_ptr", ctypes.c_void_p)]
nswindow_ptr = ctypes.cast(winobj_addr_resolve.value, ctypes.POINTER(WinStruct)).contents.win_ptr
nswindow = objc.objc_object(c_void_p=ctypes.c_void_p(nswindow_ptr))
nswindow.setAlphaValue_(0.9)
nswindow.setOpaque_(False)

view = plt.gcf().canvas
viewobj = ctypes.py_object(view)
viewobj_addr = ctypes.addressof(viewobj)
viewobj_addr_resolve = ctypes.cast(viewobj_addr, ctypes.POINTER(ctypes.c_void_p)).contents
class ViewStruct(ctypes.Structure):
    _fields_ = [("pyobj", ctypes.c_void_p), ("manager", ctypes.c_void_p), ("view_ptr", ctypes.c_void_p)]
nsview_ptr = ctypes.cast(viewobj_addr_resolve.value, ctypes.POINTER(ViewStruct)).contents.view_ptr
nsview = objc.objc_object(c_void_p=ctypes.c_void_p(nsview_ptr))

vev = AppKit.NSVisualEffectView.alloc().init()

vev.setFrame_(nsview.bounds())

vev.setBlendingMode_(1)

vev.setMaterial_(np.random.randint(14))

vev.setState_(1)

vev.setAlphaValue_(0.9)

nswindow.contentView().addSubview_(vev)

from matplotlib.animation import FuncAnimation

def updateFrame(frame):
    print(frame)
    if frame % 60 == 30:
        drawsomething()
        vev.setMaterial_(np.random.randint(14))
        print("update material...")
        
    return []

ani = FuncAnimation(plt.gcf(), updateFrame, frames=None, blit=True, interval=1000/60)

plt.show()
