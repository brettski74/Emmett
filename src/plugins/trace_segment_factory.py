"""
TraceSegmentFactory and related classes for PCB trace resistance calculation.

This module provides classes for creating trace segments and calculating
their resistance using accurate physical models.
"""

import wx

import pcbnew

import math
from typing import List, Tuple, Union, Optional
from abc import ABC, abstractmethod

from .vector_utils import add_vec, sub_vec, scale_vec, shrink_vec, normalize_vec, perp_vec, invert_vec, x_mirror_vec, y_mirror_vec

KICAD_MM = 1e3
KICAD_UNITS = 1e9

class TraceSegment(ABC):
    """
    Abstract base class for trace segments.

    All measurements are in metres to make the resistance calculations easier to follow.
    """
    
    def __init__(self, start_point: Tuple[float, float], end_point: Tuple[float, float], 
                 width: float, net: Optional[str] = None):
        """
        Initialize a trace segment.
        
        Args:
            start_point: (x, y) coordinates of start point in meters
            end_point: (x, y) coordinates of end point in meters
            width: Trace width in meters
            net: Net name for this trace segment (optional)
        """
        self.start_point = start_point
        self.end_point = end_point
        self.width = width
        self._net = net
    
    @property
    def net(self) -> Optional[str]:
        """Get the net name for this trace segment."""
        return self._net
    
    @net.setter
    def net(self, value: Optional[str]):
        """Set the net name for this trace segment."""
        self._net = value
    
    @abstractmethod
    def move(self, offset: Tuple[float, float]):
        """Move the track by the given offset."""
        pass

    @abstractmethod
    def plot(self, board: pcbnew.BOARD, offset: Optional[Tuple[float, float]] = None):
        """Plot the track on the board."""
        pass

    @abstractmethod
    def get_length(self) -> float:
        """Get the length of the trace segment in meters."""
        pass
    
    @abstractmethod
    def get_resistance(self, temperature_celsius: Optional[float] = None) -> float:
        """
        Calculate the resistance of this trace segment.
        
        Args:
            temperature_celsius: Optional temperature in °C for TCR adjustment
                               (assumes resistivity is at 20°C)
        
        Returns:
            Resistance in Ohms (temperature-adjusted if temperature provided)
        """
        pass
    
    def get_width(self) -> float:
        """Get the width of the trace segment in meters."""
        return self.width

    def __str__(self):
        return f"{self.__class__.__name__}(start={self.start_point}, end={self.end_point}, width={self.width})"

    def get_resistance(self, temperature_celsius: Optional[float] = None) -> float:
        """
        Calculate resistance of a trace segment.
        
        Args:
            temperature_celsius: Optional temperature in °C for TCR adjustment
                               (assumes resistivity is at 20°C)
        
        Returns:
            Resistance in Ohms (temperature-adjusted if temperature provided)
        """
        length = self.get_length()
        width = self.get_width()
        cross_sectional_area = width * self._factory.thickness
        
        # R = ρ * L / A
        resistance = self._factory.resistivity * length / cross_sectional_area
        
        # Apply temperature coefficient of resistance if temperature provided
        if temperature_celsius is not None:
            resistance = self._factory._apply_temperature_adjustment(resistance, temperature_celsius)
        
        return resistance


