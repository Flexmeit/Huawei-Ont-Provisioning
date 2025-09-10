import paramiko
import time

# SSH üçün istifadəçi məlumatları
username = "zamin"
password = "qa10w"

# Əlavə ediləcək yeni istifadəçi
new_user = "f"
new_password = "Fl3x4770"

# Switch siyahısını oxuyuruq
with open("switches.txt", "r") as f:
    switches = [line.strip() for line in f if line.strip()]

for ip in switches:
    print(f"\n[+] Connecting to {ip}")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, look_for_keys=False, allow_agent=False)

        try:
            shell = ssh.invoke_shell()
        except Exception as e:
            print(f"[✗] Couldn't open shell on {ip}: {e}")
            ssh.close()
            continue

        # Komandaları göndər
        commands = [
            "enable\n",
            "configure terminal\n",
            f"username {new_user} privilege 15 secret {new_password}\n",
            "end\n",
            "write memory\n",
            "exit\n"
        ]

        for cmd in commands:
            shell.send(cmd)
            time.sleep(0.5)  # bir az gözləyir
            output = shell.recv(1000).decode()
            # print(output)  # cavabı görmək istəsən

        ssh.close()
        print(f"[✓] User added on {ip}")

    except Exception as e:
        print(f"[✗] Failed to connect to {ip}: {e}")
