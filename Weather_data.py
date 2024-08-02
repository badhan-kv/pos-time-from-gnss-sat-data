import requests
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
from xyz_lla import xyz2lla


def convert_to_local_time(epoch_time_str, latitude, longitude):
    # Parse the input string into a datetime object
    utc_time = datetime.strptime(epoch_time_str, '%Y-%m-%d %H:%M:%S')

    # Set the timezone to UTC
    utc_time = utc_time.replace(tzinfo=pytz.utc)

    # Determine the local timezone from the coordinates
    tf = TimezoneFinder()
    local_tz_name = tf.timezone_at(lat=latitude, lng=longitude)
    if not local_tz_name:
        return "Timezone could not be determined from the coordinates"

    local_tz = pytz.timezone(local_tz_name)

    # Convert to local timezone
    local_time = utc_time.astimezone(local_tz)

    # Return the formatted time string
    return local_time.strftime('%Y-%m-%dT%H:%M:%S')


def get_weather_data(api_key, latitude, longitude, local_time):
    """
    Fetch weather data (humidity, temperature, pressure) for a given location and datetime.

    :param api_key: API key for Visual Crossing Weather API.
    :param latitude: Latitude of the location.
    :param longitude: Longitude of the location.
    :param datetime_str: Datetime as a string in YYYY-MM-DDTHH:MM:SS format.
    :return: A dictionary containing humidity, temperature, and pressure.
    """
    base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
    location = f"{latitude},{longitude}"
    url = f"{base_url}{location}/{local_time}?unitGroup=metric&key={api_key}&include=current"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        current_conditions = data.get('currentConditions', {})
        humidity = current_conditions.get('humidity', None)
        temp = current_conditions.get('temp', None)
        pressure = current_conditions.get('pressure', None)
        return {
            'humidity': humidity,
            'temperature': temp,
            'pressure': pressure
        }
    else:
        print(f"Error fetching weather data: {response.status_code}")
        return None


def main():
    # Example usage
    x, y, z = 4032241.29, 306056.35, 4919033.44  # Replace with your ECEF coordinates
    lat, lon, alt = xyz2lla(x, y, z)
    epoch_time = '2023-04-10 13:15:00'
    location = f"{lat},{lon}"
    latitude = float(f"{lat}")  # Example latitude for Luxembourg
    longitude = float(f"{lon}")  # Example longitude for Luxembourg
    local_time = convert_to_local_time(epoch_time, latitude, longitude)
    api_key = 'YBCMMAGSU8YPFWHQBUU2PAAAL'
    weather_data = get_weather_data(api_key, latitude, longitude, local_time)
    print(local_time)
    print (location)
    print(weather_data)

if __name__ == '__main__':
    main()