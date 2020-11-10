To execute the server follow these steps :
--- python3 Simple_ftp_server.py <port number> <filename> <p>
--- As an example : python3 Simple_ftp_server.py 7738 test_file.txt 0.1

To execute the client follow these steps :
--- python3 Simple_ftp_client.py <server host name> <server-port> <filename> <n> <mss>
--- As an example : python3 Simple_ftp_client.py 127.0.0.1 7738 sample-2mb-text-file.txt 10 500

Note: we have included 'sample-2mb-text-file.txt', which we have used to generate the report for this project.