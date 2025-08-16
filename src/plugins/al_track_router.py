"""
Simple concrete implementation of TrackRouter.

This module provides a basic track router that demonstrates how to implement
the abstract TrackRouter class.
"""
import wx
from math import sqrt, ceil, fabs

import pcbnew

from typing import List, Tuple, Optional
from .track_router import TrackRouter
from .trace_segment_factory import TraceSegment, TraceSegmentFactory, ArcSegment
from .pad_defs import RectangularPad, CircularPad
from .vector_utils import scale_vec, shrink_vec, add_vec, sub_vec, distance, perp_vec, normalize_vec

class AlTrackRouter(TrackRouter):
    """
    Track Router for aluminium PCB hotplate elements.

    All dimensions are in microns.
    
    """

    def __init__(self, factory: TraceSegmentFactory):
        super().__init__(factory)
        #self.width = 1000
        self.width = 1000
        self.spacing = 200
        self.top = 40000
        self.bottom = 140000
        self.left = 100000
        self.right = 200000
        self.margin = 500
        self.pitch = self.width + self.spacing
        self.fuse = (RectangularPad(150000,79500,5000,6000,250), RectangularPad(150000,100500,5000,6000,250))
        self.connections = (RectangularPad(143000,43500,4000,6000,300), RectangularPad(157000,43500,4000,6000,300))
        self.holes = (CircularPad(104000,44000,4500,500), CircularPad(196000,44000,4500,500), CircularPad(104000,136000,4500,500), CircularPad(196000,136000,4500,500))
        self.parent = None

        self.ystart = self.top + self.margin + self.pitch + self.width + self.spacing/2
        self.yend = self.bottom - self.margin - self.pitch

    def update_board(self, board: pcbnew.BOARD):
        """
        Update the board with the generated tracks.
        """
        pass

    def _info_msg(self, msg):
        wx.MessageBox(msg, "Emmett", wx.OK | wx.ICON_INFORMATION, self.parent)

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
        mid = add_vec(result[-1].end_point, (-pitch/2, -pitch/2))
        end = add_vec(result[-1].end_point, (-pitch, 0))
        result.append(self.factory.create_arc_segment(result[-1].end_point, mid, end, width))

        elbow = self.fuse[0].y - self.fuse_right + self.fuse[0].x
        delta = elbow / 1e6 - result[0].start_point[1]

        # TraceSegments are in metres. We are in microns
        result[0].move_start((0, delta))
        fuse_centre = shrink_vec((self.fuse[0].x, self.fuse[0].y), 1e6)

        result.append(self.factory.create_linear_segment(result[0].start_point, fuse_centre, width))

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
        mid = add_vec(result[-1].end_point, (pitch/2, pitch/2))
        end = add_vec(result[-1].end_point, (pitch, 0))
        result.append(self.factory.create_arc_segment(result[-1].end_point, mid, end, width))

        elbow = self.fuse[1].y + self.fuse[1].x - self.fuse_left
        delta = elbow / 1e6 - result[0].start_point[1]

        # TraceSegments are in metres. We are in microns
        result[0].move_start((0, delta))
        fuse_centre = shrink_vec((self.fuse[1].x, self.fuse[1].y), 1e6)

        result.append(self.factory.create_linear_segment(result[0].start_point, fuse_centre, width))

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

        result[0].move_start((0, -pitch))

        # Insert serpentine tracks in between fuse terminals
        width = self.fuse[1].clear_top() - self.fuse[0].clear_bottom()
        centre = (self.fuse[1].clear_top() + self.fuse[0].clear_bottom()) / 2
        count = self.even_tracks_under(width, self.pitch)
        ystart = centre - (count-1)*self.pitch/2

        self._info_msg(f"fuse_left: {self.fuse_left}, fuse_right: {self.fuse_right}, ystart: {ystart}, width: {width}, centre: {centre}, count: {count}")
        tracks = self.serpentine_track(
            (self.fuse_left - self.pitch/2, ystart),
            (self.fuse_right - self.pitch/2, ystart),
            self.width,
            self.spacing,
            count,
            self.factory,
            -1
        )

        tracks.append(self.corner_90(add_vec(tracks[-1].end_point, (-pitch/2, pitch/2)), tracks[-1].end_point))
        tracks.append(self.factory.create_linear_segment(tracks[-1].start_point, result[0].end_point, self.width / 1e6))
        tracks.append(self.corner_90(tracks[0].start_point, add_vec(tracks[0].start_point, (-pitch/2, -pitch/2))))
        result[0].end_point = tracks[-1].end_point

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
        self.left_pad = (pad, y + self.connections[0].height/2)
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
        self.right_pad = (pad, y + self.connections[1].height/2)
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

        #wx.MessageBox(f"total_count: {self.total_count}, fuse_count: {self.fuse_count}, left_count: {self.left_count}, right_count: {self.right_count}")

        self.fuse_left = self.fuse[0].x - (self.fuse_count-1)*self.pitch/2
        self.fuse_right = self.fuse[0].x + (self.fuse_count-1)*self.pitch/2

        return self.generate_fuse_in_tracks() + self.generate_fuse_out_tracks() + self.generate_left_tracks() + self.generate_right_tracks()

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

    def corner_90(self, start: Tuple[float, float], end: Tuple[float, float]) -> TraceSegment:
        """
        Create a 90 degree corner arc.
        """
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
