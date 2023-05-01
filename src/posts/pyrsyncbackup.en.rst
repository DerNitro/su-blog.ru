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

**Good day, casual reader!**

And so what I want to tell you today, in the depths of one small department, one small company, a small
script - and named this script pyRsyncBackup_

For what?! The task was as follows:
 * Backing up configuration files.
 * The initiator must be from outside. Because NAT.
 * Not all nodes have direct access.

First, a prototype was created that performed all these functions, worked on CRON and everyone was happy while
the number of servers did not exceed overdohuya. + the release of the new software added work on reconfiguring
pyRsyncBackup_.

More requirements have appeared:
 * Auto detection of backup modules.
 * Working in Linux daemon mode.

Which was implemented in the current version pyRsyncBackup_:
 * run as daemon.
 * Auto detection of backup modules.
 * Backing up via intermediate nodes.

What to expect next:
 * moving away from PostgreSQL, possibly into memory, perhaps into SQLite.
 * redesign of the proxy functionality, since some hosts shoot SSH connections (PAM)
 * Web interface for collecting backup files

But I will deal with these improvements, after creating a prototype of the access control system,
if I have enough time and energy, then
possibly this year as well.

Thank you.
