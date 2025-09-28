.. title: strace as a Linux Engineer's Tool
.. slug: strace-kak-instrument-sistemnogo-administratora
.. date: 2025-09-28 07:00:00 UTC+03:00
.. tags: devops, linux, debug, strace
.. category: linux, support
.. link: 
.. description: A practical guide to using strace for diagnosing and debugging applications in Linux.
.. type: text
.. author: Sergey <DerNitro> Utkin
.. previewimage: /images/posts/strace-kak-instrument-sistemnogo-administratora/christopher-bill-3l19r5EOZaw-unsplash.jpg

.. _Christopher Bill: https://unsplash.com/@umbra_media?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash
.. _Unsplash: https://unsplash.com/photos/brown-cardboard-box-on-white-surface-3l19r5EOZaw?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash

.. |PostImage| image:: /images/posts/strace-kak-instrument-sistemnogo-administratora/christopher-bill-3l19r5EOZaw-unsplash.jpg
    :width: 40%
    :target: `Christopher Bill`_

.. |PostImageTitle| replace:: Photo by `Christopher Bill`_ on Unsplash_


|PostImage|

|PostImageTitle|

The idea for this article came after a technical interview at a large Russian company.
The interview was practical: you log into a virtual machine and have to explain why certain applications aren't starting.
You run `strace`... 10-15 minutes later, the tasks are done, and you've saved each other time.

In my own practice, I've long used `strace` to understand the behavior of an application when logs are insufficient,
and the application just won't work.

In this article, we'll look at the capabilities of `strace` from a Linux administrator's perspective. Let's get started...

.. TEASER_END

Introduction
============

Linux engineers often encounter situations where an application won't start or behaves incorrectly,
and standard logs don't answer the question "why?". In such cases, an indispensable tool is 
`strace` — a utility for tracing system calls and signals, allowing you to see exactly how an application
interacts with the operating system.

This article covers practical scenarios for using `strace` to diagnose file access problems,
analyze multithreading, debug bash scripts, and network applications. The material is aimed at system administrators,
DevOps engineers, and anyone who deals with Linux support and debugging. The examples are based on real cases
and will help you quickly master the basics of the tool.

.. note::

    `strace - trace system calls and signals`

    A useful diagnostic, educational, and debugging tool. System administrators, diagnosticians, and troubleshooters
    will find it invaluable for solving problems with programs whose source code is unavailable,
    since you don't need to recompile them for tracing.

As mentioned above, `strace` allows you to trace system calls and signals in Linux.
You start tracing like this: `strace <command>`.

For example, the output of the `date` command looks like this:

