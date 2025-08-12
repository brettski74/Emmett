#!/usr/bin/python3
"""
BoardAnalyzer class for extracting trace information from KiCad PCB layouts.

This class acts as an intermediary between KiCad's PCB data structures
and our trace segment model, allowing analysis of loaded PCB layouts.
"""

import pcbnew
from typing import List, Tuple, Optional
from trace_segment_factory import TraceSegmentFactory, TraceSegment, LinearSegment, ArcSegment


class BoardAnalyzer:
    """
    Analyzes loaded KiCad PCB layouts to extract trace information.
    
    This class extracts trace segments from the currently loaded PCB
    and converts them to our trace segment model for analysis.
    """
    
    def __init__(self, board: pcbnew.BOARD):
        """
        Initialize the board analyzer.
        
        Args:
            board: KiCad board object to analyze
        """
        self.board = board
    
    def extract_trace_segments(self, factory: TraceSegmentFactory) -> List[TraceSegment]:
        """
        Extract all trace segments from the loaded PCB layout.
        
        Args:
            factory: TraceSegmentFactory instance for creating segments
            
        Returns:
            List of TraceSegment objects representing the PCB traces
        """
        trace_segments = []
        
        # Get all tracks (traces) from the board
        tracks = self.board.GetTracks()
        
        for track in tracks:
            # Skip vias - they're not trace segments
            if isinstance(track, pcbnew.PCB_VIA):
                continue
            
            # Get track properties
            start_point = track.GetStart()
            end_point = track.GetEnd()
            width = track.GetWidth()
            
            # Convert from KiCad units (nanometers) to meters
            start_m = (start_point.x / 1e9, start_point.y / 1e9)
            end_m = (end_point.x / 1e9, end_point.y / 1e9)
            width_m = width / 1e9
            
            # Check if this is an arc
            if isinstance(track, pcbnew.PCB_ARC):
                # This is an arc - get the mid point directly from KiCad
                mid_point = track.GetMid()
                mid_m = (mid_point.x / 1e9, mid_point.y / 1e9)
                
                arc_segment = factory.create_arc_segment(
                    start_point=start_m,
                    mid_point=mid_m,
                    end_point=end_m,
                    width=width_m
                )
                trace_segments.append(arc_segment)
                
            elif isinstance(track, pcbnew.PCB_TRACK):
                # This is a straight line track
                linear_segment = factory.create_linear_segment(
                    start_point=start_m,
                    end_point=end_m,
                    width=width_m
                )
                trace_segments.append(linear_segment)
        
        return trace_segments
    
    def get_board_info(self) -> dict:
        """
        Get basic information about the loaded board.
        
        Returns:
            Dictionary containing board information
        """
        board_info = {
            'filename': self.board.GetFileName(),
            'layers': self.board.GetCopperLayerCount(),
            'tracks_count': len(self.board.GetTracks()),
            'footprints_count': len(self.board.GetFootprints()),
            'nets_count': len(self.board.GetNets())
        }
        return board_info


# Example usage and testing
if __name__ == "__main__":
    # This would typically be run from within KiCad
    # For testing, we'll create a mock scenario
    
    print("BoardAnalyzer - PCB Trace Extraction Tool")
    print("=" * 50)
    print("This class is designed to work within KiCad's Python environment.")
    print("It extracts trace information from loaded PCB layouts.")
    print()
    print("To use in KiCad:")
    print("1. Load a PCB layout")
    print("2. Create a TraceSegmentFactory")
    print("3. Create a BoardAnalyzer with the board")
    print("4. Call extract_trace_segments(factory)")
    print()
    print("Example:")
    print("  factory = TraceSegmentFactory()")
    print("  analyzer = BoardAnalyzer(board)")
    print("  traces = analyzer.extract_trace_segments(factory)")
    print("  total_resistance = factory.calculate_total_resistance(traces)")
