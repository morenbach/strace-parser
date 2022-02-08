/*
 *  * Hook main() using LD_PRELOAD, because why not?
 *   * Obviously, this code is not portable. Use at your own risk.
 *    *
 *     * Compile using 'gcc hax.c -o hax.so -fPIC -shared -ldl'
 *      * Then run your program as 'LD_PRELOAD=$PWD/hax.so ./a.out'
 *       */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <dirent.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <errno.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

#define MAX 80
#define PORT 9680
#define SA struct sockaddr


#define SIGNAL_FILE_PATH "/home/administrator/signal_file/"

/* Trampoline for the real main() */
static int (*main_orig)(int, char **, char **);
static pid_t (*orig_f)(void);
//static int (*orig_execve)(const char *pathname, char *const argv[],
//		                         char *const envp[]);

	
/* Our fake main() that gets called by __libc_start_main() */
/*
int execve(const char *pathname, char *const argv[],
		                         char *const envp[]) {
	int res = orig_execve(pathname, argv, envp);
	printf ("EXECVE!!\n");
	return res;
}
*/

static int x = 0;

volatile int k[2];
void wait_vmi() {
	int x[2];
	x[0] = 0;
	x[1] = 0;
	volatile int res = 0;
	for (long long i=0;i<1e9L;i++) {
		res += (int)i;
	}

	k[res%2]++;
}
/*
void finish_vmi() {
	DIR *theFolder = opendir(SIGNAL_FILE_PATH);
	struct dirent *next_file;
	char filepath[512];
	while ( (next_file = readdir(theFolder)) != NULL ) {
		sprintf(filepath, "%s/%s", SIGNAL_FILE_PATH, next_file->d_name);
		remove(filepath);
	}
	
	closedir(theFolder);

	// wait for vmi to exit
	wait_vmi();

}
*/
pid_t fork() {
	pid_t res = orig_f();
	if (x == 2) {
		if (res == 0) {
			int cpid = getpid();	
			int sockfd, connfd;
			struct sockaddr_in servaddr, cli;
			sockfd = socket(AF_INET, SOCK_STREAM, 0);
			if (sockfd == -1) {
				printf("socket creation failed...\n");
				exit(0);
			}
			bzero(&servaddr, sizeof(servaddr));
			servaddr.sin_family = AF_INET;
			servaddr.sin_addr.s_addr = inet_addr("192.168.122.1");
			servaddr.sin_port = htons(PORT);
			if (connect(sockfd, (SA*)&servaddr, sizeof(servaddr)) != 0) {
				printf("connection with the server failed...\n");
				exit(-1);
			}

			int32_t conv = htonl(cpid);
			char *data = (char*)&conv;
			int left = sizeof(conv);
			int rc;

			do {
				rc = write(sockfd, data, left);
				if (rc < 0) {
					if ((errno == EAGAIN) || (errno == EWOULDBLOCK)) {
						continue;
					}
					else if (errno != EINTR) {
						exit(-1);
					}
				} else {
					data += rc;
					left -= rc;			
				}
			} while (left > 0);
			
		         //wait for vmi to be ready
			 char ack = 0;
	 	         read(sockfd, &ack, 1);

			close(sockfd);
		}
	}

	x++;

	return res;
}


int main_hook(int argc, char **argv, char **envp)
{
	atexit(wait_vmi);
	int ret = main_orig(argc, argv, envp);
	return ret;
}

/*
 *  * Wrapper for __libc_start_main() that replaces the real main
 *   * function with our hooked version.
 *    */
	int __libc_start_main(
			int (*main)(int, char **, char **),
			int argc,
			char **argv,
			int (*init)(int, char **, char **),
			void (*fini)(void),
			void (*rtld_fini)(void),
			void *stack_end)
{
	/* Save the real main function address */
	main_orig = main;

	/* Find the real __libc_start_main()... */
	typeof(&__libc_start_main) orig = dlsym(RTLD_NEXT, "__libc_start_main");
	orig_f = dlsym(RTLD_NEXT, "fork");
	//orig_execve = dlsym(RTLD_NEXT, "execve");

	// sleep to wait for introspection to start
	/*
	int x[2];
	x[0] = 0;
	x[1] = 0;
	volatile int res = 0;
	for (long long i=0;i<9e9L;i++) {
		res += (int)i;
	}
	*/

	/* ... and call it with our custom main function */
	return orig(main_hook, argc, argv, init, fini, rtld_fini, stack_end);// + x[res%2];
}

