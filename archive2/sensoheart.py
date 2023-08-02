from sense_hat import SenseHat
import time

sense = SenseHat()

# Set the text color
text_color = (255, 0, 0)  # Red

# Define the duration for each flash
flash_duration = 0.5  # seconds

# Function to display the message with flashing effect
def display_flashing_message(message):
    for _ in range(5):  # Repeat the flash 5 times
        sense.show_message(message, text_colour=text_color)
        time.sleep(flash_duration)
        sense.clear()
        time.sleep(flash_duration)

try:
    while True:
        display_flashing_message("I love you")

except KeyboardInterrupt:
    pass

sense.clear()
