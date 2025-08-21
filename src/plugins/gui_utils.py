import wx

parent_window = None

def find_parent_window():
    global parent_window

    if parent_window is None:
        try:
            tops = wx.GetTopLevelWindows()
            for w in tops:
                title = w.GetTitle().lower()
                if ('pcbnew' in title or 'pcb editor' in title) and not 'python' in title:
                    parent_window = w
                    break
        except:
            pass
    
    return parent_window

def info_msg(msg):
    wx.MessageBox(msg, "Emmett", wx.OK | wx.ICON_INFORMATION, find_parent_window())

def error_msg(msg):
    wx.MessageBox(msg, "Emmett Error", wx.OK | wx.ICON_ERROR, find_parent_window())

