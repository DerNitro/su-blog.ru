.. title: pySpoolerRenamer — или как переименовывать поток файлов
.. slug: pyspoolerrenamer
.. date: 2020-03-03 12:00:00 UTC+03:00
.. tags: flow, python, linux
.. category: big data
.. link:
.. description:
.. type: text
.. author: Sergey <DerNitro> Utkin
.. previewimage: /images/posts/pyspoolerrenamer/ankush-minda-7KKQG0eB_TI-unsplash.jpg


.. _Ankush Minda: https://unsplash.com/@an_ku_sh?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText
.. _Unsplash: https://unsplash.com/s/photos/train?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText
.. _pySpoolerRenamer: https://github.com/DerNitro/pySpoolerRenamer

.. |PostImage| image:: /images/posts/pyspoolerrenamer/ankush-minda-7KKQG0eB_TI-unsplash.jpg
    :width: 40%
    :target: `Ankush Minda`_

.. |PostImageTitle| replace:: Photo by `Ankush Minda`_ on Unsplash_


|PostImage|

|PostImageTitle|

**Доброго времени суток, мой дорогой друг!**

Работая с большими потоками данных и их анализом, сталкиваешься с проблемой
определения принадлежности файла, его источника, т.к. 99% от всех потоков
генерируют бездушные электрические машины.

Порой бывает сложно определить откуда пришел файл sasder345asd.txt или
123_HDR-Tas.csv(на самом деле это просто набор букв, в большинстве случаев
имена файлов имеют структурированное имя, но это все равно тяжело читать
человеку).

.. TEASER_END

Изначально решение было небольшой набор bash скриптов для элементарного
переименования файлов, все изменилось когда количество потоков резко
увеличилось. И появилась более глубокая иерархия каталогов выгрузки, например:

было

    vendor/filename

стало

    region/point_id/data_name/filename

и использование скриптов уже не помогало.

На помощь как всегда пришел python, за несколько часов был подготовлен скрипт
который справлялся с данной функцией на ура.
Пройдя несколько итераций исправлений, доработок и 2х лет работы в проде, я
готов предоставить данную утилиту общественности, пользуйтесь и наслаждайтесь
pySpoolerRenamer_
