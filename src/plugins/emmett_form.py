import wx
import pcbnew
from .emmett_dialog import EmmettDialog
from .board_builder import BoardBuilder
from .board_analyzer import BoardAnalyzer
from .trace_segment_factory import TraceSegmentFactory

class EmmettForm(EmmettDialog):
    def __init__(self, frame, board: pcbnew.BOARD, builder: BoardBuilder, analyzer: BoardAnalyzer):
        super().__init__(frame)
        self.board = board
        self.builder = builder
        self.analyzer = analyzer

    def HandleClearClick(self, event):
        self.builder.clear_tracks()

    def HandleAnalyzeClick(self, event):
        try:
            # Get the currently loaded board
            # Create the trace segment factory with default copper parameters
            factory = TraceSegmentFactory()
            
            # Extract trace segments from the board
            trace_segments = self.analyzer.extract_trace_segments(factory, layer_name = "F.Cu")
  
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
            board_info = self.analyzer.get_board_info()
            
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
