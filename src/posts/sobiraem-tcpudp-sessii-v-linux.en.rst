.. title: Collect TCP|UDP sessions in Linux
.. slug: tcpudp-sessii-v-linux
.. date: 2020-04-12 12:00:00 UTC+03:00
.. tags: linux, network, python, TCP, UDP
.. category: monitoring
.. link:
.. description:
.. type: text
.. author: Sergey <DerNitro> Utkin
.. previewimage: /images/posts/tcpudp-sessii-v-linux/hans-peter-gauster-3y1zF4hIPCg-unsplash.jpg


.. _Hans-Peter Gauster: https://unsplash.com/@sloppyperfectionist?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText
.. _Unsplash: https://unsplash.com/s/photos/network?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText

.. |PostImage| image:: /images/posts/tcpudp-sessii-v-linux/hans-peter-gauster-3y1zF4hIPCg-unsplash.jpg
    :width: 40%
    :target: `Hans-Peter Gauster`_

.. |PostImageTitle| replace:: Photo by `Hans-Peter Gauster`_ on Unsplash_


|PostImage|

|PostImageTitle|

Hello my friend!

As the saying goes, "he called himself a computer technician, get into
the IT department."

Preamble
========

Somehow I caught sight of a script to collect all connections on the host, well,
that is a good idea, we put it in a zabbix, wait ... 5 minutes ... 10 minutes ...
No values.

The error struck, the script could not keep within the allotted 30 seconds.

I will not describe my surprise when I read the script. a bunch of external
utilities were used, regexp was superimposed, etc.

And that's all on Linux, where you can get any value simply by reading
**file**!!!

.. TEASER_END

Let's start…
============

As I wrote above, to get the values we need to read the file, but which one!?
Let's go look for the answer.

We read the terms of reference, we need:
 - Source IP\|PORT and destination IP\|PORT for TCP|UDP
 - The process that generated this connection
 - Only the LISTEN and ESTABLISHED statuses need to be displayed

Great, you can start.

TCP | UDP List
--------------
For what I love Linux systems, the fact that everything in it is "File":
 - File -> File
 - Folder -> File
 - Device -> File
 - Socket -> File
 - …

Information about all TCP/UDP sessions is in the files /proc/net/tcp[6]
and /proc/net/udp[6].

.. code-block:: bash

    sl local_address rem_address  st tx_queue rx_queue tr tm->when retrnsmt  uid timeout inode
    0: 0100007F:1B1E 00000000:0000 0A 00000000:00000000 00:00000000 00000000 1000    0 53620300 1 0000000000000000 100 0 0 10 0
    1: 0100007F:DFFF 00000000:0000 0A 00000000:00000000 00:00000000 00000000 1000    0 46149718 1 0000000000000000 100 0 0 10 0
    2: 0100007F:77CA 00000000:0000 0A 00000000:00000000 00:00000000 00000000 1000    0 52642353 1 0000000000000000 100 0 0 10 0

For the structure of this format, you can refer to the documentation for the kernel
`linux <https://www.kernel.org/doc/Documentation/networking/proc_net_tcp.txt>`_

This structure contains almost everything, except for belonging to the process,
which we lack for implementation.

Processes
---------

All information about the process, where you can get ... Right from the files :)

Including about open sockets, which is stored in */proc/PID/fd/*.

For example:

.. code-block:: bash

    sergey@steel /proc/16381/fd $ for i in $(ls); do readlink $i;done
    /dev/null
    /dev/null
    socket:[49244920]
    /dev/urandom
    socket:[49244917]
    socket:[49245354]
    socket:[49244939]
    socket:[49244941]
    socket:[49234589]
    pipe:[49245313]
    pipe:[49244937]
    pipe:[49244937]

From this list, we can safely pick only socket, where the numerical value will
be the inode value.

Name and PID information can be obtained from */proc/PID/status*.

Conclusion
==========

After reading several files and combining information about sessions and
processes, using the inode key, we get all the information we need.

Because the proc file system is located in RAM, then we do not run into the
queue of block devices, and we receive information as quickly as possible.

The resulting script can be taken in
`pyTcpProcess <https://github.com/DerNitro/pyTcpProcess>`_

What was achieved was an increase in speed from 32 seconds to 0.3 seconds.
Which I think is a good indicator.

Thanks for attention.
