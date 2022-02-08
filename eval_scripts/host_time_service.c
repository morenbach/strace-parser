#include <stdio.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <time.h>
#include <sys/types.h>
#include <unistd.h> 
#include <stdlib.h>
#include <errno.h>  

#define MAX 80
#define PORT 9681
#define SA struct sockaddr
   
// Function designed for chat between client and server.
void func(int connfd)
{
    struct timespec c1, c2;
    char dummy;
    char ack = 1;
    read(connfd, &dummy, 1);
    clock_gettime(CLOCK_REALTIME, &c1);
    write(connfd, &ack, 1);
    read(connfd, &dummy, 1);
    clock_gettime(CLOCK_REALTIME, &c2);
    double total_latency = ( c2.tv_sec - c1.tv_sec ) + ( c2.tv_nsec - c1.tv_nsec ) / 1e9;
    printf("Total Latency: %lf\n", total_latency);            
    write(connfd, &ack, 1);
}
   
// Driver function
int main()
{
    int sockfd, connfd, len;
    struct sockaddr_in servaddr, cli;
   
    // socket create and verification
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd == -1) {
        printf("socket creation failed...\n");
        exit(0);
    }
    // else
    //     printf("Socket successfully created..\n");
    bzero(&servaddr, sizeof(servaddr));
   
    // assign IP, PORT
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port = htons(PORT);

    int yes = 1;
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));
   
    // Binding newly created socket to given IP and verification
    if ((bind(sockfd, (SA*)&servaddr, sizeof(servaddr))) != 0) {
        printf("socket bind failed...\n");
        exit(0);
    }
    // else
    //     printf("Socket successfully binded..\n");
   
    // Now server is ready to listen and verification
    if ((listen(sockfd, 5)) != 0) {
        printf("Listen failed...\n");
        exit(0);
    }
    // else
    //     printf("Server listening..\n");
    len = sizeof(cli);
   
    // Accept the data packet from client and verification
    connfd = accept(sockfd, (SA*)&cli, &len);
    if (connfd < 0) {
        printf("server accept failed...\n");
        exit(0);
    }
    // else
    //     printf("server accept the client...\n");
   
    // Function for measuring time
    func(connfd);
   
    // After chatting close the socket
    close(sockfd);

    return 0;
}
