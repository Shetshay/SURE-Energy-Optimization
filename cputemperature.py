from __future__ import division
import time
import psycopg2
from adafruit_motorkit import MotorKit

def get_cpu_temperature():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temperature = float(f.read()) / 1000.0
        return temperature
    except Exception as e:
        print("Error reading CPU temperature:", e)
        return None

def update_temperature(home_id, temperature, minute):
    # (Same as before, no changes needed)
    pass

def turn_on_fan():
    kit = MotorKit()
    kit.motor1.throttle = 1  # Turn on the fan at full speed

def turn_off_fan():
    kit = MotorKit()
    kit.motor1.throttle = 0  # Turn off the fan

def main():
    try:
        home_id = 1
        minute = 1
        total_minutes = 24
        temperatures = []
        fan_on_time = 0  # Variable to store the total time the fan is on (in seconds)

        start_time = time.time()

        while minute <= total_minutes:
            temperature = get_cpu_temperature()
            if temperature is not None:
                current_time = time.strftime("%H:%M:%S")  # Get the current time
                remaining_seconds = (total_minutes * 60) - (minute * 60)  # Calculate time remaining in seconds

                print("{} minute - Time: {} - Temperature: {:.1f}C - Time Remaining: {} seconds".format(minute, current_time, temperature, remaining_seconds))
                temperatures.append(temperature)

                # Check if the fan needs to be turned on
                if temperature > 50:
                    turn_on_fan()
                    fan_on_time += 1  # Increment fan_on_time by 1 second
                else:
                    turn_off_fan()

                if len(temperatures) == 60:  # Every 60 readings (60 seconds = 1 minute)
                    average_temperature = sum(temperatures) / len(temperatures)
                    update_temperature(home_id, average_temperature, minute)
                    temperatures = []
                    minute += 1

            time.sleep(1)  # Sleep for 1 second instead of 0.5 seconds

            # Check if 24 minutes have passed and exit the loop if yes
            elapsed_time = time.time() - start_time
            if elapsed_time >= (total_minutes * 60):
                break

        # Print the total time the fan was on after the 24-minute run
        print("Total fan-on time: {} seconds".format(fan_on_time))

    except KeyboardInterrupt:
        print("Stopping the temperature recording.")

    # Make sure to turn off the fan when the program ends
    turn_off_fan()

if __name__ == "__main__":
    main()
