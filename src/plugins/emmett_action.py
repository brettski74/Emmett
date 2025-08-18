import os
import pcbnew
import wx
import traceback
from datetime import datetime

from .trace_segment_factory import TraceSegmentFactory
from .board_builder import BoardBuilder
from .board_analyzer import BoardAnalyzer
from .emmett_form import EmmettForm
from .al_track_router import AlTrackRouter
from .my_debug import debug, enable_debug

class EmmettAction( pcbnew.ActionPlugin ):
 
    def defaults( self ):
        self.name = "Emmett Element Router"
        self.category = "Modify PCB"
        self.description = "Heating Element Trace Router"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "./emmett_icon.png")
        self.parent_window = None

    def Run(self):
        try:
            board = pcbnew.GetBoard()
            enable_debug(True)
            if not board:
                self._info_msg("No PCB board is currently loaded.")
                return

            # Create and show the form
            enable_debug(True)
            debug("Running Emmett")
            builder = BoardBuilder(board)
            analyzer = BoardAnalyzer(board)
            factory = TraceSegmentFactory()
            router = AlTrackRouter(factory)
            form = EmmettForm(self._find_parent_window(), board, builder, analyzer, router)
            result = form.ShowModal()
            form.Destroy()
            
            # Handle form result if needed
            if result == wx.ID_OK:
                # User clicked Generate button
                self._handle_generate_clicked(form, board)
            elif result == wx.ID_APPLY:
                # User clicked Apply button
                self._handle_apply_clicked(form, board)
            
            return

        except Exception as e:
            self._error_msg(f"Error launching form: {e}")
    
    def _find_parent_window(self):
        if self.parent_window is None:
            try:
                tops = wx.GetTopLevelWindows()
                for w in tops:
                    title = w.GetTitle().lower()
                    if ('pcbnew' in title or 'pcb editor' in title) and not 'python' in title:
                        self.parent_window = w
                        break
            except:
                pass
        
        return self.parent_window

    def _info_msg(self, msg):
        wx.MessageBox(msg, "Emmett", wx.OK | wx.ICON_INFORMATION, self._find_parent_window())

    def _error_msg(self, msg):
        wx.MessageBox(msg, "Emmett Error", wx.OK | wx.ICON_ERROR, self._find_parent_window())

    def _handle_generate_clicked(self, form, board):
        """Handle when user clicks Generate button."""
        try:
            debug(f"form.track_width_value: {form.track_width_value}, form.track_spacing_value: {form.track_spacing_value}")
            builder = form.builder
            router = form.router
            factory = router.factory
            router.parent = self.parent_window
            router.width = float(form.track_width_value) * 1e3
            router.spacing = float(form.track_spacing_value) * 1e3
            tracks = router.update_board(builder)

            cold_resistance = factory.calculate_total_resistance(tracks, float(form.ambient_temperature.GetValue()))
            hot_resistance = factory.calculate_total_resistance(tracks, float(form.maximum_temperature.GetValue()))

            analyzer = form.analyzer
            text = analyzer.find_text_element("Cold Resistance: ")
            if text is not None:
                text.SetText(f"Cold Resistance: {cold_resistance:.3f}Ω\nHot Resistance: {hot_resistance:.3f}Ω\nVoltage: {form.heater_voltage.GetValue()}V\nPower: {form.heater_power.GetValue()}W\n\nGenerated: {datetime.now().strftime('%Y%m%d-%H%M%S')}")
            
            text = analyzer.find_text_element("Maximum Temperature: ")
            if text is not None:
                text.SetText(f"Maximum Temperature: {form.maximum_temperature.GetValue()}°C\nAmbient Temperature: {form.ambient_temperature.GetValue()}°C\nThermal Resistance: {form.thermal_resistance.GetValue()}K/W\nPower Margin: {form.power_margin.GetValue()}%")

            text = analyzer.find_text_element("Track Width: ")
            if text is not None:
                text.SetText(f"Track Width: {form.track_width.GetValue()}mm\nTrack Spacing: {form.track_spacing.GetValue()}mm\nTrack Pitch: {form.track_pitch.GetValue()}mm\nWidth: {form.extent_width.GetValue()}mm\nHeight: {form.extent_height.GetValue()}mm")

        except Exception as e:
            msg = f"Error doing the shit you asked on this board: {e}"
            msg += f"\n{traceback.format_exc()}"
            self._error_msg(msg)
    
    def _handle_apply_clicked(self, form, board):
        """Handle when user clicks Apply button."""
        pass



