import time
import psycopg2

# Function to get CPU temperature (same as before)
def get_cpu_temperature():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temperature = float(f.read()) / 1000.0
        return temperature
    except Exception as e:
        print("Error reading CPU temperature: {}".format(e))
        return None

# Function to update temperature in the PostgreSQL database
def update_temperature(home_id, temperature):
    try:
        connection = psycopg2.connect(
            host="opren.cs.csub.edu",
            database="sure",
            user="postgres",
            password="9824"
        )
        cursor = connection.cursor()
        cursor.execute("UPDATE raspi SET temperature = %s WHERE home_id = %s", (temperature, home_id))
        connection.commit()
        connection.close()
    except Exception as e:
        print("Error updating temperature in the database: {}".format(e))

def main():
    try:
        home_id = 1  # Replace this with the appropriate home_id you want to update in the database
        while True:
            temperature = get_cpu_temperature()
            if temperature is not None:
                print("{:.1f}".format(temperature))
                update_temperature(home_id, temperature)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Stopping the temperature recording.")

if __name__ == "__main__":
    main()
