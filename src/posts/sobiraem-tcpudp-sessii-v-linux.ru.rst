.. title: Собираем TCP|UDP сессии в Linux
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

Приветствую тебя мой дорогой друг!

Как говорится “назвался компьютерщиком, полезай в ИТ отдел”.

Преамбула
=========

Попался мне как то на глаза скрипт, для сбора всех соединений по хосту, ну что
идея хорошая, запилили в zabbix, ждем… 5 минут… 10 минут… Нет значений.

Ошибка поразила, скрипт не смог уложится в отведенные, 30 секунд.

    Тут по идее должна быть картинка типа: “30 секунд, Карл!!!”.

Не буду описывать свое удивление когда я прочитал скрипт, вкратце это кровь из
глаз, куча матерных слов и истеричный смех, т.к. использовалось куча внешних
утилит, это все парсилось, накладывались regexp и т.д. и т.п.
И это все на Linux, где получить любое значение можно просто прочитав **файл**!!!

.. TEASER_END

Начнем…
=======

Как я написал выше, для получения значений нам нужно прочитать файл, но какой!?
Идем искать ответ.

Читаем ТЗ, нам нужно:
 - IP\|PORT источника и IP\|PORT назначения для TCP|UDP
 - Процесс, который сгенерировал это подключение
 - Отображать нужно только LISTEN и ESTABLISHED

Отлично, можно начинать.

Список TCP|UDP
--------------
За что я люблю Linux системы, это за то что в нем все, это “Файл”:
 - Файл -> Файл
 - Директория -> Файл
 - Устройство -> Файл
 - Сокет -> Файл
 - …

Информация о всех TCP/UDP сессиях так находится в файлах в /proc/net/tcp[6]
и /proc/net/udp[6].

.. code-block:: bash

    sl local_address rem_address  st tx_queue rx_queue tr tm->when retrnsmt  uid timeout inode
    0: 0100007F:1B1E 00000000:0000 0A 00000000:00000000 00:00000000 00000000 1000    0 53620300 1 0000000000000000 100 0 0 10 0
    1: 0100007F:DFFF 00000000:0000 0A 00000000:00000000 00:00000000 00000000 1000    0 46149718 1 0000000000000000 100 0 0 10 0
    2: 0100007F:77CA 00000000:0000 0A 00000000:00000000 00:00000000 00000000 1000    0 52642353 1 0000000000000000 100 0 0 10 0

По структуре данного формата можно обратится к документации по ядру
`linux <https://www.kernel.org/doc/Documentation/networking/proc_net_tcp.txt>`_

В данной структуре есть практически все, кроме принадлежности к процессу,
чего нам не хватает для реализации ТЗ.

Процессы
--------
Всю информацию о процессе, где можно получить… Правильно из файлов :)

В том числе и об открытых сокетах, которая хранится в */proc/PID/fd/*.

Вот к примеру:

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

Т.е. из данного списка мы можем спокойно забрать только socket, где числовое
значение будет значение inode.

Информацию об имени и pid можно получить из */proc/PID/status*.

Итого
=====
Прочитав несколько файлов и объединив информацию, о сессиях и процессах,
по ключу inode, мы получаем всю нужную информацию.

Т.к. файловая система proc располагается в RAM, то мы не упираемся в очереди
блочных устройств, и получаем информацию максимально быстро.

Получившийся cкрипт можно взять в
`pyTcpProcess <https://github.com/DerNitro/pyTcpProcess>`_

Что удалось добиться, увеличение скорости с 32 секунд, до 0,3 секунд.
Что я считаю хорошим показателем.

Спасибо за внимание.
