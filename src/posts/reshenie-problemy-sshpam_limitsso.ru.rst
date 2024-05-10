.. title: Решение проблемы SSH(pam_limits.so)
.. slug: sshpam_limitsso
.. date: 2020-03-16 12:00:00 UTC+03:00
.. tags: ssh, pam, linux
.. category: support
.. link:
.. description:
.. type: text
.. author: Sergey <DerNitro> Utkin
.. previewimage: /images/posts/sshpam_limitsso/florian-krumm-yLDabpoCL3s-unsplash.jpg


.. _Florian Krumm: https://unsplash.com/@floriankrumm?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText
.. _Unsplash: https://unsplash.com/s/photos/server?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText

.. |PostImage| image:: /images/posts/sshpam_limitsso/florian-krumm-yLDabpoCL3s-unsplash.jpg
    :width: 40%
    :target: `Florian Krumm`_

.. |PostImageTitle| replace:: Photo by `Florian Krumm`_ on Unsplash_


|PostImage|

|PostImageTitle|


Коллеги, добрый день!

Работая с 2007 года в технической поддержке, сталкивался со многими проблемами,
об одной из которой хотелось бы рассказать.

Введение.
=========

Как обычно ничего не предвещало беды, и в предвкушении выходных, в конце
рабочего дня приходит сообщение об ошибках работы триггеров мониторинга на
одном из боевых серверов обслуживающих клиентов от Калининграда до Сахалина.

Беглый анализ статуса сервера показал, что проблема только с триггерами,
которые для запуска вызывают оболочку Bash, что показалось очень странно.
Второй странностью показалось что сервер в Production, и проблема фиксировалась уже
около 30 минут, обращений пользователей не было!
Опрос коллег в рабочем чате, определил, что сегодня на этом сервере решали
проблему с “too many open files” и решили ее.
Запускаем SSH сессию на сервер, и… Подключения НЕТ!!!

.. TEASER_END

Проблема.
=========

Анализ логов SSH клиента показал, что канал рвется при попытке запуска
командного интерпретатора, то есть авторизация и аутентификация проходит, но
консоль не запускается. Подключение через iLo - результат тот же.

.. code-block:: bash

    [svutkin@vlg-jan-db01 ~]$ ssh 10.108.176.252 -l svutkin –vvv
    …
    debug1: Authentication succeeded (keyboard-interactive).
    Authenticated to 10.108.176.252 ([10.108.176.252]:22).
    debug2: shell request accepted on channel 0
    …
    * ********************************************************************
    * Welcome to ******************* running RedHat 7.4
    * Puppet hostgroup: Base/Oracle/RDBMS
    * AD OU: OU=DWH,OU=DB,OU=Linux,OU=UNIX,OU=Servers,DC=*******,DC=ru
    * This system supported by IT-Platform-OS-Unix@*********.
    * Run 'sudo -l' to view your privileges
    * ********************************************************************
    …
    debug2: channel 0: almost dead
    debug2: channel 0: gc: notify user
    debug2: channel 0: gc: user detached
    debug2: channel 0: send close
    debug3: send packet: type 97
    debug2: channel 0: is dead
    …
    debug1: Exit status 254


Решение
=======

Первые результаты, поисковых запросов, выдавали решение - Отключить PAM.

.. image:: /images/posts/sshpam_limitsso/2020-12-24_06-37-06.png
    :width: 40%

И привести в порядок лимиты /etc/security/limits.conf

.. image:: /images/posts/sshpam_limitsso/2020-12-24_06-37.png
    :width: 60%

Получив доступ на сервер(перезапуск и Live-CD) мы были удивлены, никаких
снятых лимитов нет!

Что произошло
=============

А произошло следующие, подключение по SSH к серверу можно разбить на следующие шаги:
 * Авторизация/Аутентификация
 * Запуск командной оболочки
 * Выделение ресурсов пользователю

Вот как раз на последнем шаге и возникла проблема,
отвечает за это - ``pam_limits.so``.

``pam_limits`` служит  для выделения ресурсов пользователю, запускается системный
вызов ``setrlimit``, помимо выделения ограничений по CPU и RAM, так же выделяется
максимальное количество открытых файлов, лог ``strace`` подтвердил что при
выделении ресурсов ``NOFILE`` происходит ошибка:

    ``setrlimit(RLIMIT_NOFILE, {rlim_cur=1685744, rlim_max=16815744}) = -1``

Понимаем что значение 1685744(/etc/security/limits.conf) не правильное,
но не понимаем почему.

Следующий час, решения проблемы, посвятили изучению документации и интернета,
и вот что мы узнали:
Значение выставляемые в ``setrlimit`` для ``NOFILE`` не должно превышать значение
/proc/sys/fs/nr_open ядра, наше значение превышало почти в 3 раза.

**Выровняв значения, проблема решилась.**

Почему так произошло?
=====================

При решение ошибки “too many open files” было выполнено увеличение параметра
на основе значения ``/proc/sys/fs/file-max``, а так же данное значение внесено
в файл ``/etc/security/limits.conf`` которое превышало ``/proc/sys/fs/nr_open``.

Почему это может произойти со мной?
===================================
1. `Например <https://discuss.elastic.co/t/too-many-open-files/14304/5>`_
2. На моей машине на которой сейчас набираю данный текст

.. code-block:: bash

    sergey@steel ~ $ cat /proc/sys/fs/file-max
    9223372036854775807
    sergey@steel ~ $ sudo cat /proc/sys/fs/nr_open
    1048576

Выводы
======
``file-max & file-nr``:

The value in file-max denotes the maximum number of file-
handles that the Linux kernel will allocate. When you get lots
of error messages about running out of file handles, you might
want to increase this limit.

``nr_open``:

This denotes the maximum number of file-handles a process can
allocate. Default value is 1024*1024 (1048576) which should be
enough for most machines. Actual limit depends on ``RLIMIT_NOFILE``
resource limit.

``pam_limits.so``  - использует ``setrlimit``, для выделения ресурсов
пользователю, который в свою очередь, использует значение ядра ``nr_open``,
для определения максимального значения файловых дескрипторов.
Какие еще приложения используют вызов ``setrlimit``, не известно,
так что **БУДЬТЕ ВНИМАТЕЛЬНЫ!!!**