class LinearSegment(TraceSegment):
    """Represents a straight line trace segment."""
    
    def __init__(self, start_point: Tuple[float, float], end_point: Tuple[float, float],
                 width: float, factory: 'TraceSegmentFactory', net: Optional[str] = None):
        """
        Initialize a linear segment.
        
        Args:
            start_point: (x, y) coordinates of start point in meters
            end_point: (x, y) coordinates of end point in meters
            width: Trace width in meters
            factory: Reference to the factory that created this segment
            net: Net name for this trace segment (optional)
        """
        super().__init__(start_point, end_point, width, net)
        self._factory = factory
    
    def get_length(self) -> float:
        """Calculate the length of the straight line segment."""
        dx = self.end_point[0] - self.start_point[0]
        dy = self.end_point[1] - self.start_point[1]
        return math.sqrt(dx*dx + dy*dy)
    
    def move_start(self, offset: Tuple[float, float]):
        """Move the start point of the segment by the given offset."""
        self.start_point = (self.start_point[0] + offset[0], self.start_point[1] + offset[1])
    
    def move_end(self, offset: Tuple[float, float]):
        """Move the end point of the segment by the given offset."""
        self.end_point = (self.end_point[0] + offset[0], self.end_point[1] + offset[1])

    def move(self, offset: Tuple[float, float]):
        """Move the start and end points of the segment by the given offset."""
        self.move_start(offset)
        self.move_end(offset)

    def __str__(self):
        return f"LinearSegment(start={self.start_point}, end={self.end_point}, width={self.width})"

    def plot(self, board: pcbnew.BOARD, offset: Optional[Tuple[float, float]] = None):
        """Plot the track on the board."""
        if offset is None:
            offset = (0.0, 0.0)

        start = scale_vec(add_vec(self.start_point, offset), KICAD_MM)
        end = scale_vec(add_vec(self.end_point, offset), KICAD_MM)
        w = self.width * KICAD_MM

        #wx.MessageBox(f"Plotting linear segment from {start} to {end} with width {w}", "Emmett", wx.OK | wx.ICON_INFORMATION)

        track = pcbnew.PCB_TRACK(board)
        track.SetStart(pcbnew.VECTOR2I_MM(start[0], start[1]))
        track.SetEnd(pcbnew.VECTOR2I_MM(end[0], end[1]))
        track.SetWidth(pcbnew.FromMM(w))

        # Set net if segment has one
        if self.net:
            net_info = board.GetNetInfo(self.net)
            if net_info:
                track.SetNet(net_info)
        
        board.Add(track)

