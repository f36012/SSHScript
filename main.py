import csv
import socket
import time

from netmiko import Netmiko
from netmiko import redispatch, exceptions
import tkinter as tk
from tkinter import filedialog, ttk


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


def ssh_to_devices():
    # Open File with Device IPs
    with open(devices_file_entry.get(), 'r') as csvfile:
        device_reader = csv.reader(csvfile)
        device_ips = []

        for row in device_reader:
            device_ips.append(row)

    with open(output_file_entry.get(), 'a') as outfile:
        for device_ip in device_ips[0]:

            print('ssh {}\n'.format(device_ip))
            try:
                try:
                    # Connect to the jump server
                    net_connect = Netmiko(device_type="terminal_server", host=server_entry.get(),
                                          username=username_entry.get(),
                                          password=password_entry.get())
                    print("Jump server prompt: " + (net_connect.find_prompt()))
                except socket.timeout:
                    print("Timeout for jump server ", server_entry.get(), ":", e)
                    outfile.write("Timeout Error,failed to connect to Jump Server :  " + device_ip + "\n")
                    outfile.write("######################################################### " + "\n")
                    continue
                except exceptions.NetmikoTimeoutException as e:
                    print("Authentication failed for jump server", server_entry.get(), ":", e)
                    outfile.write("Authentication failed for device :  " + device_ip + "\n")
                    outfile.write("######################################################### " + "\n")
                    continue
                except exceptions.ReadTimeout as e:
                    print("Error ")
                    continue
                # Login to first device
                net_connect.write_channel(f'ssh {device_ip}\n')
                time.sleep(1)
                output = net_connect.read_channel()
                print(output)
                if 'Are you sure you want to continue connecting' in output:
                    net_connect.write_channel('yes' + '\n')
                    output = net_connect.read_channel()

                # Send the device password to the jump server terminal
                if "password" in output:
                    print("**Received Password Prompt, Entering password**")
                    net_connect.write_channel(password_entry.get() + '\n')

                # Wait for the SSH connection to be established
                time.sleep(1)
                # print("Device prompt: {}".format(net_connect.find_prompt()))
                redispatch(net_connect, device_type="cisco_ios")
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

            try:
                # Execute a command on the device
                commands = commands_entry.get("1.0", "end").strip().split(",")
                outfile.write("Output for device " + device_ip + "\n")
                for command in commands:
                    print("Executing command " + command)
                    output = net_connect.send_command(command)
                    outfile.write("Output for command " + "'" + command + "'" + ":" + "\n")
                    outfile.write(output)
                    outfile.write("\n")

                outfile.write("######################################################### " + "\n")
                outfile.write("\n\n")
            except exceptions.ConnectionException as e:
                print("Could not execute command on device" + device_ip + ":", e)
                # Close the connection to the device
                net_connect.disconnect()
    # Inform the user that the output has been written to the file
    print("Output written to", output_file_entry.get())


# Create a GUI window
root = tk.Tk()
root.title("Login")

# Create entry widgets for device, username, and password
devices_file_label = tk.Label(root, text="Device IP file:")
devices_file_label.grid(row=0, column=0)
devices_file_entry = tk.Entry(root)
devices_file_entry.grid(row=0, column=1)
browse_devices_file_button = tk.Button(root, text="Browse", command=browse_devices_file)
browse_devices_file_button.grid(row=0, column=2)

server_label = tk.Label(root, text="TACACS IP")
server_label.grid(row=1, column=0)
server_entry = tk.Entry(root)
server_entry.grid(row=1, column=1)

username_label = tk.Label(root, text="Username:")
username_label.grid(row=2, column=0)
username_entry = tk.Entry(root)
username_entry.grid(row=2, column=1)

password_label = tk.Label(root, text="Password:")
password_label.grid(row=3, column=0)
password_entry = tk.Entry(root, show="*")
password_entry.grid(row=3, column=1)

output_file_label = tk.Label(root, text="Output file:")
output_file_label.grid(row=4, column=0)
output_file_entry = tk.Entry(root)
output_file_entry.grid(row=4, column=1)
browse_output_file_button = tk.Button(root, text="Browse", command=browse_output_file)
browse_output_file_button.grid(row=4, column=2)

# Create the Text widget to input the commands
commands_entry_label = tk.Label(root, text="Commands")
commands_entry_label.grid(row=5, column=0)
commands_entry = tk.Text(root, height=10, width=20)
commands_entry.grid(row=5, column=1, columnspan=2)

# Create a button to initiate the SSH connection
ssh_button = ttk.Button(root, text="Execute", command=ssh_to_devices)
ssh_button.grid(row=6, column=0, padx=10)

copyright_label = tk.Label(root, text="🔵🔵🔵🔵🔵🔵🔵🔵🔵🔵")
copyright_label.grid(row=7, column=2, columnspan=1)

# Start the GUI event loop
root.mainloop()
