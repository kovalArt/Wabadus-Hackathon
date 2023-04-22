import subprocess

# Set the domain to scan
domain = "cybers.eu"

# Run the Amass enumeration process and save the results to a file
subprocess.run(["amass", "enum", "-d", domain,"-v" ,"-o", "amass_results.txt"])

# Read the results from the file and print them to the console
with open("amass_results.txt", "r") as f:
    results = f.read()
    print(results)