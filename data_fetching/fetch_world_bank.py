import requests

WORLD_BANK_API_URL = "https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json"
REST_COUNTRIES_API_URL = "https://restcountries.com/v3.1/alpha/{country_code}"

# Dictionary to cache country names
country_name_cache = {}

def get_country_name(country_code):
    """
    Retrieve the full country name for a given ISO country code using REST Countries API.

    :param country_code: The ISO country code (e.g., 'POL' for Poland).
    :return: Full country name (e.g., 'Poland') or the country code if not found.
    """
    if country_code in country_name_cache:
        return country_name_cache[country_code]

    response = requests.get(REST_COUNTRIES_API_URL.format(country_code=country_code), verify=False)
    if response.status_code == 200:
        data = response.json()
        country_name = data[0].get("name", {}).get("common", country_code)
        country_name_cache[country_code] = country_name  # Cache the result
        return country_name

    # If API fails, return the code itself as a fallback
    return country_code

def get_neighboring_country_codes(main_country_code):
    """
    Retrieve a list of neighboring country codes for a given country using the REST Countries API.

    :param main_country_code: The country code for the main country (e.g., 'UA' for Ukraine).
    :return: A list of neighboring country codes.
    """
    response = requests.get(REST_COUNTRIES_API_URL.format(country_code=main_country_code), verify=False)
    if response.status_code == 200:
        data = response.json()
        # Extract the list of neighboring countries' codes
        neighbors = data[0].get("borders", [])
        return neighbors
    return []

def fetch_gender_equality_data(country_code, indicator_code, decimals=2):
    """
    Fetch gender equality metric from the World Bank for a specific country and indicator.

    :param country_code: Country code (e.g., 'UA' for Ukraine)
    :param indicator_code: Indicator code for the metric to fetch
    :param decimals: Number of decimal places to round the returned value
    :return: Tuple containing the latest available value (rounded to 'decimals' places) 
             and the year of that value, or (None, None) if data is unavailable.
    """
    url = WORLD_BANK_API_URL.format(country_code=country_code, indicator_code=indicator_code)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 1 and data[1]:  # Ensure data exists
            for record in data[1]:
                if record['value'] is not None:  # Find the latest non-null value
                    latest_value = round(record['value'], decimals)
                    latest_year = record['date']
                    return latest_value
    return None  # Return None for both if data is unavailable


from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_gender_equality_data_for_neighbors(main_country_code, indicators):
    """
    Fetch gender equality metrics for neighboring countries using threading for faster performance.

    :param main_country_code: The main country's code (e.g., 'UA' for Ukraine)
    :param indicators: Dictionary of indicator codes to fetch
    :return: Dictionary with neighboring country names as keys and their gender equality data as values.
    """
    neighbor_codes = get_neighboring_country_codes(main_country_code)
    neighbor_data = {}

    def fetch_data_for_country_and_indicator(country_code, indicator_key, indicator_code):
        """
        Fetch data for a specific country and indicator.
        :param country_code: ISO code of the country
        :param indicator_key: Key for the indicator in the result dictionary
        :param indicator_code: World Bank indicator code
        :return: Tuple (country_code, indicator_key, fetched_data)
        """
        return country_code, indicator_key, fetch_gender_equality_data(country_code, indicator_code)

    with ThreadPoolExecutor() as executor:
        futures = []

        # Submit all tasks for each neighbor and indicator
        for code in neighbor_codes:
            for key, indicator_code in indicators.items():
                futures.append(executor.submit(fetch_data_for_country_and_indicator, code, key, indicator_code))

        # Collect results as they complete
        for future in as_completed(futures):
            country_code, indicator_key, fetched_data = future.result()

            # Get the country name if not already cached
            country_name = get_country_name(country_code)
            if country_name not in neighbor_data:
                neighbor_data[country_name] = {}

            # Add the fetched data to the correct place
            neighbor_data[country_name][indicator_key] = fetched_data

    # Handle countries with no data (None) by assigning 'N/A'
    for country, metrics in neighbor_data.items():
        for key, value in metrics.items():
            if value is None:
                metrics[key] = "N/A"

    return neighbor_data