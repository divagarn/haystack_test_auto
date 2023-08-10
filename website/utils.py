import paramiko

def check_device_availability(remote_ip, username, password, device_name):
    try:
        # Establish SSH connection to the remote PC
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(remote_ip, username=username, password=password)

        # Run ls command to list devices in /dev folder and check if the specified device is present
        stdin, stdout, stderr = ssh.exec_command(f"ls /dev | grep {device_name}")
        device_output = stdout.read().decode('utf-8')

        if device_name in device_output:
            return True
        else:
            return False

    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your credentials.")
        return False
    except paramiko.SSHException as e:
        print("SSH connection failed:", str(e))
        return False
    except Exception as e:
        print("An error occurred:", str(e))
        return False
    finally:
        ssh.close()
