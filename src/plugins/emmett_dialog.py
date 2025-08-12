# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-0-g80c4cb6)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class EmmettDialog
###########################################################################

class EmmettDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Emmett: Heater Trace Router", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE, name = u"ghetDialog" )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer3 = wx.BoxSizer( wx.VERTICAL )

        self.m_notebook2 = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_technicalPanel = wx.Panel( self.m_notebook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer51 = wx.BoxSizer( wx.VERTICAL )

        sbSizer6 = wx.StaticBoxSizer( wx.StaticBox( self.m_technicalPanel, wx.ID_ANY, u"Track Constraints (mm)" ), wx.VERTICAL )

        fgSizer1 = wx.FlexGridSizer( 0, 6, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_staticText24 = wx.StaticText( sbSizer6.GetStaticBox(), wx.ID_ANY, u"Track Width:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText24.Wrap( -1 )

        fgSizer1.Add( self.m_staticText24, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.trackWidth = wx.TextCtrl( sbSizer6.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"trackWidth" )
        fgSizer1.Add( self.trackWidth, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )

        self.m_staticText25 = wx.StaticText( sbSizer6.GetStaticBox(), wx.ID_ANY, u"Minimum Spacing:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText25.Wrap( -1 )

        fgSizer1.Add( self.m_staticText25, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.minimumSpacing = wx.TextCtrl( sbSizer6.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"trackSpacing" )
        fgSizer1.Add( self.minimumSpacing, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )

        self.m_staticText46 = wx.StaticText( sbSizer6.GetStaticBox(), wx.ID_ANY, u"Track Pitch:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText46.Wrap( -1 )

        fgSizer1.Add( self.m_staticText46, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.trackPitch = wx.TextCtrl( sbSizer6.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"trackPitch" )
        fgSizer1.Add( self.trackPitch, 0, wx.ALL, 5 )

        self.m_staticText47 = wx.StaticText( sbSizer6.GetStaticBox(), wx.ID_ANY, u"Pad Clearance:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText47.Wrap( -1 )

        fgSizer1.Add( self.m_staticText47, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.padClearance = wx.TextCtrl( sbSizer6.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"padClearance" )
        fgSizer1.Add( self.padClearance, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )

        self.m_staticText471 = wx.StaticText( sbSizer6.GetStaticBox(), wx.ID_ANY, u"Pad Diameter:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText471.Wrap( -1 )

        fgSizer1.Add( self.m_staticText471, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.padDiameter = wx.TextCtrl( sbSizer6.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER|wx.TE_READONLY, wx.DefaultValidator, u"trackSpacing" )
        fgSizer1.Add( self.padDiameter, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )

        self.m_staticText35 = wx.StaticText( sbSizer6.GetStaticBox(), wx.ID_ANY, u"Calculated Spacing:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText35.Wrap( -1 )

        fgSizer1.Add( self.m_staticText35, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.calculatedSpacing = wx.TextCtrl( sbSizer6.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_READONLY )
        fgSizer1.Add( self.calculatedSpacing, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )


        sbSizer6.Add( fgSizer1, 1, wx.EXPAND, 5 )


        bSizer51.Add( sbSizer6, 1, wx.EXPAND, 5 )

        sbSizer12 = wx.StaticBoxSizer( wx.StaticBox( self.m_technicalPanel, wx.ID_ANY, u"Electrical Specifications" ), wx.VERTICAL )

        fgSizer8 = wx.FlexGridSizer( 0, 6, 0, 0 )
        fgSizer8.SetFlexibleDirection( wx.BOTH )
        fgSizer8.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_staticText251 = wx.StaticText( sbSizer12.GetStaticBox(), wx.ID_ANY, u"Voltage (V):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText251.Wrap( -1 )

        fgSizer8.Add( self.m_staticText251, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.heaterVoltage = wx.TextCtrl( sbSizer12.GetStaticBox(), wx.ID_ANY, u"19", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER )
        fgSizer8.Add( self.heaterVoltage, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )

        self.m_staticText262 = wx.StaticText( sbSizer12.GetStaticBox(), wx.ID_ANY, u"Power (W):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText262.Wrap( -1 )

        fgSizer8.Add( self.m_staticText262, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.heaterPower = wx.TextCtrl( sbSizer12.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER )
        fgSizer8.Add( self.heaterPower, 0, wx.ALL, 5 )

        self.m_staticText21 = wx.StaticText( sbSizer12.GetStaticBox(), wx.ID_ANY, u"Target Resistance (mΩ):", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText21.Wrap( -1 )

        fgSizer8.Add( self.m_staticText21, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.targetResistance = wx.TextCtrl( sbSizer12.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"targetResistance" )
        fgSizer8.Add( self.targetResistance, 0, wx.ALL, 5 )

        self.m_staticText351 = wx.StaticText( sbSizer12.GetStaticBox(), wx.ID_ANY, u"Max Duty (%)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText351.Wrap( -1 )

        fgSizer8.Add( self.m_staticText351, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.maxDuty = wx.TextCtrl( sbSizer12.GetStaticBox(), wx.ID_ANY, u"93", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER )
        fgSizer8.Add( self.maxDuty, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )


        sbSizer12.Add( fgSizer8, 1, wx.EXPAND, 5 )


        bSizer51.Add( sbSizer12, 1, wx.EXPAND, 5 )

        sbSizer11 = wx.StaticBoxSizer( wx.StaticBox( self.m_technicalPanel, wx.ID_ANY, u"Thermal Specifications" ), wx.VERTICAL )

        fgSizer12 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer12.AddGrowableCol( 1 )
        fgSizer12.SetFlexibleDirection( wx.BOTH )
        fgSizer12.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        fgSizer9 = wx.FlexGridSizer( 0, 4, 0, 0 )
        fgSizer9.SetFlexibleDirection( wx.BOTH )
        fgSizer9.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_staticText27 = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, u"Maximum Temperature (°C):", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText27.Wrap( -1 )

        fgSizer9.Add( self.m_staticText27, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.maxTemp = wx.TextCtrl( sbSizer11.GetStaticBox(), wx.ID_ANY, u"220", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER )
        fgSizer9.Add( self.maxTemp, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )

        self.m_staticText271 = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, u"Ambient Temperature (°C):", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText271.Wrap( -1 )

        fgSizer9.Add( self.m_staticText271, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.ambientTemp = wx.TextCtrl( sbSizer11.GetStaticBox(), wx.ID_ANY, u"20", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_READONLY )
        fgSizer9.Add( self.ambientTemp, 0, wx.ALL, 5 )

        self.m_staticText32 = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, u"Thermal Resistance (K/W):", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText32.Wrap( -1 )

        fgSizer9.Add( self.m_staticText32, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.thermalResistance = wx.TextCtrl( sbSizer11.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER )
        fgSizer9.Add( self.thermalResistance, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )

        self.m_staticText33 = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, u"Power Margin (%):", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText33.Wrap( -1 )

        fgSizer9.Add( self.m_staticText33, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.powerMargin = wx.TextCtrl( sbSizer11.GetStaticBox(), wx.ID_ANY, u"20", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER )
        self.powerMargin.SetToolTip( u"Typically in the range of 20-50%." )

        fgSizer9.Add( self.powerMargin, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )


        fgSizer12.Add( fgSizer9, 1, wx.EXPAND, 5 )

        self.logoBitmap = wx.StaticBitmap( sbSizer11.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 96,52 ), 0 )
        self.logoBitmap.SetMinSize( wx.Size( 96,52 ) )

        fgSizer12.Add( self.logoBitmap, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )


        sbSizer11.Add( fgSizer12, 1, wx.EXPAND, 5 )


        bSizer51.Add( sbSizer11, 1, wx.EXPAND, 5 )


        self.m_technicalPanel.SetSizer( bSizer51 )
        self.m_technicalPanel.Layout()
        bSizer51.Fit( self.m_technicalPanel )
        self.m_notebook2.AddPage( self.m_technicalPanel, u"Technical", True )
        self.m_boardPanel = wx.Panel( self.m_notebook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        fgSizer7 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer7.SetFlexibleDirection( wx.BOTH )
        fgSizer7.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self.m_boardPanel, wx.ID_ANY, u"Board Extents (mm)" ), wx.VERTICAL )

        fgSizer3 = wx.FlexGridSizer( 0, 4, 0, 0 )
        fgSizer3.SetFlexibleDirection( wx.BOTH )
        fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_staticText12 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"Left:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText12.Wrap( -1 )

        fgSizer3.Add( self.m_staticText12, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.boardLeft = wx.TextCtrl( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"boardLeft" )
        fgSizer3.Add( self.boardLeft, 0, wx.ALL, 5 )

        self.m_staticText13 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"Top:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText13.Wrap( -1 )

        fgSizer3.Add( self.m_staticText13, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.boardTop = wx.TextCtrl( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"boardTop" )
        fgSizer3.Add( self.boardTop, 0, wx.ALL, 5 )

        self.m_staticText14 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"Right:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText14.Wrap( -1 )

        fgSizer3.Add( self.m_staticText14, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.boardRight = wx.TextCtrl( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"boardRight" )
        fgSizer3.Add( self.boardRight, 0, wx.ALL, 5 )

        self.m_staticText15 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"Bottom:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText15.Wrap( -1 )

        fgSizer3.Add( self.m_staticText15, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.boardBottom = wx.TextCtrl( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"boardBottom" )
        fgSizer3.Add( self.boardBottom, 0, wx.ALL, 5 )

        self.m_staticText26 = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"Corner:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText26.Wrap( -1 )

        fgSizer3.Add( self.m_staticText26, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.boardCorner = wx.TextCtrl( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"boardCorner" )
        fgSizer3.Add( self.boardCorner, 0, wx.ALL, 5 )


        sbSizer1.Add( fgSizer3, 1, wx.EXPAND, 5 )


        fgSizer7.Add( sbSizer1, 1, wx.EXPAND, 5 )

        sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self.m_boardPanel, wx.ID_ANY, u"Track Ends (mm)" ), wx.VERTICAL )

        fgSizer11 = wx.FlexGridSizer( 0, 5, 0, 0 )
        fgSizer11.SetFlexibleDirection( wx.BOTH )
        fgSizer11.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_staticText1 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Track Entry", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT )
        self.m_staticText1.Wrap( -1 )

        fgSizer11.Add( self.m_staticText1, 0, wx.ALL, 5 )

        self.m_staticText8 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"X:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText8.Wrap( -1 )

        fgSizer11.Add( self.m_staticText8, 0, wx.ALL, 5 )

        self.startPointX = wx.TextCtrl( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"trackStartX" )
        fgSizer11.Add( self.startPointX, 0, wx.ALL, 5 )

        self.m_staticText2 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Y:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText2.Wrap( -1 )

        fgSizer11.Add( self.m_staticText2, 0, wx.ALL, 5 )

        self.startPointY = wx.TextCtrl( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"trackStartY" )
        fgSizer11.Add( self.startPointY, 0, wx.ALL, 5 )

        self.m_staticText3 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Track Exit", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT )
        self.m_staticText3.Wrap( -1 )

        fgSizer11.Add( self.m_staticText3, 0, wx.ALL, 5 )

        self.m_staticText9 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"X:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText9.Wrap( -1 )

        fgSizer11.Add( self.m_staticText9, 0, wx.ALL, 5 )

        self.endPointX = wx.TextCtrl( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"trackEndX" )
        fgSizer11.Add( self.endPointX, 0, wx.ALL, 5 )

        self.m_staticText4 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Y:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText4.Wrap( -1 )

        fgSizer11.Add( self.m_staticText4, 0, wx.ALL, 5 )

        self.endPointY = wx.TextCtrl( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"trackEndY" )
        fgSizer11.Add( self.endPointY, 0, wx.ALL, 5 )


        sbSizer2.Add( fgSizer11, 1, wx.EXPAND, 5 )


        fgSizer7.Add( sbSizer2, 1, wx.EXPAND, 5 )


        self.m_boardPanel.SetSizer( fgSizer7 )
        self.m_boardPanel.Layout()
        fgSizer7.Fit( self.m_boardPanel )
        self.m_notebook2.AddPage( self.m_boardPanel, u"Board Area", False )
        self.m_heaterPanel = wx.Panel( self.m_notebook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer12 = wx.BoxSizer( wx.VERTICAL )

        sbSizer21 = wx.StaticBoxSizer( wx.StaticBox( self.m_heaterPanel, wx.ID_ANY, u"Heating Element Extents (mm)" ), wx.VERTICAL )

        fgSizer4 = wx.FlexGridSizer( 0, 8, 0, 0 )
        fgSizer4.SetFlexibleDirection( wx.BOTH )
        fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_staticText121 = wx.StaticText( sbSizer21.GetStaticBox(), wx.ID_ANY, u"Left:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText121.Wrap( -1 )

        fgSizer4.Add( self.m_staticText121, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.heaterLeft = wx.TextCtrl( sbSizer21.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"heaterLeft" )
        fgSizer4.Add( self.heaterLeft, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )

        self.m_staticText131 = wx.StaticText( sbSizer21.GetStaticBox(), wx.ID_ANY, u"Top:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText131.Wrap( -1 )

        fgSizer4.Add( self.m_staticText131, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.heaterTop = wx.TextCtrl( sbSizer21.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"heaterTop" )
        fgSizer4.Add( self.heaterTop, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )

        self.m_staticText141 = wx.StaticText( sbSizer21.GetStaticBox(), wx.ID_ANY, u"Right:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText141.Wrap( -1 )

        fgSizer4.Add( self.m_staticText141, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.heaterRight = wx.TextCtrl( sbSizer21.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"heaterRight" )
        fgSizer4.Add( self.heaterRight, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )

        self.m_staticText151 = wx.StaticText( sbSizer21.GetStaticBox(), wx.ID_ANY, u"Bottom:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText151.Wrap( -1 )

        fgSizer4.Add( self.m_staticText151, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.heaterBottom = wx.TextCtrl( sbSizer21.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"beaterBottom" )
        fgSizer4.Add( self.heaterBottom, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )

        self.m_staticText261 = wx.StaticText( sbSizer21.GetStaticBox(), wx.ID_ANY, u"Corner:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText261.Wrap( -1 )

        fgSizer4.Add( self.m_staticText261, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.heaterCorner = wx.TextCtrl( sbSizer21.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"heaterCorner" )
        fgSizer4.Add( self.heaterCorner, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )


        sbSizer21.Add( fgSizer4, 1, wx.EXPAND|wx.SHAPED, 5 )


        bSizer12.Add( sbSizer21, 0, wx.EXPAND, 5 )

        sbSizer17 = wx.StaticBoxSizer( wx.StaticBox( self.m_heaterPanel, wx.ID_ANY, u"Track Specifications" ), wx.VERTICAL )

        fgSizer111 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer111.SetFlexibleDirection( wx.BOTH )
        fgSizer111.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


        sbSizer17.Add( fgSizer111, 0, wx.EXPAND, 5 )

        gSizer2 = wx.GridSizer( 0, 2, 0, 0 )

        bSizer13 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText36 = wx.StaticText( sbSizer17.GetStaticBox(), wx.ID_ANY, u"Track Thickness (µm):", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText36.Wrap( -1 )

        bSizer13.Add( self.m_staticText36, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.trackThickness = wx.TextCtrl( sbSizer17.GetStaticBox(), wx.ID_ANY, u"29", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER )
        bSizer13.Add( self.trackThickness, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )


        gSizer2.Add( bSizer13, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_LEFT, 5 )

        bSizer14 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText37 = wx.StaticText( sbSizer17.GetStaticBox(), wx.ID_ANY, u"Track Resistivity (Ωm)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText37.Wrap( -1 )

        bSizer14.Add( self.m_staticText37, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.trackResistivity = wx.TextCtrl( sbSizer17.GetStaticBox(), wx.ID_ANY, u"1.68", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER )
        bSizer14.Add( self.trackResistivity, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )


        gSizer2.Add( bSizer14, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_RIGHT, 5 )

        self.m_staticText38 = wx.StaticText( sbSizer17.GetStaticBox(), wx.ID_ANY, u"1oz = 35µm\n2oz = 70µm", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_LEFT )
        self.m_staticText38.Wrap( -1 )

        gSizer2.Add( self.m_staticText38, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_TOP|wx.ALL, 5 )

        self.m_staticText39 = wx.StaticText( sbSizer17.GetStaticBox(), wx.ID_ANY, u"Annealed Copper = 1.68x10⁻⁸", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText39.Wrap( -1 )

        gSizer2.Add( self.m_staticText39, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_TOP|wx.ALL, 5 )


        sbSizer17.Add( gSizer2, 0, wx.EXPAND, 5 )


        bSizer12.Add( sbSizer17, 1, wx.EXPAND, 5 )

        bSizer6 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText34 = wx.StaticText( self.m_heaterPanel, wx.ID_ANY, u"Heater Area (mm²):", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_staticText34.Wrap( -1 )

        bSizer6.Add( self.m_staticText34, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.heaterArea = wx.TextCtrl( self.m_heaterPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_READONLY )
        bSizer6.Add( self.heaterArea, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )


        bSizer12.Add( bSizer6, 0, wx.ALIGN_RIGHT|wx.EXPAND|wx.SHAPED, 5 )


        self.m_heaterPanel.SetSizer( bSizer12 )
        self.m_heaterPanel.Layout()
        bSizer12.Fit( self.m_heaterPanel )
        self.m_notebook2.AddPage( self.m_heaterPanel, u"Heater Area", False )

        bSizer3.Add( self.m_notebook2, 1, wx.EXPAND |wx.ALL, 5 )

        bSizer2 = wx.BoxSizer( wx.VERTICAL )

        self.enableDebug = wx.CheckBox( self, wx.ID_ANY, u"Enable Debug", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"enableDebug" )
        bSizer2.Add( self.enableDebug, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )


        bSizer3.Add( bSizer2, 0, wx.ALIGN_RIGHT|wx.EXPAND, 5 )

        gSizer1 = wx.GridSizer( 0, 2, 0, 0 )

        bSizer4 = wx.BoxSizer( wx.HORIZONTAL )

        self.loadButton = wx.Button( self, wx.ID_ANY, u"Load", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.loadButton.SetToolTip( u"Load parameters from file." )

        bSizer4.Add( self.loadButton, 0, wx.ALIGN_BOTTOM|wx.ALIGN_LEFT|wx.ALL, 5 )

        self.saveButton = wx.Button( self, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.saveButton.SetToolTip( u"Save the current parameters to a file for later re-use." )

        bSizer4.Add( self.saveButton, 0, wx.ALIGN_BOTTOM|wx.ALIGN_LEFT|wx.ALL, 5 )


        bSizer4.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.analyzeButton = wx.Button( self, wx.ID_ANY, u"Analyze", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.analyzeButton.SetToolTip( u"Analyze the current PCB to derive parameters." )

        bSizer4.Add( self.analyzeButton, 0, wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT|wx.ALL, 5 )


        gSizer1.Add( bSizer4, 0, wx.ALIGN_BOTTOM|wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5 )

        bSizer41 = wx.BoxSizer( wx.HORIZONTAL )

        self.clearButton = wx.Button( self, wx.ID_ANY, u"Clear", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.clearButton.SetToolTip( u"Clear all hotplate tracks from the current PCB." )

        bSizer41.Add( self.clearButton, 0, wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.applyButton = wx.Button( self, wx.ID_APPLY, u"Apply", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"applyButton" )
        self.applyButton.SetToolTip( u"Clear the board and generate new tracks but keep this dialog open." )

        bSizer41.Add( self.applyButton, 0, wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.generateButton = wx.Button( self, wx.ID_OK, u"Generate", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"applyButton" )

        self.generateButton.SetDefault()
        self.generateButton.SetToolTip( u"Clear the board and generate new tracks." )

        bSizer41.Add( self.generateButton, 0, wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.cancelButton = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"cancelButton" )

        self.cancelButton.SetBitmapPosition( wx.RIGHT )
        self.cancelButton.SetToolTip( u"Close this dialog without any further action." )

        bSizer41.Add( self.cancelButton, 0, wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT|wx.ALL, 5 )


        gSizer1.Add( bSizer41, 0, wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )


        bSizer3.Add( gSizer1, 0, wx.EXPAND, 5 )


        self.SetSizer( bSizer3 )
        self.Layout()
        bSizer3.Fit( self )

        self.Centre( wx.BOTH )

        # Connect Events
        self.enableDebug.Bind( wx.EVT_CHECKBOX, self.HandleDebugEnabled )
        self.loadButton.Bind( wx.EVT_BUTTON, self.HandleLoadClick )
        self.saveButton.Bind( wx.EVT_BUTTON, self.HandleSaveClick )
        self.analyzeButton.Bind( wx.EVT_BUTTON, self.HandleAnalyzeClick )
        self.clearButton.Bind( wx.EVT_BUTTON, self.HandleClearClick )
        self.applyButton.Bind( wx.EVT_BUTTON, self.HandleApplyClick )
        self.generateButton.Bind( wx.EVT_BUTTON, self.HandleGenerateClick )
        self.cancelButton.Bind( wx.EVT_BUTTON, self.HandleCancelClick )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def HandleDebugEnabled( self, event ):
        event.Skip()

    def HandleLoadClick( self, event ):
        event.Skip()

    def HandleSaveClick( self, event ):
        event.Skip()

    def HandleAnalyzeClick( self, event ):
        event.Skip()

    def HandleClearClick( self, event ):
        event.Skip()

    def HandleApplyClick( self, event ):
        event.Skip()

    def HandleGenerateClick( self, event ):
        event.Skip()

    def HandleCancelClick( self, event ):
        event.Skip()


