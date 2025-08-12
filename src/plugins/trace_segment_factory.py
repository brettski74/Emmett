#!/usr/bin/python3
"""
Hotplate Resistance Calculator for PCB Traces

This module provides a class to calculate the resistance of PCB hotplate traces,
including both straight line segments and arc segments using the annular sector model.
"""

import math
from typing import List, Tuple, Union, Optional
from abc import ABC, abstractmethod


class TraceSegment(ABC):
    """Abstract base class for trace segments."""
    
    def __init__(self, start_point: Tuple[float, float], end_point: Tuple[float, float], width: float):
        """
        Initialize a trace segment.
        
        Args:
            start_point: (x, y) coordinates of start point in meters
            end_point: (x, y) coordinates of end point in meters
            width: Trace width in meters
        """
        self.start_point = start_point
        self.end_point = end_point
        self.width = width
    
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


class LinearSegment(TraceSegment):
    """Represents a straight line trace segment."""
    
    def __init__(self, start_point: Tuple[float, float], end_point: Tuple[float, float], 
                 width: float, calculator: 'TraceSegmentFactory'):
        """
        Initialize a linear segment.
        
        Args:
            start_point: (x, y) coordinates of start point in meters
            end_point: (x, y) coordinates of end point in meters
            width: Trace width in meters
            calculator: Reference to the calculator that created this segment
        """
        super().__init__(start_point, end_point, width)
        self._calculator = calculator
    
    def get_length(self) -> float:
        """Calculate the length of the straight line segment."""
        dx = self.end_point[0] - self.start_point[0]
        dy = self.end_point[1] - self.start_point[1]
        return math.sqrt(dx*dx + dy*dy)
    
    def get_resistance(self, temperature_celsius: Optional[float] = None) -> float:
        """
        Calculate resistance of a straight line trace segment.
        
        Args:
            temperature_celsius: Optional temperature in °C for TCR adjustment
                               (assumes resistivity is at 20°C)
        
        Returns:
            Resistance in Ohms (temperature-adjusted if temperature provided)
        """
        length = self.get_length()
        width = self.get_width()
        cross_sectional_area = width * self._calculator.thickness
        
        # R = ρ * L / A
        resistance = self._calculator.resistivity * length / cross_sectional_area
        
        # Apply temperature coefficient of resistance if temperature provided
        if temperature_celsius is not None:
            resistance = self._calculator._apply_temperature_adjustment(resistance, temperature_celsius)
        
        return resistance


class ArcSegment(TraceSegment):
    """Represents an arc trace segment defined by 3 points (start, mid, end)."""
    
    def __init__(self, start_point: Tuple[float, float], mid_point: Tuple[float, float],
                 end_point: Tuple[float, float], width: float, calculator: 'TraceSegmentFactory'):
        """
        Initialize an arc segment using KiCad's 3-point definition.
        
        Args:
            start_point: (x, y) coordinates of start point in meters
            mid_point: (x, y) coordinates of mid point in meters
            end_point: (x, y) coordinates of end point in meters
            width: Trace width in meters
            calculator: Reference to the calculator that created this segment
        """
        super().__init__(start_point, end_point, width)
        self.mid_point = mid_point
        self._calculator = calculator
        
        # Calculate geometric properties from the 3 points
        self.center = self._calculate_center()
        self.radius = self._calculate_radius()
        self.start_angle = self._calculate_start_angle()
        self.end_angle = self._calculate_end_angle()
        self._arc_length = self._calculate_arc_length()
    
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
        base_resistance = (self._calculator.resistivity * angle_diff) / (self._calculator.thickness * math.log(outer_radius / inner_radius))
        
        # Apply adjustment factor to account for model limitations
        adjusted_resistance = base_resistance * self._calculator.arc_adjustment_factor
        
        # Apply temperature coefficient of resistance if temperature provided
        if temperature_celsius is not None:
            adjusted_resistance = self._calculator._apply_temperature_adjustment(adjusted_resistance, temperature_celsius)
        
        return adjusted_resistance


class TraceSegmentFactory:
    """
    Factory for creating and managing PCB trace segments.
    
    Supports both straight line traces and arc traces using the parallel conductor model.
    Acts as a factory for creating trace segments and calculating resistances.
    """
    
    # Default values
    DEFAULT_COPPER_RESISTIVITY = 1.68e-8  # Ohm-meters (copper at 20°C)
    DEFAULT_COPPER_THICKNESS = 35e-6      # meters (35 microns)
    DEFAULT_ARC_ADJUSTMENT_FACTOR = 1.1   # 10% increase for arc resistance
    DEFAULT_COPPER_TCR = 0.00393          # Temperature coefficient of resistance per °C (copper)
    
    def __init__(self, resistivity: Optional[float] = None, 
                 thickness: Optional[float] = None,
                 arc_adjustment_factor: Optional[float] = None,
                 tcr: Optional[float] = None):
        """
        Initialize the resistance calculator.
        
        Args:
            resistivity: Copper resistivity in Ohm-meters (defaults to copper at 20°C)
            thickness: Copper thickness in meters (defaults to 35 microns)
            arc_adjustment_factor: Multiplier for arc resistance (defaults to 1.1)
            tcr: Temperature coefficient of resistance per °C (defaults to copper)
        """
        self._resistivity = resistivity or self.DEFAULT_COPPER_RESISTIVITY
        self._thickness = thickness or self.DEFAULT_COPPER_THICKNESS
        self._arc_adjustment_factor = arc_adjustment_factor or self.DEFAULT_ARC_ADJUSTMENT_FACTOR
        self._tcr = tcr or self.DEFAULT_COPPER_TCR
    
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
        """Get the temperature coefficient of resistance."""
        return self._tcr
    
    @tcr.setter
    def tcr(self, value: float):
        """Set the temperature coefficient of resistance."""
        if value <= 0:
            raise ValueError("TCR must be positive")
        self._tcr = value
    
    def create_linear_segment(self, start_point: Tuple[float, float], 
                             end_point: Tuple[float, float], width: float) -> LinearSegment:
        """
        Create a linear trace segment.
        
        Args:
            start_point: (x, y) coordinates of start point in meters
            end_point: (x, y) coordinates of end point in meters
            width: Trace width in meters
            
        Returns:
            LinearSegment instance bound to this calculator
        """
        return LinearSegment(start_point, end_point, width, self)
    
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
            ArcSegment instance bound to this calculator
        """
        return ArcSegment(start_point, mid_point, end_point, width, self)
    
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
    # Create a calculator with default parameters
    calc = TraceSegmentFactory()
    
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
    print(f"Calculator parameters: resistivity={calc.resistivity:.2e} Ω·m, thickness={calc.thickness:.2e} m, arc_factor={calc.arc_adjustment_factor:.2f}, tcr={calc.tcr:.2e}")
    
    # Demonstrate parameter updates affecting all segments
    print("\nUpdating calculator parameters...")
    calc.thickness = 70e-6  # Change to 70μm thickness
    
    # Recalculate - no need to pass new parameters!
    new_straight_resistance = straight_segment.get_resistance()
    new_arc_resistance = arc_segment.get_resistance()
    new_total_resistance = calc.calculate_total_resistance([straight_segment, arc_segment])
    
    print(f"New straight segment resistance: {new_straight_resistance:.6f} Ohms")
    print(f"New arc segment resistance: {new_arc_resistance:.6f} Ohms")
    print(f"New total resistance: {new_total_resistance:.6f} Ohms")
    
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
    print("Creating calculator with different TCR (e.g., for different material):")
    
    # Create calculator with different TCR (e.g., for aluminum)
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
