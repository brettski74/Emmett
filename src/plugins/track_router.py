"""
TrackRouter abstract class for generating PCB trace layouts.

This module provides an abstract base class for different track routing algorithms,
along with utility methods for common trace patterns like serpentine traces.
"""

from math import ceil, floor, sqrt, fabs

import pcbnew

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

from .board_analyzer import BoardAnalyzer
from .board_builder import BoardBuilder
from .trace_segment_factory import TraceSegmentFactory, TraceSegment
from .vector_utils import add_vec, sub_vec, scale_vec, shrink_vec, normalize_vec, perp_vec, invert_vec, x_mirror_vec, y_mirror_vec
from .my_debug import debug, enable_debug

enable_debug()

MICRONS_TO_M = 1e-6
MICRONS_TO_MM = 1e-3
TOLERANCE = 0.00005


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

        self.width = 1000
        self.spacing = 200
        self.margin = 500
        self.update_derived_parameters()
    
    def update_derived_parameters(self):
        self.pitch = self.width + self.spacing

    @abstractmethod
    def analyze_board(self, analyzer: BoardAnalyzer):
        """
        Analyze the board and set up the router's parameters.
        """
        pass

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
    def starting_track_count(self) -> Tuple[int, float]:
        """
        Get the minimum number of tracks that is even and wider than the specified distance.
        """
        pass

    @abstractmethod
    def update_board(self, builder: BoardBuilder) -> List[TraceSegment]:
        """
        Update the board with the generated tracks.
        """
        pass

    def get_extents_mm(self) -> Tuple[float, float, float, float]:
        """
        Get the extents of the board in millimeters.
        """
        return (self.left * MICRONS_TO_MM, self.top * MICRONS_TO_MM, self.right * MICRONS_TO_MM, self.bottom * MICRONS_TO_MM)
    
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

    def optimize_tracks(self, minimum_spacing: float, target_resistance: float, target_temperature: float):
        """
        This algorithm should work for any track routing algorithm that has a track count limited by
        the number of tracks that can fit across the width of the board.

        Track resistance generally varies with track width, but creating a formula that easily relates
        track width to resistance for a given routing algorithm can be challenging. Instead, we can find
        the track pitch that corresponds to a given number of tracks across the board width. Using the
        minimum spacing, we can determine the minimum resistance for a given track count. The algorithm
        assumes that track counts must either all be even or all be odd. The even-ness or odd-ness of
        track counts is determined by the starting_track_count method. The track count is then incremented
        by 2 until to find the largest track count that produces a minimum resistance that is still less
        than the target resistance. Using the corresponding track pitch, we then reduce the track width
        until the resistance matches the target resistance.

        While it is true that total track resistance is roughly inversely proportional to track width,
        the effect of non-uniform current distribution around tight turns means that it's not exact.
        While it may seem tempting to use this to more quickly converge on the target resistance, there
        is the possibility that some parameter values could lead to non-terminating search when using
        this approach. Therefore, we use a safer bracketed search approach which might take more iterations
        but is guaranteed to converge on a value.

        Returns a two-element tuple containing the track width and track spacing in microns
        """
        # Save the current state in case we fail and want to roll back
        save_pitch = self.pitch
        save_width = self.width
        save_spacing = self.spacing

        self.spacing = minimum_spacing
        track_count, working_width = self.starting_track_count()
        debug(f"starting track count: {track_count}, working width: {working_width}, minimum spacing: {minimum_spacing}")

        resistance = 0
        last_tracks = None
        rlo = 0

        while resistance < target_resistance:
            self.pitch = working_width / track_count
            self.width = self.pitch - self.spacing

            tracks = self.generate_tracks()
            resistance = self.factory.calculate_total_resistance(tracks, target_temperature)
            debug(f"track_count: {track_count}, pitch: {self.pitch}, width: {self.width}, resistance: {resistance}")

            if resistance > target_resistance:
                track_count = track_count - 2
                tracks = last_tracks
                break

            wlo = self.width
            rlo = resistance
            last_tracks = tracks
            track_count = track_count + 2

        if resistance == 0:
            self.pitch = save_pitch
            self.width = save_width
            self.spacing = save_spacing
            raise ValueError(f"No track pitch < 2.5mm found for target resistance of {target_resistance} ohms")

        if rlo == 0:
            self.pitch = save_pitch
            self.width = save_width
            self.spacing = save_spacing
            raise ValueError(f"No high bracket found for target resistance of {target_resistance} ohms")

        resistance = self.finish_optimization(target_resistance, target_temperature, working_width/track_count - 10, minimum_spacing)
        pitch = self.pitch
        width = self.width
        error = fabs(resistance - target_resistance)
        debug(f"count: {track_count}, width: {width}, resistance: {resistance}, error: {error}")

        # Sometimes we struggle to get close enough to the target resistance at the highest possible track count, so try a
        # a couple of lower counts to see if we can get closer.
        track_count -= 2
        r2 = self.finish_optimization(target_resistance, target_temperature, working_width/track_count - 10, minimum_spacing)
        err2 = fabs(r2 - target_resistance)
        debug(f"count: {track_count}, width: {width}, resistance: {r2}, error: {err2}")
        if err2 < error:
            pitch = self.pitch
            width = self.width
            resistance = r2
            error = err2
        debug(f"width: {width}, resistance: {resistance}, error: {error}")

        track_count -= 2
        r2 = self.finish_optimization(target_resistance, target_temperature, working_width/track_count - 10, minimum_spacing)
        debug(f"count: {track_count}, width: {width}, resistance: {r2}, error: {err2}")
        if fabs(r2 - target_resistance) < (resistance - target_resistance):
            pitch = self.pitch
            width = self.width
            resistance = r2
            error = err2
        debug(f"width: {width}, resistance: {resistance}, error: {error}")

        self.pitch = pitch
        self.width = width
        self.spacing = self.pitch - self.width

        return resistance

    def finish_optimization(self, target_resistance, temperature, pitch, minimum_spacing):
        global TOLERANCE
        depth = 100

        self.pitch = pitch
        self.spacing = minimum_spacing
        self.width = self.pitch - self.spacing

        tracks = self.generate_tracks()
        rlo = self.factory.calculate_total_resistance(tracks, temperature)
        wlo = self.width
        whi = 0
        rhi = 0

        while depth > 0 and fabs(rlo - rhi) > TOLERANCE and fabs(wlo - whi) > TOLERANCE:
            depth = depth - 1

            self.width = (whi + wlo) / 2
            self.spacing = self.pitch - self.width

            tracks = self.generate_tracks()
            resistance = self.factory.calculate_total_resistance(tracks, temperature)
            debug(f"depth: {depth}, width: {self.width}, resistance: {resistance}")

            if resistance > target_resistance:
                rhi = resistance
                whi = self.width
            else:
                rlo = resistance
                wlo = self.width

        if depth <= 0:
            raise ValueError(f"Target resistance of {target_resistance} ohms not achievable with pitch of {pitch} and minimum spacing of {minimum_spacing}")

        # Pick whichever side of the bracket is closer to the target resistance
        if fabs(rlo - target_resistance) < fabs(rhi - target_resistance):
            self.width = wlo
            resistance = rlo
        else:
            self.width = whi
            resistance = rhi

        self.spacing = self.pitch - self.width

        return resistance

