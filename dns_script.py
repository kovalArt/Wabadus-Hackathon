import subprocess

url = input("Enter a domain name: ")

result = subprocess.run(["sh", "./test.sh", url], stdout=subprocess.PIPE)
            
decoded = result.stdout.decode('utf-8')
print(decoded)
