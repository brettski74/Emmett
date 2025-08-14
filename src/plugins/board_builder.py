"""
BoardBuilder class for modifying KiCad PCB boards.

This module provides functionality to clear existing tracks and add new ones
based on TraceSegment objects.
"""

import pcbnew
from typing import List, Optional, Tuple
from .trace_segment_factory import TraceSegment, LinearSegment, ArcSegment


class BoardBuilder:
    """
    Class for building and modifying PCB boards.
    
    This class provides methods to clear existing tracks and add new ones
    based on TraceSegment objects. Each TraceSegment can have its own net
    property, allowing for multi-net trace routing.
    """
    
    def __init__(self, board: pcbnew.BOARD):
        """
        Initialize the BoardBuilder.
        
        Args:
            board: The KiCad board object to modify
        """
        self.board = board
    
    def clear_tracks(self, layer: Optional[str] = None) -> int:
        """
        Remove all tracks from the specified layer.
        
        Args:
            layer: Optional layer name (e.g., "F.Cu", "B.Cu"). If None, clears all layers.
            
        Returns:
            Number of tracks removed
            
        Raises:
            ValueError: If the specified layer is not found
        """
        tracks_to_remove = []
        
        # Get all tracks from the board
        all_tracks = self.board.GetTracks()
        
        for track in all_tracks:
            # Skip vias (they're not tracks in the sense we want to clear)
            if isinstance(track, pcbnew.PCB_VIA):
                continue
                
            # If layer is specified, only remove tracks from that layer
            if layer is not None:
                track_layer_name = self.board.GetLayerName(track.GetLayer())
                if track_layer_name == layer:
                    tracks_to_remove.append(track)
            else:
                # Remove tracks from all layers
                tracks_to_remove.append(track)
        
        # Remove the tracks
        for track in tracks_to_remove:
            self.board.Remove(track)
        
        # Refresh the board
        self.board.BuildConnectivity()
        
        return len(tracks_to_remove)
    
    def add_tracks(self, trace_segments: List[TraceSegment], 
                   x_offset: float = 0.0, y_offset: float = 0.0,
                   layer: str = "F.Cu") -> int:
        """
        Add tracks to the board based on TraceSegment objects.
        
        Args:
            trace_segments: List of TraceSegment objects to add
            x_offset: X offset in meters (default: 0.0)
            y_offset: Y offset in meters (default: 0.0)
            layer: Layer name to add tracks to (default: "F.Cu")
            
        Returns:
            Number of tracks added
            
        Raises:
            ValueError: If the specified layer is not found
        """
        # Get the layer number
        layer_number = self._get_layer_number_by_name(layer)
        if layer_number is None:
            raise ValueError(f"Layer '{layer}' not found")
        
        tracks_added = 0
        
        for segment in trace_segments:
            # Apply offset to segment coordinates
            start_point = self._apply_offset(segment.start_point, x_offset, y_offset)
            end_point = self._apply_offset(segment.end_point, x_offset, y_offset)
            
            # Convert from meters to KiCad units (nanometers)
            start_nm = (int(start_point[0] * 1e9), int(start_point[1] * 1e9))
            end_nm = (int(end_point[0] * 1e9), int(end_point[1] * 1e9))
            width_nm = int(segment.width * 1e9)
            
            if isinstance(segment, LinearSegment):
                # Create a straight line track
                track = pcbnew.PCB_TRACK(self.board)
                track.SetStart(pcbnew.VECTOR2I(start_nm[0], start_nm[1]))
                track.SetEnd(pcbnew.VECTOR2I(end_nm[0], end_nm[1]))
                track.SetWidth(width_nm)
                track.SetLayer(layer_number)
                
                # Set net if segment has one
                if segment.net:
                    net_info = self.board.GetNetInfo(segment.net)
                    if net_info:
                        track.SetNet(net_info)
                
                self.board.Add(track)
                tracks_added += 1
                
            elif isinstance(segment, ArcSegment):
                # Create an arc track
                arc = pcbnew.PCB_ARC(self.board)
                arc.SetStart(pcbnew.VECTOR2I(start_nm[0], start_nm[1]))
                arc.SetEnd(pcbnew.VECTOR2I(end_nm[0], end_nm[1]))
                
                # Apply offset to mid point for arc
                mid_point = self._apply_offset(segment.mid_point, x_offset, y_offset)
                mid_nm = (int(mid_point[0] * 1e9), int(mid_point[1] * 1e9))
                arc.SetMid(pcbnew.VECTOR2I(mid_nm[0], mid_nm[1]))
                
                arc.SetWidth(width_nm)
                arc.SetLayer(layer_number)
                
                # Set net if segment has one
                if segment.net:
                    net_info = self.board.GetNetInfo(segment.net)
                    if net_info:
                        arc.SetNet(net_info)
                
                self.board.Add(arc)
                tracks_added += 1
        
        # Refresh the board
        self.board.BuildConnectivity()
        
        return tracks_added
    
    def _apply_offset(self, point: Tuple[float, float], x_offset: float, y_offset: float) -> Tuple[float, float]:
        """
        Apply offset to a point.
        
        Args:
            point: (x, y) coordinates in meters
            x_offset: X offset in meters
            y_offset: Y offset in meters
            
        Returns:
            New point with offset applied
        """
        return (point[0] + x_offset, point[1] + y_offset)
    
    def _get_layer_number_by_name(self, layer_name: str) -> Optional[int]:
        """
        Get layer number by layer name.
        
        Args:
            layer_name: Name of the layer (e.g., 'F.Cu', 'B.Cu', 'In1.Cu')
            
        Returns:
            Layer number if found, None otherwise
        """
        # Get enabled layers from board
        layers = self.board.GetEnabledLayers()
        cu_layers = layers.CuStack()
        
        for layer in cu_layers:
            name = self.board.GetLayerName(layer)
            if name == layer_name:
                return layer
        
        return None
