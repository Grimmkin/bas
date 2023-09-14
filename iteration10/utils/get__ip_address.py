# import subprocess

# def get_private_ip_address():
#     command = 'ipconfig'
#     result = subprocess.run(command, capture_output=True, text=True)
#     output = result.stdout

#     # Process the output and extract the private IP address
#     private_ip = extract_private_ip(output)
#     return private_ip

# def extract_private_ip(output):
#     # Parse the output to extract the private IP address
#     # Implement your own logic here based on the format of the output
#     # This is just a basic example assuming a simple format

#     # Splitting the output by lines
#     lines = output.split('\n')

#     for line in lines:
#         if 'IPv4 Address' in line:
#             # Extracting the IP address from the line
#             private_ip = line.split(':')[1].strip()
#             return private_ip

#     return None

# # Usage
# private_ip_address = get_private_ip_address()
# if private_ip_address:
#     print("Private IP Address:", private_ip_address)
# else:
#     print("Unable to retrieve the private IP address.")

import socket
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP