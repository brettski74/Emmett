import os
import traceback
import wx
from math import sqrt

import pcbnew

from typing import Optional

from .emmett_dialog import EmmettDialog
from .board_builder import BoardBuilder
from .board_analyzer import BoardAnalyzer
from .trace_segment_factory import TraceSegmentFactory, temperature_adjust_resistance
from .my_debug import debug,enable_debug, stringify
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
    return fnormalize(fget(a) + fget(b))

def fsub(a, b) -> str:
    return fnormalize(fget(a) - fget(b))

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

def fget(field) -> float:
    return float(field.GetValue() or 0)

def fdefault(field, value, events = False) -> str:
    val = field.GetValue()
    if val == "":
        return fset(field, value, events)
    return val

def field_normalize(field) -> str:
    value = fget(field)
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

    def derive_thermal_electrical(self, board_text: Optional[dict] = None):
        if board_text is None:
            board_text = {}

        width = float(self.extent_width.GetValue())
        height = float(self.extent_height.GetValue())
        area = width * height

        # This formula is a guess based on empirical data with 100x100mm hotplates and a conversation with GPT5.
        # It's based on the thermal resistance to ambient of many of my FR4 hotplates being measured in the 2.7-2.9 K/W range
        # And GPT5's comment that making the hotplate twice as big (ie. 4 times the area) will scale the thermal resistance
        # down by a factor of about 1/3.36. I then extrapolated that into the power formula below.
        # It may or may not work well. We would need more empirical data to be sure or maybe a Phd in physics of heat flow.
        if "Thermal Resistance" in board_text:
            self.thermal_resistance.ChangeValue(board_text["Thermal Resistance"])
            self.thermal_resistance_value = board_text["Thermal Resistance"]
            thermal_resistance = float(board_text["Thermal Resistance"])
        else:
            thermal_resistance = 2.8 * (10000/area) ** 0.874230616502018
            self.thermal_resistance_value = fset(self.thermal_resistance, thermal_resistance)

        # If power is set, then use that and calculate the power margin, otherwise calcualte required power based on the power margin
        if "Power Margin" in board_text:
            self.power_margin.ChangeValue(board_text["Power Margin"])
            self.power_margin_value = board_text["Power Margin"]
            margin = float(board_text["Power Margin"])
        else:
            margin = float(self.power_margin.GetValue() or 0)

        if "Power" in board_text:
            self.heater_power.ChangeValue(board_text["Power"])
            self.heater_power_value = board_text["Power"]
            power = float(board_text["Power"])
        elif self.heater_power.GetValue() != "":
            power = float(self.heater_power.GetValue())
            
        if "Voltage" in board_text:
            self.heater_voltage.ChangeValue(board_text["Voltage"])
            self.heater_voltage_value = board_text["Voltage"]
            voltage = float(board_text["Voltage"])
        elif self.heater_voltage.GetValue() != "":
            voltage = float(self.heater_voltage.GetValue() or 0)

        if margin <= 0:
            if power > 0:
                margin = self.calculate_power_margin(power)
                self.power_margin_value = fset(self.power_margin, round(margin, 2))
            else:
                margin = 100
                self.power_margin_value = fset(self.power_margin, margin)

        if power <= 0:
            power = self.calculate_margin_power(margin)
            self.heater_power_value = fset(self.heater_power, round(power, 2))

        if voltage <= 0:
            voltage = round(sqrt(power * thermal_resistance), 2)
            self.heater_voltage_value = fset(self.heater_voltage, voltage)

        self.calculate_cold_current()

    def click_resize_button(self, event):
        # We will work in microns and round to the nearest micron before applying to the board.
        # Get the centre point in microns
        centre = (round((fget(self.extent_left) + fget(self.extent_right))*500), round((fget(self.extent_top) + fget(self.extent_bottom))*500))

        # Get the current width and height in microns
        width = round((fget(self.extent_right) - fget(self.extent_left)) * 1000)
        height = round((fget(self.extent_bottom) - fget(self.extent_top)) * 1000)

        # Get the new width and height
        new_width = round(fget(self.extent_width) * 1000)
        new_height = round(fget(self.extent_height) * 1000)

        # Get the horizontal and vertical deltas - half-scale as we will apply equally on both sides to keep the same centre
        deltah = (new_width - width) / 2
        deltav = (new_height - height) / 2
        dx = int(deltah * 1000)
        dy = int(deltav * 1000)

        hole = self.analyzer.get_closest_hole((fget(self.extent_left)*1e6, fget(self.extent_top)*1e6))
        debug(f"hole: {stringify(hole.footprint)}, delta: ({deltah},{deltav}), dx,dy: ({-dx},{-dy})")
        hole.footprint.Move(pcbnew.VECTOR2I(-dx, -dy))

        hole = self.analyzer.get_closest_hole((fget(self.extent_right)*1e6, fget(self.extent_top)*1e6))
        debug(f"hole: {stringify(hole.footprint)}, delta: ({deltah},{deltav}), dx,dy: ({dx},{-dy})")
        hole.footprint.Move(pcbnew.VECTOR2I(dx, -dy))

        hole = self.analyzer.get_closest_hole((fget(self.extent_left)*1e6, fget(self.extent_bottom)*1e6))
        debug(f"hole: {stringify(hole.footprint)}, delta: ({deltah},{deltav}), dx,dy: ({-dx},{dy})")
        hole.footprint.Move(pcbnew.VECTOR2I(-dx, dy))

        hole = self.analyzer.get_closest_hole((fget(self.extent_right)*1e6, fget(self.extent_bottom)*1e6))
        debug(f"hole: {stringify(hole.footprint)}, delta: ({deltah},{deltav}), dx,dy: ({dx},{dy})")
        hole.footprint.Move(pcbnew.VECTOR2I(dx, dy))

        drawings = self.board.GetDrawings()
        for drawing in drawings:
            if isinstance(drawing, pcbnew.PCB_SHAPE):
                if drawing.GetLayer() == pcbnew.Edge_Cuts:
                    if drawing.ShowShape() == "Line":
                        startx = drawing.GetStartX()
                        starty = drawing.GetStartY()
                        endx = drawing.GetEndX()
                        endy = drawing.GetEndY()

                        if startx == endx:
                            # Vertical line
                            if starty > endy:
                                starty, endy = endy, starty
                            
                            if startx > centre[0]*1000:
                                newx = int(startx + deltah * 1000)
                            else:
                                newx = int(startx - deltah * 1000)
                            debug(f"newx: {newx}, start: ({startx},{starty}), end: ({endx},{endy}), delta: ({deltah},{deltav}), centre: ({centre[0]},{centre[1]})")
                            
                            drawing.SetStart(pcbnew.VECTOR2I(newx, int(starty - deltav * 1000)))
                            drawing.SetEnd(pcbnew.VECTOR2I(newx, int(endy + deltav * 1000)))
                        elif starty == endy:
                            #Horixontal line
                            if startx > endx:
                                startx, endx = endx, startx
                            
                            if starty > centre[1]*1000:
                                newy = int(starty + deltav * 1000)
                            else:
                                newy = int(starty - deltav * 1000)
                            debug(f"newy: {newy}, start: ({startx},{starty}), end: ({endx},{endy}), delta: ({deltah},{deltav}), centre: ({centre[0]},{centre[1]})")
                            
                            drawing.SetStart(pcbnew.VECTOR2I(int(startx - deltah * 1000), newy))
                            drawing.SetEnd(pcbnew.VECTOR2I(int(endx + deltah * 1000), newy))
                        else:
                            raise ValueError("Only horizontal and vertical lines are supported during resize")

                    elif drawing.ShowShape() == "Arc":
                        arc_centre = drawing.GetCenter()
                        if arc_centre[0] > centre[0]*1000:
                            dx = deltah * 1000
                        else:
                            dx = -deltah * 1000
                        
                        if arc_centre[1] > centre[1]*1000:
                            dy = deltav * 1000
                        else:
                            dy = -deltav * 1000

                        drawing.Move(pcbnew.VECTOR2I(int(dx), int(dy)))

        pcbnew.Refresh()
        self.click_analyze_button(None)

    def click_analyze_button(self, event):
        try:
            self.router.analyze_board(self.analyzer)

            left, top, right, bottom = self.router.get_extents_mm()

            self.extent_left_value = fset(self.extent_left, left)
            self.extent_top_value = fset(self.extent_top, top)
            self.extent_right_value = fset(self.extent_right, right)
            self.extent_bottom_value = fset(self.extent_bottom, bottom)
            self.extent_width_value = fset(self.extent_width, right - left)
            self.extent_height_value = fset(self.extent_height, bottom - top)

            board_text = self.analyzer.parse_board_text()

            if "Track Thickness" in board_text:
                self.track_thickness.ChangeValue(board_text["Track Thickness"])
                self.track_thickness_value = board_text["Track Thickness"]
                thickness = float(board_text["Track Thickness"]) * 1e-6
            else:
                self.track_thickness_value = fdefault(self.track_thickness, 35)
                thickness = float(self.track_thickness_value) * 1e-6

            resistivity = 1.68e-8

            factory = TraceSegmentFactory()
            factory.thickness = thickness
            factory.resistivity = resistivity

            tracks = self.analyzer.extract_trace_segments(factory, layer_name = "F.Cu")

            if "Track Pitch" in board_text:
                self.track_pitch.ChangeValue(board_text["Track Pitch"])
                self.track_pitch_value = board_text["Track Pitch"]
            elif len(tracks) > 0:
                self.track_pitch_value = fset(self.track_pitch, (self.router.width + self.router.spacing) / 1000)
            
            if "Track Spacing" in board_text:
                self.track_spacing.ChangeValue(board_text["Track Spacing"])
                self.track_spacing_value = board_text["Track Spacing"]
            elif len(tracks) > 0:
                self.track_spacing_value = fset(self.track_spacing, self.router.spacing / 1000)
            
            if "Track Width" in board_text:
                self.track_width.ChangeValue(board_text["Track Width"])
                self.track_width_value = board_text["Track Width"]
            elif len(tracks) > 0:
                self.track_width_value = fset(self.track_width, self.router.width / 1000)

            self.track_order = 0x123

            if "Ambient Temperature" in board_text:
                self.ambient_temperature.ChangeValue(board_text["Ambient Temperature"])
                self.ambient_temperature_value = board_text["Ambient Temperature"]
            else:
                self.ambient_temperature_value = fdefault(self.ambient_temperature, 25)

            if "Maximum Temperature" in board_text:
                self.maximum_temperature.ChangeValue(board_text["Maximum Temperature"])
                self.maximum_temperature_value = board_text["Maximum Temperature"]
            else:
                self.maximum_temperature_value = fdefault(self.maximum_temperature, 220)

            if "Cold Resistance" in board_text:
                self.cold_resistance.ChangeValue(board_text["Cold Resistance"])
            else:
                fset(self.cold_resistance, factory.calculate_total_resistance(tracks, float(self.ambient_temperature_value)))
            
            if "Hot Resistance" in board_text:
                self.hot_resistance.ChangeValue(board_text["Hot Resistance"])
                self.target_resistance.ChangeValue(board_text["Hot Resistance"])
                self.target_resistance_value = board_text["Hot Resistance"]
            else:
                fset(self.hot_resistance, factory.calculate_total_resistance(tracks, float(self.maximum_temperature_value)))

            self.derive_thermal_electrical(board_text)

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

    def power_margin_enter(self, event):
        self.power_margin_leave(event)

    def calculate_margin_power(self, margin: float) -> float:
        margin = margin or fget(self.power_margin)
        hold_power = (fget(self.maximum_temperature) - fget(self.ambient_temperature)) / fget(self.thermal_resistance)
        return hold_power * (1 + margin/100)

    def calculate_power_margin(self, power: float) -> float:
        power = power or fget(self.heater_power)
        hold_power = (fget(self.maximum_temperature) - fget(self.ambient_temperature)) / fget(self.thermal_resistance)
        return (power / hold_power - 1) * 100

    def calculate_target_resistance(self) -> float:
        power = fget(self.heater_power)
        voltage = fget(self.heater_voltage)
        target_resistance = voltage * voltage / power
        self.target_resistance_value = fset(self.target_resistance, target_resistance)
        self.calculate_cold_current()
        return target_resistance

    def calculate_cold_current(self):
        tr = fget(self.target_resistance)
        at = fget(self.ambient_temperature)
        mt = fget(self.maximum_temperature)
        hp = fget(self.heater_power)
        cold_resistance = temperature_adjust_resistance(tr, mt, at)
        debug(f"target_resistance: {tr}, ambient_temperature: {at}, maximum_temperature: {mt}, heater_power: {hp}, cold_resistance: {cold_resistance}")
        fset(self.cold_current, sqrt(hp / cold_resistance))

    def power_margin_leave(self, event):
        newValue = field_normalize(self.power_margin)
        debug(f"power_margin_leave: {newValue}")
        if newValue == self.power_margin_value:
            return

        self.power_margin_value = newValue

        power = self.calculate_margin_power(float(newValue))
        fset(self.heater_power, round(power, 2))
        self.heater_power_leave(event)

    def thermal_resistance_change(self, event):
        self.thermal_resistance_leave(event)

    def thermal_resistance_leave(self, event):
        newValue = field_normalize(self.thermal_resistance)
        debug(f"thermal_resistance_leave: {newValue}")
        if newValue == self.thermal_resistance_value:
            return

        self.thermal_resistance_value = newValue

        power = self.calculate_margin_power(None)
        fset(self.heater_power, round(power, 2))
        self.heater_power_leave(event)

    def heater_power_enter(self, event):
        self.heater_power_leave(event)

    def heater_power_leave(self, event):
        newValue = field_normalize(self.heater_power)
        debug(f"heater_power_leave: {newValue}")
        if newValue == self.heater_power_value:
            return

        self.heater_power_value = newValue

        margin = self.calculate_power_margin(float(newValue))
        self.power_margin_value = fset(self.power_margin, round(margin, 1))

        self.calculate_target_resistance()

    def heater_voltage_enter(self, event):
        self.heater_voltage_leave(event)

    def heater_voltage_leave(self, event):
        newValue = field_normalize(self.heater_voltage)
        debug(f"heater_voltage_leave: {newValue}")
        if newValue == self.heater_voltage_value:
            return

        self.heater_voltage_value = newValue

        self.calculate_target_resistance()

    def ambient_temperature_enter(self, event):
        self.ambient_temperature_leave(event)

    def ambient_temperature_leave(self, event):
        newValue = field_normalize(self.ambient_temperature)
        debug(f"ambient_temperature_leave: {newValue}")
        if newValue == self.ambient_temperature_value:
            return

        self.ambient_temperature_value = newValue

        power = self.calculate_margin_power(None)
        fset(self.heater_power, round(power, 2))
        self.heater_power_leave(event)

    def maximum_temperature_enter(self, event):
        self.maximum_temperature_leave(event)

    def maximum_temperature_leave(self, event):
        newValue = field_normalize(self.maximum_temperature)
        debug(f"maximum_temperature_leave: {newValue}")
        if newValue == self.maximum_temperature_value:
            return

        self.maximum_temperature_value = newValue

        power = self.calculate_margin_power(None)
        fset(self.heater_power, round(power, 2))
        self.heater_power_leave(event)

    def click_geometryze_button(self, event):
        try:
            self.router.optimize_tracks(fget(self.minimum_spacing) * 1000, fget(self.target_resistance), fget(self.maximum_temperature))

            self.track_pitch_value = fset(self.track_pitch, self.router.pitch / 1000, True)
            self.track_spacing_value = fset(self.track_spacing, self.router.spacing / 1000, True)
            self.track_width_value = fset(self.track_width, self.router.width / 1000, True)
            self.track_order = 0x231

            self.m_main_notebook.ChangeSelection(1)
        except Exception as e:
            msg = f"Error optimizing tracks: {e}"
            msg += f"\n{traceback.format_exc()}"
            wx.MessageBox(msg, "Emmett Error", wx.OK | wx.ICON_ERROR)
