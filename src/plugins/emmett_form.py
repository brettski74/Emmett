import os
import traceback
import wx
import pcbnew
from .emmett_dialog import EmmettDialog
from .board_builder import BoardBuilder
from .board_analyzer import BoardAnalyzer
from .trace_segment_factory import TraceSegmentFactory
from .my_debug import debug,enable_debug
from .track_router import TrackRouter
from .al_track_router import AlTrackRouter

enable_debug()

def resource_dir() -> str:
    plugin_dir = os.path.dirname(os.path.abspath(__file__))
    namespace = os.path.basename(plugin_dir)
    plugin_parent = os.path.dirname(plugin_dir)
    third_party_dir = os.path.dirname(plugin_parent)
    
    result = os.path.join(third_party_dir, "resources", namespace)
    return result

def fadd(a, b) -> str:
    return fnormalize(float(a.GetValue() or 0) + float(b.GetValue() or 0))

def fsub(a, b) -> str:
    return fnormalize(float(a.GetValue() or 0) - float(b.GetValue() or 0))

def fnormalize(value) -> str:
    return f"{value:.3f}".rstrip('0').rstrip('.')

def fset(field, value, events = False) -> str:
    val = fnormalize(value)
    if events:
        debug(f"fset: {field.GetName()}: {val}")
        field.SetValue(val)
    else:
        field.ChangeValue(val)

    return val

def fdefault(field, value, events = False) -> str:
    val = field.GetValue()
    if val == "":
        return fset(field, value, events)
    return val

def field_normalize(field) -> str:
    value = float(field.GetValue() or 0)
    result = fnormalize(value)
    field.ChangeValue(result)
    return result

class EmmettForm(EmmettDialog):
    def __init__(self, frame, board: pcbnew.BOARD, builder: BoardBuilder, analyzer: BoardAnalyzer, router: TrackRouter):
        super().__init__(frame)

        self.logo_bitmap.SetBitmap(wx.Bitmap(os.path.join(resource_dir(), "emmett-192.png")))
        self.calculation_bitmap.SetBitmap(wx.Bitmap(os.path.join(resource_dir(), "emmett-excited-192.png")))
        self.board = board
        self.builder = builder
        self.analyzer = analyzer
        self.router = router

        self.track_width_value = ""
        self.track_spacing_value = ""
        self.track_pitch_value = ""
        self.track_order = 0x123

        self.click_analyze_button(None)

        self.m_main_notebook.ChangeSelection(0)
        self.heater_voltage.SetFocus()

    def click_clear_button(self, event):
        self.builder.clear_tracks()

    def click_analyze_button(self, event):
        try:
            self.router.analyze_board(self.analyzer)

            left, top, right, bottom = self.router.get_extents_mm()

            fset(self.extent_left, left)
            fset(self.extent_top, top)
            fset(self.extent_right, right)
            fset(self.extent_bottom, bottom)

            thickness = float(fdefault(self.track_thickness, 35)) * 1e-6
            resistivity = float(fdefault(self.track_resistivity, 1.68)) * 1e-8

            factory = TraceSegmentFactory()
            factory.thickness = thickness
            factory.resistivity = resistivity

            tracks = self.analyzer.extract_trace_segments(factory, layer_name = "F.Cu")

            if len(tracks) > 0:
                debug(f"router.spacing: {self.router.spacing}, router.width: {self.router.width}")
                self.track_pitch_value = fset(self.track_pitch, (self.router.width + self.router.spacing) / 1000, True)
                self.track_spacing_value = fset(self.track_spacing, self.router.spacing / 1000, True)
                self.track_width_value = fset(self.track_width, self.router.width / 1000, True)
                self.track_order = 0x123

            cold = fdefault(self.ambient_temperature, 25)
            hot = fdefault(self.maximum_temperature, 220)

            fset(self.cold_resistance, factory.calculate_total_resistance(tracks, float(cold)))
            fset(self.hot_resistance, factory.calculate_total_resistance(tracks, float(hot)))

            self.m_main_notebook.ChangeSelection(1)
            self.m_calculationPanel.SetFocus()

        except Exception as e:
            msg = f"Error analyzing board: {e}"
            msg += f"\n{traceback.format_exc()}"
            wx.MessageBox(msg, "Emmett Error", wx.OK | wx.ICON_ERROR)

    def old_analyze(self, event):
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
            msg = f"Error while opening Emmett form: {e}"
            msg += f"\n{traceback.format_exc()}"
            wx.MessageBox(msg, "Emmett Error", wx.OK | wx.ICON_ERROR)

    def track_width_enter(self, event):
        self.track_width_leave(event)

    def track_width_leave(self, event):
        newValue = field_normalize(self.track_width)
        if newValue == self.track_width_value:
            return

        debug(f"track_width_leave: {newValue}")
        self.track_width_value = newValue

        spacing_order = (self.track_order & 0x0f0) >> 4
        pitch_order = self.track_order & 0x00f

        debug(f"track_order: {self.track_order:#03x}, spacing_order: {spacing_order}, pitch_order: {pitch_order}")

        if spacing_order > pitch_order:
            self.track_order = 0x132
            newValue = fsub(self.track_pitch, self.track_width)
            self.track_spacing.ChangeValue(newValue)
            self.track_spacing_value = newValue
        else:
            self.track_order = 0x123
            newValue = fadd(self.track_width, self.track_spacing)
            self.track_pitch.ChangeValue(newValue)
            self.track_pitch_value = newValue

    def track_pitch_enter(self, event):
        self.track_pitch_leave(event)

    def track_pitch_leave(self, event):
        newValue = field_normalize(self.track_pitch)
        debug(f"track_pitch_leave: {newValue}, {self.track_pitch_value}")
        if newValue == self.track_pitch_value:
            return

        self.track_pitch_value = newValue

        spacing_order = (self.track_order & 0x0f0) >> 4
        width_order = (self.track_order & 0xf00) >> 8

        debug(f"track_order: {self.track_order:#03x}, width_order: {width_order}, spacing_order: {spacing_order}")

        if spacing_order <= width_order:
            self.track_order = 0x321
            newValue = fsub(self.track_pitch, self.track_spacing)
            self.track_width.ChangeValue(newValue)
            self.track_width_value = newValue
        else:
            self.track_order = 0x231
            newValue = fsub(self.track_pitch, self.track_width)
            self.track_spacing.ChangeValue(newValue)
            self.track_spacing_value = newValue

    def track_spacing_enter(self, event):
        self.track_spacing_leave(event)

    def track_spacing_leave(self, event):
        newValue = field_normalize(self.track_spacing)
        newSpacing = float(newValue)
        debug(f"track_spacing_leave: {newValue}, {newSpacing}")

        if newValue == self.track_spacing_value:
            return

        debug(f"track_spacing_leave: {newValue}")

        self.track_spacing_value = newValue

        pitch_order = (self.track_order & 0x00f)
        width_order = (self.track_order & 0xf00) >> 8

        debug(f"track_order: {self.track_order:#03x}, width_order: {width_order}, pitch_order: {pitch_order}")

        if pitch_order <= width_order:
            self.track_order = 0x312
            newValue = fsub(self.track_pitch, self.track_spacing)
            self.track_width.ChangeValue(newValue)
            self.track_width_value = newValue
        else:
            self.track_order = 0x213
            newValue = fadd(self.track_width, self.track_spacing)
            self.track_pitch.ChangeValue(newValue)
            self.track_pitch_value = newValue