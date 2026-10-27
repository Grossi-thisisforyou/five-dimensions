#!/usr/bin/env bash
# Set up the Raspberry Pi to run stage.py. Run it once, on the Pi, from this folder:
#
#     bash install.sh               # install what stage.py needs
#     bash install.sh --autostart   # ... and start the show when the Pi's desktop starts
#
# Everything comes from Raspberry Pi OS's own packages (apt), nothing from the internet
# beyond that. It asks for your password once, for sudo.
set -euo pipefail
cd "$(dirname "$0")"

echo "== Installing camera, video, window and microphone libraries"
sudo apt-get update
sudo apt-get install -y python3-opencv opencv-data python3-numpy python3-pygame libportaudio2
# The microphone library. If it isn't in apt, stage.py still runs, just without the mic.
sudo apt-get install -y python3-sounddevice || echo "!! python3-sounddevice not found: the show runs without the microphone"

echo "== Making a media folder at ~/media (put one video or image in each of ch1..ch4)"
mkdir -p ~/media/ch1 ~/media/ch2 ~/media/ch3 ~/media/ch4

echo "== Checking"
python3 -c "import cv2, numpy, pygame; print('opencv', cv2.__version__, '| pygame', pygame.version.ver)"
python3 -c "import sounddevice as sd; print(sd.query_devices())" || true
ls /dev/video* 2>/dev/null || echo "!! no camera found yet (plug in a USB camera and check: ls /dev/video*)"

if [[ "${1:-}" == "--autostart" ]]; then
    echo "== Starting the show with the desktop"
    mkdir -p ~/.config/autostart
    cat > ~/.config/autostart/five-dimensions.desktop <<DESKTOP
[Desktop Entry]
Type=Application
Name=Five Dimensions
Exec=python3 $PWD/stage.py --fullscreen --media $HOME/media
DESKTOP
    echo "   Remove ~/.config/autostart/five-dimensions.desktop to stop that."
fi

echo
echo "Done. Try it:  python3 stage.py --media ~/media      (D shows the sensors, Esc quits)"
