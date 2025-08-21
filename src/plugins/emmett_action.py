import os
import pcbnew
import wx
import traceback

from .trace_segment_factory import TraceSegmentFactory
from .board_builder import BoardBuilder
from .board_analyzer import BoardAnalyzer
from .emmett_form import EmmettForm
from .al_track_router import AlTrackRouter
from .my_debug import debug, enable_debug
from .gui_utils import info_msg, error_msg

class EmmettAction( pcbnew.ActionPlugin ):
 
    def defaults( self ):
        self.name = "Emmett Element Router"
        self.category = "Modify PCB"
        self.description = "Heating Element Trace Router"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "./emmett_icon.png")

    def Run(self):
        try:
            board = pcbnew.GetBoard()
            enable_debug(True)
            if not board:
                info_msg("No PCB board is currently loaded.")
                return

            # Create and show the form
            enable_debug(True)
            debug("Running Emmett")
            builder = BoardBuilder(board)
            analyzer = BoardAnalyzer(board)
            factory = TraceSegmentFactory()

            router = AlTrackRouter(factory)
            form = EmmettForm(board, builder, analyzer, router)

            form.ShowModal()
            form.Destroy()
            
            return

        except Exception as e:
            msg = f"Error launching form: {e}"
            msg += f"\n{traceback.format_exc()}"
            error_msg(msg)
    