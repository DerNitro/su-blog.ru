.. title: pyRsyncBackup
.. slug: pyrsyncbackup
.. date: 2020-02-10 12:00:00 UTC+03:00
.. tags: linux, python, pyRsyncBackup, backup
.. category: backup
.. link:
.. description:
.. type: text
.. author: Sergey <DerNitro> Utkin
.. previewimage: /images/posts/pyrsyncbackup/everyday-basics-cLXI3dVvqEY-unsplash.jpg


.. _Everyday basics: https://unsplash.com/@zanardi?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText
.. _Unsplash: https://unsplash.com/s/photos/storage?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText
.. _pyRsyncBackup: https://github.com/DerNitro/pyRsyncBackup

.. |PostImage| image:: /images/posts/pyrsyncbackup/everyday-basics-cLXI3dVvqEY-unsplash.jpg
    :width: 40%
    :target: `Everyday basics`_

.. |PostImageTitle| replace:: Photo by `Everyday basics`_ on Unsplash_


|PostImage|

|PostImageTitle|

**Доброго времени суток, случайный читатель!**

И так о чем хочу рассказать сегодня, в недрах одного небольшого отдела,
одной небольшой компании родился небольшой скрипт — и назвали этот
скрипт pyRsyncBackup_

Для чего?! Задача была следующая:
 * Резервное копирование конфигурационных файлов.
 * Инициатор должен быть из вне. Т.к. NAT.
 * Не до всех узлов есть прямой доступ.

Сначала был создан прототип, который выполнял все эти функции, работал по крону
и все были довольны, пока количество серверов не перевалило за overdohuya.
+ выход нового софта добавлял работы по переконфигурации бекапов.

От сюда вылезли еще требования:
 * Автообнаружение модулей резервного копирования.
 * Работа в режиме демона.

Что и было реализовано в текущей версии pyRsyncBackup_, и так что она позволяет:
 * run as daemon.
 * Автообнаружение модулей резервного копирования.
 * Резервное копирование через промежуточные узлы.

Что ждать дальше:
 * уход от СУБД PostgreSQL, возможно в память, возможно в SQLite.
 * переработка функционала proxy, т.к. часть хостов отстреливает SSH подключения(PAM)
 * Веб интерфейс для забора backup файлов

Но данными доработками займусь, после создания прототипа системы контроля
доступа, если хватит сил и времени, то возможно и в этом году.

Спасибо.