class ArcSegment(TraceSegment):
    """Represents an arc trace segment defined by 3 points (start, mid, end)."""
    
    def __init__(self, start_point: Tuple[float, float], mid_point: Tuple[float, float],
                 end_point: Tuple[float, float], width: float, factory: 'TraceSegmentFactory', 
                 net: Optional[str] = None):
        """
        Initialize an arc segment using KiCad's 3-point definition.
        
        Args:
            start_point: (x, y) coordinates of start point in meters
            mid_point: (x, y) coordinates of mid point in meters
            end_point: (x, y) coordinates of end point in meters
            width: Trace width in meters
            factory: Reference to the factory that created this segment
            net: Net name for this trace segment (optional)
        """
        super().__init__(start_point, end_point, width, net)
        self.mid_point = mid_point
        self._factory = factory
        
        # Calculate geometric properties from the 3 points
        self.center = self._calculate_center()
        self.radius = self._calculate_radius()
        self.start_angle = self._calculate_start_angle()
        self.end_angle = self._calculate_end_angle()
        self._arc_length = self._calculate_arc_length()
    
    def __str__(self):
        return f"ArcSegment(start={self.start_point}, mid={self.mid_point}, end={self.end_point}, centre={self.center}, radius={self.radius}, start_angle={self.start_angle}, end_angle={self.end_angle}, arc_length={self._arc_length}, width={self.width})"

    def plot(self, board: pcbnew.BOARD, offset: Optional[Tuple[float, float]] = None):
        """Plot the track on the board."""
        if offset is None:
            offset = (0.0, 0.0)

        start = scale_vec(add_vec(self.start_point, offset), KICAD_MM)
        mid = scale_vec(add_vec(self.mid_point, offset), KICAD_MM)
        end = scale_vec(add_vec(self.end_point, offset), KICAD_MM)
        
        track = pcbnew.PCB_ARC(board)
        track.SetStart(pcbnew.VECTOR2I_MM(start[0], start[1]))
        track.SetMid(pcbnew.VECTOR2I_MM(mid[0], mid[1]))
        track.SetEnd(pcbnew.VECTOR2I_MM(end[0], end[1]))
        track.SetWidth(pcbnew.FromMM(self.width * KICAD_MM))

        # Set net if segment has one
        if self.net:
            net_info = board.GetNetInfo(self.net)
            if net_info:
                track.SetNet(net_info)
        
        board.Add(track)

    def move(self, offset: Tuple[float, float]):
        """Move the start and end points of the segment by the given offset."""
        self.start_point = (self.start_point[0] + offset[0], self.start_point[1] + offset[1])
        self.mid_point = (self.mid_point[0] + offset[0], self.mid_point[1] + offset[1])
        self.end_point = (self.end_point[0] + offset[0], self.end_point[1] + offset[1])

    def _calculate_center(self) -> Tuple[float, float]:
        """
        Calculate the center of the arc from 3 points.
        Uses the perpendicular bisector method to find the center.
        """
        # Get the 3 points
        x1, y1 = self.start_point
        x2, y2 = self.mid_point
        x3, y3 = self.end_point
        
        # Check if the three points are collinear (form a straight line)
        # If they are, we can't form an arc
        area = x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)
        if abs(area) < 1e-10:  # Small threshold for floating point comparison
            raise ValueError(f"Invalid arc: the three points are collinear (form a straight line): start=({x1}, {y1}), mid=({x2}, {y2}), end=({x3}, {y3})")
        
        # Calculate perpendicular bisectors
        # For line 1-2: midpoint and perpendicular slope
        mid_x1 = (x1 + x2) / 2
        mid_y1 = (y1 + y2) / 2
        slope1 = (y2 - y1) / (x2 - x1) if x2 != x1 else float('inf')
        perp_slope1 = -1 / slope1 if slope1 != 0 else float('inf')
        
        # For line 2-3: midpoint and perpendicular slope
        mid_x2 = (x2 + x3) / 2
        mid_y2 = (y2 + y3) / 2
        slope2 = (y3 - y2) / (x3 - x2) if x3 != x2 else float('inf')
        perp_slope2 = -1 / slope2 if slope2 != 0 else float('inf')
        
        # Find intersection of perpendicular bisectors
        if perp_slope1 == float('inf'):
            # First line is vertical, center is on x = mid_x1
            if perp_slope2 == float('inf'):
                # Second line is also vertical - this shouldn't happen for valid arcs
                raise ValueError("Invalid arc: both lines are vertical")
            else:
                # Second line has slope, find intersection
                center_x = mid_x1
                center_y = perp_slope2 * (center_x - mid_x2) + mid_y2
        elif perp_slope2 == float('inf'):
            # Second line is vertical, center is on x = mid_x2
            center_x = mid_x2
            center_y = perp_slope1 * (center_x - mid_x1) + mid_y1
        elif abs(perp_slope1 - perp_slope2) < 1e-10:
            # Perpendicular slopes are nearly equal - this means the points form a straight line
            raise ValueError(f"Invalid arc: the three points form a straight line: start=({x1}, {y1}), mid=({x2}, {y2}), end=({x3}, {y3})")
        else:
            # Both lines have slopes, find intersection
            # y = m1*(x - x1) + y1 = m2*(x - x2) + y2
            # Solve for x: m1*x - m1*x1 + y1 = m2*x - m2*x2 + y2
            # x*(m1 - m2) = m1*x1 - y1 - m2*x2 + y2
            center_x = (perp_slope1 * mid_x1 - mid_y1 - perp_slope2 * mid_x2 + mid_y2) / (perp_slope1 - perp_slope2)
            center_y = perp_slope1 * (center_x - mid_x1) + mid_y1
        
        return (center_x, center_y)
    
    def _calculate_radius(self) -> float:
        """Calculate the radius from center to start point."""
        dx = self.start_point[0] - self.center[0]
        dy = self.start_point[1] - self.center[1]
        return math.sqrt(dx*dx + dy*dy)
    
    def _calculate_start_angle(self) -> float:
        """Calculate the start angle in radians."""
        dx = self.start_point[0] - self.center[0]
        dy = self.start_point[1] - self.center[1]
        return math.atan2(dy, dx)
    
    def _calculate_end_angle(self) -> float:
        """Calculate the end angle in radians."""
        dx = self.end_point[0] - self.center[0]
        dy = self.end_point[1] - self.center[1]
        return math.atan2(dy, dx)
    
    def _calculate_arc_length(self) -> float:
        """Calculate the arc length in meters."""
        # Calculate the angle difference, handling angle wrapping
        angle_diff = self.end_angle - self.start_angle
        
        # Normalize to [0, 2π) range
        while angle_diff < 0:
            angle_diff += 2 * math.pi
        while angle_diff >= 2 * math.pi:
            angle_diff -= 2 * math.pi
        
        # For arcs, we want the smaller angle (not the reflex angle)
        if angle_diff > math.pi:
            angle_diff = 2 * math.pi - angle_diff
        
        return self.radius * angle_diff
    
    def get_length(self) -> float:
        """Get the arc length in meters."""
        return self._arc_length
    
    def get_resistance(self, temperature_celsius: Optional[float] = None) -> float:
        """
        Calculate resistance of an arc trace segment using the correct parallel conductor model.
        
        The formula is: R = ρ × θ / (thickness × ln(R_outer / R_inner))
        This models the arc as an infinite number of infinitesimally small parallel arc segments
        and integrates the unequal current flow in conductors of different lengths.
        
        Args:
            temperature_celsius: Optional temperature in °C for TCR adjustment
                               (assumes resistivity is at 20°C)
        
        Returns:
            Resistance in Ohms (temperature-adjusted if temperature provided)
        """
        # Calculate the angle difference in radians
        angle_diff = self.end_angle - self.start_angle
        
        # Normalize to [0, 2π) range
        while angle_diff < 0:
            angle_diff += 2 * math.pi
        while angle_diff >= 2 * math.pi:
            angle_diff -= 2 * math.pi
        
        # For arcs, we want the smaller angle (not the reflex angle)
        if angle_diff > math.pi:
            angle_diff = 2 * math.pi - angle_diff
        
        # Calculate outer and inner radii
        width = self.get_width()
        outer_radius = self.radius + width / 2
        inner_radius = self.radius - width / 2
        
        # Ensure inner radius is positive
        if inner_radius <= 0:
            raise ValueError(f"Invalid arc: trace width ({width}) is too large for radius ({self.radius})")
        
        # Calculate resistance using the correct formula
        # R = ρ × θ / (thickness × ln(R_outer / R_inner))
        base_resistance = (self._factory.resistivity * angle_diff) / (self._factory.thickness * math.log(outer_radius / inner_radius))
        
        # Apply adjustment factor to account for model limitations
        adjusted_resistance = base_resistance * self._factory.arc_adjustment_factor
        
        # Apply temperature coefficient of resistance if temperature provided
        if temperature_celsius is not None:
            adjusted_resistance = self._factory._apply_temperature_adjustment(adjusted_resistance, temperature_celsius)
        
        return adjusted_resistance


