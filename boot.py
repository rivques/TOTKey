import digitalio
import board
import storage

# mount the filesystem if GP10 is high
centerButton = digitalio.DigitalInOut(board.GP10)
centerButton.direction = digitalio.Direction.INPUT
centerButton.pull = digitalio.Pull.UP
if centerButton.value:
    print("Filesystem is NOT writeable by computer")
    storage.remount("/", False)
else:
    print("Filesystem IS writeable by computer")