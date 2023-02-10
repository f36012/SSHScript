import csv
import socket
import paramiko
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def browse_devices_file():
    devices_file_entry.delete(0, tk.END)
    devices_file = filedialog.askopenfilename(initialdir="/", title="Select file",
                                              filetypes=(("Comma Separated Values", "*.csv"), ("all files", "*.*")))
    devices_file_entry.insert(0, devices_file)


def browse_output_file():
    output_file_entry.delete(0, tk.END)
    output_file = filedialog.asksaveasfilename(initialdir="/", title="Select file",
                                               filetypes=(("Text files", "*.txt"), ("all files", "*.*")))
    output_file_entry.insert(0, output_file)


def ssh_to_device():
    # Create the progress bar
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="indeterminate")
    progress_bar.grid(row=5, column=1, padx=10)
    progress_bar.start()
    with open(devices_file_entry.get(), 'r') as csvfile:
        device_reader = csv.reader(csvfile)
        # device_ips = [row[0] for row in device_reader]
        device_ips = []

        for row in device_reader:
            device_ips.append(row)
        print(device_ips[0])
    # Create an SSH client
    client = paramiko.SSHClient()

    # Set policy to automatically add the host key
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    with open(output_file_entry.get(), 'a') as outfile:
        for device_ip in device_ips[0]:
            try:
                # Connect to the device
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)  # set a timeout of 10 seconds
                client.connect(hostname=device_ip, username=username_entry.get(), password=password_entry.get())
            except socket.gaierror:
                # messagebox.showerror("Error",
                #                      "Failed to connect to the device. Hostname or IP address could not be resolved.")
                outfile.write("Failed to connect to the device. Hostname or IP address could not be resolved :  "
                              + device_ip + "\n")
                outfile.write("######################################################### " + "\n")
                continue
            except socket.timeout:
                outfile.write("Timeout Error :  " + device_ip + "\n")
                outfile.write("######################################################### " + "\n")
                continue
            except paramiko.ssh_exception.NoValidConnectionsError:
                # messagebox.showerror("Error", "Unable to connect to the device on port 22 : " + device_ip)
                outfile.write("Unable to connect to the device on port 22 :  " + device_ip + "\n")
                outfile.write("######################################################### " + "\n")
                continue
            except paramiko.ssh_exception.AuthenticationException as e:
                print("Authentication failed for device", device_ip, ":", e)
                outfile.write("Authentication failed for device :  " + device_ip + "\n")
                outfile.write("######################################################### " + "\n")
                continue
            except paramiko.ssh_exception.SSHException as e:
                print("Could not establish SSH connection to device", device_ip, ":", e)
                outfile.write("Could not establish SSH connection to device" + device_ip + "\n")
                outfile.write("######################################################### " + "\n")
                continue
            try:
                # Execute a command on the device
                commands = ["code -v", "cd"]

                outfile.write("Output for device " + device_ip + "\n")
                for command in commands:
                    stdin, stdout, stderr = client.exec_command(command)
                    output = stdout.read().decode("utf-8")
                    outfile.write("Output for command " + "'" + command + "'" + ":" + "\n")
                    outfile.write(output)
                    outfile.write("\n")
                # stdin, stdout, stderr = client.exec_command("code -v; cd")
                # Write the output of the command to the output file

                # outfile.write(stdout.read().decode("utf-8"))

                outfile.write("######################################################### " + "\n")
                outfile.write("\n\n")
            except paramiko.ssh_exception.SSHException as e:
                print("Could not execute command on device" + device_ip + ":", e)

        # Close the connection to the device
        client.close()
    progress_bar.stop()
    # Inform the user that the output has been written to the file
    print("Output written to", output_file_entry.get())


# Create a GUI window
root = tk.Tk()
root.title("Login to Cisco Device")

# Create entry widgets for device, username, and password
devices_file_label = tk.Label(root, text="Device IP file:")
devices_file_label.grid(row=0, column=0)
devices_file_entry = tk.Entry(root)
devices_file_entry.grid(row=0, column=1)
browse_devices_file_button = tk.Button(root, text="Browse", command=browse_devices_file)
browse_devices_file_button.grid(row=0, column=2)

username_label = tk.Label(root, text="Username:")
username_label.grid(row=1, column=0)
username_entry = tk.Entry(root)
username_entry.grid(row=1, column=1)

password_label = tk.Label(root, text="Password:")
password_label.grid(row=2, column=0)
password_entry = tk.Entry(root, show="*")
password_entry.grid(row=2, column=1)

output_file_label = tk.Label(root, text="Output file:")
output_file_label.grid(row=3, column=0)
output_file_entry = tk.Entry(root)
output_file_entry.grid(row=3, column=1)
browse_output_file_button = tk.Button(root, text="Browse", command=browse_output_file)
browse_output_file_button.grid(row=3, column=2)

# Create a button to initiate the SSH connection
ssh_button = ttk.Button(root, text="SSH", command=ssh_to_device)
ssh_button.grid(row=4, column=0, padx=10)

# Start the GUI event loop
root.mainloop()
