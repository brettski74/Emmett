import os
import pcbnew
import wx
import traceback

from .trace_segment_factory import TraceSegmentFactory
from .board_builder import BoardBuilder
from .board_analyzer import BoardAnalyzer
from .emmett_form import EmmettForm
from .al_track_router import AlTrackRouter

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
            if not board:
                self._info_msg("No PCB board is currently loaded.")
                return

            # Create and show the dialog
            builder = BoardBuilder(board)
            analyzer = BoardAnalyzer(board)
            dialog = EmmettForm(self._find_parent_window(), board, builder, analyzer)
            result = dialog.ShowModal()
            dialog.Destroy()
            
            # Handle dialog result if needed
            if result == wx.ID_OK:
                # User clicked Generate button
                self._handle_generate_clicked(dialog, board)
            elif result == wx.ID_APPLY:
                # User clicked Apply button
                self._handle_apply_clicked(dialog, board)
            
            return

        except Exception as e:
            self._error_msg(f"Error launching dialog: {e}")
    
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

    def _handle_generate_clicked(self, dialog, board):
        """Handle when user clicks Generate button."""
        try:
            # Get the currently loaded board
            board = pcbnew.GetBoard()
            if not board:
                self._info_msg("No PCB board is currently loaded.")
                return
            
            factory = TraceSegmentFactory()
            builder = dialog.builder
            analyzer = dialog.analyzer
            router = AlTrackRouter(factory)
            router.parent = self.parent_window
            tracks = router.generate_tracks()
            #self._info_msg(router.log)
            builder.add_tracks(tracks)

            # Calculate total resistance
            total_resistance = factory.calculate_total_resistance(tracks)
            
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
    
    def _handle_apply_clicked(self, dialog, board):
        """Handle when user clicks Apply button."""
        pass



