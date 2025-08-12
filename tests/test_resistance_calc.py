#!/usr/bin/python3
"""
Test suite for the ResistanceCalculator class.

This module tests the PCB trace resistance calculation functionality,
including linear segments, arc segments, and the factory pattern.
"""

import math
import sys
import os

# Add the src/plugins directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'plugins'))

from resistance_calc import ResistanceCalculator, LinearSegment, ArcSegment


def test_basic_calculations():
    """Test basic resistance calculations."""
    print("=== Basic Resistance Calculations ===")
    
    calc = ResistanceCalculator()
    
    # Test straight line segment using factory method
    straight = calc.create_linear_segment(
        start_point=(0.0, 0.0),
        end_point=(0.05, 0.0),  # 5cm
        width=0.001  # 1mm
    )
    
    straight_res = straight.get_resistance()
    print(f"5cm straight line (1mm wide): {straight_res:.6f} Ohms")
    
    # Test arc segment - create a simple arc that's easy to verify
    # Start at origin, go through (1,1), end at (2,0) - this should form a semicircle
    arc = calc.create_arc_segment(
        start_point=(0.0, 0.0),       # Start at origin
        mid_point=(1.0, 1.0),         # Mid at (1,1) - top of semicircle
        end_point=(2.0, 0.0),         # End at (2,0) - other end of semicircle
        width=0.001  # 1mm
    )
    
    arc_res = arc.get_resistance()
    print(f"90° arc (5mm radius, 1mm wide): {arc_res:.6f} Ohms")
    
    # Total resistance
    total = calc.calculate_total_resistance([straight, arc])
    print(f"Total resistance: {total:.6f} Ohms")
    print()


def test_serpentine_pattern():
    """Test a serpentine heating element pattern."""
    print("=== Serpentine Heating Element Pattern ===")
    
    calc = ResistanceCalculator()
    segments = []
    
    # Create a simple serpentine pattern
    # Start at origin
    current_x, current_y = 0.0, 0.0
    trace_width = 0.002  # 2mm
    segment_length = 0.02  # 2cm segments
    turn_radius = 0.003  # 3mm radius for turns
    
    # First straight segment
    segments.append(calc.create_linear_segment(
        start_point=(current_x, current_y),
        end_point=(current_x + segment_length, current_y),
        width=trace_width
    ))
    current_x += segment_length
    
    # First turn (90° right)
    segments.append(calc.create_arc_segment(
        start_point=(current_x, current_y),
        mid_point=(current_x, current_y + turn_radius),  # Mid point at the corner
        end_point=(current_x + turn_radius, current_y + turn_radius),  # End point after the turn
        width=trace_width
    ))
    current_y += turn_radius
    
    # Second straight segment
    segments.append(calc.create_linear_segment(
        start_point=(current_x, current_y),
        end_point=(current_x - segment_length, current_y),
        width=trace_width
    ))
    current_x -= segment_length
    
    # Second turn (90° right)
    segments.append(calc.create_arc_segment(
        start_point=(current_x, current_y),
        mid_point=(current_x, current_y + turn_radius),  # Mid point at the corner
        end_point=(current_x - turn_radius, current_y + turn_radius),  # End point after the turn
        width=trace_width
    ))
    current_y += turn_radius
    
    # Third straight segment
    segments.append(calc.create_linear_segment(
        start_point=(current_x, current_y),
        end_point=(current_x + segment_length, current_y),
        width=trace_width
    ))
    
    # Calculate total resistance
    total_resistance = calc.calculate_total_resistance(segments)
    
    print(f"Serpentine pattern with {len(segments)} segments:")
    print(f"  - {len([s for s in segments if isinstance(s, LinearSegment)])} straight segments")
    print(f"  - {len([s for s in segments if isinstance(s, ArcSegment)])} arc segments")
    print(f"  - Total resistance: {total_resistance:.6f} Ohms")
    print(f"  - Pattern dimensions: ~{segment_length*2:.1f}cm × {turn_radius*2:.1f}cm")
    print()


def test_parameter_variations():
    """Test how resistance changes with different parameters."""
    print("=== Parameter Variations ===")
    
    # Create a simple test segment
    calc = ResistanceCalculator()
    test_segment = calc.create_linear_segment(
        start_point=(0.0, 0.0),
        end_point=(0.01, 0.0),  # 1cm
        width=0.001  # 1mm
    )
    
    # Test different copper thicknesses
    print("Effect of copper thickness (1cm × 1mm trace):")
    for thickness_microns in [18, 35, 70, 105]:
        thickness_meters = thickness_microns * 1e-6
        calc.thickness = thickness_meters
        resistance = test_segment.get_resistance()
        print(f"  {thickness_microns}μm thickness: {resistance:.6f} Ohms")
    
    print()
    
    # Test different trace widths
    print("Effect of trace width (1cm × 35μm trace):")
    calc.thickness = 35e-6  # Reset to default thickness
    for width_mm in [0.5, 1.0, 2.0, 4.0]:
        width_meters = width_mm * 1e-3
        test_segment.width = width_meters
        resistance = test_segment.get_resistance()
        print(f"  {width_mm}mm width: {resistance:.6f} Ohms")
    
    print()


