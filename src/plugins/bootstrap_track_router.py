"""
New implementation of the TrackRouter interface to generate bootstrappable
aluminium PCB hotplates.
"""

import wx
from math import sqrt, ceil, fabs, floor

import pcbnew

from typing import List, Tuple, Optional, Dict
from .track_router import TrackRouter, PRECISION
from .trace_segment_factory import TraceSegment, TraceSegmentFactory, ArcSegment, LinearSegment
from .pad_defs import RectangularPad, CircularPad
from .vector_utils import scale_vec, shrink_vec, add_vec, sub_vec, distance, perp_vec, normalize_vec
from .board_analyzer import BoardAnalyzer
from .board_builder import BoardBuilder
from .my_debug import debug, enable_debug

KICAD_MICRONS = 1e-3

class BootstrapTrackRouter(TrackRouter):
    """
    Track Router for bootstrappable aluminium PCB hotplate elements.

    All dimensions are in microns.

    This router generates tracks with exposed traces and a small screw hole in the middle.
    This allows the two halves of the heating element to be able to be shorted together with
    a small M2 screw, nut and washer. The heating element can then be used to preheat the
    hotplate to facilitate initial setup by hand soldering the fuse link and power connections
    in place.

    The class expects a PCB layout that has:
    
    * 4 M3 mounting holes in the corners
    * two power connection pads near the top edge of the PCB
    * two thermal fuse pads near the centre of the PCB
    * a small M2 mounting hole near the centre of the PCB
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
        self.analyzer = analyzer

        centre = ((left + right) / 2, (top + bottom) / 2)

        self.left = left * KICAD_MICRONS
        self.top = top * KICAD_MICRONS
        self.right = right * KICAD_MICRONS
        self.bottom = bottom * KICAD_MICRONS
        self.centre = (centre[0] * KICAD_MICRONS, centre[1] * KICAD_MICRONS)

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

        # Bootstrap screw terminal is expected to be near the centre of the board
        self.bootstrap = analyzer.get_closest_hole((centre[0], centre[1]), KICAD_MICRONS)

        self.update_derived_parameters()

    def update_board(self, builder: BoardBuilder) -> List[TraceSegment]:
        """
        Update the board with the generated tracks.
        """
        builder.clear_tracks()
        tracks = self.generate_tracks()

        builder.add_tracks(tracks)

        # Move the fuse footprint off-centre to sit in between tracks
        # fp = self.fuse[0].footprint
        # position = fp.GetPosition()
        # position.x = int((self.fuse_right + self.fuse_left) * 500) # Average and convert to nm
        # fp.SetPosition(position)

        # Move the power connections to sit in between tracks
        self.connections[0].sync_position()
        self.connections[1].sync_position()
        self.create_jumper_mask()

        pcbnew.Refresh()

        return tracks

    def generate_left_tracks(self) -> List[TraceSegment]:
        """
        Generate tracks as per this router's algorithm and parameters.
            
        Returns:
            List of TraceSegment objects forming heating element.
        """
        xstart = self.vert_centre - self.pitch/2

        result = self.serpentine_track(
            (xstart, self.vert_top),
            (xstart, self.vert_bottom),
            self.width,
            self.spacing,
            self.vert_lcount,
            self.factory,
            -1
        )

        scaled_pitch = self.pitch * 1e-6
        self.shorten_track_pair(result, 3, scaled_pitch)
        result[0].move_start((0, scaled_pitch))

        self.avoid_pad(result, self.fuse[0])
        self.avoid_pad(result, self.connections[0])

        second = self.serpentine_track(
            (self.split_left, self.split_top),
            (self.split_centre - self.pitch_plus, self.split_top),
            self.width,
            self.spacing,
            self.split_count / 2,
            self.factory,
            -1
        )

        # Arcs in metres, left/centre in microns
        i = self.closest_arc(second, (self.left * 1e-6, self.centre[1] * 1e-6))
        self.high_jumper_arc = second[i]

        conn_top = self.connections[0].top() + self.width/2
        conn_left = self.connections[0].x
        conn_right = xstart - self.pitch_plus
        conn_corner_start = scale_vec((conn_right, conn_top), 1e-6)

        fuse_right = self.split_centre
        fuse_top = self.fuse[0].y
        fuse_bottom = second[-1].end_point[1] - self.pitch_plus * 1e-6
        fuse_corner_start = (fuse_right * 1e-6, fuse_bottom)

        link_left = result[-1].end_point[0] * 1e6
        link_right = link_left + self.pitch_plus
        link_bottom = self.split_top
        link_top = link_bottom - self.pitch_plus
        link_start = scale_vec((link_right, link_bottom), 1e-6)
        second[0].start_point = link_start
        
        extra = [
            # Link the first serpentine to the power connection pad
            self.factory.create_linear_segment(scale_vec((conn_left, conn_top), 1e-6), conn_corner_start, self.width * 1e-6),
            self.corner_90(conn_corner_start, result[0].start_point),

            # Link the second serpentine to the thermal fuse pad
            self.factory.create_linear_segment(scale_vec((fuse_right, fuse_top), 1e-6), fuse_corner_start, self.width * 1e-6),
            self.corner_90(fuse_corner_start, second[-1].end_point),

            # Link the first serpentine to the second serpentine
            self.corner_90(link_start, scale_vec((link_left, link_top), 1e-6)),
        ]

        result.extend(second)
        result.extend(extra)

        #self.avoid_hole(result, hole, hole.clear_radius() + self.pitch)
        self.avoid_hole(result, self.holes[0])
        self.avoid_hole(result, self.holes[2])
        self.avoid_pad(second, self.fuse[0])

        return result

    def generate_right_tracks(self) -> List[TraceSegment]:
        """
        Generate tracks as per this router's algorithm and parameters.
            
        Returns:
            List of TraceSegment objects forming heating element.
        """
        xstart = self.vert_centre + self.pitch/2

        result = self.serpentine_track(
            (xstart, self.vert_top),
            (xstart, self.vert_bottom),
            self.width,
            self.spacing,
            self.vert_count - self.vert_lcount,
            self.factory,
            1
        )

        self.avoid_hole(result, self.holes[1])

        scaled_pitch = self.pitch * 1e-6
        self.shorten_track_pair(result, 3, scaled_pitch)
        self.shorten_track_pair(result, 7, scaled_pitch)
        result[0].move_start((0, scaled_pitch))

        self.avoid_pad(result, self.fuse[0])
        self.avoid_pad(result, self.connections[1])

        xend = self.split_centre + self.pitch_plus

        second = self.serpentine_track(
            (self.split_right, self.split_top),
            (xend, self.split_top),
            self.width,
            self.spacing,
            self.split_count,
            self.factory,
            1
        )

        xright = self.centre[0] + self.pitch * (self.vert_count / 2 - 0.5)
        ybottom = self.bottom - self.margin - self.edge_offset

        third = self.serpentine_track(
            (xright, self.split_bottom + self.pitch_plus),
            (xright, ybottom),
            self.width,
            self.spacing,
            self.vert_count,
            self.factory,
            -1
        )

        self.avoid_hole(third, self.holes[2])
        self.avoid_hole(third, self.holes[3])
        self.avoid_pad(third, self.fuse[1])

        fourth = self.serpentine_track(
            (self.split_left, self.split_bottom),
            (self.split_centre - self.pitch_plus, self.split_bottom),
            self.width,
            self.spacing,
            self.split_count / 2,
            self.factory,
            1
        )

        # Arcs in metres, left/centre in microns
        i = self.closest_arc(fourth, (self.left * 1e-6, self.centre[1] * 1e-6))
        self.low_jumper_arc = fourth[i]

        conn_top = self.connections[1].top() + self.width/2
        conn_right = self.connections[1].x
        conn_left = xstart + self.pitch_plus
        conn_corner_end = scale_vec((conn_left, conn_top), 1e-6)

        fuse_right = self.split_centre
        fuse_bottom = self.fuse[1].y
        fuse_top = fourth[-1].end_point[1] + self.pitch_plus * 1e-6
        fuse_corner_end = (fuse_right * 1e-6, fuse_top)

        link12_right = result[-1].end_point[0] * 1e6
        link12_left = link12_right - self.pitch_plus
        link12_top = result[-1].end_point[1] * 1e6
        link12_bottom = link12_top + self.pitch_plus
        link12_end = scale_vec((link12_left, link12_bottom), 1e-6)
        second[0].start_point = link12_end

        link23_right = third[0].start_point[0] * 1e6
        link23_left = link23_right - self.pitch_plus
        link23_bottom = third[0].start_point[1] * 1e6
        link23_top = link23_bottom - self.pitch_plus
        link23_start = scale_vec((link23_left, link23_top), 1e-6)
        second[-1].end_point = link23_start

        link34_left = third[-1].end_point[0] * 1e6
        link34_right = link34_left + self.pitch_plus
        link34_bottom = third[-1].end_point[1] * 1e6
        link34_top = link34_bottom - self.pitch_plus
        link34_end = scale_vec((link34_right, link34_top), 1e-6)
        fourth[0].start_point = link34_end

        self.avoid_pad(fourth, self.fuse[1])
        
        extra = [
            # Link the first serpentine to the power connection pad
            self.factory.create_linear_segment(scale_vec((conn_right, conn_top), 1e-6), conn_corner_end, self.width * 1e-6),
            self.corner_90(result[0].start_point, conn_corner_end),

            # Link the last serpentine to the thermal fuse pad
            self.factory.create_linear_segment(scale_vec((fuse_right, fuse_bottom), 1e-6), fuse_corner_end, self.width * 1e-6),
            self.corner_90(fourth[-1].end_point, fuse_corner_end),

            # Link the first serpentine to the second serpentine
            self.corner_90(scale_vec((link12_right, link12_top), 1e-6), link12_end),

            # Link the second serpentine to the third serpentine
            self.corner_90(link23_start, scale_vec((link23_right, link23_bottom), 1e-6)),

            # Link the third serpentine to the fourth serpentine
            self.corner_90(scale_vec((link34_left, link34_bottom), 1e-6), link34_end),
        ]

        ## Extend the one track pair in the centre opposite wheter the two traces turn to connect to the fuse pads
        ref_point = (self.split_centre * 1e-6, self.centre[1] * 1e-6)
        i_extend = self.closest_arc(second, ref_point)
        i_centre = self.closest_arc(fourth, ref_point)
        c_extend = self.arc_centre(second[i_extend])
        c_centre = self.arc_centre(fourth[i_centre])

        new_xc = round(c_centre[0] + sqrt(5) * self.pitch * 1e-6, PRECISION)
        deltax = c_extend[0] - new_xc
        self.shorten_track_pair(second, i_extend, deltax)

        result.extend(second)
        result.extend(third)
        result.extend(fourth)
        result.extend(extra)

        return result

    def generate_tracks(self) -> List[TraceSegment]:
        """
        Generate tracks as per this router's algorithm and parameters.
            
        Returns:
            List of TraceSegment objects forming heating element.
        """
        self.update_derived_parameters()

        self.edge_offset = (self.width + self.pitch)/2
        self.pitch_plus = self.pitch * 3 / 2

        # Needs to be a number == 2 mod 4, so it's even, but splits into two odd halves
        self.split_count = 2 * self.odd_tracks_under(self.fuse[1].bottom() - self.fuse[0].top(), self.pitch * 2)

        # The width of the serpentine tracks in the split regions
        self.split_width = self.split_count * self.pitch
        
        self.split_top = self.centre[1] - self.pitch * (self.split_count / 2 - 0.5)
        self.split_bottom = self.centre[1] + self.pitch * (self.split_count / 2 - 0.5)

        self.vert_top = self.top + self.margin + self.edge_offset
        self.vert_bottom = self.split_top - self.pitch_plus
        
        # Fudge factor added in to avoid undercounting due to rounding errors
        # Remember that we have one more trace than track pitches between traces
        self.vert_count = floor((self.right - self.left - 2*self.margin - self.width + 0.01) / self.pitch) + 1
        self.vert_centre = self.centre[0]
        self.vert_lcount = self.vert_count / 2

        if (self.vert_count % 4 == 0):
            self.vert_lcount = self.vert_lcount - 1
            self.vert_centre = self.vert_centre - self.pitch

            # Fudge Factor to ensure clearance from adjacent trace
            self.connections[1].move_clear_left(self.vert_centre - self.spacing/2 + 5*self.pitch - 0.00001)
        else:
            # Fudge Factor to ensure clearance from adjacent trace
            self.connections[1].move_clear_left(self.vert_centre - self.spacing/2 + 3*self.pitch - 0.00001)

        # Fudge Factor to ensure clearance from adjacent trace
        self.connections[0].move_clear_right(self.vert_centre + self.spacing/2 - 3*self.pitch + 0.00001)
        self.connections[0].move_top(self.top + self.margin)
        self.connections[1].move_top(self.top + self.margin)

        self.split_left = self.left + self.margin + self.edge_offset
        self.split_right = self.right - self.margin - self.edge_offset
        self.split_centre = self.fuse[0].right() - self.width / 2

        return self.generate_left_tracks() + self.generate_right_tracks()

    def create_jumper_mask(self):
        """
        Create and/or move the jumper mask to the appropriate size and position.
        """

        hja = self.high_jumper_arc
        lja = self.low_jumper_arc

        # Need coordinates in nanometres. arcs are in metres. pitch is in microns
        hi_point = (int(hja.mid_point[0] * 1e9), int(hja.mid_point[1] * 1e9))
        lo_point = (int(lja.mid_point[0] * 1e9), int(lja.mid_point[1] * 1e9))

        drawings = []
        drawings.extend(self.analyzer.board.GetDrawings())
        hi_mask = self.analyzer.find_closest_mask_arc(hi_point, drawings)
        if hi_mask is not None:
            drawings.remove(hi_mask)

        lo_mask = self.analyzer.find_closest_mask_arc(lo_point, drawings)

        hi_start = pcbnew.VECTOR2I(int(hja.start_point[0] * 1e9), int(hja.start_point[1] * 1e9))
        hi_end = pcbnew.VECTOR2I(int(hja.end_point[0] * 1e9), int(hja.end_point[1] * 1e9))
        hi_centre = pcbnew.VECTOR2I(int(hja.center[0] * 1e9), int(hja.center[1] * 1e9))
        hi_mid = pcbnew.VECTOR2I(int(hja.mid_point[0] * 1e9), int(hja.mid_point[1] * 1e9))
        hi_width = int(hja.width * 1e9) - 260000 # 0.13mm inset from track edge based on JLCPCB capabilities

        lo_start = pcbnew.VECTOR2I(int(lja.start_point[0] * 1e9), int(lja.start_point[1] * 1e9))
        lo_end = pcbnew.VECTOR2I(int(lja.end_point[0] * 1e9), int(lja.end_point[1] * 1e9))
        lo_centre = pcbnew.VECTOR2I(int(lja.center[0] * 1e9), int(lja.center[1] * 1e9))
        lo_mid = pcbnew.VECTOR2I(int(lja.mid_point[0] * 1e9), int(lja.mid_point[1] * 1e9))
        lo_width = int(lja.width * 1e9) - 260000 # 0.13mm inset from track edge based on JLCPCB capabilities

        if hi_mask is None or hi_mask is lo_mask:
            hi_mask = pcbnew.PCB_SHAPE(self.analyzer.board)
            hi_mask.SetShape(pcbnew.SHAPE_T_ARC)
            hi_mask.SetLayer(pcbnew.F_Mask)
            self.analyzer.board.Add(hi_mask)

        if lo_mask is None:
            lo_mask = pcbnew.PCB_SHAPE(self.analyzer.board)
            lo_mask.SetShape(pcbnew.SHAPE_T_ARC)
            lo_mask.SetLayer(pcbnew.F_Mask)
            self.analyzer.board.Add(lo_mask)

        self.align_arc_mask(hja, hi_mask)

        self.align_arc_mask(lja, lo_mask)

    def align_arc_mask(self, arc: ArcSegment, mask: pcbnew.PCB_SHAPE):
        """
        Align an arc mask to an arc segment.
        """
        arc_mid = pcbnew.VECTOR2I(int(arc.mid_point[0] * 1e9), int(arc.mid_point[1] * 1e9))
        arc_start = pcbnew.VECTOR2I(int(arc.start_point[0] * 1e9), int(arc.start_point[1] * 1e9))
        arc_end = pcbnew.VECTOR2I(int(arc.end_point[0] * 1e9), int(arc.end_point[1] * 1e9))
        arc_centre = pcbnew.VECTOR2I(int(arc.center[0] * 1e9), int(arc.center[1] * 1e9))
        arc_width = int(arc.width * 1e9) - 260000 # 0.13mm inset from track edge based on JLCPCB capabilities
        
        mask.SetStartEnd(arc_start, arc_end)
        mask.SetCenter(arc_centre)
        mask.SetWidth(arc_width)

        if distance(mask.GetArcMid(), arc_mid) > 1000:
            mask.SetStartEnd(arc_end, arc_start)
