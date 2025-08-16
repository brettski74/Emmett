"""
BoardAnalyzer class for extracting trace information from KiCad PCB layouts.

This class acts as an intermediary between KiCad's PCB data structures
and our trace segment model, allowing analysis of loaded PCB layouts.
"""

import pcbnew
from typing import List, Tuple, Optional, Union
from .trace_segment_factory import TraceSegmentFactory, TraceSegment, LinearSegment, ArcSegment

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
    
    def get_extents(self) -> Tuple[float, float, float, float]:
        """
        Get the extents of the board.
        """
        box = self.board.GetBoardEdgesBoundingBox()

        return (
            box.GetLeft() / self.KICAD_UNITS,
            box.GetTop() / self.KICAD_UNITS,
            box.GetRight() / self.KICAD_UNITS,
            box.GetBottom() / self.KICAD_UNITS
        )
    
    def get_closest_pad(self, point: Tuple[float, float], layer: str) -> RectangularPad:
        """
        Get the closest pad to a point.
        """
        pads = self.board.GetPads()
        closest = None
        closest_distance = float('inf')

        for pad in pads:
            if pad.GetLayerSet().Contains(layer_id):
                distance = distance(point, (pad.GetPosition().x, pad.GetPosition().y))
                if distance < closest_distance:
                    closest = pad
                    closest_distance = distance

        if closest is None:
            raise Exception(f"No pad found on layer {layer} near {point}")

        # Return a RectangularPad object representing the location of the pad and it's size
        # and courtyard size

        return closest
    
    def extract_trace_segments(self, factory: TraceSegmentFactory, 
                              layer_name: Optional[str] = None,
                              net_filter: Optional[Union[str, int]] = None) -> List[TraceSegment]:
        """
        Extract trace segments from the loaded PCB layout with optional filtering.
        
        Args:
            factory: TraceSegmentFactory instance for creating segments
            layer_name: Optional layer name to filter by (e.g., 'F.Cu', 'B.Cu')
            net_filter: Optional net filter by name or number (e.g., 'GND', 0)
            
        Returns:
            List of TraceSegment objects representing the filtered PCB traces
        """
        trace_segments = []
        
        # Get all tracks (traces) from the board
        tracks = self.board.GetTracks()
        
        # Convert net name to number if string is provided
        net_number = None
        if isinstance(net_filter, str):
            net_number = self._get_net_number_by_name(net_filter)
            if net_number is None:
                print(f"Warning: Net '{net_filter}' not found on board")
                return []
        elif isinstance(net_filter, int):
            net_number = net_filter
        
        # Get layer number if layer name is provided
        layer_number = None
        if layer_name:
            layer_number = self._get_layer_number_by_name(layer_name)
            if layer_number is None:
                print(f"Warning: Layer '{layer_name}' not found on board")
                return []
        
        for track in tracks:
            # Skip vias - they're not trace segments
            if isinstance(track, pcbnew.PCB_VIA):
                continue
            
            # Apply layer filter if specified
            if layer_number is not None and track.GetLayer() != layer_number:
                continue
            
            # Apply net filter if specified
            if net_number is not None and track.GetNetCode() != net_number:
                continue
            
            # Get track properties
            start_point = track.GetStart()
            end_point = track.GetEnd()
            width = track.GetWidth()
            
            # Get net information
            net_info = track.GetNet()
            net_name = net_info.GetNetname() if net_info else None
            
            # Convert from KiCad units (nanometers) to meters
            start_m = (start_point.x / self.KICAD_UNITS, start_point.y / self.KICAD_UNITS)
            end_m = (end_point.x / self.KICAD_UNITS, end_point.y / self.KICAD_UNITS)
            width_m = width / self.KICAD_UNITS
            
            # Check if this is an arc
            if isinstance(track, pcbnew.PCB_ARC):
                # This is an arc - get the mid point directly from KiCad
                mid_point = track.GetMid()
                mid_m = (mid_point.x / self.KICAD_UNITS, mid_point.y / self.KICAD_UNITS)
                
                arc_segment = factory.create_arc_segment(
                    start_point=start_m,
                    mid_point=mid_m,
                    end_point=end_m,
                    width=width_m
                )
                # Set the net from the track
                if net_name:
                    arc_segment.net = net_name
                trace_segments.append(arc_segment)
                
            elif isinstance(track, pcbnew.PCB_TRACK):
                # This is a straight line track
                linear_segment = factory.create_linear_segment(
                    start_point=start_m,
                    end_point=end_m,
                    width=width_m
                )
                # Set the net from the track
                if net_name:
                    linear_segment.net = net_name
                trace_segments.append(linear_segment)
        
        return trace_segments
    
    def _get_net_number_by_name(self, net_name: str) -> Optional[int]:
        """
        Get net number by net name.
        
        Args:
            net_name: Name of the net (e.g., 'GND', 'VCC', 'SIGNAL')
            
        Returns:
            Net number if found, None otherwise
        """
        # Get all nets from the board
        nets = self.board.GetNets()
        
        # Search for net by name
        for net_code, net_info in nets.items():
            if net_info.GetNetname() == net_name:
                return net_code
        
        return None
    
    def _get_layer_number_by_name(self, layer_name: str) -> Optional[int]:
        """
        Get layer number by layer name.
        
        Args:
            layer_name: Name of the layer (e.g., 'F.Cu', 'B.Cu', 'In1.Cu')
            
        Returns:
            Layer number if found, None otherwise
        """
        # Get layer manager from board
        layers = self.board.GetEnabledLayers()
        cu_layers = layers.CuStack()
        for layer in cu_layers:
            name = self.board.GetLayerName(layer)
            if name == layer_name:
                return layer
        return None
        # return self.board.GetLayerId(layer_name)
        #layer_manager = self.board.GetLayerManager()
        
        # Search for layer by name
        #for layer_id in range(pcbnew.PCB_LAYER_ID_COUNT):
            #if layer_manager.GetLayerName(layer_id) == layer_name:
                #return layer_id
        
        #return None
    
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
            'nets_count': self.board.GetNetCount()
        }
        return board_info

    def get_available_nets(self) -> List[Tuple[int, str]]:
        """
        Get list of available nets on the board.
        
        Returns:
            List of tuples (net_code, net_name)
        """
        nets = self.board.GetNets()
        return [(net_code, net_info.GetNetname()) for net_code, net_info in nets.items()]
    
    def get_available_layers(self) -> List[Tuple[int, str]]:
        """
        Get list of available layers on the board.
        
        Returns:
            List of tuples (layer_id, layer_name)
        """
        layer_manager = self.board.GetLayerManager()
        layers = []
        
        for layer_id in range(pcbnew.PCB_LAYER_ID_COUNT):
            layer_name = layer_manager.GetLayerName(layer_id)
            if layer_name:  # Only include layers with names
                layers.append((layer_id, layer_name))
        
        return layers


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
    print("Filtering examples:")
    print("  # Get all traces")
    print("  traces = analyzer.extract_trace_segments(factory)")
    print()
    print("  # Get traces only on front copper layer")
    print("  traces = analyzer.extract_trace_segments(factory, layer_name='F.Cu')")
    print()
    print("  # Get traces only on GND net")
    print("  traces = analyzer.extract_trace_segments(factory, net_filter='GND')")
    print()
    print("  # Get traces on specific layer and net")
    print("  traces = analyzer.extract_trace_segments(factory, layer_name='B.Cu', net_filter='VCC')")
    print()
    print("  # Get available nets and layers")
    print("  nets = analyzer.get_available_nets()")
    print("  layers = analyzer.get_available_layers()")
