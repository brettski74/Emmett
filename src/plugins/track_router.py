"""
TrackRouter abstract class for generating PCB trace layouts.

This module provides an abstract base class for different track routing algorithms,
along with utility methods for common trace patterns like serpentine traces.
"""

from math import ceil, floor

import pcbnew

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from .trace_segment_factory import TraceSegmentFactory, TraceSegment
from math import sqrt

from .vector_utils import add_vec, sub_vec, scale_vec, shrink_vec, normalize_vec, perp_vec, invert_vec, x_mirror_vec, y_mirror_vec

MICRONS_TO_M = 1e-6
MICRONS_TO_MM = 1e-3


def mm(microns):
    if isinstance(microns, tuple):
        return (f"{(microns[0] * MICRONS_TO_MM):.3f}", f"{(microns[1] * MICRONS_TO_MM):.3f}")
    elif isinstance(microns, float) or isinstance(microns, int):
        return f"{(microns * MICRONS_TO_MM):.3f}"
    else:
        raise ValueError(f"Invalid type: {type(microns)}")

def metres(microns):
    if isinstance(microns, tuple):
        return (microns[0] * MICRONS_TO_M, microns[1] * MICRONS_TO_M)
    elif isinstance(microns, float) or isinstance(microns, int):
        return microns * MICRONS_TO_M
    else:
        raise ValueError(f"Invalid type: {type(microns)}")

class TrackRouter(ABC):
    """
    Abstract base class for PCB track routing algorithms.

    All dimensions are in microns.
    
    This class defines the interface that all track routers must implement.
    It also provides utility methods for common trace patterns that can be
    used by concrete router implementations.
    """
    
    def __init__(self, factory: TraceSegmentFactory):
        """
        Initialize the track router.
        
        Args:
            factory: TraceSegmentFactory instance for creating trace segments
        """
        self.factory = factory
        self.log = ""
    
    @abstractmethod
    def generate_tracks(self) -> List[TraceSegment]:
        """
        Generate tracks as per this router's algorithm and parameters.
        
        This is the main method that concrete routers must implement.
        The specific routing algorithm and parameters are determined
        by the concrete implementation.
        
        Returns:
            List of TraceSegment objects representing the routed traces
        """
        pass
    
    @abstractmethod
    def update_board(self, board: pcbnew.BOARD):
        """
        Update the board with the generated tracks.
        """
        pass
    
    def even_tracks_over(self, distance: float, pitch: float) -> int:
        """
        Get the minimum number of tracks that is even and wider than the specified distance.
        """
        result = ceil(distance / pitch)
        if result % 2 == 1:
            result += 1
        return result

    def odd_tracks_over(self, distance: float, pitch: float) -> int:
        """
        Get the minimum number of tracks that is odd and wider than the specified distance.
        """
        result = ceil(distance / pitch)
        if result % 2 == 0:
            result += 1
        return result

    def even_tracks_under(self, distance: float, pitch: float) -> int:
        """
        Get the minimum number of tracks that is even and narrower than the specified distance.
        """
        result = floor(distance / pitch)
        if result % 2 == 1:
            result -= 1

        if result < 2:
          result = 2

        return result

    def odd_tracks_under(self, distance: float, pitch: float) -> int:
        """
        Get the minimum number of tracks that is odd and narrower than the specified distance.
        """
        result = floor(distance / pitch)
        if result % 2 == 0:
            result -= 1

        if result < 1:
          result = 1

        return result

    def normalize_vector(self, vector: Tuple[float, float], length: float) -> Tuple[float, float]:
        """
        Normalize a vector to a unit length.
        """
        current = sqrt(vector[0]*vector[0] + vector[1]*vector[1])
        return (vector[0] * length / current, vector[1] * length / current)
    
    def serpentine_track(self, start_point: Tuple[float, float],
                        end_point: Tuple[float, float],
                        width: float,
                        spacing: float,
                        count: int,
                        factory: TraceSegmentFactory,
                        direction: Optional[int] = 1) -> List[TraceSegment]:
        """
        Generate a serpentine trace pattern extending outward from a basis line.
        
        Args:
            start_point: (x, y) start point of the basis line
            end_point: (x, y) end point of the basis line
            width: Trace width in meters
            spacing: Spacing between parallel trace segments in meters
            count: number of linear segments to generate
            
        Returns:
            List of TraceSegment objects forming the serpentine pattern
            
        Raises:
            ValueError: If the parameters create an invalid pattern
        """
        if count < 0:
            raise ValueError("count must be at least 0")
        
        if spacing < 0.0002:
            raise ValueError("spacing must be greater than 0.0002m")

        if direction == 0:
            raise ValueError("direction must be 1 or -1")
        
        # Calculate the gradient of the basis line
        pitch = width + spacing
        gradient = normalize_vec( ( end_point[0] - start_point[0], end_point[1] - start_point[1] ), pitch )
        normal = normalize_vec( ( direction * (end_point[1] - start_point[1]), direction * (start_point[0] - end_point[0] ) ), pitch )
        diagonal = add_vec(scale_vec(normal, 0.5), scale_vec(gradient, 0.5))
        antidiag = sub_vec(scale_vec(normal, 0.5), scale_vec(gradient, 0.5))

        end_mid = add_vec(end_point, diagonal)
        start_mid = add_vec(start_point, antidiag)

        self.log = f"pitch: {mm(pitch)}\ngradient: {mm(gradient)}\nnormal: {mm(normal)}\ndiagonal: {mm(diagonal)}\nantidiag: {mm(antidiag)}"

        result = [ factory.create_linear_segment(metres(start_point), metres(end_point), metres(width)) ]
        self.log += f"\nsegment: {metres(start_point)}, {metres(end_point)}, {metres(width)}"

        count -= 1
        while count > 0:
            arc_end = add_vec(end_point, normal)
            result.append(factory.create_arc_segment(metres(end_point), metres(end_mid), metres(arc_end), metres(width)))
            self.log += f"\narc: {metres(end_point)}, {metres(end_mid)}, {metres(arc_end)}, {metres(width)}"

            end_point, start_point = add_vec(start_point, normal), add_vec(end_point, normal)
            end_mid, start_mid = add_vec(start_mid, normal), add_vec(end_mid, normal)

            result.append(factory.create_linear_segment(metres(start_point), metres(end_point), metres(width)))
            self.log += f"\nsegment: {metres(start_point)}, {metres(end_mid)}, {metres(width)}"

            count -= 1

        return result

