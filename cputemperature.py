import time
import psycopg2

def get_cpu_temperature():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temperature = float(f.read()) / 1000.0
        return temperature
    except Exception as e:
        print("Error reading CPU temperature: {}".format(e))
        return None

def update_temperature(home_id, temperature, minute):
    try:
        connection = psycopg2.connect(
            host="opren.cs.csub.edu",
            database="sure",
            user="postgres",
            password="9824"
        )
        cursor = connection.cursor()
        # Add temp_x column if it does not exist
        column_name = f"temp_{minute}"
        cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='raspi' AND column_name=%s", (column_name,))
        result = cursor.fetchone()
        if result is None:
            cursor.execute(f"ALTER TABLE raspi ADD COLUMN {column_name} DOUBLE PRECISION")

        # Update the temp_x column with the temperature
        cursor.execute(f"UPDATE raspi SET {column_name} = %s WHERE home_id = %s", (temperature, home_id))
        connection.commit()
        connection.close()
    except Exception as e:
        print("Error updating temperature in the database: {}".format(e))

def main():
    try:
        home_id = 1
        minute = 1
        total_minutes = 24
        temperatures = []
        start_time = time.time()

        while minute <= total_minutes:
            temperature = get_cpu_temperature()
            if temperature is not None:
                print(f"{minute} minute - Temperature: {temperature:.1f}")
                temperatures.append(temperature)

                if len(temperatures) == 12:  # Every 12 readings (12 * 0.5 seconds = 1 minute)
                    average_temperature = sum(temperatures) / len(temperatures)
                    update_temperature(home_id, average_temperature, minute)
                    temperatures.clear()
                    minute += 1

            time.sleep(0.5)

            # Check if 24 minutes have passed and exit the loop if yes
            elapsed_time = time.time() - start_time
            if elapsed_time >= (total_minutes * 60):
                break

    except KeyboardInterrupt:
        print("Stopping the temperature recording.")

if __name__ == "__main__":
    main()
