import requests
import pybreaker

# Create a circuit breaker instance
circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=3,          # after 3 failures -> open circuit
    reset_timeout=10     # try again after 10 seconds
)

@circuit_breaker
def safe_request(method, url, **kwargs):
    """Wrap requests with a circuit breaker."""
    response = requests.request(method, url, **kwargs)
    response.raise_for_status()
    return response
