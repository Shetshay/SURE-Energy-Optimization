from __future__ import division
import time
import psycopg2
from adafruit_motorkit import MotorKit
import matplotlib.pyplot as plt

def get_cpu_temperature():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temperature = round(float(f.read()) / 1000.0, 2)  # Round to 2 decimal places
        return temperature
    except Exception as e:
        print("Error reading CPU temperature:", e)
        return None

def update_temperature(data, temperature, fan_on_time, minute):
    try:
        connection = psycopg2.connect(
            host="opren.cs.csub.edu",
            database="sure",
            user="postgres",
            password="9824"
        )
        cursor = connection.cursor()

        # Check if the data row exists in the database
        cursor.execute("SELECT * FROM raspi WHERE data_ = %s", (data,))
        result = cursor.fetchone()

        if result is None:
            # Insert a new row for the given data
            cursor.execute("INSERT INTO raspi (data_) VALUES (%s)", (data,))
            connection.commit()

        # Update the temperature, fan_on_time, and cost for the given minute
        column_name_temp = f"temp_{minute}"
        cursor.execute(f"ALTER TABLE raspi ADD COLUMN IF NOT EXISTS {column_name_temp} DOUBLE PRECISION")
        cursor.execute(f"UPDATE raspi SET {column_name_temp} = %s WHERE data_ = %s", (temperature, data))

        column_name_fan = f"fan_{minute}"
        cursor.execute(f"ALTER TABLE raspi ADD COLUMN IF NOT EXISTS {column_name_fan} DOUBLE PRECISION")
        cursor.execute(f"UPDATE raspi SET {column_name_fan} = %s WHERE data_ = %s", (fan_on_time, data))

        column_name_cost = f"cost_{minute}"
        cursor.execute(f"ALTER TABLE raspi ADD COLUMN IF NOT EXISTS {column_name_cost} DOUBLE PRECISION")
        cursor.execute(f"UPDATE raspi SET {column_name_cost} = %s WHERE data_ = %s", (fan_on_time * 0.1, data))  # Replace 0.1 with the actual cost calculation formula

        connection.commit()

        connection.close()
    except Exception as e:
        print("Error updating data in the database:", e)

def turn_on_fan(kit):
    kit.motor1.throttle = 1  # Turn on the fan at full speed

def turn_off_fan(kit):
    kit.motor1.throttle = 0  # Turn off the fan

def plot_live_data(x_data, y_data):
    plt.clf()
    plt.plot(x_data, y_data, marker='o')
    plt.xlabel('Time (seconds)')
    plt.ylabel('CPU Temperature (Celsius)')
    plt.title('CPU Temperature vs. Time')
    plt.grid(True)
    plt.pause(0.01)

def main():
    try:
        kit = MotorKit()  # Define the 'kit' object at the beginning of the main() function
        data = 1  # Single row for all data
        minute = 1
        total_minutes = 24
        temperatures = []
        fan_on_time = 0  # Variable to store the total time the fan is on (in seconds)
        x_data = []
        y_data = []

        start_time = time.time()

        plt.ion()  # Turn on interactive mode for live plotting

        while minute <= total_minutes:
            temperature = get_cpu_temperature()
            if temperature is not None:
                elapsed_seconds = int(time.time() - start_time)  # Elapsed time in seconds
                remaining_seconds = (total_minutes * 60) - elapsed_seconds  # Calculate time remaining in seconds

                print("{} minute - Elapsed Time: {} seconds - Temperature: {:.2f}C - Time Remaining: {} seconds".format(minute, elapsed_seconds, temperature, remaining_seconds))
                temperatures.append(temperature)
                x_data.append(elapsed_seconds)  # Use elapsed time as the x-coordinate
                y_data.append(temperature)

                plot_live_data(x_data, y_data)  # Plot live data

                # Check if the fan needs to be turned on
                if temperature >= 50:  # Change the threshold value to 50 degrees Celsius
                    turn_on_fan(kit)
                    fan_on_time += 1  # Increment fan_on_time by 1 second
                else:
                    turn_off_fan(kit)

                if len(temperatures) == 60:  # Every 60 readings (60 seconds = 1 minute)
                    average_temperature = round(sum(temperatures) / len(temperatures), 2)  # Round to 2 decimal places
                    update_temperature(data, average_temperature, fan_on_time, minute)  # Update data for minute
                    temperatures = []
                    minute += 1
                    fan_on_time = 0  # Reset fan_on_time for the next minute

            time.sleep(1)  # Sleep for 1 second instead of 0.5 seconds

            # Increment fan_on_time when the fan is on
            if kit.motor1.throttle > 0:
                fan_on_time += 1

        # Print the total time the fan was on after the 24-minute run
        print("Total fan-on time: {} seconds".format(fan_on_time))

    except KeyboardInterrupt:
        print("Stopping the temperature recording.")

    # Make sure to turn off the fan when the program ends
    turn_off_fan(kit)

if __name__ == "__main__":
    main()

