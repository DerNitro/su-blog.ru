.. title: Парсим ini files
.. slug: parse-ini-file
.. date: 2021-03-02 07:27:07 UTC+03:00
.. tags: linux, python
.. category: utils
.. link:
.. description:
.. type: text
.. author: Sergey <DerNitro> Utkin
.. previewimage: /images/posts/ini-file/sincerely-media-m8GQrw9dop0-unsplash.jpg


.. _Sincerely Media: https://unsplash.com/@sincerelymedia?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText
.. _Unsplash: https://unsplash.com/s/photos/file?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText
.. _ini-file: https://github.com/DerNitro/ini-file

.. |PostImage| image:: /images/posts/ini-file/sincerely-media-m8GQrw9dop0-unsplash.jpg
    :width: 40%
    :target: `Sincerely Media`_

.. |PostImageTitle| replace:: Photo by `Sincerely Media`_ on Unsplash_

|PostImage|

|PostImageTitle|

Добрый день случайный читатель.

В рамках одного проекта потребовалось получить значение переменной из ini файла.

И вроде как решение простое, однострочный скрипт ввида:

.. code-block:: bash

    grep dbname db.conf | awk -F '=' '{ print $2 }'

Но что делать если значений будет несколько в разных секциях?
То уже в однострочный скрипт не уложишься.

Поиск решения для linux результатов не дал :(, хотя может быть я просто ленивый
и не все результаты поиска просмотрел.

Решение было принято быстро, берем Python и пакет ``configparser``. Результат
ini-file_.