class TraceSegmentFactory:
    """
    Factory for creating and managing PCB trace segments.
    
    Supports both straight line traces and arc traces using the parallel conductor model.
    Acts as a factory for creating trace segments and calculating resistances.
    
    The factory can be configured with default parameters (resistivity, thickness, etc.)
    that will be applied to all segments created by it. The net parameter allows
    setting a default net name for all segments, which can be overridden on individual
    segments after creation.
    """
    
    # Default values
    DEFAULT_COPPER_RESISTIVITY = 1.68e-8  # Ohm-meters (copper at 20°C)
    DEFAULT_COPPER_THICKNESS = 35e-6      # meters (35 microns)
    DEFAULT_ARC_ADJUSTMENT_FACTOR = 1.1   # 10% increase for arc resistance
    DEFAULT_COPPER_TCR = 0.00393          # Temperature coefficient of resistance per °C (copper)
    
    def __init__(self, resistivity: Optional[float] = None, 
                 thickness: Optional[float] = None,
                 arc_adjustment_factor: Optional[float] = None,
                 tcr: Optional[float] = None,
                 net: Optional[str] = None):
        """
        Initialize the factory.
        
        Args:
            resistivity: Copper resistivity in Ohm-meters (defaults to copper at 20°C)
            thickness: Copper thickness in meters (defaults to 35 microns)
            arc_adjustment_factor: Multiplier for arc resistance (defaults to 1.1)
            tcr: Temperature coefficient of resistance per °C (defaults to copper)
            net: Default net name for trace segments created by this factory
        """
        self._resistivity = resistivity or self.DEFAULT_COPPER_RESISTIVITY
        self._thickness = thickness or self.DEFAULT_COPPER_THICKNESS
        self._arc_adjustment_factor = arc_adjustment_factor or self.DEFAULT_ARC_ADJUSTMENT_FACTOR
        self._tcr = tcr or self.DEFAULT_COPPER_TCR
        self._net = net
    
    @property
    def resistivity(self) -> float:
        """Get the copper resistivity in Ohm-meters."""
        return self._resistivity
    
    @resistivity.setter
    def resistivity(self, value: float):
        """Set the copper resistivity in Ohm-meters."""
        if value <= 0:
            raise ValueError("Resistivity must be positive")
        self._resistivity = value
    
    @property
    def thickness(self) -> float:
        """Get the copper thickness in meters."""
        return self._thickness
    
    @thickness.setter
    def thickness(self, value: float):
        """Set the copper thickness in meters."""
        if value <= 0:
            raise ValueError("Thickness must be positive")
        self._thickness = value
    
    @property
    def arc_adjustment_factor(self) -> float:
        """Get the arc adjustment factor."""
        return self._arc_adjustment_factor
    
    @arc_adjustment_factor.setter
    def arc_adjustment_factor(self, value: float):
        """Set the arc adjustment factor."""
        if value <= 0:
            raise ValueError("Arc adjustment factor must be positive")
        self._arc_adjustment_factor = value
    
    @property
    def tcr(self) -> float:
        """Get the temperature coefficient of resistance per °C."""
        return self._tcr
    
    @tcr.setter
    def tcr(self, value: float):
        """Set the temperature coefficient of resistance."""
        if value <= 0:
            raise ValueError("TCR must be positive")
        self._tcr = value
    
    @property
    def net(self) -> Optional[str]:
        """Get the default net name for trace segments."""
        return self._net
    
    @net.setter
    def net(self, value: Optional[str]):
        """Set the default net name for trace segments."""
        self._net = value
    
    def create_linear_segment(self, start_point: Tuple[float, float], 
                             end_point: Tuple[float, float], width: float) -> LinearSegment:
        """
        Create a linear trace segment.
        
        Args:
            start_point: (x, y) coordinates of start point in meters
            end_point: (x, y) coordinates of end point in meters
            width: Trace width in meters
            
        Returns:
            LinearSegment instance bound to this factory
        """
        return LinearSegment(start_point, end_point, width, self, self._net)
    
    def create_arc_segment(self, start_point: Tuple[float, float], 
                          mid_point: Tuple[float, float],
                          end_point: Tuple[float, float], width: float) -> ArcSegment:
        """
        Create an arc trace segment using KiCad's 3-point definition.
        
        Args:
            start_point: (x, y) coordinates of start point in meters
            mid_point: (x, y) coordinates of mid point in meters
            end_point: (x, y) coordinates of end point in meters
            width: Trace width in meters
            
        Returns:
            ArcSegment instance bound to this factory
        """
        return ArcSegment(start_point, mid_point, end_point, width, self, self._net)
    
    def calculate_total_resistance(self, segments: List[TraceSegment], temperature_celsius: Optional[float] = None) -> float:
        """
        Calculate total resistance of multiple trace segments.
        
        Args:
            segments: List of TraceSegment objects
            temperature_celsius: Optional temperature in °C for TCR adjustment
                               (applied to final result, assumes resistivity is at 20°C)
            
        Returns:
            Total resistance in Ohms (temperature-adjusted if temperature provided)
        """
        total_resistance = 0.0
        
        # Calculate all resistances at 20°C (no temperature adjustment in individual calls)
        for segment in segments:
            segment_resistance = segment.get_resistance()
            total_resistance += segment_resistance
        
        # Apply temperature coefficient of resistance to final result if temperature provided
        if temperature_celsius is not None:
            total_resistance = self._apply_temperature_adjustment(total_resistance, temperature_celsius)
        
        return total_resistance
    
    def _apply_temperature_adjustment(self, resistance_at_20c: float, temperature_celsius: float) -> float:
        """
        Apply temperature coefficient of resistance adjustment.
        
        Args:
            resistance_at_20c: Resistance at 20°C
            temperature_celsius: Temperature in °C
        
        Returns:
            Temperature-adjusted resistance
        """
        # TCR formula: R(T) = R(20°C) * [1 + α * (T - 20°C)]
        # where α is the temperature coefficient of resistance
        temperature_diff = temperature_celsius - 20.0
        adjusted_resistance = resistance_at_20c * (1 + self.tcr * temperature_diff)
        return adjusted_resistance


    

