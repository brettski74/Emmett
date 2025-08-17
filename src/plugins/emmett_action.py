import os
import pcbnew
import wx
import traceback

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

            # Calculate temperature-compensated resistances
            resistance_20c = factory.calculate_total_resistance(tracks, temperature_celsius=20)
            resistance_220c = factory.calculate_total_resistance(tracks, temperature_celsius=220)
            
            # Format the resistance values with appropriate units
            def format_resistance(resistance):
                if resistance >= 10.0:
                    return f"{resistance:.3f} Ω"
                else:
                    # Convert to milliohms for values less than 10 ohms
                    resistance_milliohms = resistance * 1000
                    return f"{resistance_milliohms:.1f} mΩ"
            
            resistance_20c_text = format_resistance(resistance_20c)
            resistance_220c_text = format_resistance(resistance_220c)
            
            # Create detailed message with temperature information
            message = f"Trace resistance analysis:\n\n"
            message += f"At 20°C (room temperature): {resistance_20c_text}\n"
            message += f"At 220°C (operating temperature): {resistance_220c_text}\n\n"
            
            self._info_msg(message)
            
        except Exception as e:
            msg = f"Error doing the shit you asked on this board: {e}"
            msg += f"\n{traceback.format_exc()}"
            self._error_msg(msg)
    
    def _handle_apply_clicked(self, form, board):
        """Handle when user clicks Apply button."""
        pass



