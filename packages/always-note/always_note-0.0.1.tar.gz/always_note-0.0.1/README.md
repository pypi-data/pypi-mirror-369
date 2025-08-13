# Always note

A note that is always on the screen.

I use it in workshops and presentations when I want to always display some information on the screen.

![Always note](docs/note.png)

The text will automatically scale to the size of the note window.

You can modify the color and font by right-clicking on the window.

## Install

```bash
pip install always_note
```

## Usage

Run:

```bash
always_note
```

Specify the text:

```bash
always_note -t "Your note here"
```

Get help:

```bash
always_note --help
```

## Development

To run the code for development, clone the repository, and install the package in editable mode:

```bash
git clone https://github.com/martinohanlon/always_note
cd always_note
pip install -e .
```

Then run always_note:

```bash
python run.py --text "Your note here"
```

## Build

Install the build tools:

```bash
pip install setuptools[core]
pip install build
```

To build the package, run:

```bash
python -m build
```

## Status

Beta - Working. A bit "cobbled together". I use it tho!

## Change log

- no releases yet