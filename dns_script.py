import subprocess
import os

class DnsCheck:
    def __init__(self, domain):
        self.domain = domain
    
    def run_amass(self):
        # Change the current working directory to the directory where this script is located
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        # amass command with the domain as an argument and limit the number of DNS queries to 10
        cmd1 = ['amass', 'enum','-ip','port', 'src','-min-for-recursive', self.domain]
        try:
            output1 = subprocess.check_output(cmd1, stderr=subprocess.STDOUT)
            print(output1.decode('utf-8'))
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.output.decode('utf-8')}")

        # Run the amass intel command with the domain as an argument
        # cmd2 = ['amass', 'intel', '-d', self.domain]
        # try:
        #     output2 = subprocess.check_output(cmd2, stderr=subprocess.STDOUT)
        #     print(output2.decode('utf-8'))
        # except subprocess.CalledProcessError as e:
        #     print(f"Error: {e.output.decode('utf-8')}")

# enter a domain name
domain = input("Enter a domain name: ")

# print the domain name entered by the user
print(f"Scanning subdomains for domain: {domain}")

# create a DnsCheck object and run the Amass commands
dns_check = DnsCheck(domain)
dns_check.run_amass()

