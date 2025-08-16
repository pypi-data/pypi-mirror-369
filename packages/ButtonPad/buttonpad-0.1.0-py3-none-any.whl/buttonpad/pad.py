\
from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass, field
from typing import Callable, List, Tuple, Dict, Optional

LabelMatrix = List[List[str]]
Coord = Tuple[int, int]

BUTTON_MIN_WIDTH = 10
BUTTON_MIN_HEIGHT = 10

def _parse_labels(label_text: Optional[str]) -> LabelMatrix:
    default = """1,2,3
4,5,6
7,8,9
*,0,#"""
    if not label_text or not label_text.strip():
        label_text = default
    rows = []
    for raw_line in label_text.strip().splitlines():
        parts = [p.strip() for p in raw_line.split(",")]
        if len(parts) == 1 and parts[0] == "":
            parts = []
        rows.append(parts)
    # validate rectangle
    if not rows:
        raise ValueError("No labels provided.")
    width = len(rows[0])
    for r in rows:
        if len(r) != width:
            raise ValueError("All rows must have the same number of comma-separated labels.")
    return rows

@dataclass
class Button:
    """A handle for a single logical button in the grid."""
    caption: str
    widget: tk.Button
    on_click: Optional[Callable[["Button"], None]] = None
    on_enter: Optional[Callable[["Button"], None]] = None
    on_exit: Optional[Callable[["Button"], None]] = None

    def __post_init__(self):
        # Bind default events
        self.widget.configure(command=self._handle_click)
        self.widget.bind("<Enter>", self._handle_enter)
        self.widget.bind("<Leave>", self._handle_exit)

    # Property proxies for convenience
    @property
    def bg(self) -> str:
        return str(self.widget.cget("bg"))

    @bg.setter
    def bg(self, value: str) -> None:
        self.widget.configure(bg=value, activebackground=value)

    @property
    def fg(self) -> str:
        return str(self.widget.cget("fg"))

    @fg.setter
    def fg(self, value: str) -> None:
        self.widget.configure(fg=value, activeforeground=value)

    @property
    def text(self) -> str:
        return str(self.widget.cget("text"))

    @text.setter
    def text(self, value: str) -> None:
        self.caption = value
        self.widget.configure(text=value)

    # Event dispatchers
    def _handle_click(self):
        if self.on_click:
            self.on_click(self)

    def _handle_enter(self, _event):
        if self.on_enter:
            self.on_enter(self)

    def _handle_exit(self, _event):
        if self.on_exit:
            self.on_exit(self)

