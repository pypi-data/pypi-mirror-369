# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 18:52:20 2024

@author: Thomas
"""

from ctypes import windll, byref, Structure, WinError, POINTER, WINFUNCTYPE
from ctypes.wintypes import BOOL, HMONITOR, HDC, RECT, LPARAM, DWORD, BYTE, WCHAR, HANDLE

_MONITORENUMPROC = WINFUNCTYPE(BOOL, HMONITOR, HDC, POINTER(RECT), LPARAM)
 
 
class _PHYSICAL_MONITOR(Structure):
    _fields_ = [('handle', HANDLE),
                ('description', WCHAR * 128)]
 
 
def _iter_physical_monitors(close_handles=True):
    """Iterates physical monitors.
 
    The handles are closed automatically whenever the iterator is advanced.
    This means that the iterator should always be fully exhausted!
 
    If you want to keep handles e.g. because you need to store all of them and
    use them later, set `close_handles` to False and close them manually."""
 
    def callback(hmonitor, hdc, lprect, lparam):
        monitors.append(HMONITOR(hmonitor))
        return True
 
    monitors = []
    if not windll.user32.EnumDisplayMonitors(None, None, _MONITORENUMPROC(callback), None):
        raise WinError('EnumDisplayMonitors failed')
 
    for monitor in monitors:
        # Get physical monitor count
        count = DWORD()
        if not windll.dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(monitor, byref(count)):
            raise WinError()
        # Get physical monitor handles
        # print("Monitor count:" + str(count))
        physical_array = (_PHYSICAL_MONITOR * count.value)()
        if not windll.dxva2.GetPhysicalMonitorsFromHMONITOR(monitor, count.value, physical_array):
            raise WinError()
        for physical in physical_array:
            yield physical.handle
            if close_handles:
                if not windll.dxva2.DestroyPhysicalMonitor(physical.handle):
                    raise WinError()
 
 
def set_vcp_feature(monitor, code, value):
    """Sends a DDC command to the specified monitor.

    See this link for a list of commands:
ftp://ftp.cis.nctu.edu.tw/pub/csie/Software/X11/private/VeSaSpEcS/VESA_Document_Center_Monitor_Interface/mccsV3.pdf
    """
    if not windll.dxva2.SetVCPFeature(HANDLE(monitor), BYTE(code), DWORD(value)):
    # if not windll.dxva2.SetVCPFeature(HANDLE(monitor), code, value):
        raise WinError()

def get_vcp_feature(monitor, code):
    """Reads a VCP feature from the specified monitor."""
    current_value = DWORD()
    maximum_value = DWORD()
    if not windll.dxva2.GetVCPFeatureAndVCPFeatureReply(HANDLE(monitor), BYTE(code), None, byref(current_value), byref(maximum_value)):
        raise WinError()
    return current_value.value, maximum_value.value

def test_camera_vcp_support(monitor):
    """Test if monitor supports camera VCP codes (VCP 233)."""
    try:
        # 嘗試讀取 VCP code 233 (相機控制)
        current, maximum = get_vcp_feature(monitor, 0xE9)  # 0xE9 = 233
        print(f"  VCP test success: current={current}, maximum={maximum}")
        return True
    except Exception as e:
        # 如果讀取失敗，表示不支援此 VCP code
        print(f"  VCP test failed: {e}")
        return False

def test_all_monitors():
    """Test all monitors for camera VCP support."""
    print("=== 測試所有螢幕的相機 VCP 支援度 ===")
    handles = _iter_physical_monitors()
    set_cnt = 0
    results = []
    
    for handle in handles:
        print(f"Monitor {set_cnt}:")
        try:
            is_supported = test_camera_vcp_support(handle)
            results.append({
                "monitor": set_cnt,
                "supported": is_supported,
                "handle": handle
            })
            print(f"  Result: {'支援' if is_supported else '不支援'}")
        except Exception as e:
            print(f"  Error: {e}")
            results.append({
                "monitor": set_cnt,
                "supported": False,
                "error": str(e)
            })
        set_cnt += 1
    
    print(f"=== 總結: {len(results)} 個螢幕，{sum(1 for r in results if r['supported'])} 個支援相機控制 ===")
    return results

def vcp_setting_tool(vcp_code:int, feature_code:int) -> str:
    """
    Used to set vcp_code and feature_code to enable or disable background or auto framing.
    vcp_code is 233 and feature_code is 11520 for disable background blur,
    vcp_code is 233 and feature_code is 11521 for enable background blur,
    vcp_code is 233 and feature_code is 11264 for disable auto framing,
    vcp_code is 233 and feature_code is 11265 for enable auto framing.
    """
    # VCP (Virtual Control Panel) 
    info = "Camera setting is not work."
    handles = _iter_physical_monitors()
    set_cnt = 0
    for handle in handles:
        print(f"Monitor {set_cnt}: {test_camera_vcp_support(handle)}")
        # print(handle)
        # if set_cnt == 1: #change here to send to different monitor
        if set_cnt > 0: #change here to send to different monitor
            if vcp_code == 233 and feature_code == 11520:
                set_vcp_feature(handle, 0xE9, 0x2D00)
                info = "Backgroung blur disable completed"
            elif vcp_code == 233 and feature_code == 11521:
                set_vcp_feature(handle, 0xE9, 0x2D01)
                info = "Backgroung blur enable completed"
            elif vcp_code == 233 and feature_code == 11264:
                set_vcp_feature(handle, 0xE9, 0x2C00)
                info = "AutoFraming disable completed"
            elif vcp_code == 233 and feature_code == 11265:
                set_vcp_feature(handle, 0xE9, 0x2C01)
                info = "AutoFraming enable completed"
            else:
                ...            
        
        set_cnt = set_cnt + 1        
    return info

if __name__ == "__main__": 
    # 測試所有螢幕的 VCP 支援度
    test_all_monitors()
    
    # 測試設定功能（取消註解來測試）
    # vcp_setting_tool(233, 11520)
    # # Switch to SOFT-OFF, wait for the user to press return and then back to ON
    # handles = _iter_physical_monitors()
    # set_cnt = 0
    # for handle in handles:
    #     # if set_cnt == 0: #change here to send to different monitor
    #     if set_cnt > 0: #change here to send to different monitor
    #         # set_vcp_feature(handle, 0xE9, 0x2D00) #BLur Off
    #         # set_vcp_feature(handle, 0xE9, 0x2D01) #Blur On
    #         # set_vcp_feature(handle, 0x10, 5)
    #         # set_vcp_feature(handle, 0xDC, 0x0000) #Native
    #         # set_vcp_feature(handle, 0xDC, 0x0001) #sRGB
    #         # set_vcp_feature(handle, 0xDC, 0x0002) #BT.709
    #         # set_vcp_feature(handle, 0xDC, 0x0013) #Warm
    #         # set_vcp_feature(handle, 0xDC, 0x0014) #Cool
    #         # set_vcp_feature(handle, 0xDC, 0x0015) #Neutral
    #         # set_vcp_feature(handle, 0xEE, 0x02) #HP Enhane+
    #         # set_vcp_feature(handle, 0xDC, 0x0015)
    #     set_cnt = set_cnt + 1
        
        
        