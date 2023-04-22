import sys
import nmap
import subprocess
from zapv2 import ZAPv2
import time
import requests 


class WebScanner:

    ports_scanned = []
    ssh_port = 0
    ftp_port = 0
    web_dirs = []
    xss_vulnr = []
    sqli_vulnr = []

    usernames = open("../wordlists/usernames.txt", "r")
    passwords = open("../wordlists/passwords.txt", "r")


    def __init__(self, domain) -> None:
        self.domain = domain
        
    '''---Nmap function Implement the hydra for the FTP and SSH credentials with SSL Certificates---'''


    def nmap_hydra_ssl(domain, ports):
         # Define the hydra command for SSH brute-force
        ssh_command = f'hydra -l %s -P %s ssh://{domain}:{WebScanner.ssh_port}'

        # Define the hydra command for FTP brute-force
        ftp_command = f'hydra -l %s -P %s ftp://{domain}:{WebScanner.ftp_port}'

        nm = nmap.PortScanner()
        # ports = '1-1000'

        nm.scan(domain, arguments=f'{ports} -p- --script ssl-enum-ciphers -sV -O')

        # Loop through each host that was scanned
        for host in nm.all_hosts():
            
            #Search for the SSH and TCP. Wait for Hydra
            for port in nm[host]['tcp']:
                # Check if the port is open and identify the service
                if nm[host]['tcp'][port]['state'] == 'open':
                    if nm[host]['tcp'][port]['name'] == 'ssh':
                        print('SSH is open on port', port, 'on host', host)
                        WebScanner.ssh_port = port

                        #---Hydra SSH---
                        for username in WebScanner.usernames:
                            for password in WebScanner.passwords:
                                # Execute the SSH brute-force command with the current username and password
                                ssh_process = subprocess.Popen(ssh_command % (username, password), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                ssh_output, ssh_error = ssh_process.communicate()
                                
                                # Check if the SSH password was found
                                if 'password:' in str(ssh_output):
                                    print(f'SSH Password found: {username}:{password}')

                    elif nm[host]['tcp'][port]['name'] == 'ftp':
                        print('FTP is open on port', port, 'on host', host)
                        WebScanner.ftp_port = port

                        #---Hydra FTP---
                        for username in WebScanner.usernames:
                            for password in WebScanner.passwords:
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
                        WebScanner.ports_scanned.append(port_scanned)
                        
            print(WebScanner.ports_scanned)
            
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

    def get_dirs(self):
        try: 
            zap = ZAPv2()
            scanner = zap.spider.scan(self.domain)
            while (int(zap.spider.status(scanner)) < 100):
                time.sleep(1)
            self.web_dirs = zap.spider.results(scanner)
            return self.web_dirs
        except Exception as ex:
            raise ex

    def xss_payloads_check(self, target_url):
        base_url = 'http://localhost:8080/'

        payload = '<script>alert("XSS Vulnerability Found!");</script>'

        # Set up the ZAP API endpoints for the spider and active scan
        spider_url = base_url + '/JSON/spider/action/scan/?url=' + target_url
        scan_url = base_url + '/JSON/ascan/action/scan/?url=' + target_url

        response = requests.get(base_url + '/JSON/core/newSession/')
        session_id = response.json()['session']

        # Configure the ZAP spider to crawl the target URL
        response = requests.get(spider_url)
        scan_id = response.json()['scan']

        # Wait for the spider to complete
        while (True):
            response = requests.get(base_url + '/JSON/spider/view/status/?scanId=' + str(scan_id))
            status = response.json()['status']
            if (status == '100'):
                break

        # Configure the ZAP active scanner to scan the target URL for XSS vulnerabilities
        response = requests.get(scan_url)
        scan_id = response.json()['scan']

        # Wait for the scan to complete
        while (True):
            response = requests.get(base_url + '/JSON/ascan/view/status/?scanId=' + str(scan_id))
            status = response.json()['status']
            if (status == '100'):
                break

        # Retrieve the ZAP alerts for the session and print any XSS vulnerabilities found
        response = requests.get(base_url + '/JSON/core/alert/view/alerts/?baseurl=' + target_url)
        alerts = response.json()
        for alert in alerts:
            if (alert['risk'] == 'High' and alert['alert'] == 'XSS'):
                print('XSS Vulnerability Found: ' + alert['url'])

    def sqli_check(self):
        pass
