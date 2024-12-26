from cryptography.fernet import Fernet
import requests

def decrypt_url():
  """
  Decrypts the URL stored in the encrypted file.
  """
  with open("secret.key", "rb") as key_file:
    key = key_file.read()

  f = Fernet(key)
  with open("url.data", "rb") as encrypted_file:
    encrypted_url = encrypted_file.read()

  decrypted_url = f.decrypt(encrypted_url).decode()
  return decrypted_url

def connectivity_test(service_url):
  try:
    health_url = service_url + '/health'
    response = requests.get(health_url)
    response.raise_for_status()
    return True
  except requests.exceptions.ConnectionError:
    print("Error: Could not connect to the service. Please check the network connectivity and try again.")
    return False
  except requests.exceptions.Timeout:
    print("Error: Connection timed out. The service might be unavailable or overloaded.")
    return False
  except requests.exceptions.HTTPError:
    print("Error: The service returned an error. Please check the service status.")
    return False
  except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    return False
