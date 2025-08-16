# ButtonPad

`ButtonPad` is a tiny, pure-standard-library (Tkinter) package that creates a resizable
grid of buttons. Buttons can span rectangular regions (like HTML `rowspan`/`colspan`),
and each button supports `on_click`, `on_enter`, and `on_exit` callbacks as well as
runtime changes to caption and colors.

## Quick start

```bash
python -m buttonpad
```

This runs the phone-keypad demo.

## Usage

```python
from buttonpad import ButtonPad

labels = """1,2,3
4,5,6
7,8,9
*,0,#"""

pad = ButtonPad(
    labels,
    button_width_px=100,
    button_height_px=60,
    hgap_px=8,
    vgap_px=8,
    button_bg="#eeeeee",
    button_fg="#000000",
    window_bg="#f0f0f0",
    title="ButtonPad Demo",
    resizable=True,
)

# Access buttons (top-left owners in row-major order)
for b in pad.buttons:
    b.on_click = lambda btn=b: print("Clicked:", btn.caption)

pad.run()
```

## Spanning example

```
Hello, Hello, 3
Hello, Hello, 6
7, 8, 9
*, 0, #
```

The four `Hello` cells form one 2x2 button.

## License

MIT
