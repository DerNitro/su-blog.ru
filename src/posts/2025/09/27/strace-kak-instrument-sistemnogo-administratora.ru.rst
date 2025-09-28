.. title: strace как инструмент linux инженера
.. slug: strace-kak-instrument-sistemnogo-administratora
.. date: 2025-09-28 07:00:00 UTC+03:00
.. tags: devops, linux, debug, strace
.. category: linux, support
.. link: 
.. description: Практическое руководство по использованию strace для диагностики и отладки приложений в Linux.
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

Идея написания данной статьи родилась после прохождения технического интервью, в одной крупной российской компании.
Само интервью состояло из практики, заходишь на виртуальную машину, и должен рассказать почему не запускаются, те или иные приложения.
Запускаем `strace`... 10 - 15 минут и задачи закончились, сэкономили друг другу время.

В своей практике я давно уже использую инструмент `strace`, чтобы узнать поведение запускаемого приложения, когда логов уже не достаточно,
а приложение так и не работает.

В данной статье разберем возможности `strace` с позиции linux администратора. И так поехали...

.. TEASER_END

Введение
========

В работе Linux-инженера часто возникают ситуации, когда приложение не запускается или ведёт себя некорректно,
а стандартные логи не дают ответа на вопрос "почему?". В таких случаях незаменимым инструментом становится 
`strace` — утилита для трассировки системных вызовов и сигналов, позволяющая увидеть, как именно приложение
взаимодействует с операционной системой.

В этой статье рассмотрим практические сценарии использования `strace` для диагностики проблем с доступом к файлам,
анализом многопоточности, отладкой bash-скриптов и сетевых приложений. Материал ориентирован на системных администраторов,
DevOps-инженеров и всех, кто сталкивается с задачами поддержки и отладки Linux-систем. Примеры основаны на реальных кейсах
и помогут быстро освоить основные возможности инструмента.

.. note::

    `strace - trace system calls and signals`

    Полезный диагностический, обучающий и отладочный инструмент. Системные администраторы, диагносты и специалисты
    по устранению неполадок найдут его бесценным для решения проблем с программами, исходный код которых недоступен,
    поскольку их не нужно перекомпилировать для трассировки.

Как выше сказано, `strace` позволяет выполнить трассировку системных вызовов и сигналов в операционных системах Linux,
запуск трассировки выглядит следующим образом `strace \<command\>`.

Например вывод команды `date` будет выглядеть следующим образом:

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
    Вс 20 апр 2025 08:56:05 MSK
    write(1, "\320\222\321\201 20 \320\260\320\277\321\200 2025 08:56:05 MSK"..., 33) = 33
    close(1)                                = 0
    close(2)                                = 0
    +++ exited with 0 +++

Каждая строка трассировки содержит имя системного вызова, за которым в скобках следуют его аргументы и возвращаемое значение.
Более подробное описание можно найти на странице `man strace <https://man7.org/linux/man-pages/man1/strace.1.html>`_.
Полный список системных вызовов можно посмотреть на странице `man syscalls <https://man7.org/linux/man-pages/man2/syscalls.2.html>`_

Файловый доступ
===============

На моей практике большинство проблем некорректной работы приложений, является проблема с отсутствием доступа к файловым ресурсам,
а как мы знаем в `Linux` все является файлами.

Возьмем предыдущий пример, с запуском команды `date` и посмотрим доступ к каким файлам необходим для данной команды.
Для этого мы будем использовать фильтр `--trace=%file`

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

Внушительный список, для столь простой команды. Как вы могли заметить, по выводу трассировки, часть файлов не доступна, но это
не повлияло на результат. Для вывода только успешных и не успешных системных вызовов можно добавить дополнительные ключи
`-z` и `-Z` соответсвенно.

Так давайте разберем на примере не успешного доступа к файлу, у нас имеется простой скрипт на `Python`, который требует наличие доступа 
к файлу `/root/test`

.. code-block:: python

    #!/usr/bin/env python3

    import sys

    try:
        with open('/root/test') as f:
            f.readlines()
    except:
        sys.exit(1)

    sys.exit(0)

Запуск данного скрипта выдаст `return code` равный `1`. Что для диагностики как то маловато. Посмотрим что покажет нам `strace`,
Для этого мы запустим команду с флагом `-Z`, что бы увидить только не успешные системные вызовы

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

