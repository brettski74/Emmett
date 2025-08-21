"""
BoardAnalyzer class for extracting trace information from KiCad PCB layouts.

This class acts as an intermediary between KiCad's PCB data structures
and our trace segment model, allowing analysis of loaded PCB layouts.

Measurements are returned in metres.
"""

from math import fabs
import wx
import pcbnew
import re
from typing import List, Tuple, Optional, Union
from .trace_segment_factory import TraceSegmentFactory, TraceSegment, LinearSegment, ArcSegment
from .pad_defs import RectangularPad, CircularPad
from .vector_utils import distance
from .my_debug import debug, stringify, enable_debug, stringify

KICAD_UNITS = 1e-9
KICAD_MM = 1e-6


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
        self.parent = None

    def find_text_element(self, prefix: str) -> pcbnew.PCB_TEXT:
        """
        Find the first text element on the board with text content starting with the specified prefix.
        """
        drawings = self.board.GetDrawings()
        for d in drawings:
            if isinstance(d, pcbnew.PCB_TEXT):
                if d.GetText().startswith(prefix):
                    return d
        return None

    def parse_board_text(self) -> dict:
        result = {}

        r = re.compile(r"^([\w ]+): ([\d.]+).*(\n|$)")

        drawings = self.board.GetDrawings()
        for drawing in drawings:
            if isinstance(drawing, pcbnew.PCB_TEXT):
                txt = drawing.GetText()

                while m := r.match(txt):
                    result[m.group(1)] = m.group(2)
                    txt = r.sub("", txt)

        return result

    def get_extents(self, units: float = KICAD_UNITS) -> Tuple[float, float, float, float]:
        """
        Get the extents of the board.
        """
        left = float('inf')
        top = float('inf')
        right = float('-inf')
        bottom = float('-inf')

        drawings = self.board.GetDrawings()
        for d in drawings:
            if isinstance(d, pcbnew.PCB_SHAPE):
                if d.ShowShape() == "Line":
                    if d.GetLayer() == pcbnew.Edge_Cuts:
                        if d.GetStartX() < left:
                            left = d.GetStartX()
                        if d.GetEndX() < left:
                            left = d.GetEndX()

                        if d.GetStartY() < top:
                            top = d.GetStartY()
                        if d.GetEndY() < top:
                            top = d.GetEndY()

                        if d.GetStartX() > right:
                            right = d.GetStartX()
                        if d.GetEndX() > right:
                            right = d.GetEndX()

                        if d.GetStartY() > bottom:
                            bottom = d.GetStartY()
                        if d.GetEndY() > bottom:
                            bottom = d.GetEndY()

        return (left * units, top * units, right * units, bottom * units)
    
    def get_closest_pad(self, point: Tuple[float, float], layer: str, units: float = KICAD_UNITS) -> RectangularPad:
        """
        Get the closest pad to a point.
        """
        layer_id = self.board.GetLayerID(layer)
        footprints = self.board.GetFootprints()
        closest = None
        footprint = None
        closest_distance = float('inf')

        for fp in footprints:
            pads = fp.Pads()
            for pad in pads:
                if pad.GetLayerSet().Contains(layer_id):
                    d = distance(point, (pad.GetPosition().x, pad.GetPosition().y))
                    if d < closest_distance:
                        closest = pad
                        footprint = fp
                        closest_distance = d

        if closest is None:
            raise Exception(f"No pad found on layer {layer} near ({point[0]*KICAD_MM:.3f}, {point[1]*KICAD_MM:.3f})")

        # Return a RectangularPad object representing the location of the pad and it's size
        # and courtyard size
        # TODO: Hack for now is to assume 0.250mm clearance until I can figure out how to read
        # the courtyard details from the footprint.
        
        if 45 <= fabs(footprint.GetOrientationDegrees()) <= 135:
            width = closest.GetSizeY()
            height = closest.GetSizeX()
        else:
            width = closest.GetSizeX()
            height = closest.GetSizeY()

        result = RectangularPad(
            closest.GetPosition().x * units,
            closest.GetPosition().y * units,
            width * units,
            height * units,
            2.5e5 * units # 0.250mm in nm
        )
        result.footprint = footprint

        return result
    
    def get_closest_hole(self, point: Tuple[float, float], units: float = KICAD_UNITS) -> CircularPad:
        """
        Get the closest hole to a point.
        """
        f_cu = self.board.GetLayerID("F.Cu")
        footprints = self.board.GetFootprints()
        closest = None
        closest_distance = float('inf')

        for fp in footprints:
            if fp.HasThroughHolePads() and not fp.IsOnLayer(f_cu):
                d = distance(point, (fp.GetPosition().x, fp.GetPosition().y))
                if d < closest_distance:
                    closest = fp
                    closest_distance = d
            
        if closest is None:
            raise Exception(f"No hole found near ({point[0]*KICAD_MM:.3f}, {point[1]*KICAD_MM:.3f})")
          
        # Return a CircularPad object representing the location of the hole and it's size
        # and courtyard size
        # TODO: Hack for now is to assume 3.2mm hole and a 10mm courtyard diameter
        result = CircularPad(
            closest.GetPosition().x * units,
            closest.GetPosition().y * units,
            1.6e6 * units, # 3.2mm diameter in nm radius
            3.4e6 * units # 6.8mm diameter in nm radius to make up the 10mm clearance
        )

        result.footprint = closest
        return result

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
            start_m = (start_point.x * KICAD_UNITS, start_point.y * KICAD_UNITS)
            end_m = (end_point.x * KICAD_UNITS, end_point.y * KICAD_UNITS)
            width_m = width * KICAD_UNITS
            
            # Check if this is an arc
            if isinstance(track, pcbnew.PCB_ARC):
                # This is an arc - get the mid point directly from KiCad
                mid_point = track.GetMid()
                mid_m = (mid_point.x * KICAD_UNITS, mid_point.y * KICAD_UNITS)
                
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
