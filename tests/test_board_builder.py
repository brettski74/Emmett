"""
Unit tests for BoardBuilder class.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock pcbnew before importing BoardBuilder
with patch.dict('sys.modules', {'pcbnew': Mock()}):
    from plugins.board_builder import BoardBuilder
    from plugins.trace_segment_factory import TraceSegmentFactory, LinearSegment, ArcSegment


class TestBoardBuilder(unittest.TestCase):
    """Test cases for BoardBuilder class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock board
        self.mock_board = Mock()
        self.mock_board.GetTracks.return_value = []
        self.mock_board.GetEnabledLayers.return_value = Mock()
        self.mock_board.GetEnabledLayers().CuStack.return_value = [0, 1]
        self.mock_board.GetLayerName.side_effect = lambda x: "F.Cu" if x == 0 else "B.Cu"
        
        # Create the builder
        self.builder = BoardBuilder(self.mock_board)
        
        # Create a trace segment factory for testing
        self.factory = TraceSegmentFactory()
    
    def test_init(self):
        """Test BoardBuilder initialization."""
        self.assertEqual(self.builder.board, self.mock_board)
    
    def test_clear_tracks_no_layer_specified(self):
        """Test clearing tracks from all layers."""
        # Mock tracks
        mock_track1 = Mock()
        mock_track1.GetLayer.return_value = 0
        mock_track1.GetStart.return_value = Mock(x=0, y=0)
        mock_track1.GetEnd.return_value = Mock(x=1000000, y=0)
        mock_track1.GetWidth.return_value = 100000
        
        mock_track2 = Mock()
        mock_track2.GetLayer.return_value = 1
        mock_track2.GetStart.return_value = Mock(x=0, y=0)
        mock_track2.GetEnd.return_value = Mock(x=1000000, y=0)
        mock_track2.GetWidth.return_value = 100000
        
        mock_via = Mock()
        mock_via.GetLayer.return_value = 0
        
        self.mock_board.GetTracks.return_value = [mock_track1, mock_track2, mock_via]
        
        # Clear all tracks
        removed_count = self.builder.clear_tracks()
        
        # Should remove 2 tracks (skip the via)
        self.assertEqual(removed_count, 2)
        self.assertEqual(self.mock_board.Remove.call_count, 2)
        self.mock_board.BuildConnectivity.assert_called_once()
    
    def test_clear_tracks_specific_layer(self):
        """Test clearing tracks from a specific layer."""
        # Mock tracks
        mock_track1 = Mock()
        mock_track1.GetLayer.return_value = 0  # F.Cu
        mock_track1.GetStart.return_value = Mock(x=0, y=0)
        mock_track1.GetEnd.return_value = Mock(x=1000000, y=0)
        mock_track1.GetWidth.return_value = 100000
        
        mock_track2 = Mock()
        mock_track2.GetLayer.return_value = 1  # B.Cu
        mock_track2.GetStart.return_value = Mock(x=0, y=0)
        mock_track2.GetEnd.return_value = Mock(x=1000000, y=0)
        mock_track2.GetWidth.return_value = 100000
        
        self.mock_board.GetTracks.return_value = [mock_track1, mock_track2]
        
        # Clear only F.Cu tracks
        removed_count = self.builder.clear_tracks("F.Cu")
        
        # Should remove only 1 track from F.Cu
        self.assertEqual(removed_count, 1)
        self.assertEqual(self.mock_board.Remove.call_count, 1)
        self.mock_board.BuildConnectivity.assert_called_once()
    
    def test_clear_tracks_layer_not_found(self):
        """Test clearing tracks from a non-existent layer."""
        # This should not raise an error, just return 0
        removed_count = self.builder.clear_tracks("NonExistentLayer")
        self.assertEqual(removed_count, 0)
    
    def test_add_tracks_linear_segments(self):
        """Test adding linear track segments."""
        # Create test segments
        segment1 = self.factory.create_linear_segment(
            start_point=(0.0, 0.0),
            end_point=(0.001, 0.0),  # 1mm
            width=0.0001  # 0.1mm
        )
        
        segment2 = self.factory.create_linear_segment(
            start_point=(0.001, 0.0),
            end_point=(0.002, 0.0),  # 1mm
            width=0.0001  # 0.1mm
        )
        
        segments = [segment1, segment2]
        
        # Mock net info
        mock_net = Mock()
        self.mock_board.GetNetInfo.return_value = mock_net
        
        # Add tracks
        added_count = self.builder.add_tracks(segments, layer="F.Cu", net_code=1)
        
        # Should add 2 tracks
        self.assertEqual(added_count, 2)
        self.assertEqual(self.mock_board.Add.call_count, 2)
        self.mock_board.BuildConnectivity.assert_called_once()
    
    def test_add_tracks_arc_segments(self):
        """Test adding arc track segments."""
        # Create test arc segment with larger, more stable coordinates
        arc_segment = self.factory.create_arc_segment(
            start_point=(0.0, 0.0),
            mid_point=(0.005, 0.005),  # 5mm, 5mm - larger radius
            end_point=(0.01, 0.0),     # 10mm, 0mm - larger radius
            width=0.001                 # 1mm - larger width
        )
        
        segments = [arc_segment]
        
        # Mock net info
        mock_net = Mock()
        self.mock_board.GetNetInfo.return_value = mock_net
        
        # Add tracks
        added_count = self.builder.add_tracks(segments, layer="F.Cu", net_code=1)
        
        # Should add 1 arc track
        self.assertEqual(added_count, 1)
        self.assertEqual(self.mock_board.Add.call_count, 1)
        self.mock_board.BuildConnectivity.assert_called_once()
    
    def test_add_tracks_with_offset(self):
        """Test adding tracks with offset."""
        # Create test segment
        segment = self.factory.create_linear_segment(
            start_point=(0.0, 0.0),
            end_point=(0.001, 0.0),  # 1mm
            width=0.0001  # 0.1mm
        )
        
        segments = [segment]
        
        # Mock net info
        mock_net = Mock()
        self.mock_board.GetNetInfo.return_value = mock_net
        
        # Add tracks with offset
        added_count = self.builder.add_tracks(segments, x_offset=0.01, y_offset=0.02, layer="F.Cu")
        
        # Should add 1 track
        self.assertEqual(added_count, 1)
        self.assertEqual(self.mock_board.Add.call_count, 1)
        self.mock_board.BuildConnectivity.assert_called_once()
    
    def test_add_tracks_layer_not_found(self):
        """Test adding tracks to a non-existent layer."""
        # Create test segment
        segment = self.factory.create_linear_segment(
            start_point=(0.0, 0.0),
            end_point=(0.001, 0.0),
            width=0.0001
        )
        
        segments = [segment]
        
        # Try to add to non-existent layer
        with self.assertRaises(ValueError):
            self.builder.add_tracks(segments, layer="NonExistentLayer")
    
    def test_apply_offset(self):
        """Test offset application to points."""
        point = (1.0, 2.0)
        x_offset = 0.5
        y_offset = -0.3
        
        result = self.builder._apply_offset(point, x_offset, y_offset)
        expected = (1.5, 1.7)
        
        self.assertEqual(result, expected)
    
    def test_get_layer_number_by_name(self):
        """Test getting layer number by name."""
        # Test existing layer
        layer_num = self.builder._get_layer_number_by_name("F.Cu")
        self.assertEqual(layer_num, 0)
        
        # Test non-existing layer
        layer_num = self.builder._get_layer_number_by_name("NonExistent")
        self.assertIsNone(layer_num)


if __name__ == '__main__':
    unittest.main()

