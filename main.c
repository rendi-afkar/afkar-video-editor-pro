#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <limits.h>
#include <libgen.h>
#include <string.h>

int main(int argc, char **argv) {
    char exe[PATH_MAX];
    ssize_t n = readlink("/proc/self/exe", exe, sizeof(exe) - 1);
    if (n < 0) {
        perror("readlink");
        return 1;
    }
    exe[n] = '\0';

    char basedir[PATH_MAX];
    char script[PATH_MAX];
    snprintf(basedir, sizeof(basedir), "%s", dirname(exe));
    snprintf(script, sizeof(script), "%s/lib/core.py", basedir);

    if (access(script, R_OK) != 0) {
        fprintf(stderr, "[X] File lib/core.py tidak ditemukan.\n");
        return 1;
    }

    char **args = calloc((size_t)argc + 2, sizeof(char *));
    if (!args) {
        perror("calloc");
        return 1;
    }
    args[0] = "python";
    args[1] = script;
    for (int i = 1; i < argc; i++) args[i + 1] = argv[i];
    args[argc + 1] = NULL;
    execvp("python", args);
    perror("python");
    free(args);
    return 1;
}