class ButtonPad:
    """
    Create a window showing a grid of buttons that can span across cells.
    Configure via kwargs; sensible defaults are provided.

    Sizing:
      - Initial window size is computed from button_*_px and gap sizes.
      - If resizable=True, grid weights make buttons flex to fill space.
    """

    def __init__(
        self,
        labels: Optional[str] = None,
        *,
        button_width_px: int = 100,
        button_height_px: int = 60,
        hgap_px: int = 8,
        vgap_px: int = 8,
        button_bg: str = "#eeeeee",
        button_fg: str = "#000000",
        window_bg: str = "#f0f0f0",
        border_px: int = 8,
        title: str = "ButtonPad",
        resizable: bool = True,
    ) -> None:
        self.labels_matrix: LabelMatrix = _parse_labels(labels)
        self.rows = len(self.labels_matrix)
        self.cols = len(self.labels_matrix[0])

        self.button_width_px = max(10, int(button_width_px))
        self.button_height_px = max(10, int(button_height_px))
        self.hgap_px = max(0, int(hgap_px))
        self.vgap_px = max(0, int(vgap_px))
        self.button_bg = button_bg
        self.button_fg = button_fg
        self.window_bg = window_bg
        self.title = title
        self.resizable = bool(resizable)
        self.border_px = max(0, int(border_px))

        # Tk setup
        self.root = tk.Tk()
        self.root.title(self.title)
        self.root.configure(bg=self.window_bg)
        self.root.resizable(self.resizable, self.resizable)

        # Container for grid; we use spacer rows/cols for exact pixel gaps
        self.grid_frame = tk.Frame(self.root, bg=self.window_bg, highlightthickness=0, bd=0)
        self.grid_frame.grid(row=0, column=0, sticky="nsew", padx=self.border_px, pady=self.border_px)
        self.root.grid_rowconfigure(0, weight=1 if self.resizable else 0)
        self.root.grid_columnconfigure(0, weight=1 if self.resizable else 0)

        # Build spanning map and widgets
        self.buttons: List[Button] = []
        self._owner_for_cell: Dict[Coord, Button] = {}  # maps each logical cell to its top-left owner button
        spans = self._compute_spans(self.labels_matrix)
        self._build_grid(spans)

        # Initial geometry (approximate): sum of button sizes and gaps
        total_w = self.cols * self.button_width_px + (self.cols - 1) * self.hgap_px + (self.border_px * 2)
        total_h = self.rows * self.button_height_px + (self.rows - 1) * self.vgap_px + (self.border_px * 2)
        self.root.update_idletasks()
        self.root.geometry(f"{total_w}x{total_h}")

    # Public API
    def run(self) -> None:
        self.root.mainloop()

    def __getitem__(self, rc: Coord) -> Button:
        """Get the button covering logical cell (row, col)."""
        r, c = rc
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            raise IndexError("Row/col out of range.")
        return self._owner_for_cell[(r, c)]

    # Internal helpers
    @staticmethod
    def _compute_spans(labels: LabelMatrix) -> List[Tuple[int, int, int, int, str]]:
        """
        Return a list of rectangles (r, c, rowspan, colspan, caption).
        Adjacent identical labels are merged into one rectangle; must form rectangles.
        """
        rows = len(labels)
        cols = len(labels[0])
        visited = [[False] * cols for _ in range(rows)]
        rects = []

        for r in range(rows):
            for c in range(cols):
                if visited[r][c]:
                    continue
                lab = labels[r][c]
                # compute width
                w = 1
                while c + w < cols and labels[r][c + w] == lab:
                    w += 1
                # compute height with rectangular check
                h = 1
                done = False
                while not done and r + h < rows:
                    for cc in range(c, c + w):
                        if labels[r + h][cc] != lab or visited[r + h][cc]:
                            done = True
                            break
                    if not done:
                        h += 1
                # verify rectangle consistency
                for rr in range(r, r + h):
                    for cc in range(c, c + w):
                        if labels[rr][cc] != lab:
                            raise ValueError("Spans must be solid rectangles of identical labels.")
                        visited[rr][cc] = True
                rects.append((r, c, h, w, lab))
        return rects

    def _build_grid(self, rects: List[Tuple[int, int, int, int, str]]) -> None:
        # Configure spacer columns/rows for exact gaps
        # Logical grid (rows x cols) -> physical grid has 2*rows-1 and 2*cols-1 with spacers in between
        phys_rows = 2 * self.rows - 1 if self.rows > 0 else 0
        phys_cols = 2 * self.cols - 1 if self.cols > 0 else 0

        for pr in range(phys_rows):
            if pr % 2 == 0:
                # button row
                self.grid_frame.grid_rowconfigure(pr, weight=1 if self.resizable else 0, minsize=BUTTON_MIN_HEIGHT)
            else:
                # spacer row
                self.grid_frame.grid_rowconfigure(pr, weight=0, minsize=self.vgap_px)

        for pc in range(phys_cols):
            if pc % 2 == 0:
                self.grid_frame.grid_columnconfigure(pc, weight=1 if self.resizable else 0, minsize=BUTTON_MIN_WIDTH, uniform="btncols" if self.resizable else None)
            else:
                self.grid_frame.grid_columnconfigure(pc, weight=0, minsize=self.hgap_px)

        # Create buttons
        for (r, c, rs, cs, caption) in rects:
            pr = 2 * r
            pc = 2 * c
            prs = (rs - 1) * 2 + 1  # include spacer rows
            pcs = (cs - 1) * 2 + 1  # include spacer cols

            btn_widget = tk.Button(
                self.grid_frame,
                text=caption,
                bg=self.button_bg,
                fg=self.button_fg,
                activebackground=self.button_bg,
                activeforeground=self.button_fg,
                relief=tk.RAISED,
                bd=1,
            )
            btn_widget.grid(row=pr, column=pc, rowspan=prs, columnspan=pcs, sticky="nsew")

            btn = Button(caption=caption, widget=btn_widget)
            self.buttons.append(btn)

            # Map all covered logical cells to this owner button
            for rr in range(r, r + rs):
                for cc in range(c, c + cs):
                    self._owner_for_cell[(rr, cc)] = btn
