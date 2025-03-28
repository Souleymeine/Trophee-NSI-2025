import sys
from core.escape_sequences import cat_bgcolor, cat_goto, goto
from tui.base import ClickableElement, ColorsOnMouse, Positioning
from type_def.data_types import RGB, Coord
from type_def.input_properties import MouseInfo


class Surface(ClickableElement):
    def __init__(self, positioning: Positioning, col = RGB(0, 0, 0), z_index: int = 0, visible: bool = True):
        self._col = col
        super().__init__(positioning, ColorsOnMouse(), z_index, visible)

    def _on_click(self, info: MouseInfo):
        return super()._on_click(info)
    def _on_hover(self, info: MouseInfo):
        return super()._on_hover(info)
    def _on_mouse_exit(self, info: MouseInfo):
        return super()._on_mouse_exit(info)
    
    def render(self):
        goto(Coord(self.positioning.origin.x, self.positioning.origin.y))
        area = self.positioning.width * self.positioning.height
        # Initialize la table en avance pour éviter les copies et réalocation en mémoire : moins lent
        cells : list = area * [None]
        line: int = 0
        for i in range(area):
            if i % self.positioning.width == 0:
                cells[i] = cat_goto(Coord(self.top_left_coord.x, self.top_left_coord.y + line))
                line += 1
            cells[i] = cat_bgcolor(self._col)

        sys.stdout.write(''.join(cells))

