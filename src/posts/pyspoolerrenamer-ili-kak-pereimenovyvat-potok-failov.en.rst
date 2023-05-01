.. title: pySpoolerRenamer — or how to rename a file stream
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

**Hello my friend!**

Working with large data streams and analyzing them, you face a problem
determining the ownership of the file, its source, since 99% of all flows
generate soulless electric machines.

Sometimes it can be difficult to determine where the sasder345asd.txt or
123_HDR-Tas.csv file came from (in fact, this is just a set of letters,
in most cases the file names have a structured name, but this is still hard
to read for a person).

.. TEASER_END

Initially, the solution was a small set of bash scripts for elementary renaming
of files, everything changed when the number of threads increased dramatically.
And a deeper hierarchy of unloading directories appeared, for example:

before

    vendor/filename

became

    region/point_id/data_name/filename

and using scripts didn't help anymore.

As always, python came to the rescue, in a few hours a script was prepared
that coped with this function. After going through several iterations of fixes,
improvements and 2 years of work in production, I am ready to provide this
utility to the public - pySpoolerRenamer_

