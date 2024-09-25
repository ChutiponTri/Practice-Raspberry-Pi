import math

def estimate_distance(rssi, reference_rssi, n):
    # Calculate estimated distance in meters
    distance = 10 ** ((reference_rssi - rssi) / (10 * n))
    return distance

# Example parameters (to be adjusted based on calibration and environment)
reference_rssi = -80  # RSSI at 1 meter (example reference distance)
n = 2.0  # Path loss exponent (example value, typically ranges from 2 to 4)

# Example usage
measured_rssi = -90  # Example measured RSSI
estimated_distance = estimate_distance(measured_rssi, reference_rssi, n)
print(f"Estimated distance: {estimated_distance:.2f} meters")
