import sys
import nmap
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import subprocess
from zapv2 import ZAPv2
import time


class WebApp:

    ports_scanned = []
    ssh_port = 0
    ftp_port = 0
    

    usernames = ['admin', 'root', 'user']
    passwords = ['password1', 'password2', 'password3']

   

    def __init__(self, domain) -> None:
        self.domain = domain
        
    '''---Nmap function--- '''
    #Implement the hydra for the FTP and SSH credentials 

    def nmap(domain, ports):
         # Define the hydra command for SSH brute-force
        ssh_command = f'hydra -l %s -P %s ssh://{domain}:{WebApp.ssh_port}'

        # Define the hydra command for FTP brute-force
        ftp_command = f'hydra -l %s -P %s ftp://{domain}:{WebApp.ftp_port}'

        nm = nmap.PortScanner()
        # ports = '1-1000'

        nm.scan(domain, arguments=f'{ports} -p- -sV -O')

        # Loop through each host that was scanned
        for host in nm.all_hosts():
            
            #Search for the SSH and TCP. Wait for Hydra
            for port in nm[host]['tcp']:
                # Check if the port is open and identify the service
                if nm[host]['tcp'][port]['state'] == 'open':
                    if nm[host]['tcp'][port]['name'] == 'ssh':
                        print('SSH is open on port', port, 'on host', host)
                        WebApp.ssh_port = port

                        #---Hydra SSH---
                        for username in WebApp.usernames:
                            for password in WebApp.passwords:
                                # Execute the SSH brute-force command with the current username and password
                                ssh_process = subprocess.Popen(ssh_command % (username, password), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                ssh_output, ssh_error = ssh_process.communicate()
                                
                                # Check if the SSH password was found
                                if 'password:' in str(ssh_output):
                                    print(f'SSH Password found: {username}:{password}')

                    elif nm[host]['tcp'][port]['name'] == 'ftp':
                        print('FTP is open on port', port, 'on host', host)
                        WebApp.ftp_port = port

                        #---Hydra FTP---
                        for username in WebApp.usernames:
                            for password in WebApp.passwords:
                                ftp_process = subprocess.Popen(ftp_command % (username, password), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                ftp_output, ftp_error = ftp_process.communicate()
                                
                                # Check if the FTP password was found
                                if 'password:' in str(ftp_output):
                                    print(f'FTP Password found: {username}:{password}')


            
            for host in nm.all_hosts():
                print('----------------------------------------------------')
                print('Host : %s (%s)' % (host, nm[host].hostname()))
                print('State : %s' % nm[host].state())
                for proto in nm[host].all_protocols():
                    print('----------')
                    print('Protocol : %s' % proto)
            
                    lport = nm[host][proto].keys()
                    
                    for port in lport:
                        print ('port : %s\tstate : %s' % (port, nm[host][proto][port]['state']))
                        port_scanned = {'port': port, 'status': nm[host][proto][port]['state']}
                        WebApp.ports_scanned.append(port_scanned)
                        
            print(WebApp.ports_scanned)
            
            # if 'osmatch' in nm[host]:
            #     for osmatch in nm[host]['osmatch']:
            #         print("=============")
            #         print('Os match name : %s' % osmatch['name'])
            #         print('Accuracy : %s' % osmatch['accuracy'])
            #         print('Line : %s' % osmatch['line'])
            #         print("=============")


            #     if 'osclass' in nm[host]:
            #         for osclass in nm[host]['osclass']:
            #             print("=============")

            #             print('Os class type : %s' % osclass['type'])
            #             print('Vendor : %s' % osclass['vendor'])
            #             print('Os family : %s' % osclass['osfamily'])
            #             print('Os gen : %s' % osclass['osgen'])
            #             print('Accuracy : %s' % osclass['accuracy'])

            #             print("=============")

    def owasp_zap(domain):
        zap = ZAPv2(proxies={'http': 'http://localhost:8080', 'https': 'http://localhost:8080'})
        zap.spider.scan(domain)
        while (int(zap.spider.status()) < 100):
            print('Spider progress %: ' + zap.spider.status())
            time.sleep(5)
        
        zap.ascan.scan(domain)
        while (int(zap.ascan.status()) < 100):
            print('Scan progress %: ' + zap.ascan.status())
            time.sleep(5)

        alerts = zap.core.alerts()

        # Print the alerts
        for alert in alerts:
            print(alert)
                
    
    # def xss_attack():
    #     # Set up a Selenium webdriver instance with headless mode
    #     chrome_options = Options()
    #     chrome_options.add_argument("--headless")
    #     driver = webdriver.Chrome(options=chrome_options)

    #     # Navigate to the login page of the web application you want to test
    #     driver.get("https://example.com/login")

    #     # Find the input field where you want to inject the payload
    #     input_field = driver.find_element("username")

    #     # Inject a simple XSS payload into the input field
    #     payload = "<script>alert('XSS!');</script>"
    #     input_field.send_keys(payload)

    #     # Submit the form and see if the payload is executed
    #     submit_button = driver.find_element("submit")
    #     submit_button.click()

    #     # Check if the payload was executed
    #     if "XSS!" in driver.page_source:
    #         print("XSS vulnerability detected!")
    #     else:
    #         print("XSS vulnerability not detected.")

    

# Check if parameter is passed through command line

if __name__ == "__main__":

    if len(sys.argv) > 1:
        domain = sys.argv[1]
        print("The domain is: ", domain)
        # nmap_ports = input("Enter the ports for the scan (format x-xxx): ")

        WebApp = WebApp
        # WebApp.nmap(domain, nmap_ports)
        # WebApp.xss_attack()
        WebApp.owasp_zap(domain)

    else:
        print("Enter the domain name")