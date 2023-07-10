import time
import os
import subprocess

# Command to start stress-ng
stress_command = "stress-ng --cpu 4 --timeout 0s"
stress_process = None

# Temperature thresholds
stop_threshold = 77
resume_threshold = 70

# File and interval settings
filename = "temperaturereadings.txt"
duration = 1800  # 30 minutes (in seconds)
interval = 0.5  # 0.5 seconds

start_time = time.time()
end_time = start_time + duration

paused = False
paused_duration = 0

def set_sensor_color(color):
    # Set the color on the sensor screen
    # Replace this with the code to set the color on your specific sensor
    pass

with open(filename, "w") as file:
    while time.time() < end_time:
        # Execute vcgencmd measure_temp command
        temperature_output = os.popen('vcgencmd measure_temp').readline()
        
        # Extract temperature value
        temperature = float(temperature_output.strip().split("=")[1].split("'")[0])
        
        # Check temperature and control stress-ng
        if temperature >= stop_threshold:
            if stress_process is not None:
                stress_process.terminate()
                stress_process = None
            paused = True
            paused_duration += time.time() - start_time
        elif temperature <= resume_threshold and paused:
            if stress_process is None:
                stress_process = subprocess.Popen(stress_command, shell=True)
            start_time = time.time() - paused_duration
            paused = False
        elif temperature <= resume_threshold and stress_process is None:
            if stress_process is None:
                stress_process = subprocess.Popen(stress_command, shell=True)
        
        # Write temperature to file
        file.write("{:.1f}\n".format(temperature))
        file.flush()  # Flush the buffer to ensure immediate write
        
        # Display temperature on command prompt
        print("Current Temperature: {:.1f}".format(temperature))
        
        # Set sensor screen color based on temperature
        if temperature <= resume_threshold:
            set_sensor_color((0, 255, 0))  # Set color to green
        else:
            set_sensor_color((255, 255, 255))  # Set color to white
        
        # Wait for the specified interval
        time.sleep(interval)

# Stop stress-ng if it is still running
if stress_process is not None:
    stress_process.terminate()

# Read the temperature file and calculate average temperature
readings = []
with open(filename, "r") as file:
    for line in file:
        # Extract the temperature value from the line
        temperature = float(line.strip())
        readings.append(temperature)

# Calculate average temperature
average_temperature = sum(readings) / len(readings)

# Display average temperature
print("Average Temperature: {:.1f}".format(average_temperature))
