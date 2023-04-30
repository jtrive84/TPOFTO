Title: Using R's Socket Interface for Interprocess Communication
Date: 2023-04-23           
Category: R                
Tags: R 
Authors: James D. Triveri                      
Summary: Using R's Socket Interface for Interprocess Communication 


Often it is necessary to communicate runtime execution details from one process to another process or monitoring utility. The 
information can be used for logging, debugging, tracing or simply to relay the status or progress of a running program. In this post, 
I'll demonstrate how to perform interprocess communication between two separate R processes using functions available in base R. 


In order to setup a communication channel between separately running R instances, it is first necessary to initialize the socket 
server. A very simple example of a socket server that echoes the client's messages is provided below. I'll save it in a file named 
*server.R*:

```R
# server.R: Example of a socket server in listening mode.
serverSocket = make.socket(host="localhost", port=6000, server=TRUE)

while(TRUE) {
    statusMsg = read.socket(serverSocket)
    print(statusMsg)
    if (nchar(statusMsg)==0) break
} 

close.socket(serverSocket)
```

We first call `make.socket` with `server=TRUE`, and `port=6000`. The port number can be any integer between 0-65535 (port numbers are 
unsigned 16-bit integers), but should always be set to something greater than 1024, since ports 0-1024 are reserved for privileged 
services. Next a looping construct is setup and the socket is read from until a message is received having character length 0. Once 
the zero-length character message is received, iteration ceases and `serverSocket` is closed by calling `close.socket`.

Next we implement the client socket and the logic to facilitate message passing between two R processes. In this example, a random 
poisson number is generated, the client sleeps for 1 second, then writes the current time along with the randomly generated poisson 
number to the server listening on port 6000. We save the code that follows in a file named *client.R*:

```R
# client.R: Example of socket client and message generating logic.
clientSocket = make.socket(host="localhost", port=6000, server=FALSE)

for (ii in 1:10) {
    rp = rpois(1,10)
    Sys.sleep(1)
    msg = paste0("[",Sys.time(), "] - Random Poisson: ", rp)
    write.socket(clientSocket, msg)
}

close.socket(clientSocket)
```

The call to `make.socket` is similar to that in *server.R*, except in *client.R*, `server=FALSE` (note that `server=FALSE` is the 
default for `make.socket`, but listing it explicitly helps to clearly indicate the purpose of each socket). 
All that remains is to kick them off. As mentioned earlier, it’s imperative to first run *server.R*. The socket server will enter 
listening mode, waiting on messages from *client.R*. If you attempt to run client.R without server.R already running, an exception 
will be generated, along the lines of:


```R
Error in make.socket(host="localhost", port=6000, server=FALSE) : 

  socket not established
```

From RStudio, a separate R process can be established by selecting *Session > New Session*. First kickoff *server.R*. Once running, 
start *client.R*. The image below shows *client.R* on the left and *server.R* on the right:

![socket1](https://drive.google.com/uc?export=view&id=1Vj5S8CnSmgCYcbbVDGzTRCp5kYqwlk4A)


The output written to the *server.R* console confirms that our socket setup successfully communicated information between separate 
invocations of R. 
