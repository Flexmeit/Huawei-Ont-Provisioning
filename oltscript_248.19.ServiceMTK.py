import time
import re
import paramiko
import random  # Dinamik slot ID seçimi üçün

# SSH client initialization
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connection information
hostname = "172.16.248.19"
username = "py.script"
password = "Almyaa2025"
port = 22

# Dynamic Slot and Port
slot = str(random.choice([0, 1]))  # Slot dinamik seçimi, 0 və 1 arasında
port_number = "14"  # Port nömrəsi bu halda hələ də təyin olunur
vlan = "14"  # VLAN

# Connect to the device
ssh_client.connect(hostname, port, username, password)
connection = ssh_client.invoke_shell()

time.sleep(0.5)
connection.send('enable\n')
time.sleep(0.5)
connection.send('config\n')
time.sleep(0.5)
connection.send('display ont autofind all \n')
time.sleep(2)

router_output = connection.recv(10000).decode("utf-8")
print(router_output)

# Extract SNs and Port Numbers
def extract_sn(output):
    matches = re.findall(r"Ont SN\s*:\s*([A-Fa-f0-9]{16})", output)
    return matches

def extract_port_number(output):
    matches = re.findall(r"F/S/P\s*:\s*\d+/\d+/(\d+)", output)
    return matches

sn_list = extract_sn(router_output)
port_list = extract_port_number(router_output)

if not sn_list or not port_list:
    print("Required data could not be extracted. Exiting.")
    ssh_client.close()
    exit()

print(f"Extracted SNs: {sn_list}")
print(f"Extracted Port Numbers: {port_list}")

# Extract ONT ID
def extract_ont_id(output):
    match = re.search(r"ONTID\s*:\s*(\d+)", output)
    if match:
        return match.group(1)
    else:
        print("ONT ID not found in output!")
        return None

# Send `ont confirm` command for each ONT found
def process_ont(sn, port):
    time.sleep(1)
    connection.send('\n')
    time.sleep(0.5)
    connection.send(f"interface gpon 0/{slot} \n")
    time.sleep(1)
    connection.send('\n')
    connection.recv(5000)

    time.sleep(0.5)
    connection.send(f"ont confirm {port} sn-auth {sn} omci ont-lineprofile-id 10 ont-srvprofile-id 1 desc 'auto_registering'\n")
    time.sleep(2)
    connection.send('\n')
    time.sleep(1)
    confirm_output = connection.recv(10000).decode("utf-8")
    print(confirm_output)

    ont = extract_ont_id(confirm_output)
    if not ont:
        print("ONT ID could not be extracted for SN: " + sn)
        return

    print(f"ONT ID: {ont} for SN: {sn}")

    connection.send("quit\n")
    time.sleep(0.5)
    connection.recv(5000)

    connection.send('\n')
    time.sleep(0.5)
    connection.send(f"service-port vlan {vlan} gpon 0/{slot}/{port} ont {ont} gemport 1 multi-service user-vlan {vlan}\n")
    time.sleep(2)
    connection.send('\n')
    service_output = connection.recv(10000).decode("utf-8")
    print(service_output)

    print(f"Registration completed successfully for SN: {sn} and Port: {port}")

# Process all extracted ONT data
for sn, port in zip(sn_list, port_list):
    print(f"Processing SN: {sn} on Port: {port}")
    process_ont(sn, port)

print("Thank you for your time")