По последним строкам вывода мы можем предположить, что наше приложение падает, из-за отсутсвия доступа к файлу `/root/test`. 
И запустив наше приложение с `sudo`, получим результат который нас устраивает.

.. warning::

    Будьте осторожны при использовании `sudo` для запуска незнакомых приложений или скриптов. 
    Запуск с повышенными правами может привести к повреждению системы, потере данных или компрометации безопасности. 
    Перед выполнением убедитесь, что доверяете исходному коду и понимаете его действия.

.. code-block::

    $> sudo python3 main.py 
    $> echo $?
    0


Просмотр многопоточных приложений
=================================

Уже на протяжении нескольких десятков лет, никого не удивить многоядерными CPU, и для полной утилизации CPU применятеся
многопоточность в приложениях.

На текущий момент можно разделить много поточность на 2 типа реализации:

* Запуск дочернего процесса с отдельным пространством памяти.
* Запуск дочернего процесса с возможностью совместно использовать виртуальное адресное пространство, файловые дескрипторы и таблицу обработчиков сигналов.

Но как отличить что же использует приложение например `nginx`?

.. code-block::

    root        6215  0.0  0.0  11156  1596 ?        Ss   08:20   0:00 nginx: master process /usr/sbin/nginx -g daemon on; master_process on;
    www-data    6216  0.0  0.1  12880  4284 ?        S    08:20   0:00  \_ nginx: worker process
    www-data    6217  0.0  0.1  12880  4284 ?        S    08:20   0:00  \_ nginx: worker process

Давай те смоделируем, обе технологии. И будем использовать фильтр `%process`.

process
-------

.. code-block:: python

    #!/usr/bin/env python3

    '''
        Пример №2:
        Создание fork
    '''

    import sys
    import subprocess
    import random

    subprocess.Popen(["sleep", f"{random.randrange(0,15)}"])

    sys.exit(0)


Результат запуска мы видим системные вызовы `vfork <https://man7.org/linux/man-pages/man2/vfork.2.html>`_ в котором 
идет запуск `execve("/usr/bin/sleep"... <https://man7.org/linux/man-pages/man2/execve.2.html>`_ и родителю передается 
ожидание выпонения `wait4(8644,... <https://man7.org/linux/man-pages/man2/wait4.2.html>`_

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

Никакой неожиданости, как и ожидалось был вызван системный вызов `vfork`, который более эффективно работает чем `fork`, 
за счет отсутсвия копирования страниц памяти. Вместо этого потомок и родитель делят память до тех пор, пока один из них
не выполнит успешный вызов `exec()` или `_exit()`.

thread
------

