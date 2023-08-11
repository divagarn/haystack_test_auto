import paramiko
import os

def scp_copy_file(host, port, username, password, remote_path, local_destination):
    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        remote_filename = os.path.basename(remote_path)
        local_path = os.path.join(local_destination, remote_filename)
        
        sftp.get(remote_path, local_path)
        
        print(f"File copied successfully from {remote_path} to {local_path}")
        
        sftp.close()
        transport.close()
    except Exception as e:
        print(f"Error: {e}")

# Replace with your own values
host = 'remote_host'
port = 22
username = 'your_username'
password = 'your_password'
remote_path = '/path/to/remote/file.txt'
local_destination = '/path/to/local/folder/'

scp_copy_file(host, port, username, password, remote_path, local_destination)