# Example usage and testing
if __name__ == "__main__":
    # Create a factory with default parameters and a net
    calc = TraceSegmentFactory(net="GND")
    
    # Example: Create some test segments using the factory methods
    # Straight line segment: 10cm long, 2mm wide
    straight_segment = calc.create_linear_segment(
        start_point=(0.0, 0.0),
        end_point=(0.1, 0.0),  # 10cm
        width=0.002  # 2mm
    )
    
    # Arc segment: 90-degree turn, 2mm wide, 5mm radius
    arc_segment = calc.create_arc_segment(
        start_point=(0.1, 0.0),
        mid_point=(0.105, 0.005),  # Mid point at the corner of the 90-degree arc
        end_point=(0.11, 0.0),     # End point completing the arc (different y-coordinate)
        width=0.002  # 2mm
    )
    
    # Calculate resistances
    straight_resistance = straight_segment.get_resistance()
    arc_resistance = arc_segment.get_resistance()
    total_resistance = calc.calculate_total_resistance([straight_segment, arc_segment])
    
    print(f"Straight segment resistance: {straight_resistance:.6f} Ohms")
    print(f"Arc segment resistance: {arc_resistance:.6f} Ohms")
    print(f"Total resistance: {total_resistance:.6f} Ohms")
    print(f"factory parameters: resistivity={calc.resistivity:.2e} Ω·m, thickness={calc.thickness:.2e} m, arc_factor={calc.arc_adjustment_factor:.2f}, tcr={calc.tcr:.2e}")
    print(f"Net: {calc.net}")
    print(f"Segment nets: straight={straight_segment.net}, arc={arc_segment.net}")
    
    # Demonstrate parameter updates affecting all segments
    print("\nUpdating factory parameters...")
    calc.thickness = 70e-6  # Change to 70μm thickness
    
    # Recalculate - no need to pass new parameters!
    new_straight_resistance = straight_segment.get_resistance()
    new_arc_resistance = arc_segment.get_resistance()
    new_total_resistance = calc.calculate_total_resistance([straight_segment, arc_segment])
    
    print(f"New straight segment resistance: {new_straight_resistance:.6f} Ohms")
    print(f"New arc segment resistance: {new_arc_resistance:.6f} Ohms")
    print(f"New total resistance: {new_total_resistance:.6f} Ohms")
    
    # Demonstrate net changes
    print("\nChanging net on factory...")
    calc.net = "VCC"
    print(f"Factory net: {calc.net}")
    print(f"Existing segment nets unchanged: straight={straight_segment.net}, arc={arc_segment.net}")
    
    # Create new segments with new net
    new_straight_segment = calc.create_linear_segment(
        start_point=(0.0, 0.0),
        end_point=(0.05, 0.0),  # 5cm
        width=0.001  # 1mm
    )
    print(f"New segment net: {new_straight_segment.net}")
    
    # Demonstrate individual segment net updates
    print("\nUpdating individual segment nets...")
    straight_segment.net = "SIGNAL1"
    arc_segment.net = "SIGNAL2"
    print(f"Updated segment nets: straight={straight_segment.net}, arc={arc_segment.net}")
    
    # Demonstrate temperature compensation
    print("\n=== Temperature Compensation Demo ===")
    print("Resistance at different temperatures (same trace):")
    
    # Test temperature effects on the straight segment
    for temp in [20, 50, 100, 150]:
        resistance = straight_segment.get_resistance(temperature_celsius=temp)
        print(f"  At {temp}°C: {resistance:.6f} Ohms")
    
    # Test temperature effects on total resistance
    print(f"\nTotal resistance at different temperatures:")
    for temp in [20, 50, 100, 150]:
        total_res = calc.calculate_total_resistance([straight_segment, arc_segment], temperature_celsius=temp)
        print(f"  At {temp}°C: {total_res:.6f} Ohms")
    
    # Demonstrate configurable TCR
    print(f"\n=== Configurable TCR Demo ===")
    print("Creating factory with different TCR (e.g., for different material):")
    
    # Create factory with different TCR (e.g., for aluminum)
    calc_aluminum = TraceSegmentFactory(tcr=0.00429)  # Aluminum TCR
    print(f"Aluminum TCR: {calc_aluminum.tcr:.5f} per °C")
    
    # Compare temperature effects
    print(f"Copper vs Aluminum temperature effects (same trace at 100°C):")
    copper_res = straight_segment.get_resistance(temperature_celsius=100)
    aluminum_res = calc_aluminum.create_linear_segment(
        start_point=(0.0, 0.0),
        end_point=(0.1, 0.0),
        width=0.002
    ).get_resistance(temperature_celsius=100)
    
    print(f"  Copper TCR: {calc.tcr:.5f} → {copper_res:.6f} Ohms")
    print(f"  Aluminum TCR: {calc_aluminum.tcr:.5f} → {aluminum_res:.6f} Ohms")
