import time
import subprocess
import board
from adafruit_motorkit import MotorKit

# Command to start stress-ng
stress_command = "stress-ng --cpu 4 --timeout 0s"
stress_process = None

# Temperature thresholds and fan control settings
fan_on_threshold = 74
throttle_1_threshold = 75
throttle_1_value = 1.0
throttle_2_value = 0.5

# File and interval settings
filename = "temperature_readings.txt"
duration = 1800  # 30 minutes (in seconds)
interval = 0.5  # 0.5 seconds

start_time = time.time()
end_time = start_time + duration

throttle = None

kit = MotorKit(i2c=board.I2C())
kit.motor1.throttle = 1.0

def turn_off_fan():
    # Turn off the fan by setting throttle to 0
    kit.motor1.throttle = 0

def get_colored_temperature(temperature):
    if temperature >= 79:
        return "\033[91m{}\033[0m".format(temperature)  # Red
    elif temperature >= 76:
        return "\033[93m{}\033[0m".format(temperature)  # Yellow
    elif temperature >= 75:
        return "\033[92m{}\033[0m".format(temperature)  # Green
    else:
        return str(temperature)

with open(filename, "w") as file:
    # Start stress-ng command
    stress_process = subprocess.Popen(stress_command, shell=True)
    
    try:
        while time.time() < end_time:
            # Execute vcgencmd measure_temp command
            temperature_output = subprocess.check_output(['vcgencmd', 'measure_temp']).decode('utf-8')
            
            # Extract temperature value
            temperature = float(temperature_output.strip().split("=")[1].split("'")[0])
            
            # Check temperature and control fan and throttle
            if temperature >= fan_on_threshold and throttle != throttle_1_value:
                throttle = throttle_1_value
                kit.motor1.throttle = throttle
                print("Throttle: {:.1f}".format(throttle))
            elif temperature < fan_on_threshold and throttle != throttle_2_value:
                throttle = throttle_2_value
                kit.motor1.throttle = throttle
                print("Throttle: {:.1f}".format(throttle))
            
            # Write temperature and throttle status to file
            file.write("{:.3f}, {:.1f}\n".format(temperature, throttle))
            file.flush()  # Flush the buffer to ensure immediate write
            
            # Display temperature on command prompt
            colored_temperature = get_colored_temperature(temperature)
            print("Current Temperature: {}".format(colored_temperature))
            
            # Wait for the specified interval
            time.sleep(interval)

    except KeyboardInterrupt:
        # Program stopped abruptly, turn off the fan
        turn_off_fan()

# Stop stress-ng after the duration
if stress_process is not None:
    stress_process.terminate()

# Read the temperature file and calculate average temperature
readings = []
with open(filename, "r") as file:
    for line in file:
        # Extract the temperature and throttle values from the line
        temperature, throttle = line.strip().split(", ")
        readings.append(float(temperature))

# Calculate average temperature
average_temperature = sum(readings) / len(readings)

# Display average temperature (rounded to 2 decimal places)
rounded_average_temperature = round(average_temperature, 2)
print("Average Temperature: {:.3f}".format(rounded_average_temperature))
