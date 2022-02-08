/*
 *  * Hook main() using LD_PRELOAD, because why not?
 *   * Obviously, this code is not portable. Use at your own risk.
 *    *
 *     * Compile using 'gcc ld_preload.c -o ld_preload.so -fPIC -shared -ldl'
 *      * Then run your program as 'LD_PRELOAD=$PWD/ld_preload.so ./a.out'
 *       */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

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
	for (long long i=0;i<9e9L;i++) {
		res += (int)i;
	}

	k[res%2]++;
}

pid_t fork() {
	pid_t res = orig_f();
	if (x == 2) {
		printf("FORK %d\n", res);
		if (res == 0) {
			wait_vmi();
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

