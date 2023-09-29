import digitalio
import board
import storage

# mount the filesystem if GP10 is high
centerButton = digitalio.DigitalInOut(board.GP10)
centerButton.direction = digitalio.Direction.INPUT
centerButton.pull = digitalio.Pull.UP
if centerButton.value:
    storage.remount("/", False)