.. code-block::

    $> strace -z date
    execve("/usr/bin/date", ["date"], 0x7ffdd7a8c9c8 /* 75 vars */) = 0
    brk(NULL)                               = 0x587a7e7bf000
    mmap(NULL, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7c97fd31c000
    openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
    fstat(3, {st_mode=S_IFREG|0644, st_size=115355, ...}) = 0
    mmap(NULL, 115355, PROT_READ, MAP_PRIVATE, 3, 0) = 0x7c97fd2ff000
    close(3)                                = 0
    openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
    read(3, "\177ELF\2\1\1\3\0\0\0\0\0\0\0\0\3\0>\0\1\0\0\0\220\243\2\0\0\0\0\0"..., 832) = 832
    pread64(3, "\6\0\0\0\4\0\0\0@\0\0\0\0\0\0\0@\0\0\0\0\0\0\0@\0\0\0\0\0\0\0"..., 784, 64) = 784
    fstat(3, {st_mode=S_IFREG|0755, st_size=2125328, ...}) = 0
    pread64(3, "\6\0\0\0\4\0\0\0@\0\0\0\0\0\0\0@\0\0\0\0\0\0\0@\0\0\0\0\0\0\0"..., 784, 64) = 784
    mmap(NULL, 2170256, PROT_READ, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0x7c97fd000000
    mmap(0x7c97fd028000, 1605632, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x28000) = 0x7c97fd028000
    mmap(0x7c97fd1b0000, 323584, PROT_READ, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x1b0000) = 0x7c97fd1b0000
    mmap(0x7c97fd1ff000, 24576, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x1fe000) = 0x7c97fd1ff000
    mmap(0x7c97fd205000, 52624, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x7c97fd205000
    close(3)                                = 0
    mmap(NULL, 12288, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7c97fd2fc000
    arch_prctl(ARCH_SET_FS, 0x7c97fd2fc740) = 0
    set_tid_address(0x7c97fd2fca10)         = 30773
    set_robust_list(0x7c97fd2fca20, 24)     = 0
    rseq(0x7c97fd2fd060, 0x20, 0, 0x53053053) = 0
    mprotect(0x7c97fd1ff000, 16384, PROT_READ) = 0
    mprotect(0x587a79412000, 8192, PROT_READ) = 0
    mprotect(0x7c97fd354000, 8192, PROT_READ) = 0
    prlimit64(0, RLIMIT_STACK, NULL, {rlim_cur=8192*1024, rlim_max=RLIM64_INFINITY}) = 0
    munmap(0x7c97fd2ff000, 115355)          = 0
    getrandom("\xd9\xf1\xf0\xc3\xcb\x19\x41\xc4", 8, GRND_NONBLOCK) = 8
    brk(NULL)                               = 0x587a7e7bf000
    brk(0x587a7e7e0000)                     = 0x587a7e7e0000
    openat(AT_FDCWD, "/usr/lib/locale/locale-archive", O_RDONLY|O_CLOEXEC) = 3
    fstat(3, {st_mode=S_IFREG|0644, st_size=5728464, ...}) = 0
    mmap(NULL, 5728464, PROT_READ, MAP_PRIVATE, 3, 0) = 0x7c97fca00000
    close(3)                                = 0
    openat(AT_FDCWD, "/etc/localtime", O_RDONLY|O_CLOEXEC) = 3
    fstat(3, {st_mode=S_IFREG|0644, st_size=1535, ...}) = 0
    fstat(3, {st_mode=S_IFREG|0644, st_size=1535, ...}) = 0
    read(3, "TZif2\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\21\0\0\0\21\0\0\0\0"..., 4096) = 1535
    lseek(3, -927, SEEK_CUR)                = 608
    read(3, "TZif2\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\21\0\0\0\21\0\0\0\0"..., 4096) = 927
    close(3)                                = 0
    fstat(1, {st_mode=S_IFCHR|0620, st_rdev=makedev(0x88, 0), ...}) = 0
    Sun Apr 20 09:10:39 MSK 2025
    write(1, "\320\222\321\201 20 \320\260\320\277\321\200 2025 08:56:05 MSK"..., 33) = 33
    close(1)                                = 0
    close(2)                                = 0
    +++ exited with 0 +++

Each trace line contains the system call name, followed by its arguments in parentheses and the return value.
A more detailed description can be found on the `man strace <https://man7.org/linux/man-pages/man1/strace.1.html>`_ page.
The full list of system calls is available at `man syscalls <https://man7.org/linux/man-pages/man2/syscalls.2.html>`_

File Access
===========

In my experience, most application malfunctions are due to lack of access to file resources,
and as we know, in `Linux` everything is a file.

Let's take the previous example with the `date` command and see which files it needs access to.
We'll use the `--trace=%file` filter.

.. code-block::

    $> strace --trace=%file date
    execve("/usr/bin/date", ["date"], 0x7fff97977278 /* 36 vars */) = 0
    access("/etc/ld.so.preload", R_OK)      = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
    openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
    openat(AT_FDCWD, "/usr/lib/locale/locale-archive", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/share/locale/locale.alias", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/lib/locale/C.UTF-8/LC_IDENTIFICATION", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/lib/locale/C.utf8/LC_IDENTIFICATION", O_RDONLY|O_CLOEXEC) = 3
    openat(AT_FDCWD, "/usr/lib/x86_64-linux-gnu/gconv/gconv-modules.cache", O_RDONLY|O_CLOEXEC) = 3
    openat(AT_FDCWD, "/usr/lib/locale/C.UTF-8/LC_MEASUREMENT", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/lib/locale/C.utf8/LC_MEASUREMENT", O_RDONLY|O_CLOEXEC) = 3
    openat(AT_FDCWD, "/usr/lib/locale/C.UTF-8/LC_TELEPHONE", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/lib/locale/C.utf8/LC_TELEPHONE", O_RDONLY|O_CLOEXEC) = 3
    openat(AT_FDCWD, "/usr/lib/locale/C.UTF-8/LC_ADDRESS", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/lib/locale/C.utf8/LC_ADDRESS", O_RDONLY|O_CLOEXEC) = 3
    openat(AT_FDCWD, "/usr/lib/locale/C.UTF-8/LC_NAME", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/lib/locale/C.utf8/LC_NAME", O_RDONLY|O_CLOEXEC) = 3
    openat(AT_FDCWD, "/usr/lib/locale/C.UTF-8/LC_PAPER", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/lib/locale/C.utf8/LC_PAPER", O_RDONLY|O_CLOEXEC) = 3
    openat(AT_FDCWD, "/usr/lib/locale/C.UTF-8/LC_MESSAGES", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/lib/locale/C.utf8/LC_MESSAGES", O_RDONLY|O_CLOEXEC) = 3
    openat(AT_FDCWD, "/usr/lib/locale/C.utf8/LC_MESSAGES/SYS_LC_MESSAGES", O_RDONLY|O_CLOEXEC) = 3
    openat(AT_FDCWD, "/usr/lib/locale/C.UTF-8/LC_MONETARY", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/lib/locale/C.utf8/LC_MONETARY", O_RDONLY|O_CLOEXEC) = 3
    openat(AT_FDCWD, "/usr/lib/locale/C.UTF-8/LC_COLLATE", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/lib/locale/C.utf8/LC_COLLATE", O_RDONLY|O_CLOEXEC) = 3
    openat(AT_FDCWD, "/usr/lib/locale/C.UTF-8/LC_TIME", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/lib/locale/C.utf8/LC_TIME", O_RDONLY|O_CLOEXEC) = 3
    openat(AT_FDCWD, "/usr/lib/locale/C.UTF-8/LC_NUMERIC", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/lib/locale/C.utf8/LC_NUMERIC", O_RDONLY|O_CLOEXEC) = 3
    openat(AT_FDCWD, "/usr/lib/locale/C.UTF-8/LC_CTYPE", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/lib/locale/C.utf8/LC_CTYPE", O_RDONLY|O_CLOEXEC) = 3
    openat(AT_FDCWD, "/etc/localtime", O_RDONLY|O_CLOEXEC) = 3
    Sun Apr 20 09:10:39 MSK 2025
    +++ exited with 0 +++

Quite a list for such a simple command. As you can see, some files are inaccessible, but this
didn't affect the result. To display only successful or unsuccessful system calls, you can add the
`-z` and `-Z` flags respectively.

Let's look at an example of unsuccessful file access. We have a simple Python script that requires access to `/root/test`.

.. code-block:: python

    #!/usr/bin/env python3

    import sys

    try:
        with open('/root/test') as f:
            f.readlines()
    except:
        sys.exit(1)

    sys.exit(0)

Running this script will return code `1`, which isn't very informative for diagnostics. Let's see what `strace` shows.
We'll run the command with the `-Z` flag to see only unsuccessful system calls.

.. code-block:: bash

    $> strace -Z python3 main.py 
    access("/etc/ld.so.preload", R_OK)      = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/lib/locale/locale-archive", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/share/locale/locale.alias", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/lib/locale/C.UTF-8/LC_CTYPE", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
    newfstatat(AT_FDCWD, "/home/sutkin/.pyenv/plugins/pyenv-virtualenv/shims/python3", 0x7ffcce915cb0, 0) = -1 ENOENT (No such file or directory)
    newfstatat(AT_FDCWD, "/home/sutkin/.pyenv/shims/python3", 0x7ffcce915cb0, 0) = -1 ENOENT (No such file or directory)
    newfstatat(AT_FDCWD, "/home/sutkin/.pyenv/bin/python3", 0x7ffcce915cb0, 0) = -1 ENOENT (No such file or directory)
    newfstatat(AT_FDCWD, "/usr/local/sbin/python3", 0x7ffcce915cb0, 0) = -1 ENOENT (No such file or directory)
    newfstatat(AT_FDCWD, "/usr/local/bin/python3", 0x7ffcce915cb0, 0) = -1 ENOENT (No such file or directory)
    newfstatat(AT_FDCWD, "/usr/sbin/python3", 0x7ffcce915cb0, 0) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/pyvenv.cfg", O_RDONLY) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/bin/pyvenv.cfg", O_RDONLY) = -1 ENOENT (No such file or directory)
    readlink("/usr/bin/python3.12", 0x7ffcce910cd0, 4096) = -1 EINVAL (Invalid argument)
    openat(AT_FDCWD, "/usr/bin/python3._pth", O_RDONLY) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/bin/python3.12._pth", O_RDONLY) = -1 ENOENT (No such file or directory)
    openat(AT_FDCWD, "/usr/bin/pybuilddir.txt", O_RDONLY) = -1 ENOENT (No such file or directory)
    newfstatat(AT_FDCWD, "/usr/bin/Modules/Setup.local", 0x7ffcce915cb0, 0) = -1 ENOENT (No such file or directory)
    newfstatat(AT_FDCWD, "/usr/bin/lib/python312.zip", 0x7ffcce915a70, 0) = -1 ENOENT (No such file or directory)
    newfstatat(AT_FDCWD, "/usr/lib/python312.zip", 0x7ffcce915ad0, 0) = -1 ENOENT (No such file or directory)
    newfstatat(AT_FDCWD, "/usr/bin/lib/python3.12/os.py", 0x7ffcce915ad0, 0) = -1 ENOENT (No such file or directory)
    newfstatat(AT_FDCWD, "/usr/bin/lib/python3.12/os.pyc", 0x7ffcce915ad0, 0) = -1 ENOENT (No such file or directory)
    newfstatat(AT_FDCWD, "/usr/bin/lib/python3.12/lib-dynload", 0x7ffcce915ad0, 0) = -1 ENOENT (No such file or directory)
    newfstatat(AT_FDCWD, "/usr/lib/python312.zip", 0x7ffcce915500, 0) = -1 ENOENT (No such file or directory)
    newfstatat(AT_FDCWD, "/usr/lib/python312.zip", 0x7ffcce915880, 0) = -1 ENOENT (No such file or directory)
    newfstatat(AT_FDCWD, "/usr/lib/python3.12/encodings/__init__.cpython-312-x86_64-linux-gnu.so", 0x7ffcce915880, 0) = -1 ENOENT (No such file or directory)
    newfstatat(AT_FDCWD, "/usr/lib/python3.12/encodings/__init__.abi3.so", 0x7ffcce915880, 0) = -1 ENOENT (No such file or directory)
    newfstatat(AT_FDCWD, "/usr/lib/python3.12/encodings/__init__.so", 0x7ffcce915880, 0) = -1 ENOENT (No such file or directory)
    ioctl(3, TCGETS, 0x7ffcce9154c0)        = -1 ENOTTY (Inappropriate ioctl for device)
    ioctl(3, TCGETS, 0x7ffcce914a40)        = -1 ENOTTY (Inappropriate ioctl for device)
    ioctl(3, TCGETS, 0x7ffcce915550)        = -1 ENOTTY (Inappropriate ioctl for device)
    lseek(0, 0, SEEK_CUR)                   = -1 ESPIPE (Illegal seek)
    lseek(1, 0, SEEK_CUR)                   = -1 ESPIPE (Illegal seek)
    lseek(2, 0, SEEK_CUR)                   = -1 ESPIPE (Illegal seek)
    newfstatat(AT_FDCWD, "/usr/bin/pyvenv.cfg", 0x7ffcce9154c0, 0) = -1 ENOENT (No such file or directory)
    newfstatat(AT_FDCWD, "/usr/pyvenv.cfg", 0x7ffcce915520, 0) = -1 ENOENT (No such file or directory)
    newfstatat(AT_FDCWD, "/home/sutkin/.local/lib/python3.12/site-packages", 0x7ffcce9156f0, 0) = -1 ENOENT (No such file or directory)
    newfstatat(AT_FDCWD, "/usr/lib/python3.12/dist-packages", 0x7ffcce915750, 0) = -1 ENOENT (No such file or directory)
    ioctl(3, TCGETS, 0x7ffcce915030)        = -1 ENOTTY (Inappropriate ioctl for device)
    ioctl(3, TCGETS, 0x7ffcce9149c0)        = -1 ENOTTY (Inappropriate ioctl for device)
    ioctl(3, TCGETS, 0x7ffcce915b90)        = -1 ENOTTY (Inappropriate ioctl for device)
    readlink("main.py", 0x7ffcce905330, 4096) = -1 EINVAL (Invalid argument)
    readlink("/home/sutkin/strace/01/main.py", 0x7ffcce904ed0, 1023) = -1 EINVAL (Invalid argument)
    ioctl(3, TCGETS, 0x7ffcce9162c0)        = -1 ENOTTY (Inappropriate ioctl for device)
    openat(AT_FDCWD, "/root/test", O_RDONLY|O_CLOEXEC) = -1 EACCES (Permission denied)
    +++ exited with 1 +++


From the last lines, we can assume the application fails due to lack of access to `/root/test`.
If we run the application with `sudo`, we get the expected result.

.. warning::

    Be careful when using `sudo` to run unfamiliar applications or scripts.
    Running with elevated privileges can damage your system, cause data loss, or compromise security.
    Make sure you trust the source code and understand its actions before executing.

.. code-block:: bash

    $> sudo python3 main.py 
    $> echo $?
    0


Viewing Multithreaded Applications
==================================

For decades now, multi-core CPUs have been common, and multithreading is used to fully utilize CPU resources.

Currently, multithreading can be implemented in two ways:

* Launching a child process with a separate memory space.
* Launching a child process that can share virtual address space, file descriptors, and signal handler tables.

But how do you tell what an application like `nginx` uses?

.. code-block::

    root        6215  0.0  0.0  11156  1596 ?        Ss   08:20   0:00 nginx: master process /usr/sbin/nginx -g daemon on; master_process on;
    www-data    6216  0.0  0.1  12880  4284 ?        S    08:20   0:00  \_ nginx: worker process
    www-data    6217  0.0  0.1  12880  4284 ?        S    08:20   0:00  \_ nginx: worker process

Let's model both technologies. We'll use the `%process` filter.

process
-------

.. code-block:: python

    #!/usr/bin/env python3

    '''
        Example #2:
        Creating fork
    '''

    import sys
    import subprocess
    import random

    subprocess.Popen(["sleep", f"{random.randrange(0,15)}"])

    sys.exit(0)


The result shows `vfork <https://man7.org/linux/man-pages/man2/vfork.2.html>`_ system calls,
where `execve("/usr/bin/sleep"... <https://man7.org/linux/man-pages/man2/execve.2.html>`_ is launched,
and the parent waits for completion with `wait4(8644,... <https://man7.org/linux/man-pages/man2/wait4.2.html>`_

.. code-block:: bash

    $> strace --trace=%process -f python3 02/main.py
    execve("/usr/bin/python3", ["python3", "02/main.py"], 0x7ffde05d94f8 /* 36 vars */) = 0
    vfork(strace: Process 8827 attached
    <unfinished ...>
    [pid  8827] execve("/home/sutkin/.pyenv/plugins/pyenv-virtualenv/shims/sleep", ["sleep", "6"], 0x7fff752cbdb0 /* 36 vars */) = -1 ENOENT (No such file or directory)
    [pid  8827] execve("/home/sutkin/.pyenv/shims/sleep", ["sleep", "6"], 0x7fff752cbdb0 /* 36 vars */) = -1 ENOENT (No such file or directory)
    [pid  8827] execve("/home/sutkin/.pyenv/bin/sleep", ["sleep", "6"], 0x7fff752cbdb0 /* 36 vars */) = -1 ENOENT (No such file or directory)
    [pid  8827] execve("/usr/local/sbin/sleep", ["sleep", "6"], 0x7fff752cbdb0 /* 36 vars */) = -1 ENOENT (No such file or directory)
    [pid  8827] execve("/usr/local/bin/sleep", ["sleep", "6"], 0x7fff752cbdb0 /* 36 vars */) = -1 ENOENT (No such file or directory)
    [pid  8827] execve("/usr/sbin/sleep", ["sleep", "6"], 0x7fff752cbdb0 /* 36 vars */) = -1 ENOENT (No such file or directory)
    [pid  8827] execve("/usr/bin/sleep", ["sleep", "6"], 0x7fff752cbdb0 /* 36 vars */ <unfinished ...>
    [pid  8826] <... vfork resumed>)        = 8827
    [pid  8827] <... execve resumed>)       = 0
    [pid  8826] wait4(8827, 0x7fff752cb4fc, WNOHANG, NULL) = 0
    [pid  8826] exit_group(0)               = ?
    [pid  8826] +++ exited with 0 +++
    exit_group(0)                           = ?
    +++ exited with 0 +++

No surprises: as expected, `vfork` is called, which is more efficient than `fork` because it doesn't copy memory pages.
Instead, the child and parent share memory until one successfully calls `exec()` or `_exit()`.

thread
------

.. code-block:: python

    #!/usr/bin/env python3

    '''
        Example #3:
        Creating thread
    '''

    import sys
    from threading import Thread
    import random
    import time

    def foo():
        time.sleep(random.randrange(0,15))


    t = Thread(target=foo)
    t.start()

    sys.exit(0)

The result is a `clone3 <https://man7.org/linux/man-pages/man2/clone3.2.html>`_ call, which returns the PID of the new process.
The `clone3` call is similar to `fork`, i.e., it creates a separate process, but allows you to control creation stages via flags.

From the flags, we can immediately see:

* Parent and child share virtual memory (`CLONE_VM`)
* Parent and child share filesystem attributes (`CLONE_FS`)
* Parent and child share open file descriptor table (`CLONE_FILES`)
* Places the child in the same thread group as its parent (`CLONE_THREAD`)

.. code-block:: bash

    $> strace --trace=%process -f python3 03/main.py
    execve("/usr/bin/python3", ["python3", "03/main.py"], 0x7fff929b4dc8 /* 36 vars */) = 0
    clone3({flags=CLONE_VM|CLONE_FS|CLONE_FILES|CLONE_SIGHAND|CLONE_THREAD|CLONE_SYSVSEM|CLONE_SETTLS|CLONE_PARENT_SETTID|CLONE_CHILD_CLEARTID, child_tid=0x7101922de990, parent_tid=0x7101922de990, exit_signal=0, stack=0x710191ade000, stack_size=0x7fff80, tls=0x7101922de6c0} => {parent_tid=[8991]}, 88) = 8991
    strace: Process 8991 attached
    [pid  8991] exit(0)                     = ?
    [pid  8991] +++ exited with 0 +++
    exit_group(0)                           = ?
    +++ exited with 0 +++

.. note::

    Using the `%process` filter, you can determine how multithreading is organized in an application.

Back to `nginx`, we see it uses `clone` without shared memory, which makes sense—no need to fight over shared resources.

.. code-block:: bash

    $> sudo strace --trace=%process -f /usr/sbin/nginx -g 'master_process on;'
    [sudo] password for sutkin: 
    execve("/usr/sbin/nginx", ["/usr/sbin/nginx", "-g", "master_process on;"], 0x7ffe908b5210 /* 23 vars */) = 0
    clone(child_stack=NULL, flags=CLONE_CHILD_CLEARTID|CLONE_CHILD_SETTID|SIGCHLDstrace: Process 9670 attached
    , child_tidptr=0x7c345a1bea10) = 9670
    [pid  9670] clone(child_stack=NULL, flags=CLONE_CHILD_CLEARTID|CLONE_CHILD_SETTID|SIGCHLD <unfinished ...>
    [pid  9669] exit_group(0strace: Process 9671 attached
    )               = ?
    [pid  9670] <... clone resumed>, child_tidptr=0x7c345a1bea10) = 9671
    [pid  9670] clone(child_stack=NULL, flags=CLONE_CHILD_CLEARTID|CLONE_CHILD_SETTID|SIGCHLD <unfinished ...>
    [pid  9669] +++ exited with 0 +++
    strace: Process 9672 attached
    [pid  9670] <... clone resumed>, child_tidptr=0x7c345a1bea10) = 9672
    ^Cstrace: Process 9670 detached
    strace: Process 9672 detached
    strace: Process 9671 detached

Command Line
============

One use case for `strace` is debugging bash scripts. For example, it's hard to analyze a 4500-line script by eye or with debug mode,
like `Node Version Manager <https://github.com/nvm-sh/nvm/blob/master/nvm.sh>`_.

Here's a simple bash script:

.. code-block:: bash

    #!/bin/bash

    eval $(printf "\145\143\150\157\40\42\110\145\154\154\157\42")
    eval $(echo "dt" | sed 's/t/ate/')
    eval $(echo "bHMK" | base64 -d)

It's hard to tell at a glance what this script does. Let's run it through `strace` and see the result.

.. code-block:: bash

    $> strace --trace=execve -f 04/main.sh 2>&1 | grep execve
    execve("04/main.sh", ["04/main.sh"], 0x7ffc0a9ebdc0 /* 39 vars */) = 0
    [pid  4799] execve("/usr/bin/date", ["date"], 0x5e11f9af7120 /* 38 vars */) = 0
    [pid  4802] execve("/usr/bin/sed", ["sed", "s/t/ate/"], 0x5e11f9af7120 /* 38 vars */) = 0
    [pid  4803] execve("/usr/bin/date", ["date"], 0x5e11f9af7120 /* 38 vars */) = 0
    [pid  4806] execve("/usr/bin/base64", ["base64", "-d"], 0x5e11f9af7120 /* 38 vars */) = 0
    [pid  4807] execve("/usr/bin/date", ["date"], 0x5e11f9af7120 /* 38 vars */) = 0

If you add the `-v` flag, you'll also see the arguments passed.

Creating Socket and Sending Data
================================

To avoid inventing code, let's use an example from the documentation
`Python Socket Programming: Server and Client Example Guide <https://www.digitalocean.com/community/tutorials/python-socket-programming-server-client>`_.

The application is simple: a server is started, a client connects and sends a message.

.. code-block:: python

    #!/usr/bin/env python3

    import socket

    def server_program():
        host = socket.gethostname()
        port = 5000

        server_socket = socket.socket()
        server_socket.bind((host, port))

        server_socket.listen(2)
        conn, address = server_socket.accept()
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
        conn.close()

    if __name__ == '__main__':
        server_program()

.. code-block:: python

    #!/usr/bin/env python3

    import socket

    def client_program():
        host = socket.gethostname()
        port = 5000

        client_socket = socket.socket()
        client_socket.connect((host, port))

        message = 'data'

        client_socket.send(message.encode())
        client_socket.close()

    if __name__ == '__main__':
        client_program()

Let's run the server and client and see what useful data we can get by analyzing only system calls.

.. code-block:: bash

    $> strace --trace=socket,bind,recvfrom,sendto,accept4 -z python3 05/server_program.py 
    socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_IP) = 3
    ...
    bind(3, {sa_family=AF_INET, sin_port=htons(5000), sin_addr=inet_addr("127.0.1.1")}, 16) = 0
    listen(3, 2)                            = 0
    accept4(3, {sa_family=AF_INET, sin_port=htons(40876), sin_addr=inet_addr("127.0.0.1")}, [16], SOCK_CLOEXEC) = 4
    recvfrom(4, "data", 1024, 0, NULL, NULL) = 4
    recvfrom(4, "", 1024, 0, NULL, NULL)    = 0
    +++ exited with 0 +++

* `bind` - Binds the socket to a specific IP address and port on your machine. This is its "registration". After this, the socket "knows" which address to accept incoming connections or send outgoing ones. The parameters show which address and port the application will listen on.
* `listen` - Puts the socket into listening mode.
* `accept4` - Extracts the first connection request from the queue for the listening socket and creates a new connected socket. The parameters contain information about the client.
* `recvfrom` - Received the sent data.

.. code-block:: bash

    $> strace -v --trace=socket,connect,sendto,recvfrom -z python3 05/client_program.py 
    socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_IP) = 3
    ...
    connect(3, {sa_family=AF_INET, sin_port=htons(5000), sin_addr=inet_addr("127.0.1.1")}, 16) = 0
    sendto(3, "data", 4, 0, NULL, 0)        = 4
    +++ exited with 0 +++

The client side output is simpler:

* `connect` - After creating the socket, this system call handles all the work of establishing a TCP connection; the server address is passed as a parameter.
* `sendto` - Sends data.

Of course, it's hard to imagine debugging a high-load network application this way, but without this example, the article would feel incomplete.

Getting Syscall Statistics
==========================

As a bonus, running with the `-c` flag simply outputs statistics on system call usage.

.. code-block:: bash

    $> strace -c -z date
    Sun Sep 28 06:51:34 MSK 2025
    % time     seconds  usecs/call     calls    errors syscall
    ------ ----------- ----------- --------- --------- ----------------
    28.02    0.000325          15        21           mmap
    18.97    0.000220          12        17           openat
    16.03    0.000186           9        19           close
    14.66    0.000170           8        19           fstat
    6.72     0.000078          26         3           mprotect
    2.84     0.000033          11         3           read
    1.98     0.000023          23         1           write
    1.98     0.000023           7         3           brk
    1.38     0.000016           8         2           pread64
    1.38     0.000016          16         1           getrandom
    1.03     0.000012          12         1           arch_prctl
    0.95     0.000011          11         1           set_tid_address
    0.95     0.000011          11         1           set_robust_list
    0.95     0.000011          11         1           prlimit64
    0.86     0.000010          10         1           rseq
    0.69     0.000008           8         1           futex
    0.60     0.000007           7         1           lseek
    0.00     0.000000           0         1           munmap
    0.00     0.000000           0         1           execve
    ------ ----------- ----------- --------- --------- ----------------
    100.00    0.001160          11        98           total


Conclusion
==========

`strace` is an indispensable tool for diagnosing and debugging applications in Linux, especially when standard logs don't answer
the question "why doesn't it work?". I hope this article is useful and helps someone fix production issues
or at least pass an interview in the future. **Good luck to all.**
