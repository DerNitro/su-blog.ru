.. title: Parsing ini files
.. slug: parse-ini-file
.. date: 2021-03-02 07:27:07 UTC+03:00
.. tags: linux, python
.. category: utils
.. link:
.. description:
.. type: text
.. author: Sergey <DerNitro> Utkin
.. previewimage: /images/posts/ini-file/sincerely-media-m8GQrw9dop0-unsplash.jpg
.. medium: yes


.. _Sincerely Media: https://unsplash.com/@sincerelymedia?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText
.. _Unsplash: https://unsplash.com/s/photos/file?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText
.. _ini-file: https://github.com/DerNitro/ini-file

.. |PostImage| image:: /images/posts/ini-file/sincerely-media-m8GQrw9dop0-unsplash.jpg
    :width: 40%
    :target: `Sincerely Media`_

.. |PostImageTitle| replace:: Photo by `Sincerely Media`_ on Unsplash_

|PostImage|

|PostImageTitle|

Good afternoon, casual reader.

For one project, it was required to get the value of a variable
from an ini file.

And it seems like the solution is simple, a one-line script like:

.. code-block:: bash

    grep dbname db.conf | awk -F '=' '{ print $2 }'

But what if there are several values in different sections?
Then a one-line script will not work anymore.

Search for a solution for linux gave no results :(,
although maybe I'm just lazy and have not looked through all the search results.

The decision was made quickly, we take Python and the ``configparser`` package.
Result ini-file_.
