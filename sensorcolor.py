from sense_hat import SenseHat
import time

sense = SenseHat()

# Define the starting and ending colors for the gradient
green_color = (0, 255, 0)  # Green
orange_color = (255, 165, 0)  # Orange
red_color = (255, 0, 0)  # Red

# Calculate the color gradient between green and orange
gradient_green_orange = []
steps = 32
for i in range(steps):
    r = int(green_color[0] + (orange_color[0] - green_color[0]) * i / steps)
    g = int(green_color[1] + (orange_color[1] - green_color[1]) * i / steps)
    b = int(green_color[2] + (orange_color[2] - green_color[2]) * i / steps)
    gradient_green_orange.append((r, g, b))

# Calculate the color gradient between orange and red
gradient_orange_red = []
for i in range(steps):
    r = int(orange_color[0] + (red_color[0] - orange_color[0]) * i / steps)
    g = int(orange_color[1] + (red_color[1] - orange_color[1]) * i / steps)
    b = int(orange_color[2] + (red_color[2] - orange_color[2]) * i / steps)
    gradient_orange_red.append((r, g, b))

# Function to get the CPU temperature
def get_cpu_temperature():
    res = None
    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
        res = f.read()
    if res:
        temp = float(res) / 1000.0
        return temp
    return None

# Function to display the color gradient based on CPU temperature
def display_gradient_based_on_temperature():
    cpu_temp = get_cpu_temperature()

    if cpu_temp is not None:
        if cpu_temp <= 70:
            sense.clear(green_color)
        elif cpu_temp <= 75:
            gradient_index = int((cpu_temp - 75) * (steps / 5))
            color = gradient_green_orange[gradient_index]
            sense.clear(color)
        else:
            gradient_index = int((cpu_temp - 80) * (steps / 5))
            color = gradient_orange_red[gradient_index]
            sense.clear(color)

try:
    while True:
        display_gradient_based_on_temperature()

except KeyboardInterrupt:
    pass

sense.clear()
