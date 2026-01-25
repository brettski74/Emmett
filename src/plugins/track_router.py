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
from .trace_segment_factory import TraceSegmentFactory, TraceSegment, ArcSegment
from .pad_defs import RectangularPad, CircularPad
from .vector_utils import add_vec, sub_vec, scale_vec, shrink_vec, normalize_vec, distance, perp_vec, invert_vec, x_mirror_vec, y_mirror_vec
from .my_debug import debug, enable_debug

# Roundeing errors will be the death of us!
# Number of decimal poalces to round to to avoid spurious mathematical and/or layout errors due to rounding errors
PRECISION = 9

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

def overlap(a1, a2, b1, b2):
    amin = min(a1, a2)
    amax = max(a1, a2)
    bmin = min(b1, b2)
    bmax = max(b1, b2)
    
    if amin >= bmin and amin <= bmax:
        return True

    if bmin >= amin and bmin <= amax:
        return True

    return False

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
    
    def working_width(self, spacing: Optional[float] = None, margin: Optional[float] = None ) -> float:
        """
        Get the working width of the board - the width across which a serpentine track with the current track pitch and spacing can fit.
        """
        if spacing is None:
            spacing = self.spacing
        if margin is None:
            margin = self.margin
        return self.right - self.left - 2*margin + spacing

    def starting_track_count(self, spacing: Optional[float] = None, margin: Optional[float] = None) -> int:
        """
        Get a low number of tracks to start at for track optimization.
        """
        working_width = self.working_width(spacing, margin)
        maximum_pitch = self.maximum_track_pitch()

        guess = floor(working_width / maximum_pitch) + 1
        if guess % 2 != 0:
            guess += 1

        return guess

    def maximum_track_pitch(self) -> int:
        """
        Return the maximum track pitch to assume when optimizing tracks in microns.
        """
        return 6000

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
            raise ValueError(f"count ({count}) must be at least 0")
        
        if spacing < 0.0002:
            raise ValueError(f"spacing ({spacing}) must be greater than 0.0002m")

        if direction == 0:
            raise ValueError(f"direction ({direction}) must be 1 or -1")
        
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

    def increment_track_count(self, count: int) -> int:
        """
        Increment the track count to the next permissable track count above the provided count.

        The default implementation simply increments the track count by 2.
        """
        return count+2

    def decrement_track_count(self, count: int) -> int:
        """
        Decrement the track count to the next permissable track count below the provided count.

        The default implementation simply decrements the track count by 2.
        """
        return count-2

    def optimize_tracks(self, minimum_spacing: float, target_resistance: float, target_temperature: float, track_thickness: Optional[float] = None):
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
        if track_thickness is not None:
            # TODO: implement track thickness
            self.factory.thickness = track_thickness

        # Save the current state in case we fail and want to roll back
        save_pitch = self.pitch
        save_width = self.width
        save_spacing = self.spacing

        self.spacing = minimum_spacing
        track_count = self.starting_track_count(self.spacing, self.margin)

        resistance = 0
        last_tracks = None
        rlo = 0

        while resistance < target_resistance:
            working_width = self.working_width(self.spacing, self.margin)
            
            # Remember that there is one more track than track pitches between them
            self.pitch = working_width / (track_count - 1)
            self.width = self.pitch - self.spacing

            tracks = self.generate_tracks()
            resistance = self.factory.calculate_total_resistance(tracks, target_temperature)

            if resistance > target_resistance:
                track_count = self.decrement_track_count(track_count)
                tracks = last_tracks
                break

            wlo = self.width
            rlo = resistance
            last_tracks = tracks
            track_count = self.increment_track_count(track_count)

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

        resistance = self.finish_optimization(target_resistance, target_temperature, track_count, minimum_spacing)
        pitch = self.pitch
        width = self.width
        error = fabs(resistance - target_resistance)

        self.pitch = pitch
        self.width = width
        self.spacing = self.pitch - self.width

        return resistance

    def avoid_pad(self, tracks: List[TraceSegment], pad: RectangularPad):
        """
        Adjust tracks to avoid a pad.
        """
        for i in range(len(tracks)):
            if type(tracks[i]) != ArcSegment:
                continue

            t = tracks[i]

            # Determine axial alignment of the arc segment
            if t.start_point[1] != t.end_point[1]:
                self.avoid_pad_x(tracks, i, pad)
            else:
                self.avoid_pad_y(tracks, i, pad)

    def avoid_pad_x(self, tracks: List[TraceSegment], index: int, pad: RectangularPad):
        inl = tracks[index-1]
        arc = tracks[index]
        out = tracks[index+1]

        # Determine if the arc segment is completely above the pad
        width = arc.width
        arc_top = round(min(arc.start_point[1], arc.end_point[1]) - width/2, PRECISION)
        arc_bottom = round(max(arc.start_point[1], arc.end_point[1]) + width/2, PRECISION)
        arc_mid = round((arc_top + arc_bottom) / 2, PRECISION)

        pad_top = round(pad.clear_top() * 1e-6, PRECISION)
        pad_bottom = round(pad.clear_bottom() * 1e-6, PRECISION)
        offset = 0

        # No vertical overlap, nothing to do
        if not overlap(arc_top, arc_bottom, pad_top, pad_bottom):
            return

        pad_left = round(pad.clear_left() * 1e-6, PRECISION)
        pad_right = round(pad.clear_right() * 1e-6, PRECISION)

        # Determine direction of the arc segment - right side arcs
        if arc.start_point[0] < arc.mid_point[0]:
            line_left = round(min(inl.start_point[0], inl.end_point[0], out.start_point[0], out.end_point[0]), PRECISION)

            # Skip this if the pad is closer to the other end of the lines
            arc_left = round(arc.start_point[0], PRECISION)
            if (pad_left - line_left) < (arc_left - pad_right):
                return

            arc_radius = round((arc_bottom - arc_mid), PRECISION)
            arc_right = round(arc_left + arc_radius, PRECISION)

            if arc_mid >= pad_top and arc_mid <= pad_bottom and arc_right > pad_left:
                offset = round(pad_left - arc_right, PRECISION)

            elif arc_mid < pad_top and arc_bottom > pad_top and (arc_left >= pad_left or distance((arc_left, arc_mid), (pad_left, pad_top)) < arc_radius):
                deltay = round(pad_top - arc_mid, PRECISION)
                new_left = round(pad_left - sqrt(arc_radius*arc_radius - deltay*deltay), PRECISION)
                offset = round(new_left - arc_left, PRECISION)
            
            elif arc_mid > pad_bottom and arc_top < pad_bottom and (arc_left >= pad_left or distance((arc_left, arc_mid), (pad_left, pad_bottom)) < arc_radius):
                deltay = round(arc_mid - pad_bottom, PRECISION)
                new_left = round(pad_left - sqrt(arc_radius*arc_radius - deltay*deltay), PRECISION)
                offset = round(new_left - arc_left, PRECISION)

        else:
            line_right = max(inl.start_point[0], inl.end_point[0], out.start_point[0], out.end_point[0])

            # TODO: Incomplete case!

        if offset != 0:
            arc.move((offset, 0))
            inl.move_end((offset, 0))
            out.move_start((offset, 0))

    def avoid_pad_y(self, tracks: List[TraceSegment], index: int, pad: RectangularPad):
        inl = tracks[index-1]
        arc = tracks[index]
        out = tracks[index+1]

        # Determine if the arc segment is completely above the pad
        width = arc.width
        arc_left = round(min(arc.start_point[0], arc.end_point[0]) - width/2, PRECISION)
        arc_right = round(max(arc.start_point[0], arc.end_point[0]) + width/2, PRECISION)
        arc_mid = round((arc_left + arc_right) / 2, PRECISION)

        pad_left = round(pad.clear_left() * 1e-6, PRECISION)
        pad_right = round(pad.clear_right() * 1e-6, PRECISION)
        offset = 0

        # No horizontal overlap, nothing to do
        if not overlap(arc_left, arc_right, pad_left, pad_right):
            return

        pad_top = round(pad.clear_top() * 1e-6, PRECISION)
        pad_bottom = round(pad.clear_bottom() * 1e-6, PRECISION)

        # Determine direction of the arc segment - Bottom side arcs
        if arc.start_point[1] < arc.mid_point[1]:
            line_top = round(min(inl.start_point[1], inl.end_point[1], out.start_point[1], out.end_point[1]), PRECISION)

            arc_top = round(arc.start_point[1], PRECISION)
            # Skip this if the pad is closer to the other end of the lines
            if (pad_top - line_top) < (arc_top - pad_bottom):
                return

            arc_radius = round((arc_right - arc_mid), PRECISION)
            arc_bottom = round(arc_top + arc_radius, PRECISION)

            if arc_mid >= pad_left and arc_mid <= pad_right and arc_bottom > pad_top:
                offset = round(pad_top - arc_bottom, PRECISION)

            elif arc_mid < pad_left and arc_right > pad_left and (arc_top >= pad_top or distance((arc_top, arc_mid), (pad_left, pad_top)) < arc_radius):
                deltax = round(pad_left - arc_mid, PRECISION)
                new_top = round(pad_top - sqrt(arc_radius*arc_radius - deltax*deltax), PRECISION)
                offset = round(new_top - arc_top, PRECISION)

            elif arc_mid > pad_right and arc_left < pad_right and (arc_top >= pad_top or distance((arc_top, arc_mid), (pad_right, pad_top)) < arc_radius):
                deltax = round(arc_mid - pad_right, PRECISION)
                new_top = round(pad_top - sqrt(arc_radius*arc_radius - deltax*deltax), PRECISION)
                offset = round(new_top - arc_top, PRECISION)

        # Else top side arcs
        else:
            line_bottom = round(max(inl.start_point[1], inl.end_point[1], out.start_point[1], out.end_point[1]), PRECISION)
            arc_bottom = round(arc.start_point[1], PRECISION)
            # Skip this if the pad is closer to the other end of the lines
            if (pad_bottom - line_bottom) > (arc_bottom - pad_top):
                return

            arc_radius = round((arc_right - arc_mid), PRECISION)
            arc_top = round(arc_bottom - arc_radius, PRECISION)

            if arc_mid >= pad_left and arc_mid <= pad_right and arc_top < pad_bottom:
                offset = round(pad_bottom - arc_top, PRECISION)

            elif arc_mid < pad_left and arc_right > pad_left and (arc_bottom <= pad_bottom or distance((arc_mid, arc_bottom), (pad_left, pad_bottom)) < arc_radius):
                deltax = round(pad_left - arc_mid, PRECISION)
                new_bottom = round(pad_bottom + sqrt(arc_radius*arc_radius - deltax*deltax), PRECISION)
                offset = round(new_bottom - arc_bottom, PRECISION)

            elif arc_mid > pad_right and arc_left < pad_right and (arc_bottom <= pad_bottom or distance((arc_mid, arc_bottom), (pad_right, pad_bottom)) < arc_radius):
                deltax = round(arc_mid - pad_right, PRECISION)
                new_bottom = round(pad_bottom + sqrt(arc_radius*arc_radius - deltax*deltax), PRECISION)
                offset = new_bottom - arc_bottom

        if offset != 0:
            arc.move((0, offset))
            inl.move_end((0, offset))
            out.move_start((0, offset))

    def avoid_hole(self, tracks: List[TraceSegment], hole: CircularPad, clearance: Optional[float] = -1.0):
        """
        Adjust tracks to avoid a hole.
        """
        if clearance <= 0.0:
            clearance = hole.clear_radius()
        
        clearance += self.pitch
        cl2 = clearance * clearance
        ycentre = (self.top + self.bottom) / 2
        left = hole.x - clearance
        right = hole.x + clearance

        hc = (hole.x, hole.y)

        # Still need distance check because the x-coordinate alone may pick up corners at the wrond end.
        # sqrt(2) * clearance should catch everything. 1.5 x gives a little extra margin while still
        # avoiding incorrectly picking up corners at the wrong end,
        close = clearance * 1.5

        for i in range(len(tracks)):
            if type(tracks[i]) != ArcSegment:
                continue

            t = tracks[i]

            if t.start_point[1] != t.end_point[1]:
                continue
            
            centre = (t.mid_point[0] * 1e6, t.start_point[1] * 1e6)
            d = distance(centre, hc)

            if left <= centre[0] <= right and d < close:
                dx = hc[0] - centre[0]
                dy = sqrt(cl2 - dx*dx)

                if hc[1] < ycentre:
                    y = hc[1] + dy
                else:
                    y = hc[1] - dy

                ddy = y/1e6 - t.start_point[1]
                self.shorten_track_pair(tracks, i, fabs(ddy));

    def arc_centre(self, arc: ArcSegment) -> Tuple[float, float]:
        """
        Calculate the centre of an arc segment.
        """
        sx = arc.start_point[0]
        sy = arc.start_point[1]
        ex = arc.end_point[0]
        ey = arc.end_point[1]
        mx = arc.mid_point[0]
        my = arc.mid_point[1]
        D = 2 * (sx * (my - ey) + mx * (ey - sy) + ex * (sy - my))
        if D == 0:
            raise ValueError(f"Invalid arc: the three points form a straight line: start=({sx}, {sy}), mid=({mx}, {my}), end=({ex}, {ey})")

        sm = sx*sx + sy*sy
        mm = mx*mx + my*my
        em = ex*ex + ey*ey

        cx = round((sm*(my-ey) + mm*(ey-sy) + em*(sy-my)) / D, PRECISION)
        cy = round((sm*(ex-mx) + mm*(sx-ex) + em*(mx-sx)) / D, PRECISION)

        return (cx, cy)

    def closest_arc(self, tracks: List[TraceSegment], point: Tuple[float, float]) -> int:
        """
        Find the index of the closest arc segment to a given point.

        This method only considered arcs where the arc is closer to the reference pointthan its centre.

        Closest is evaluated based on the distance from the reference point to the arc's centre.
        """
        closest = None
        closest_distance = float('inf')

        for i in range(len(tracks)):
            if type(tracks[i]) != ArcSegment:
                continue

            t = tracks[i]
            
            centre = self.arc_centre(t)

            d_cp = distance(point, centre)
            d_mp = distance(point, t.mid_point)

            # Only consider arcs where the arc is closer to the reference point than the centre
            if d_mp > d_cp:
                continue

            if d_cp < closest_distance:
                closest = i
                closest_distance = d_cp

        return closest

    def shorten_track_pair(self, list: List[TraceSegment], index: int, offset: float):
        """
        Shorten a pair of tracks in a serpentine track to avoid an obstacle.

        The track pair is identified by the arc segment that joins them. For a normal
        serpentine track, the index of arc segments will be odd.

        Args:
            list: List of TraceSegment objects
            index: Index of the arc segment that joins the track pair together
            offset: The offset to apply to the ends of the two tracks
        """
        if type(list[index]) != ArcSegment:
            raise ValueError(f"Track {index} is not an arc segment")

        inl= list[index-1]
        arc = list[index]
        out = list[index+1]

        if arc.start_point[1] < arc.mid_point[1]:
            offset = -offset

        # Determine axial direction
        if abs(arc.start_point[0] - arc.end_point[0]) < 1e-9:
            arc.move((offset, 0))
            inl.move_end((offset, 0))
            out.move_start((offset, 0))
        else:
            arc.move((0, offset))
            inl.move_end((0, offset))
            out.move_start((0, offset))

    def corner_90(self, start: Tuple[float, float], end: Tuple[float, float], scale: float = 1.0) -> TraceSegment:
        """
        Create a 90 degree corner arc.
        """
        start = scale_vec(start, scale)
        end = scale_vec(end, scale)

        deltax = end[0] - start[0]
        deltay = end[1] - start[1]
        quadrant = deltax * deltay

        if abs(deltax) - abs(deltay) > 1e-9:
            raise ValueError(f"Corner 90: Either deltax or deltay should be nonzero, but not both: deltax: {deltax}, deltay: {deltay}")

        if abs(deltax) < 1e-9:
            raise ValueError("Corner 90: deltax is zero")
        
        if quadrant < 0:
            mid = (end[0] - deltax/sqrt(2), start[1] + deltay/sqrt(2))
        else:
            mid = (start[0] + deltax/sqrt(2), end[1] - deltay/sqrt(2))

        return self.factory.create_arc_segment(start, mid, end, self.width / 1e6)

    def finish_optimization(self, target_resistance, temperature, track_count, minimum_spacing):
        global TOLERANCE
        depth = 100

        self.spacing = minimum_spacing
        working_width = self.working_width(self.spacing, self.margin)
        
        # Remember that there is one more tack than the track pitches between them
        self.pitch = working_width / (track_count - 1)
        self.width = self.pitch - self.spacing

        tracks = self.generate_tracks()
        rlo = self.factory.calculate_total_resistance(tracks, temperature)
        slo = self.spacing

        shi = self.pitch / 2
        self.spacing = shi
        working_width = self.working_width(self.spacing, self.margin)

        # Remember that there is one more tack than the track pitches between them
        self.pitch = working_width / (track_count - 1)
        self.width = self.pitch - self.spacing
        tracks = self.generate_tracks()
        rhi = self.factory.calculate_total_resistance(tracks, temperature)

        while depth > 0 and fabs(rlo - rhi) > TOLERANCE and fabs(slo - shi) > TOLERANCE:
            depth = depth - 1

            self.spacing = (shi + slo) / 2
            working_width = self.working_width(self.spacing, self.margin)

            # Remember that there is one more tack than the track pitches between them
            self.pitch = working_width / (track_count - 1)
            self.width = self.pitch - self.spacing

            tracks = self.generate_tracks()
            resistance = self.factory.calculate_total_resistance(tracks, temperature)

            if resistance > target_resistance:
                rhi = resistance
                shi = self.spacing
            else:
                rlo = resistance
                slo = self.spacing

        if depth <= 0:
            raise ValueError(f"Target resistance of {target_resistance} ohms not achievable with pitch of {pitch} and minimum spacing of {minimum_spacing}")

        # Pick whichever side of the bracket is closer to the target resistance
        if fabs(rlo - target_resistance) < fabs(rhi - target_resistance):
            self.spacing = slo
            resistance = rlo
        else:
            self.spacing = shi
            resistance = rhi

        working_width = self.working_width(self.spacing, self.margin)

        # Remember that there is one more tack than the track pitches between them
        self.pitch = working_width / (track_count - 1)
        self.width = self.pitch - self.spacing

        return resistance