.. code-block:: python

    #!/usr/bin/env python3

    '''
        Пример №3:
        Создание thread
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

Результатом будет вызов `clone3 <https://man7.org/linux/man-pages/man2/clone3.2.html>`_, который результатом вернул 
номер PID нового процесса. Вызов `clone3` очень похож на вызов `fork`, т.е. создается отдельный процесс, 
но позволяет контролировать этапы создания процесса, на основе переданных `flags`

По переданым флагам мы можем сразу увидить

* Родитель и потомок разделяют виртуальную память(`CLONE_VM`)
* Родитель и потомок разделяют атрибуты, относящиеся к файловой системе(`CLONE_FS`)
* Родитель и потомок разделяют таблицу дескрипторов открытых файлов(`CLONE_FILES`)
* Помещает потомка в одну группу потоков выполнения с его родителем(`CLONE_THREAD`)

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

    С помощью фильтра `%process` мы можем определить как в приложении организована многопоточность.

Вернемся к `nginx`, видим что используется `clone` без общего доступа к памяти, что логично, не нужно бороться за общие ресурсы

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

Строка запуска
==============

Одной из задач, использования `strace`, может послужить для отладки `bash` скриптов. К примеру будет сложновато, глазами
или с ипользованием debug режима, проанализировать скрипт на 4500 строк, как например 
`Node Version Manager <https://github.com/nvm-sh/nvm/blob/master/nvm.sh>`_.

Для примера напишем простой скрипт на `bash`

.. code-block:: bash

    #!/bin/bash

    eval $(printf "\145\143\150\157\40\42\110\145\154\154\157\42")
    eval $(echo "dt" | sed 's/t/ate/')
    eval $(echo "bHMK" | base64 -d)

Сложно с превого взгляда определить что же все таки будет выполнять данный скрипт, давайте пропустим его выполнение через
`strace` и посмотрим на результат

.. code-block:: bash

    $> strace --trace=execve -f 04/main.sh 2>&1 | grep execve
    execve("04/main.sh", ["04/main.sh"], 0x7ffc0a9ebdc0 /* 39 vars */) = 0
    [pid  4799] execve("/usr/bin/date", ["date"], 0x5e11f9af7120 /* 38 vars */) = 0
    [pid  4802] execve("/usr/bin/sed", ["sed", "s/t/ate/"], 0x5e11f9af7120 /* 38 vars */) = 0
    [pid  4803] execve("/usr/bin/date", ["date"], 0x5e11f9af7120 /* 38 vars */) = 0
    [pid  4806] execve("/usr/bin/base64", ["base64", "-d"], 0x5e11f9af7120 /* 38 vars */) = 0
    [pid  4807] execve("/usr/bin/date", ["date"], 0x5e11f9af7120 /* 38 vars */) = 0

Если добавим еще и ключ `-v` то получим результат еще и с передаными аргументами.

Создание сокетов или отправка данных
====================================

Для того что бы не придумывать код возьмем его пример из документации 
`Python Socket Programming: Server and Client Example Guide <https://www.digitalocean.com/community/tutorials/python-socket-programming-server-client>`_ 
от `digitalocean.com`.

Приложение очень простое, поднимается серверная часть, к которой подключается клиент и отправляет сообщение.

.. code-block:: python

    #!/usr/bin/env python3

    import socket

    def server_program():
        # get the hostname
        host = socket.gethostname()
        port = 5000  # initiate port no above 1024

        server_socket = socket.socket()  # get instance
        # look closely. The bind() function takes tuple as argument
        server_socket.bind((host, port))  # bind host address and port together

        # configure how many client the server can listen simultaneously
        server_socket.listen(2)
        conn, address = server_socket.accept()  # accept new connection
        while True:
            # receive data stream. it won't accept data packet greater than 1024 bytes
            data = conn.recv(1024).decode()
            if not data:
                # if data is not received break
                break
        conn.close()  # close the connection


    if __name__ == '__main__':
        server_program()


.. code-block:: python

    #!/usr/bin/env python3

    import socket

    def client_program():
        host = socket.gethostname()  # as both code is running on same pc
        port = 5000  # socket server port number

        client_socket = socket.socket()  # instantiate
        client_socket.connect((host, port))  # connect to the server

        message = 'data'

        client_socket.send(message.encode())  # send message
        client_socket.close()  # close the connection


    if __name__ == '__main__':
        client_program()

Запустим серверную и клиентскую часть и посмотрим какие полезные данные мы можем получить, анализирую только системные вызовы

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


* `bind` - Системный вызов привязывает сокет к конкретному IP-адресу и порту на твоей машине. Это его "прописка". После этого сокет "знает", по какому адресу ему принимать входящие соединения или откуда отправлять исходящие. Параметры нам показывают какой адрес и порт будет слушать приложение.
* `listen` - Перевели созданый сокет в режим ожидания входящих сообщений
* `accept4` - Извлекаем первый запрос на подключение из очереди ожидающих подключений для прослушиваемого сокета и создаём новый подключенный сокет. В параметрах данного вызова у нас будет информаци о клиенте.
* `recvfrom` - Получили отправленые данные

.. code-block:: bash

    $> strace -v --trace=socket,connect,sendto,recvfrom -z python3 05/client_program.py 
    socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_IP) = 3
    ...
    connect(3, {sa_family=AF_INET, sin_port=htons(5000), sin_addr=inet_addr("127.0.1.1")}, 16) = 0
    sendto(3, "data", 4, 0, NULL, 0)        = 4
    +++ exited with 0 +++

Со стороны клиента немного по проще вывод

* `connect` - После создания сокета, всю работу по созданию TCP соединению берет на себя данный системный вызов, в параметрах передается адрес сервера
* `sendto` - Отправляем данные

Конечно сложно представить проведения отладки высоконагруженного сетевого приложения, но без данного примера мне казалось 
статья будет не полной.

Получение статистики по syscall
===============================

В качестве бонуса запуск с ключём `-c` который просто выведет статистику по использованию системных вызовов

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


Заключение
==========

`strace` — незаменимый инструмент для диагностики и отладки приложений в Linux, особенно когда стандартные логи не дают
ответа на вопрос "почему не работает?". Надеюсь данная статья будет полезна, и поможет кому нибудь в будующем починить прод
ну или хотя бы пройти собеседование. **Всем удачи.**
