import subprocess
import time
import requests

#                                                              Globally used

# Set the target URL and port
target_url = "https://example.com"

# Read in usernames from file
with open("../wordlists/usernames.txt", "r") as f:
    usernames = [line.strip() for line in f]

# Read in passwords from file
with open("../wordlists/passwords.txt", "r") as f:
    passwords = [line.strip() for line in f]

# Set the Burp Suite path and command to start it in headless mode
burp_path = "/path/to/burp.jar"
burp_command = ["java", "-jar", burp_path, "--collaborator-server=burp-collaborator.example.com", "--config-file=burp_config.json", "--project-file=burp_project.burp", "--headless"]

# Start Burp Suite in headless mode
burp_process = subprocess.Popen(burp_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Wait for Burp Suite to start up and initialize
time.sleep(10)

# Set the Burp Suite proxy address and port
proxy_address = "127.0.0.1"
proxy_port = "8080"

# Set the target URL to include the Burp Suite proxy address and port
target_url = f"http://{proxy_address}:{proxy_port}/{target_url}"

# Send a request to the target URL to trigger the 2FA mechanism
response = requests.get(target_url)

# Extract the time-based code from the response
# Assumes the code is in a format like "123456"
code = response.text.strip()

#                                                         Time-based code issues

# Generate a time-based code using pyotp
# Assumes the code is generated using the TOTP algorithm with a shared secret key
# Replace the "shared_secret" value with the actual shared secret for the target application
import pyotp
totp = pyotp.TOTP("shared_secret")
generated_code = totp.now()

# Compare the generated code with the extracted code
if code == generated_code:
    output = "Time-based code is valid\n"
else:
    output = "Time-based code is invalid\n"

#                                                               Code reuse

# Loop through the list of usernames
for username in usernames:

    # Send a login request to the target URL with the username
    # Assumes the login page is at a path like "/login"
    # Assumes the login form has fields for "username" and "password"
    data = {"username": username, "password": password}
    response = requests.post(f"{target_url}/login", data=data, proxies={"http": f"http://{proxy_address}:{proxy_port}", "https": f"http://{proxy_address}:{proxy_port}"})

    # Check if the response indicates that 2FA is required
    if "2FA" in response.text:

        # Send a second login request with the username and token
        # Assumes the 2FA form has fields for "username" and "token"
        data = {"username": username, "token": code}
        response = requests.post(f"{target_url}/2fa", data=data, proxies={"http": f"http://{proxy_address}:{proxy_port}", "https": f"http://{proxy_address}:{proxy_port}"})

        # Check if the response indicates that the login was successful
        if "logged in" in response.text:
            output += f"Code reuse vulnerability detected for username '{username}'\n"
        else:
            output += f"No code reuse vulnerability detected for username '{username}'\n"

#                                                       Vulnerable 2FA implementation

# Send a request with a crafted token to test for a vulnerable implementation
# Assumes the vulnerable implementation allows tokens to be used multiple times
crafted_token = code
response = requests.get(f"{target_url}/login?2fa_token={crafted_token}")

# Check if the response indicates successful authentication
# Assumes a successful authentication response contains the text "Welcome"
if "Welcome" in response.text:
    output += "Vulnerable 2FA implementation detected\n"
else:
    output += "2FA mechanism appears to be secure\n"

#                                             Stop the Burp Suite process and write to log file

# Stop the Burp Suite process
burp_process.terminate()

# Write the results to a log file
with open("output.txt", "w") as f:
    f.write("Results of 2fa test:\n")
    f.write(output, "\n\n")
