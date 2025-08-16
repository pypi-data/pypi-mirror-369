from .pad import ButtonPad

def main():
    labels = """1,2,3
4,5,6
7,8,9
*,0,#"""
    pad = ButtonPad(labels, title="ButtonPad Phone Demo")
    # Simple demo: print which button is clicked
    for b in pad.buttons:
        b.on_click = lambda btn=b: print("Clicked:", btn.caption)
    pad.run()

if __name__ == "__main__":
    main()
