import pcbnew
import os
import wx

class EmmettAction( pcbnew.ActionPlugin ):
 
    def defaults( self ):
        self.name = "Emmett Element Router"
        self.category = "Modify PCB"
        self.description = "Heating Element Trace Router"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "./emmett_icon.png")

    def Run( self ):
        wx.MessageBox("Hi! This is Emmett!")
        return


