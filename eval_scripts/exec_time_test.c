// Simple C program to use fork() & exec() system call for process creation and
// measure time via host server
#include <linux/unistd.h>
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h> 
#include <stdlib.h>
#include <errno.h>  
#include <sys/wait.h>
#include <string.h>
  
#include <time.h>
#include <netdb.h>
#include <sys/socket.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/syscall.h>

#define MAX 80
#define PORT 9681
#define SA struct sockaddr

volatile int dummy = 0;
#define ITERATIONS 100000000

int main(int argc, char* argv[]){
   int ret = 1;
   int status;

      if (argc < 2) {
         printf("Must get command to execute\n");
         exit(-1);
      }

      int sockfd, connfd;
      struct sockaddr_in servaddr, cli;
      
      // socket create and varification
      sockfd = socket(AF_INET, SOCK_STREAM, 0);
      if (sockfd == -1) {
         printf("socket creation failed...\n");
         exit(0);
      }
      else
         printf("Socket successfully created..\n");
      bzero(&servaddr, sizeof(servaddr));
      
      // assign IP, PORT
      servaddr.sin_family = AF_INET;
      servaddr.sin_addr.s_addr = inet_addr("192.168.122.1");
      servaddr.sin_port = htons(PORT);
      
      // connect the client socket to server socket
      if (connect(sockfd, (SA*)&servaddr, sizeof(servaddr)) != 0) {
         printf("connection with the server failed...\n");
         exit(0);
      }
      else
         printf("connected to the server..\n");         

      // send request to start timer
      //
      char req = 1;
      char ack = 0;

      int p = fork();

      if (p == 0) {
         if (argc > 2 && strcmp(argv[2],"vmi") == 0) {
            int sockfd1, connfd1;
            struct sockaddr_in servaddr1, cli1;
         
            // socket create and varification
            sockfd1 = socket(AF_INET, SOCK_STREAM, 0);
            if (sockfd1 == -1) {
               printf("socket creation failed...\n");
               exit(0);
            }
            else
               printf("Socket successfully created..\n");
            bzero(&servaddr1, sizeof(servaddr1));
         
            // assign IP, PORT
            servaddr1.sin_family = AF_INET;
            servaddr1.sin_addr.s_addr = inet_addr("192.168.122.1");
            servaddr1.sin_port = htons(9680);
         
            // connect the client socket to server socket
            if (connect(sockfd1, (SA*)&servaddr1, sizeof(servaddr1)) != 0) {
               printf("connection with the server failed...\n");
               exit(0);
            }
            else
               printf("connected to the server..\n");           

            int cpid = getpid();
            char ack = 0;
            int32_t conv = htonl(cpid);
            char *data = (char*)&conv;
            int left = sizeof(conv);
            int rc;
            do {
               rc = write(sockfd1, data, left);
               if (rc < 0) {
                     if ((errno == EAGAIN) || (errno == EWOULDBLOCK)) {
                        continue;
                     }
                     else if (errno != EINTR) {
                        exit(-1);
                     }
               }
               else {
                     data += rc;
                     left -= rc;
               }
            }
            while (left > 0);

            // wait for vmi to be ready
            //
            read(sockfd1, &ack, 1);

            close(sockfd1);

	    sleep(1);
         }

         write(sockfd, &req, 1);
         read(sockfd, &ack, 1);

         // close the socket
         close(sockfd);

         execl("/home/administrator/ransomwares/Ransomware-PoC/bin/main/main", "/home/administrator/ransomwares/Ransomware-PoC/bin/main/main", "-p", "/home/morenbach/test_ransomware/", "-e", NULL);      
      } else { // parent
         waitpid(p, &status, 0);
         // end timer
         write(sockfd, &req, 1);
         read(sockfd, &ack, 1);     

         close(sockfd); 
      } 

      exit(0);

   return 0;
}
