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

        self.m_main_notebook = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_technicalPanel = wx.Panel( self.m_main_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bTechnicalPanel = wx.BoxSizer( wx.VERTICAL )

        bElectricalThermalLogo = wx.BoxSizer( wx.HORIZONTAL )

        bSizer13 = wx.BoxSizer( wx.VERTICAL )

        sbElectricalSpecifications = wx.StaticBoxSizer( wx.StaticBox( self.m_technicalPanel, wx.ID_ANY, u"Electrical Specifications" ), wx.VERTICAL )

        fgElectricalSpecifications = wx.FlexGridSizer( 0, 6, 0, 0 )
        fgElectricalSpecifications.SetFlexibleDirection( wx.BOTH )
        fgElectricalSpecifications.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_Voltage = wx.StaticText( sbElectricalSpecifications.GetStaticBox(), wx.ID_ANY, u"Voltage (V):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_Voltage.Wrap( -1 )

        fgElectricalSpecifications.Add( self.m_Voltage, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.heater_voltage = wx.TextCtrl( sbElectricalSpecifications.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER, wx.DefaultValidator, u"heater_voltage" )
        fgElectricalSpecifications.Add( self.heater_voltage, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )

        self.m_Power = wx.StaticText( sbElectricalSpecifications.GetStaticBox(), wx.ID_ANY, u"Power (W):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_Power.Wrap( -1 )

        fgElectricalSpecifications.Add( self.m_Power, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.heater_power = wx.TextCtrl( sbElectricalSpecifications.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER, wx.DefaultValidator, u"heater_power" )
        fgElectricalSpecifications.Add( self.heater_power, 0, wx.ALL, 5 )

        self.m_TargetResistance = wx.StaticText( sbElectricalSpecifications.GetStaticBox(), wx.ID_ANY, u"Target Resistance (Ω):", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_TargetResistance.Wrap( -1 )

        fgElectricalSpecifications.Add( self.m_TargetResistance, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.target_resistance = wx.TextCtrl( sbElectricalSpecifications.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"target_resistance" )
        fgElectricalSpecifications.Add( self.target_resistance, 0, wx.ALL, 5 )


        sbElectricalSpecifications.Add( fgElectricalSpecifications, 1, wx.EXPAND, 5 )


        bSizer13.Add( sbElectricalSpecifications, 1, wx.EXPAND, 5 )

        sbThermalSpecifications = wx.StaticBoxSizer( wx.StaticBox( self.m_technicalPanel, wx.ID_ANY, u"Thermal Specifications" ), wx.VERTICAL )

        fgThermalAndLogo = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgThermalAndLogo.AddGrowableCol( 1 )
        fgThermalAndLogo.SetFlexibleDirection( wx.BOTH )
        fgThermalAndLogo.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        fgThermalSpecifications = wx.FlexGridSizer( 0, 4, 0, 0 )
        fgThermalSpecifications.SetFlexibleDirection( wx.BOTH )
        fgThermalSpecifications.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_MaximumTemperature = wx.StaticText( sbThermalSpecifications.GetStaticBox(), wx.ID_ANY, u"Maximum Temperature (°C):", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_MaximumTemperature.Wrap( -1 )

        fgThermalSpecifications.Add( self.m_MaximumTemperature, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.maximum_temperature = wx.TextCtrl( sbThermalSpecifications.GetStaticBox(), wx.ID_ANY, u"220", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER, wx.DefaultValidator, u"maximum_temperature" )
        fgThermalSpecifications.Add( self.maximum_temperature, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )

        self.m_AmbientTemperature = wx.StaticText( sbThermalSpecifications.GetStaticBox(), wx.ID_ANY, u"Ambient Temperature (°C):", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_AmbientTemperature.Wrap( -1 )

        fgThermalSpecifications.Add( self.m_AmbientTemperature, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.ambient_temperature = wx.TextCtrl( sbThermalSpecifications.GetStaticBox(), wx.ID_ANY, u"25", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_READONLY, wx.DefaultValidator, u"ambient_temperature" )
        fgThermalSpecifications.Add( self.ambient_temperature, 0, wx.ALL, 5 )

        self.m_ThermalResistance = wx.StaticText( sbThermalSpecifications.GetStaticBox(), wx.ID_ANY, u"Thermal Resistance (K/W):", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_ThermalResistance.Wrap( -1 )

        fgThermalSpecifications.Add( self.m_ThermalResistance, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.thermal_resistance = wx.TextCtrl( sbThermalSpecifications.GetStaticBox(), wx.ID_ANY, u"2.8", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER, wx.DefaultValidator, u"thermal_resistance" )
        fgThermalSpecifications.Add( self.thermal_resistance, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )

        self.m_PowerMargin = wx.StaticText( sbThermalSpecifications.GetStaticBox(), wx.ID_ANY, u"Power Margin (%):", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_PowerMargin.Wrap( -1 )

        fgThermalSpecifications.Add( self.m_PowerMargin, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.power_margin = wx.TextCtrl( sbThermalSpecifications.GetStaticBox(), wx.ID_ANY, u"100", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER, wx.DefaultValidator, u"power_margin" )
        self.power_margin.SetToolTip( u"Typically in the range of 20-50%." )

        fgThermalSpecifications.Add( self.power_margin, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )


        fgThermalAndLogo.Add( fgThermalSpecifications, 1, wx.EXPAND, 5 )


        sbThermalSpecifications.Add( fgThermalAndLogo, 1, wx.EXPAND, 5 )


        bSizer13.Add( sbThermalSpecifications, 1, wx.EXPAND, 5 )


        bElectricalThermalLogo.Add( bSizer13, 1, wx.EXPAND, 5 )

        self.logo_bitmap = wx.StaticBitmap( self.m_technicalPanel, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 192,192 ), 0 )
        self.logo_bitmap.SetMinSize( wx.Size( 192,192 ) )

        bElectricalThermalLogo.Add( self.logo_bitmap, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL|wx.RIGHT|wx.SHAPED, 5 )


        bTechnicalPanel.Add( bElectricalThermalLogo, 2, wx.EXPAND, 5 )

        sbTrackSpecifications = wx.StaticBoxSizer( wx.StaticBox( self.m_technicalPanel, wx.ID_ANY, u"Track Specifications" ), wx.VERTICAL )

        gTrackSpecifications = wx.GridSizer( 0, 3, 0, 0 )

        bMinimumSpacing = wx.BoxSizer( wx.HORIZONTAL )

        self.m_MinimumSpacing = wx.StaticText( sbTrackSpecifications.GetStaticBox(), wx.ID_ANY, u"Minimum Spacing:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_MinimumSpacing.Wrap( -1 )

        bMinimumSpacing.Add( self.m_MinimumSpacing, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.minimum_spacing = wx.TextCtrl( sbTrackSpecifications.GetStaticBox(), wx.ID_ANY, u"0.2", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"minimum_spacing" )
        bMinimumSpacing.Add( self.minimum_spacing, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )


        gTrackSpecifications.Add( bMinimumSpacing, 1, wx.EXPAND, 5 )

        bTrackThickness = wx.BoxSizer( wx.HORIZONTAL )

        self.m_TrackThickness = wx.StaticText( sbTrackSpecifications.GetStaticBox(), wx.ID_ANY, u"Track Thickness (µm):", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_TrackThickness.Wrap( -1 )

        bTrackThickness.Add( self.m_TrackThickness, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.track_thickness = wx.TextCtrl( sbTrackSpecifications.GetStaticBox(), wx.ID_ANY, u"35", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER, wx.DefaultValidator, u"track_thickness" )
        bTrackThickness.Add( self.track_thickness, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )


        gTrackSpecifications.Add( bTrackThickness, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_LEFT, 5 )

        bTrackResistivity = wx.BoxSizer( wx.HORIZONTAL )

        self.m_TrackResistivity = wx.StaticText( sbTrackSpecifications.GetStaticBox(), wx.ID_ANY, u"Track Resistivity (x10⁻⁸ Ωm)", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_TrackResistivity.Wrap( -1 )

        bTrackResistivity.Add( self.m_TrackResistivity, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.track_resistivity = wx.TextCtrl( sbTrackSpecifications.GetStaticBox(), wx.ID_ANY, u"1.68", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER, wx.DefaultValidator, u"track_resistivity" )
        bTrackResistivity.Add( self.track_resistivity, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )


        gTrackSpecifications.Add( bTrackResistivity, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_RIGHT, 5 )

        self.m_BlankUndeMinSpacing = wx.StaticText( sbTrackSpecifications.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_LEFT )
        self.m_BlankUndeMinSpacing.Wrap( -1 )

        gTrackSpecifications.Add( self.m_BlankUndeMinSpacing, 0, wx.ALL, 5 )

        self.m_CopperWeights = wx.StaticText( sbTrackSpecifications.GetStaticBox(), wx.ID_ANY, u"1oz Copper = 35µm\n2oz Copper = 70µm", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_LEFT )
        self.m_CopperWeights.Wrap( -1 )

        gTrackSpecifications.Add( self.m_CopperWeights, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_TOP|wx.ALL, 5 )

        self.m_EDCopper = wx.StaticText( sbTrackSpecifications.GetStaticBox(), wx.ID_ANY, u"Measured at 20°C\nED Copper = 1.68", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_EDCopper.Wrap( -1 )

        gTrackSpecifications.Add( self.m_EDCopper, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_TOP|wx.ALL, 5 )


        sbTrackSpecifications.Add( gTrackSpecifications, 0, wx.EXPAND, 5 )


        bTechnicalPanel.Add( sbTrackSpecifications, 1, wx.EXPAND, 5 )


        self.m_technicalPanel.SetSizer( bTechnicalPanel )
        self.m_technicalPanel.Layout()
        bTechnicalPanel.Fit( self.m_technicalPanel )
        self.m_main_notebook.AddPage( self.m_technicalPanel, u"Technical", True )
        self.m_calculationPanel = wx.Panel( self.m_main_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bCalculationPanel = wx.BoxSizer( wx.VERTICAL )

        sbTrackGeometry = wx.StaticBoxSizer( wx.StaticBox( self.m_calculationPanel, wx.ID_ANY, u"Track Geometry" ), wx.VERTICAL )

        fgTrackGeometry = wx.FlexGridSizer( 0, 6, 0, 0 )
        fgTrackGeometry.SetFlexibleDirection( wx.BOTH )
        fgTrackGeometry.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_TrackWidth = wx.StaticText( sbTrackGeometry.GetStaticBox(), wx.ID_ANY, u"Track Width:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_TrackWidth.Wrap( -1 )

        fgTrackGeometry.Add( self.m_TrackWidth, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.track_width = wx.TextCtrl( sbTrackGeometry.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"track_width" )
        fgTrackGeometry.Add( self.track_width, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )

        self.m_TrackSpacing = wx.StaticText( sbTrackGeometry.GetStaticBox(), wx.ID_ANY, u"Track Spacing:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_TrackSpacing.Wrap( -1 )

        fgTrackGeometry.Add( self.m_TrackSpacing, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.track_spacing = wx.TextCtrl( sbTrackGeometry.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"track_spacing" )
        fgTrackGeometry.Add( self.track_spacing, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )

        self.m_TrackPitch = wx.StaticText( sbTrackGeometry.GetStaticBox(), wx.ID_ANY, u"Track Pitch:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_TrackPitch.Wrap( -1 )

        fgTrackGeometry.Add( self.m_TrackPitch, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.track_pitch = wx.TextCtrl( sbTrackGeometry.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_PROCESS_ENTER, wx.DefaultValidator, u"track_pitch" )
        fgTrackGeometry.Add( self.track_pitch, 0, wx.ALL, 5 )


        sbTrackGeometry.Add( fgTrackGeometry, 1, wx.EXPAND, 5 )


        bCalculationPanel.Add( sbTrackGeometry, 1, wx.EXPAND, 5 )

        bSizer11 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer12 = wx.BoxSizer( wx.VERTICAL )

        sbBoardExtents = wx.StaticBoxSizer( wx.StaticBox( self.m_calculationPanel, wx.ID_ANY, u"Board Extents (mm)" ), wx.HORIZONTAL )

        fgBoardExtents = wx.FlexGridSizer( 0, 8, 0, 0 )
        fgBoardExtents.SetFlexibleDirection( wx.BOTH )
        fgBoardExtents.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_ExtentLeft = wx.StaticText( sbBoardExtents.GetStaticBox(), wx.ID_ANY, u"Left:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_ExtentLeft.Wrap( -1 )

        fgBoardExtents.Add( self.m_ExtentLeft, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.extent_left = wx.TextCtrl( sbBoardExtents.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_READONLY, wx.DefaultValidator, u"extent_left" )
        self.extent_left.Enable( False )

        fgBoardExtents.Add( self.extent_left, 0, wx.ALL, 5 )

        self.m_ExtentTop = wx.StaticText( sbBoardExtents.GetStaticBox(), wx.ID_ANY, u"Top:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_ExtentTop.Wrap( -1 )

        fgBoardExtents.Add( self.m_ExtentTop, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.extent_top = wx.TextCtrl( sbBoardExtents.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_READONLY, wx.DefaultValidator, u"extent_top" )
        self.extent_top.Enable( False )

        fgBoardExtents.Add( self.extent_top, 0, wx.ALL, 5 )

        self.m_ExtentRight = wx.StaticText( sbBoardExtents.GetStaticBox(), wx.ID_ANY, u"Right:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_ExtentRight.Wrap( -1 )

        fgBoardExtents.Add( self.m_ExtentRight, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.extent_right = wx.TextCtrl( sbBoardExtents.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_READONLY, wx.DefaultValidator, u"extent_right" )
        self.extent_right.Enable( False )

        fgBoardExtents.Add( self.extent_right, 0, wx.ALL, 5 )

        self.m_ExtentBottom = wx.StaticText( sbBoardExtents.GetStaticBox(), wx.ID_ANY, u"Bottom:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
        self.m_ExtentBottom.Wrap( -1 )

        fgBoardExtents.Add( self.m_ExtentBottom, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.extent_bottom = wx.TextCtrl( sbBoardExtents.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_READONLY, wx.DefaultValidator, u"extent_bottom" )
        self.extent_bottom.Enable( False )

        fgBoardExtents.Add( self.extent_bottom, 0, wx.ALL, 5 )


        sbBoardExtents.Add( fgBoardExtents, 1, wx.EXPAND, 5 )


        bSizer12.Add( sbBoardExtents, 1, wx.EXPAND, 5 )

        sbCalculatedElectrical = wx.StaticBoxSizer( wx.StaticBox( self.m_calculationPanel, wx.ID_ANY, u"Electrical" ), wx.VERTICAL )

        fgCalculatedElectrical = wx.FlexGridSizer( 0, 6, 0, 0 )
        fgCalculatedElectrical.SetFlexibleDirection( wx.BOTH )
        fgCalculatedElectrical.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.m_ColdResistance = wx.StaticText( sbCalculatedElectrical.GetStaticBox(), wx.ID_ANY, u"Cold Resistance (Ω):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_ColdResistance.Wrap( -1 )

        fgCalculatedElectrical.Add( self.m_ColdResistance, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.cold_resistance = wx.TextCtrl( sbCalculatedElectrical.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_READONLY, wx.DefaultValidator, u"cold_resistance" )
        self.cold_resistance.Enable( False )

        fgCalculatedElectrical.Add( self.cold_resistance, 0, wx.ALL, 5 )

        self.m_HotResistance = wx.StaticText( sbCalculatedElectrical.GetStaticBox(), wx.ID_ANY, u"Hot Resistance (Ω):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_HotResistance.Wrap( -1 )

        fgCalculatedElectrical.Add( self.m_HotResistance, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.hot_resistance = wx.TextCtrl( sbCalculatedElectrical.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_READONLY, wx.DefaultValidator, u"hot_resistance" )
        self.hot_resistance.Enable( False )

        fgCalculatedElectrical.Add( self.hot_resistance, 0, wx.ALL, 5 )


        sbCalculatedElectrical.Add( fgCalculatedElectrical, 1, wx.EXPAND, 5 )


        bSizer12.Add( sbCalculatedElectrical, 1, wx.EXPAND, 5 )


        bSizer11.Add( bSizer12, 1, wx.EXPAND, 5 )

        self.calculation_bitmap = wx.StaticBitmap( self.m_calculationPanel, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 192,192 ), 0 )
        self.calculation_bitmap.SetMinSize( wx.Size( 192,192 ) )

        bSizer11.Add( self.calculation_bitmap, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL|wx.RIGHT|wx.SHAPED, 5 )


        bCalculationPanel.Add( bSizer11, 2, wx.EXPAND, 5 )


        self.m_calculationPanel.SetSizer( bCalculationPanel )
        self.m_calculationPanel.Layout()
        bCalculationPanel.Fit( self.m_calculationPanel )
        self.m_main_notebook.AddPage( self.m_calculationPanel, u"Calculations", False )

        bSizer3.Add( self.m_main_notebook, 1, wx.EXPAND |wx.ALL, 5 )

        gSizer1 = wx.GridSizer( 0, 2, 0, 0 )

        bSizer4 = wx.BoxSizer( wx.HORIZONTAL )

        self.load_button = wx.Button( self, wx.ID_ANY, u"Load", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.load_button.SetToolTip( u"Load parameters from file." )

        bSizer4.Add( self.load_button, 0, wx.ALIGN_BOTTOM|wx.ALIGN_LEFT|wx.ALL, 5 )

        self.save_button = wx.Button( self, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.save_button.SetToolTip( u"Save the current parameters to a file for later re-use." )

        bSizer4.Add( self.save_button, 0, wx.ALIGN_BOTTOM|wx.ALIGN_LEFT|wx.ALL, 5 )


        bSizer4.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.analyze_button = wx.Button( self, wx.ID_ANY, u"Analyze", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.analyze_button.SetToolTip( u"Analyze the current PCB to derive parameters." )

        bSizer4.Add( self.analyze_button, 0, wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT|wx.ALL, 5 )


        gSizer1.Add( bSizer4, 0, wx.ALIGN_BOTTOM|wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5 )

        bSizer41 = wx.BoxSizer( wx.HORIZONTAL )

        self.clear_button = wx.Button( self, wx.ID_ANY, u"Clear Tracks", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.clear_button.SetToolTip( u"Clear all hotplate tracks from the current PCB." )

        bSizer41.Add( self.clear_button, 0, wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.apply_button = wx.Button( self, wx.ID_OK, u"Apply 1.21GW!", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"applyButton" )

        self.apply_button.SetDefault()
        self.apply_button.SetToolTip( u"Clear the board and generate new tracks." )

        bSizer41.Add( self.apply_button, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.close_button = wx.Button( self, wx.ID_CANCEL, u"Close", wx.DefaultPosition, wx.DefaultSize, 0, wx.DefaultValidator, u"cancelButton" )

        self.close_button.SetBitmapPosition( wx.RIGHT )
        self.close_button.SetToolTip( u"Close this dialog without any further action." )

        bSizer41.Add( self.close_button, 0, wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT|wx.ALL, 5 )


        gSizer1.Add( bSizer41, 0, wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT|wx.ALL|wx.EXPAND, 5 )


        bSizer3.Add( gSizer1, 0, wx.EXPAND, 5 )


        self.SetSizer( bSizer3 )
        self.Layout()
        bSizer3.Fit( self )

        self.Centre( wx.BOTH )

        # Connect Events
        self.heater_voltage.Bind( wx.EVT_KILL_FOCUS, self.heater_voltage_leave )
        self.heater_voltage.Bind( wx.EVT_TEXT, self.heater_voltage_change )
        self.heater_voltage.Bind( wx.EVT_TEXT_ENTER, self.heater_voltage_enter )
        self.heater_power.Bind( wx.EVT_KILL_FOCUS, self.heater_power_leave )
        self.heater_power.Bind( wx.EVT_TEXT, self.heater_power_change )
        self.heater_power.Bind( wx.EVT_TEXT_ENTER, self.heater_power_enter )
        self.target_resistance.Bind( wx.EVT_KILL_FOCUS, self.target_resistance_leave )
        self.target_resistance.Bind( wx.EVT_TEXT, self.target_resistance_change )
        self.target_resistance.Bind( wx.EVT_TEXT_ENTER, self.target_resistance_enter )
        self.maximum_temperature.Bind( wx.EVT_KILL_FOCUS, self.maximum_temperature_leave )
        self.maximum_temperature.Bind( wx.EVT_TEXT, self.maximum_temperature_change )
        self.maximum_temperature.Bind( wx.EVT_TEXT_ENTER, self.maximum_temperature_enter )
        self.ambient_temperature.Bind( wx.EVT_KILL_FOCUS, self.ambient_temperature_leave )
        self.ambient_temperature.Bind( wx.EVT_TEXT, self.ambient_temperature_change )
        self.ambient_temperature.Bind( wx.EVT_TEXT_ENTER, self.ambient_temperature_enter )
        self.thermal_resistance.Bind( wx.EVT_KILL_FOCUS, self.thermal_resistance_leave )
        self.thermal_resistance.Bind( wx.EVT_TEXT, self.thermal_resistance_change )
        self.thermal_resistance.Bind( wx.EVT_TEXT_ENTER, self.thermal_resistance_enter )
        self.power_margin.Bind( wx.EVT_KILL_FOCUS, self.power_margin_leave )
        self.power_margin.Bind( wx.EVT_TEXT, self.power_margin_change )
        self.power_margin.Bind( wx.EVT_TEXT_ENTER, self.power_margin_enter )
        self.minimum_spacing.Bind( wx.EVT_KILL_FOCUS, self.minimum_spacing_leave )
        self.minimum_spacing.Bind( wx.EVT_TEXT, self.minimum_spacing_change )
        self.minimum_spacing.Bind( wx.EVT_TEXT_ENTER, self.minimum_spacing_enter )
        self.track_thickness.Bind( wx.EVT_KILL_FOCUS, self.track_thickness_leave )
        self.track_thickness.Bind( wx.EVT_TEXT, self.track_thickness_change )
        self.track_thickness.Bind( wx.EVT_TEXT_ENTER, self.track_thickness_enter )
        self.track_resistivity.Bind( wx.EVT_KILL_FOCUS, self.track_resistivity_leave )
        self.track_resistivity.Bind( wx.EVT_TEXT, self.track_resistivity_change )
        self.track_resistivity.Bind( wx.EVT_TEXT_ENTER, self.track_resistivity_enter )
        self.track_width.Bind( wx.EVT_KILL_FOCUS, self.track_width_leave )
        self.track_width.Bind( wx.EVT_TEXT, self.track_width_change )
        self.track_width.Bind( wx.EVT_TEXT_ENTER, self.track_width_enter )
        self.track_spacing.Bind( wx.EVT_KILL_FOCUS, self.track_spacing_leave )
        self.track_spacing.Bind( wx.EVT_TEXT, self.track_spacing_change )
        self.track_spacing.Bind( wx.EVT_TEXT_ENTER, self.track_spacing_enter )
        self.track_pitch.Bind( wx.EVT_KILL_FOCUS, self.track_pitch_leave )
        self.track_pitch.Bind( wx.EVT_TEXT, self.track_pitch_change )
        self.track_pitch.Bind( wx.EVT_TEXT_ENTER, self.track_pitch_enter )
        self.load_button.Bind( wx.EVT_BUTTON, self.click_load_button )
        self.save_button.Bind( wx.EVT_BUTTON, self.click_save_button )
        self.analyze_button.Bind( wx.EVT_BUTTON, self.click_analyze_button )
        self.clear_button.Bind( wx.EVT_BUTTON, self.click_clear_button )
        self.apply_button.Bind( wx.EVT_BUTTON, self.click_apply_button )
        self.close_button.Bind( wx.EVT_BUTTON, self.click_close_button )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def heater_voltage_leave( self, event ):
        event.Skip()

    def heater_voltage_change( self, event ):
        event.Skip()

    def heater_voltage_enter( self, event ):
        event.Skip()

    def heater_power_leave( self, event ):
        event.Skip()

    def heater_power_change( self, event ):
        event.Skip()

    def heater_power_enter( self, event ):
        event.Skip()

    def target_resistance_leave( self, event ):
        event.Skip()

    def target_resistance_change( self, event ):
        event.Skip()

    def target_resistance_enter( self, event ):
        event.Skip()

    def maximum_temperature_leave( self, event ):
        event.Skip()

    def maximum_temperature_change( self, event ):
        event.Skip()

    def maximum_temperature_enter( self, event ):
        event.Skip()

    def ambient_temperature_leave( self, event ):
        event.Skip()

    def ambient_temperature_change( self, event ):
        event.Skip()

    def ambient_temperature_enter( self, event ):
        event.Skip()

    def thermal_resistance_leave( self, event ):
        event.Skip()

    def thermal_resistance_change( self, event ):
        event.Skip()

    def thermal_resistance_enter( self, event ):
        event.Skip()

    def power_margin_leave( self, event ):
        event.Skip()

    def power_margin_change( self, event ):
        event.Skip()

    def power_margin_enter( self, event ):
        event.Skip()

    def minimum_spacing_leave( self, event ):
        event.Skip()

    def minimum_spacing_change( self, event ):
        event.Skip()

    def minimum_spacing_enter( self, event ):
        event.Skip()

    def track_thickness_leave( self, event ):
        event.Skip()

    def track_thickness_change( self, event ):
        event.Skip()

    def track_thickness_enter( self, event ):
        event.Skip()

    def track_resistivity_leave( self, event ):
        event.Skip()

    def track_resistivity_change( self, event ):
        event.Skip()

    def track_resistivity_enter( self, event ):
        event.Skip()

    def track_width_leave( self, event ):
        event.Skip()

    def track_width_change( self, event ):
        event.Skip()

    def track_width_enter( self, event ):
        event.Skip()

    def track_spacing_leave( self, event ):
        event.Skip()

    def track_spacing_change( self, event ):
        event.Skip()

    def track_spacing_enter( self, event ):
        event.Skip()

    def track_pitch_leave( self, event ):
        event.Skip()

    def track_pitch_change( self, event ):
        event.Skip()

    def track_pitch_enter( self, event ):
        event.Skip()

    def click_load_button( self, event ):
        event.Skip()

    def click_save_button( self, event ):
        event.Skip()

    def click_analyze_button( self, event ):
        event.Skip()

    def click_clear_button( self, event ):
        event.Skip()

    def click_apply_button( self, event ):
        event.Skip()

    def click_close_button( self, event ):
        event.Skip()


