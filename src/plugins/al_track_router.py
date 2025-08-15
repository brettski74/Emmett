"""
Simple concrete implementation of TrackRouter.

This module provides a basic track router that demonstrates how to implement
the abstract TrackRouter class.
"""
import wx
from math import sqrt, ceil

import pcbnew

from typing import List, Tuple
from .track_router import TrackRouter
from .trace_segment_factory import TraceSegment, TraceSegmentFactory, ArcSegment
from .pad_defs import RectangularPad
from .vector_utils import shrink_vec, add_vec

class AlTrackRouter(TrackRouter):
    """
    Track Router for aluminium PCB hotplate elements.

    All dimensions are in microns.
    
    """

    def __init__(self, factory: TraceSegmentFactory):
        super().__init__(factory)
        self.width = 1000
        self.spacing = 200
        self.top = 40000
        self.bottom = 140000
        self.left = 100000
        self.right = 200000
        self.margin = 500
        self.pitch = self.width + self.spacing
        self.fuse = (RectangularPad(150000,79500,5000,6000,500), RectangularPad(150000,100500,5000,6000,500))
        self.connections = (RectangularPad(143000,43500,5000,6000,250), RectangularPad(157000,43500,5000,6000,250))

        self.ystart = self.top + self.margin + self.pitch + self.pitch
        self.yend = self.bottom - self.margin - self.pitch

    def update_board(self, board: pcbnew.BOARD):
        """
        Update the board with the generated tracks.
        """
        pass

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
        ylimit = (self.top + self.margin + self.connections[0].clear_height() - self.width/2) / 1e6
        pitch = self.pitch / 1e6

        for i in range(count):
            n = i*4 + 3
            arc = result[n]
            offset = arc.mid_point[1] - ylimit
            self.shorten_track_pair(result, n, offset)

        result[0].move_start((0, -pitch))

        # Insert serpentine tracks in between fuse terminals
        width = self.fuse[1].clear_top() - self.fuse[0].clear_bottom()
        centre = (self.fuse[1].clear_top() + self.fuse[0].clear_bottom()) / 2
        count = self.even_tracks_under(width, self.pitch)
        ystart = centre - (count-1)*self.pitch/2

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

        result.extend(tracks)

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
        ylimit = (self.top + self.margin + self.connections[0].clear_height() - self.width/2) / 1e6

        for i in range(count):
            n = i*4 + 1
            arc = result[n]
            offset = arc.mid_point[1] - ylimit
            self.shorten_track_pair(result, n, offset)

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

        wx.MessageBox(f"total_count: {self.total_count}, fuse_count: {self.fuse_count}, left_count: {self.left_count}, right_count: {self.right_count}")

        self.fuse_left = self.fuse[0].x - (self.fuse_count-1)*self.pitch/2
        self.fuse_right = self.fuse[0].x + (self.fuse_count-1)*self.pitch/2

        return self.generate_fuse_in_tracks() + self.generate_fuse_out_tracks() + self.generate_left_tracks() + self.generate_right_tracks()

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

        if arc.start_point[1] > arc.mid_point[1]:
            arc.move((0, -offset))
            inl.move_end((0, -offset))
            out.move_start((0, -offset))
        else:
            arc.move((0, offset))
            inl.move_end((0, offset))
            out.move_start((0, offset))
