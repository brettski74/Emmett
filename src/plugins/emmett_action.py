import os
import pcbnew
import wx

from .trace_segment_factory import TraceSegmentFactory
from .board_builder import BoardBuilder
from .board_analyzer import BoardAnalyzer
from .emmett_form import EmmettForm

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
                wx.MessageBox("No PCB board is currently loaded.", "Emmett", wx.OK | wx.ICON_INFORMATION)
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
            wx.MessageBox(f"Error launching dialog: {e}", "Emmett Error", wx.OK | wx.ICON_ERROR)
    
    def _find_parent_window(self):
        if self.parent_window is None:
            try:
                tops = wx.GetTopLevelWindows()
                for w in tops:
                    if 'pcbnew' in w.GetTitle().lower() and not 'python' in w.GetTitle().lower():
                        self.parent_window = w
                        break
            except:
                pass
        
        return self.parent_window

    def _handle_generate_clicked(self, dialog, board):
        """Handle when user clicks Generate button."""
        try:
            # Get the currently loaded board
            # Create the trace segment factory with default copper parameters
            factory = TraceSegmentFactory()
            
            # Create the board analyzer
            analyzer = BoardAnalyzer(board)
            
            # Extract trace segments from the board
            trace_segments = analyzer.extract_trace_segments(factory, layer_name = "F.Cu")
  
            if not trace_segments:
                wx.MessageBox("No trace segments found on the board.", "Emmett", wx.OK | wx.ICON_INFORMATION)
                return
            
            # Calculate total resistance
            total_resistance = factory.calculate_total_resistance(trace_segments)
            
            # Calculate temperature-compensated resistances
            resistance_20c = factory.calculate_total_resistance(trace_segments, temperature_celsius=20)
            resistance_220c = factory.calculate_total_resistance(trace_segments, temperature_celsius=220)
            
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
            
            # Get board info for context
            board_info = analyzer.get_board_info()
            
            # Create detailed message with temperature information
            message = f"Trace resistance analysis:\n\n"
            message += f"At 20°C (room temperature): {resistance_20c_text}\n"
            message += f"At 220°C (operating temperature): {resistance_220c_text}\n\n"
            message += f"Board: {board_info['filename']}\n"
            message += f"Trace segments: {len(trace_segments)}\n"
            message += f"Copper layers: {board_info['layers']}\n"
            message += f"Total tracks: {board_info['tracks_count']}"
            
            wx.MessageBox(message, "Emmett Element Router", wx.OK | wx.ICON_INFORMATION)
            
        except Exception as e:
            wx.MessageBox(f"Error analyzing board: {e}", "Emmett Error", wx.OK | wx.ICON_ERROR)
    
    def _handle_apply_clicked(self, dialog, board):
        """Handle when user clicks Apply button."""
        try:
            # Similar to generate but keep dialog open
            # For now, just show a message
            wx.MessageBox("Apply functionality not yet implemented.", "Emmett", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"Error applying changes: {e}", "Emmett Error", wx.OK | wx.ICON_ERROR)


