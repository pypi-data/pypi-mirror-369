from .note import Note

description = """Always-on note.

A simple application to always display a note.
Super useful for presentations, when you need a reminder on the screen.

Right-click to open the settings.
"""

def main():
    
    from argparse import ArgumentParser

    parser = ArgumentParser(description=description)
    parser.add_argument("-t", "--text")
    args = parser.parse_args()

    Note(**vars(args)).display()
