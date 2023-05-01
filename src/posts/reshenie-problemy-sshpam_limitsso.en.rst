.. title: Solution to the problem SSH(pam_limits.so)
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


Colleagues, good afternoon!

Having worked in support since 2007, I faced many problems,
one of which I would like to talk about.

Introduction
============

One Friday at the end of the working day, a message is received about errors
from one production server serving clients from Kaliningrad to Sakhalin.

A quick analysis of the server status showed that the problem is only with
triggers that call the Bash shell to run, which seemed very strange.
The second oddity seemed that the server was in production, and the problem
had been fixed for about 30 minutes, there were no user requests!
A survey of colleagues in a working chat, determined that today on this server
they solved the problem with “too many open files” and solved it.
We launch an SSH session on the server, and ... NO connection !!!

.. TEASER_END

Problem
=======

Analysis of the SSH client logs showed that the channel breaks when trying
to start the command interpreter, i.e. authorization and authentication goes
through, but the console does not start.
Connecting via iLo - the result is the same.

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


Solution
========

The first search results came up with a solution - Disable PAM.

.. image:: /images/posts/sshpam_limitsso/2020-12-24_06-37-06.png
    :width: 40%

And change /etc/security/limits.conf

.. image:: /images/posts/sshpam_limitsso/2020-12-24_06-37.png
    :width: 60%

After gaining access to the server (restart and LiveCD) we were surprised,
there are no lifted limits!

What happened
=============

The SSH connection to the server can be broken down into the following steps:
 * Authorization/Authentication
 * Starting a command shell
 * Allocating resources to the user

At the last step, the problem arose, it is responsible for this -
**pam_limits.so**.

**pam_limits** serves to allocate resources to the user,
the setrlimit system call is launched, in addition to allocating restrictions
on CPU and RAM, the maximum number of open files is also allocated.
The strace log confirmed that an error occurs when allocating NOFILE resources:

    ``setrlimit(RLIMIT_NOFILE, {rlim_cur=1685744, rlim_max=16815744}) = -1``

We understand that the value 1685744 (/etc/security/limits.conf) is not correct,
but we do not understand why.

The next hour, solving the problem, was devoted to studying the documentation
and the Internet, and this is what we learned:
The value set in setrlimit for NOFILE should not exceed the value
/proc/sys/fs/nr_open core, our value was almost 3 times higher.

**Aligning the values, the problem was solved.**

Why did it happen?
==================

When solving the error “too many open files”, the parameter was increased based
on the value of /proc/sys/fs/file-max, as well as this value was added to
the file /etc/security/limits.conf which exceeded /proc/sys/fs/nr_open.

Why can this happen to me?
==========================
1. `for example <https://discuss.elastic.co/t/too-many-open-files/14304/5>`_
2. On my machine on which I am typing this text now

.. code-block:: bash

    sergey@steel ~ $ cat /proc/sys/fs/file-max
    9223372036854775807
    sergey@steel ~ $ sudo cat /proc/sys/fs/nr_open
    1048576

Conclusions
===========
**file-max & file-nr**:

The value in file-max denotes the maximum number of file-
handles that the Linux kernel will allocate. When you get lots
of error messages about running out of file handles, you might
want to increase this limit.

**nr_open**:

This denotes the maximum number of file-handles a process can
allocate. Default value is 1024*1024 (1048576) which should be
enough for most machines. Actual limit depends on RLIMIT_NOFILE
resource limit.

**pam_limits.so**  - uses *setrlimit*, to allocate resources to the user,
which in turn uses the kernel's nr_open value to determine the maximum value
for file descriptors.
What other applications use the *setrlimit* call is not known,
so **BE CAREFUL ON DEPLOYING !!!**