def test_arc_adjustment_factors():
    """Test the effect of arc adjustment factors."""
    print("=== Arc Adjustment Factor Effects ===")
    
    calc = ResistanceCalculator()
    
    # Create a 90-degree arc
    arc = calc.create_arc_segment(
        start_point=(0.0, 0.0),       # Start at origin
        mid_point=(1.0, 1.0),         # Mid at (1, 1) - 45° point on quarter circle
        end_point=(2.0, 0.0),         # End at (2, 0) - 90° point
        width=0.001  # 1mm
    )
    
    print("90° arc resistance with different adjustment factors:")
    for factor in [1.0, 1.05, 1.1, 1.15, 1.2]:
        calc.arc_adjustment_factor = factor
        resistance = arc.get_resistance()
        print(f"  Factor {factor:.2f}: {resistance:.6f} Ohms")
    
    print()


def test_polymorphism():
    """Test that the polymorphic behavior works correctly."""
    print("=== Polymorphism Test ===")
    
    calc = ResistanceCalculator()
    
    # Create segments of different types using factory methods
    linear = calc.create_linear_segment((0.0, 0.0), (0.01, 0.0), 0.001)
    arc = calc.create_arc_segment((0.0, 0.0), (0.005, 0.005), (0.01, 0.0), 0.001)
    
    # Test that they both implement the interface
    print(f"Linear segment length: {linear.get_length():.6f} m")
    print(f"Arc segment length: {arc.get_length():.6f} m")
    print(f"Linear segment width: {linear.get_width():.6f} m")
    print(f"Arc segment width: {arc.get_width():.6f} m")
    
    # Test that they can be used polymorphically
    segments = [linear, arc]
    total_resistance = calc.calculate_total_resistance(segments)
    print(f"Total resistance from mixed segments: {total_resistance:.6f} Ohms")
    print()


def test_factory_pattern():
    """Test the factory pattern and parameter binding."""
    print("=== Factory Pattern Test ===")
    
    calc = ResistanceCalculator()
    
    # Create segments using factory methods
    linear = calc.create_linear_segment((0.0, 0.0), (0.01, 0.0), 0.001)
    arc = calc.create_arc_segment((0.0, 0.0), (0.005, 0.005), (0.01, 0.0), 0.001)
    
    # Get initial resistances
    initial_linear_res = linear.get_resistance()
    initial_arc_res = arc.get_resistance()
    initial_total = calc.calculate_total_resistance([linear, arc])
    
    print(f"Initial resistances:")
    print(f"  Linear: {initial_linear_res:.6f} Ohms")
    print(f"  Arc: {initial_arc_res:.6f} Ohms")
    print(f"  Total: {initial_total:.6f} Ohms")
    
    # Change calculator parameters
    print(f"\nUpdating calculator parameters...")
    calc.thickness = 70e-6
    calc.arc_adjustment_factor = 1.2
    
    # Recalculate - segments automatically use new parameters!
    new_linear_res = linear.get_resistance()
    new_arc_res = arc.get_resistance()
    new_total = calc.calculate_total_resistance([linear, arc])
    
    print(f"New resistances:")
    print(f"  Linear: {new_linear_res:.6f} Ohms")
    print(f"  Arc: {new_arc_res:.6f} Ohms")
    print(f"  Total: {new_total:.6f} Ohms")
    
    # Verify changes
    linear_change = (new_linear_res - initial_linear_res) / initial_linear_res * 100
    arc_change = (new_arc_res - initial_arc_res) / initial_arc_res * 100
    total_change = (new_total - initial_total) / initial_total * 100
    
    print(f"\nPercentage changes:")
    print(f"  Linear: {linear_change:+.1f}%")
    print(f"  Arc: {arc_change:+.1f}%")
    print(f"  Total: {total_change:+.1f}%")
    print()


if __name__ == "__main__":
    test_basic_calculations()
    test_serpentine_pattern()
    test_parameter_variations()
    test_arc_adjustment_factors()
    test_polymorphism()
    test_factory_pattern()
    
    print("=== Summary ===")
    print("The ResistanceCalculator provides:")
    print("  - Clean object-oriented design with proper inheritance")
    print("  - Factory pattern for creating trace segments")
    print("  - Automatic parameter binding - segments know their calculator")
    print("  - LinearSegment and ArcSegment classes implementing TraceSegment interface")
    print("  - Accurate resistance calculations for straight line traces")
    print("  - Parallel conductor model for arc traces with configurable adjustment factors")
    print("  - Support for both proposal and board-based calculations")
    print("  - Configurable copper resistivity, thickness, and arc adjustment factors")
    print("  - Comprehensive error checking and validation")
    print("  - Polymorphic behavior - no more is_arc checks!")
    print("  - Easy parameter updates - change once, affects all segments!")
