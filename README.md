# Matrix Wallpaper

A live "digital rain" wallpaper. Green characters fall down the screen in a seamless loop.

`generate.py` renders the animation to `matrix.mp4`. Any live wallpaper tool that plays a video can use the file.

## Generate the video

Requirements: [uv](https://docs.astral.sh/uv/), `ffmpeg`, and a monospace font.

```bash
uv run generate.py -o matrix.mp4
```

Useful options (run `uv run generate.py --help` for all):

- `--width`, `--height`: video size. Use the resolution of one monitor.
- `--cell`: glyph size in pixels.
- `--seconds`: loop length.
- `--drops`: drops per column (rain density).
- `--color`: rain colour as hex RGB, for example `00ff46`.
- `--font`: path to the font file. The default is DejaVu Sans Mono on Ubuntu.

The script checks that the last frame matches the first frame, so the loop has no visible jump.

## Ubuntu (GNOME, Wayland or X11)

Use the [Hanabi](https://github.com/jeffshee/gnome-ext-hanabi) extension.

1. Install the GTK4 video sink:

   ```bash
   sudo apt install gstreamer1.0-gtk4
   ```

2. Install Hanabi. Use the `javascript` branch for GNOME 45 to 50, and `main` for GNOME 50 and later:

   ```bash
   git clone -b javascript https://github.com/jeffshee/gnome-ext-hanabi.git
   make -C gnome-ext-hanabi install
   ```

3. Log out and log in again.
4. Enable the extension and set the video:

   ```bash
   gnome-extensions enable hanabi-extension@jeffshee.github.io
   gsettings --schemadir ~/.local/share/glib-2.0/schemas set io.github.jeffshee.hanabi-extension video-path "$PWD/matrix.mp4"
   gsettings --schemadir ~/.local/share/glib-2.0/schemas set io.github.jeffshee.hanabi-extension mute true
   ```

## Windows

Use [Lively Wallpaper](https://www.rocksdanister.com/lively/) (free) or Wallpaper Engine. Drag `matrix.mp4` into the app.

## macOS

Use a video wallpaper app and select `matrix.mp4`.
