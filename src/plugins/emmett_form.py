import pcbnew
from .emmett_dialog import EmmettDialog
from .board_builder import BoardBuilder
from .board_analyzer import BoardAnalyzer

class EmmettForm(EmmettDialog):
    def __init__(self, frame, board: pcbnew.BOARD, builder: BoardBuilder, analyzer: BoardAnalyzer):
        super().__init__(frame)
        self.board = board
        self.builder = builder
        self.analyzer = analyzer

    def HandleClearClick(self, event):
        self.builder.clear_tracks()

