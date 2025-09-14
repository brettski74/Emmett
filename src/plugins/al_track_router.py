"""
Simple concrete implementation of TrackRouter.

This module provides a basic track router that demonstrates how to implement
the abstract TrackRouter class.
"""
import wx
from math import sqrt, ceil, fabs, floor

import pcbnew

from .my_debug import debug, enable_debug

from typing import List, Tuple, Optional, Dict
from .track_router import TrackRouter
from .trace_segment_factory import TraceSegment, TraceSegmentFactory, ArcSegment, LinearSegment
from .pad_defs import RectangularPad, CircularPad
from .vector_utils import scale_vec, shrink_vec, add_vec, sub_vec, distance, perp_vec, normalize_vec
from .board_analyzer import BoardAnalyzer
from .board_builder import BoardBuilder
from .my_debug import debug, enable_debug

KICAD_MICRONS = 1e-3

class AlTrackRouter(TrackRouter):
    """
    Track Router for aluminium PCB hotplate elements.

    All dimensions are in microns.
    
    """

    def __init__(self, factory: TraceSegmentFactory):
        # Don't set board extents until we've analyzed the board
        self.top = 0
        self.bottom = 0
        self.left = 0
        self.right = 0

        super().__init__(factory)
        # Some sane defaults
        self.width = 1000
        self.spacing = 200
        self.margin = 500

        self.fuse = None
        self.connections = None
        self.holes = None

    def update_derived_parameters(self):
        super().update_derived_parameters()
        self.ystart = self.top + self.margin + self.pitch + self.width + self.spacing/2
        self.yend = self.bottom - self.margin - self.pitch

    def derive_width(self, tracks: List[TraceSegment]) -> int:
        """
        Analyze the set of tracks on the board to derive the track width that was used.

        The algorithm used looks at the widths of all tracks, both linear and arcs and uses the track width that is most common, rounded to the nearest micron.
        """
        widths = {}
        mode = None
        mode_count = 0

        for track in tracks:
            width = round(track.width * 1e6)
            key = str(width)
            widths[key] = (widths.get(key) or 0) + 1

            if widths[key] > mode_count:
                mode_count = widths[key]
                mode = width
        
        return mode or 1000

    def derive_spacing(self, tracks: List[TraceSegment]) -> int:
        """
        Analyze the set of tracks on the board to derive the track spacing that was used.

        The algorithm used looks at all pairs of horizontal and vertical linear tracks and uses the spacing that is most common, rounded to the nearest micron.
        """
        def tgap(t1, t2, i):
            return round((fabs(t1.start_point[i] - t2.start_point[i]) - (t1.width + t2.width)/2) * 1e6)

        gaps = {}
        mode = None
        mode_count = 0

        htracks = [t for t in tracks if isinstance(t, LinearSegment) and fabs(t.end_point[1] - t.start_point[1]) < 1e-8]
        vtracks = [t for t in tracks if isinstance(t, LinearSegment) and fabs(t.end_point[0] - t.start_point[0]) < 1e-8]

        for i in range(len(htracks)):
            first = htracks[i]
            for j in range(i+1, len(htracks)):
                second = htracks[j]
                gap = tgap(first, second, 1)
                key = str(gap)
                gaps[key] = (gaps.get(key) or 0) + 1
                if gaps[key] > mode_count:
                    mode_count = gaps[key]
                    mode = gap

        for i in range(len(vtracks)):
            first = vtracks[i]
            for j in range(i+1, len(vtracks)):
                second = vtracks[j]
                gap = tgap(first, second, 0)
                key = str(gap)
                gaps[key] = (gaps.get(key) or 0) + 1
                if gaps[key] > mode_count:
                    mode_count = gaps[key]
                    mode = gap

        return mode or 200

    def analyze_board(self, analyzer: BoardAnalyzer):
        """
        Analyze the board and set up the router's parameters.
        """
        left, top, right, bottom = analyzer.get_extents(1)

        centre = ((left + right) / 2, (top + bottom) / 2)

        self.left = left * KICAD_MICRONS
        self.top = top * KICAD_MICRONS
        self.right = right * KICAD_MICRONS
        self.bottom = bottom * KICAD_MICRONS

        factory = TraceSegmentFactory()
        tracks = analyzer.extract_trace_segments(factory)
        self.width = self.derive_width(tracks)
        self.spacing = self.derive_spacing(tracks)

        FIND_OFFSET = 10000000 # 10mm in nm
        # Fuse pads are expected to be near the centre of the board aligned vertically
        self.fuse = (
            analyzer.get_closest_pad((centre[0], centre[1] - FIND_OFFSET), "F.Cu", KICAD_MICRONS),
            analyzer.get_closest_pad((centre[0], centre[1] + FIND_OFFSET), "F.Cu", KICAD_MICRONS)
        )
        
        # Power connections are expected to be either side of the centre of the top edge of the board
        self.connections = (
            analyzer.get_closest_pad((left, top), "F.Cu", KICAD_MICRONS),
            analyzer.get_closest_pad((right, top), "F.Cu", KICAD_MICRONS)
        )

        # Mounting holes are expected to be in the four corners of the board
        self.holes = (
            analyzer.get_closest_hole((left, top), KICAD_MICRONS),
            analyzer.get_closest_hole((right, top), KICAD_MICRONS),
            analyzer.get_closest_hole((left, bottom), KICAD_MICRONS),
            analyzer.get_closest_hole((right, bottom), KICAD_MICRONS)
        )

        self.update_derived_parameters()

    def update_board(self, builder: BoardBuilder) -> List[TraceSegment]:
        """
        Update the board with the generated tracks.
        """
        builder.clear_tracks()
        tracks = self.generate_tracks()

        builder.add_tracks(tracks)

        # Move the fuse footprint off-centre to sit in between tracks
        fp = self.fuse[0].footprint
        position = fp.GetPosition()
        position.x = int((self.fuse_right + self.fuse_left) * 500) # Average and convert to nm
        fp.SetPosition(position)

        # Move the power connections to sit in between tracks
        fp = self.connections[0].footprint
        position = pcbnew.VECTOR2I_MM(self.left_pad[0]*1e-3, self.left_pad[1]*1e-3)
        fp.SetPosition(position)
        fp = self.connections[1].footprint
        position = pcbnew.VECTOR2I_MM(self.right_pad[0]*1e-3, self.right_pad[1]*1e-3)
        fp.SetPosition(position)

        pcbnew.Refresh()

        return tracks

    def generate_fuse_in_tracks(self) -> List[TraceSegment]:
        """
        Generate tracks as per this router's algorithm and parameters.
            
        Returns:
            List of TraceSegment objects forming heating element.
        """
        yend = self.fuse[0].clear_top() - (self.pitch + self.width)/2

        result = self.serpentine_track(
            (self.fuse_right, yend),
            (self.fuse_right, self.ystart - self.pitch),
            self.width,
            self.spacing,
            self.fuse_count,
            self.factory,
            1
        )

        pitch = self.pitch / 1e6
        width = self.width / 1e6
        result[0].move_start((0, pitch/2))
        mid = add_vec(result[-1].end_point, (-pitch/2, -pitch/2))
        end = add_vec(result[-1].end_point, (-pitch, 0))
        result.append(self.factory.create_arc_segment(result[-1].end_point, mid, end, width))

        # TraceSegments are in metres. We are in microns
        fc = (self.fuse_left + self.fuse_right)/2
        fuse_centre = shrink_vec((fc, self.fuse[0].y), 1e6)

        elbow = shrink_vec((fc + (self.fuse[0].width - self.width)/2, self.fuse[0].y), 1e6)

        result.append(self.factory.create_linear_segment(result[0].start_point, elbow, width))
        result.append(self.factory.create_linear_segment(elbow, fuse_centre, width))

        return result

    def generate_fuse_out_tracks(self) -> List[TraceSegment]:
        """
        Generate tracks as per this router's algorithm and parameters.
            
        Returns:
            List of TraceSegment objects forming heating element.
        """
        ystart = self.fuse[1].clear_bottom() + (self.pitch + self.width)/2

        result = self.serpentine_track(
            (self.fuse_left, ystart),
            (self.fuse_left, self.yend),
            self.width,
            self.spacing,
            self.fuse_count,
            self.factory,
            1
        )

        pitch = self.pitch / 1e6
        width = self.width / 1e6
        result[0].move_start((0, -pitch/2))
        mid = add_vec(result[-1].end_point, (pitch/2, pitch/2))
        end = add_vec(result[-1].end_point, (pitch, 0))
        result.append(self.factory.create_arc_segment(result[-1].end_point, mid, end, width))

        # TraceSegments are in metres. We are in microns
        fc = (self.fuse_left + self.fuse_right)/2
        fuse_centre = shrink_vec((fc, self.fuse[1].y), 1e6)
        elbow = shrink_vec((fc - (self.fuse[1].width - self.width)/2, self.fuse[1].y), 1e6)

        result.append(self.factory.create_linear_segment(result[0].start_point, elbow, width))
        result.append(self.factory.create_linear_segment(elbow, fuse_centre, width))

        return result

    def generate_left_tracks(self) -> List[TraceSegment]:
        """
        Generate tracks as per this router's algorithm and parameters.
            
        Returns:
            List of TraceSegment objects forming heating element.
        """
        xstart = self.fuse_left - self.pitch
        xend = self.left + self.margin

        result = self.serpentine_track(
            (xstart, self.ystart),
            (xstart, self.yend),
            self.width,
            self.spacing,
            self.left_count,
            self.factory,
            -1
        )

        count = int(self.even_tracks_over(self.connections[0].clear_width(), self.pitch) / 2)
        ylimit = (self.top + self.margin + self.connections[0].clear_height() + self.width/2) / 1e6
        pitch = self.pitch / 1e6

        pad = 0
        for i in range(count):
            n = i*4 + 3
            arc = result[n]
            offset = ylimit - arc.mid_point[1]
            pad += arc.mid_point[0]
            self.shorten_track_pair(result, n, offset)

        pad = pad * 1e6 / count
        self.left_pad = (pad, self.top + self.margin + self.connections[0].height/2)

        result[0].move_start((0, -pitch))

        # Insert serpentine tracks in between fuse terminals
        spacing_adjust = self.pitch/(self.fuse_count-1)
        xfstart = self.fuse_right
        yfstart = self.fuse[0].clear_bottom() + self.width/2 + 1.5*self.pitch + spacing_adjust/2
        yfend = self.fuse[1].clear_top() - self.pitch + self.spacing/2 - spacing_adjust/2
        
        tracks = self.serpentine_track(
            (xfstart, yfstart),
            (xfstart, yfend),
            self.width,
            self.spacing + spacing_adjust,
            self.fuse_count,
            self.factory,
            -1
        )

        tracks.append(self.factory.create_linear_segment(
            scale_vec(((self.fuse_left - self.pitch/2), (self.fuse[0].clear_bottom() + self.width/2)), 1e-6),
            scale_vec(((self.fuse_right - 1.5*self.pitch - spacing_adjust/2), (self.fuse[0].clear_bottom() + self.width/2)), 1e-6),
            self.width / 1e6
        ))
        tracks.append(self.corner_90(tracks[-1].end_point, tracks[0].start_point))
        tracks[-3].end_point = result[0].end_point
        result[0].end_point = (result[0].end_point[0], tracks[-2].start_point[1] - self.pitch*5e-7)
        tracks.append(self.corner_90(tracks[-2].start_point, result[0].end_point))

        hole = self.holes[0]

        # Create linear tracks from the pad
        y = self.top + self.margin + self.width/2
        rsum = hole.clear_radius() + 2*self.pitch
        yc = y + 1.5 * self.pitch
        dy = hole.y - yc
        dx = sqrt(rsum*rsum - dy*dy)
        x = hole.x + dx
        line = normalize_vec((-dx, dy), 1.5*self.pitch)
        start = (x, y);
        elbow = (pad, y)
        tracks.append(self.factory.create_linear_segment(scale_vec(start, 1e-6), scale_vec(elbow, 1e-6), self.width * 1e-6))
        tracks.append(self.factory.create_linear_segment(scale_vec(elbow, 1e-6), scale_vec(self.left_pad, 1e-6), self.width * 1e-6))

        # Create arcs around edge of left top hole
        end = add_vec((x, yc), line)
        mid = add_vec((x, yc), normalize_vec(perp_vec(sub_vec(start, end)), 1.5*self.pitch))
        tracks.append(self.factory.create_arc_segment(scale_vec(start, 1e-6), scale_vec(mid, 1e-6), scale_vec(end, 1e-6), self.width / 1e6))

        x = result[-1].end_point[0] * 1e6
        xc = x + 1.5 * self.pitch
        dx = xc - hole.x
        dy = sqrt(rsum*rsum - dx*dx)
        y = hole.y + dy
        result[-1].move_end((0, y*1e-6 - result[-1].end_point[1]))
        line = normalize_vec((-dx, -dy), 1.5*self.pitch)
        end = add_vec((xc, y), line)
        mid = add_vec((xc, y), normalize_vec(perp_vec(sub_vec(start, end)), 1.5*self.pitch))
        tracks.append(self.factory.create_arc_segment(result[-1].end_point, scale_vec(mid, 1e-6), scale_vec(end, 1e-6), self.width / 1e6))

        start = tracks[-1].end_point
        end = tracks[-2].end_point
        radius = hole.clear_radius() + self.pitch/2
        mid = add_vec((hole.x * 1e-6, hole.y * 1e-6), normalize_vec(perp_vec(sub_vec(start, end)), 1e-6 * radius))
        tracks.append(self.factory.create_arc_segment(start, mid, end, self.width / 1e6))

        result.extend(tracks)

        self.avoid_hole(result, hole, hole.clear_radius() + self.pitch)
        self.avoid_hole(result, self.holes[2])

        return result

    def generate_right_tracks(self) -> List[TraceSegment]:
        """
        Generate tracks as per this router's algorithm and parameters.
            
        Returns:
            List of TraceSegment objects forming heating element.
        """
        xstart = self.fuse_right + self.pitch
        xend = self.right - self.margin

        result = self.serpentine_track(
            (xstart, self.yend),
            (xstart, self.ystart),
            self.width,
            self.spacing,
            self.right_count,
            self.factory,
            -1
        )

        count = int(self.even_tracks_over(self.connections[1].clear_width(), self.pitch) / 2)
        ylimit = (self.top + self.margin + self.connections[0].clear_height() + self.width/2) / 1e6

        pad = 0

        for i in range(count):
            n = i*4 + 1
            arc = result[n]
            offset = ylimit - arc.mid_point[1]
            pad += arc.mid_point[0]
            self.shorten_track_pair(result, n, offset)

        pad = pad * 1e6 / count
        self.right_pad = (pad, self.top + self.margin + self.connections[1].height/2)

        hole = self.holes[1]

        # TODO: A lot of repetition of left side calculations here. Would be good to try to make
        # this more reusable and only write it once.
        y = self.top + self.margin + self.width/2
        rsum = hole.clear_radius() + 2*self.pitch
        yc = y + 1.5 * self.pitch
        dy = hole.y - yc
        dx = sqrt(rsum*rsum - dy*dy)
        x = hole.x - dx
        line = normalize_vec((dx, dy), 1.5*self.pitch)
        start = (x, y);
        elbow = (pad, y)
        tracks = [
            self.factory.create_linear_segment(scale_vec(start, 1e-6), scale_vec(elbow, 1e-6), self.width * 1e-6),
            self.factory.create_linear_segment(scale_vec(elbow, 1e-6), scale_vec(self.right_pad, 1e-6), self.width * 1e-6)
        ]

        # Create arcs around edge of right top hole
        end = add_vec((x, yc), line)
        mid = add_vec((x, yc), normalize_vec(perp_vec(sub_vec(end, start)), 1.5*self.pitch))
        tracks.append(self.factory.create_arc_segment(scale_vec(start, 1e-6), scale_vec(mid, 1e-6), scale_vec(end, 1e-6), self.width / 1e6))

        x = result[-1].end_point[0] * 1e6
        xc = x - 1.5 * self.pitch
        dx = hole.x - xc
        dy = sqrt(rsum*rsum - dx*dx)
        y = hole.y + dy
        result[-1].move_end((0, y*1e-6 - result[-1].end_point[1]))
        line = normalize_vec((dx,-dy), 1.5*self.pitch)
        end = add_vec((xc, y), line)
        mid = add_vec((xc, y), normalize_vec(perp_vec(sub_vec(end, start)), 1.5*self.pitch))
        tracks.append(self.factory.create_arc_segment(result[-1].end_point, scale_vec(mid, 1e-6), scale_vec(end, 1e-6), self.width / 1e6))

        start = tracks[-1].end_point
        end = tracks[-2].end_point
        radius = hole.clear_radius() + self.pitch/2
        mid = add_vec((hole.x * 1e-6, hole.y * 1e-6), normalize_vec(perp_vec(sub_vec(end, start)), 1e-6 * radius))
        tracks.append(self.factory.create_arc_segment(start, mid, end, self.width / 1e6))

        self.avoid_hole(result, hole, hole.clear_radius() + self.pitch)
        self.avoid_hole(result, self.holes[3])

        result.extend(tracks)

        return result

    def generate_tracks(self) -> List[TraceSegment]:
        """
        Generate tracks as per this router's algorithm and parameters.
            
        Returns:
            List of TraceSegment objects forming heating element.
        """
        self.update_derived_parameters()

        self.total_count = self.even_tracks_under(self.right - self.left - 2*self.margin + self.spacing, self.pitch)
        self.fuse_count = self.odd_tracks_over(self.fuse[0].clear_width(), self.pitch)
        self.left_count = ceil((self.total_count - self.fuse_count) / 2)
        if self.left_count % 2 == 0:
            self.right_count = self.left_count - 1
            self.fuse[0].x = (self.left + self.right + self.pitch) / 2
        else:
            self.right_count = self.left_count
            self.left_count = self.right_count - 1
            self.fuse[0].x = (self.left + self.right - self.pitch) / 2

        self.right_count = self.total_count - self.left_count - self.fuse_count

        self.fuse_left = self.fuse[0].x - (self.fuse_count-1)*self.pitch/2
        self.fuse_right = self.fuse[0].x + (self.fuse_count-1)*self.pitch/2

        return self.generate_left_tracks() + self.generate_right_tracks() + self.generate_fuse_in_tracks() + self.generate_fuse_out_tracks()

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
            raise ValueError("Corner 90: deltax and deltay are not equal")

        if abs(deltax) < 1e-9:
            raise ValueError("Corner 90: deltax is zero")
        
        if quadrant < 0:
            mid = (end[0] - deltax/sqrt(2), start[1] + deltay/sqrt(2))
        else:
            mid = (start[0] + deltax/sqrt(2), end[1] - deltay/sqrt(2))

        return self.factory.create_arc_segment(start, mid, end, self.width / 1e6)

    def shorten_track_pair(self, result: List[TraceSegment], index: int, offset: float):
        """
        Shorten a pair of track to avoid an obstacle.
        """
        if type(result[index]) != ArcSegment:
            raise ValueError(f"Track {index} is not an arc segment")

        inl= result[index-1]
        arc = result[index]
        out = result[index+1]

        if arc.start_point[1] < arc.mid_point[1]:
            offset = -offset

        arc.move((0, offset))
        inl.move_end((0, offset))
        out.move_start((0, offset))

    def starting_track_count(self) -> int:
        # Assume that we're never going to have track widths greater than 2.5mm
        # The -10 on the end is a hedge against rounding errors - hopefully enough!
        working_width = self.right - self.left - 2*self.margin + self.spacing - 10
        debug(f"working width: {working_width}, left: {self.left}, right: {self.right}, margin: {self.margin}, spacing: {self.spacing}")
        return (2 * floor(working_width / 5000), working_width)

