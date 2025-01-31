.. title: pyRMA or how I wrote an access system
.. slug: pyrma-ili-kak-ia-pisal-sistemu-dostupa
.. date: 2025-01-31 00:00:00 UTC+03:00
.. tags: ssh, security, pyrma, remote access
.. category: linux
.. link: 
.. description: pyRMA - Remote access control system for server and network equipment via SSH and TELNET protocols.
.. type: text
.. author: Sergey <DerNitro> Utkin
.. previewimage: /images/posts/pyrma-ili-kak-ia-pisal-sistemu-dostupa/patrick-robert-doyle--XiKxvvFGgU-unsplash.jpg

.. _Patrick Robert Doyle: https://unsplash.com/@teapowered?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash
.. _Unsplash: https://unsplash.com/photos/a-red-and-white-sign-sitting-on-the-side-of-a-road--XiKxvvFGgU?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash

.. |PostImage| image:: /images/posts/pyrma-ili-kak-ia-pisal-sistemu-dostupa/patrick-robert-doyle--XiKxvvFGgU-unsplash.jpg
    :width: 40%
    :target: `Patrick Robert Doyle`_

.. |PostImageTitle| replace:: Photo by `Patrick Robert Doyle`_ on Unsplash_

.. _Python: https://www.python.org/
.. |Python| replace:: **Python**

.. _pyRMA: https://github.com/DerNitro/pyRMA
.. |pyRMA| replace:: **pyRMA**

.. _npyscreen: https://github.com/npcole/npyscreen
.. |npyscreen| replace:: npyscreen

.. _alembic: https://alembic.sqlalchemy.org/en/latest/tutorial.html
.. |alembic| replace:: alembic

.. _Linux PAM: https://www.man7.org/linux/man-pages/man8/pam.8.html
.. |Linux PAM| replace:: Linux PAM

.. _python-pam: https://pypi.org/project/python-pam/
.. |python-pam| replace:: python-pam


|PostImage|

|PostImageTitle|

------

2014. I am a young and promising technical support engineer and I was assigned to assist my senior colleague in creating
an access control system for our clients' hardware and software systems.

The concept was simple: set up an `"SSH jump"` node where the desired client node could be selected via the CLI.
The system would record who connected, where, and when, and based on this data, it would be possible to reconstruct the
picture if something suddenly went wrong on the client systems.

The solution was ready, on `freebsd` using native `jail <https://docs.freebsd.org/en/books/handbook/jails/#classic-jail>`_
and CLI based on bash script. But when submitting user load - problems arose, and the system became inoperative, 
I don't remember the details, but they were related to locks when working with the database, which was on
`sqlite <https://www.sqlite.org/>`_.

While the senior engineer was tweaking the bash scripts, I wrote my own python interpretation of the problem, which worked,
and I was given carte blanche to improve it. Development of the freebsd solution was stopped.

Years passed, the solution worked, but the code written "on the knee" created a huge technical debt, and at some point, 
the development of the system became impossible. It was time to rewrite and `share the code <https://github.com/DerNitro/pyRMA>`_
with the world.

Well, let's see what came out of it.

.. note::

    I am not a real programmer, so I do not claim that:

    * The system architecture is perfect
    * The code is written professionally
    * The system is secure
    * etc

    But creating this system helped me develop my skills, which helped me in my future work.

.. TEASER_END

Requirements
============

Over several years of operation of the first version of the access system, a list of requirements was determined:

1. Connect to client systems via SSH and Telnet protocols, including `Jump host <https://www.ssh.com/academy/ssh/command#ssh-command-line-options>`_ support
#. Restricting access to client systems for a user or group of users
#. Ability to request and approve access to user client systems
#. Ability to transfer/download files from client systems
#. Possibility of TCP/UDP port forwarding to client systems
#. Possibility of connection to the client equipment management interface
#. Ability to view user session
#. Separation of roles [1]_ of user, operator and administrator of the access system

Description of the system
=========================

As mentioned earlier, the system code is written in |Python|_ and consists of the following elements:

* Connection console
* Data transfer console
* WEB console
* iptables rules management module
* PostgreSQL Database

At its core, the system is a "single entry point" that allows the user to select the host of interest and connect to it.

.. image:: /images/posts/pyrma-ili-kak-ia-pisal-sistemu-dostupa/pyrma.png

The user scenario looks like this:

1. The user connects to the access system via the SSH protocol.
#. The user attribute based access system determines whether a user can have access; if the user is connecting for the 
   first time, an access request is generated and sent to the system administrator for approval.
#. After successfully connecting to the system, the console interface will be launched, which will display a list of all registered nodes.
#. The user selects the desired node and can choose several types of actions:
  
    * Connect to the node using `SSH` or `Telnet` protocol
    * Connect to the node in file transfer mode
    * Connect only `Services` to node [2]_

#. If the user is not allowed to connect, an access request will be created and sent to the operator for approval.
#. After the user's connection to the node is complete, session information, TTY console recording, and network traffic
   dumps will be saved in the access system and available for viewing by the administrator and system operator.

System pyRMA
============

Connecting to pyRMA
-------------------

Connection to the system is carried out via the SSH protocol, and it was necessary to resolve several issues at once

1. Authentication of users who should get directly into the access system, and who into the command interpreter of the operating system.
#. Launching the console interface of the access system
#. Recording a TTY session

The first attempt to organize user authentication was based on the `pam-pgsql <https://github.com/pam-pgsql/pam-pgsql>`_
project, which allows storing user data in the PostgreSQL DBMS, but this solution had to be abandoned, as it required
large investments, such as:

* Ensuring information security when storing user data in a DBMS
* Development of a mechanism for synchronization with corporate systems `Directory Services`
* `pam-pgsql` is a half-dead project, there are unresolved tickets with problems from 2016, there is a big risk of
  rewriting part of the authentication in the system.

The solution was to leave authorization on |Linux PAM|_, when connecting via SSH PAM is enabled by the parameter
``UsePAM yes``, and for the web interface the module |python-pam|_ is used, which allowed leaving the source of data
for authentication at the discretion of the system administrator.

For further work with user data, we obtain information about the user and his groups through the capabilities of
the standard library |Python|_ `pwd — Password database <https://docs.python.org/3.8/library/pwd.html>`_ and
`grp — Group database <https://docs.python.org/3.8/library/grp.html>`_, based on the user's groups,
the system determines access rights and display of information.

After passing authentication and authorization, we need to launch the access system interface, for this we will replace
the command interpreter with launching our console.

`SSHD <https://man7.org/linux/man-pages/man5/sshd_config.5.html>`_ allows users to override the startup command on connection.

.. note::

    ForceCommand
        Forces the execution of the command specified by
        ForceCommand, ignoring any command supplied by the client
        and ~/.ssh/rc if present.  The command is invoked by
        using the user's login shell with the -c option.  This
        applies to shell, command, or subsystem execution.  It is
        most useful inside a Match block.  The command originally
        supplied by the client is available in the
        SSH_ORIGINAL_COMMAND environment variable.  Specifying a
        command of internal-sftp will force the use of an in-
        process SFTP server that requires no support files when
        used with ChrootDirectory.  The default is none.

Let's override this setting for all users except system administrators.

.. code-block::

    Match User *,!acs,!root
        ForceCommand /srv/acs/bin/pyrma.sh
        AllowTcpForwarding no
        X11Forwarding no

and add the redefined interpreter to the trusted ``/etc/shells`` list. Now all users connecting via SSH will get into our script,
which will launch the console interface of the access system and record the TTY session.

As a utility for capturing the user's terminal, the choice fell on `asciinema <https://docs.asciinema.org/>`_.
At the time of development, it had a number of advantages:

* Active development of the project
* The repository contains an APT package for Linux Ubuntu 20.04 OS
* There is an embedded HTML player, which is successfully integrated into the WEB interface.
* Recording the stdin channel allowed us to analyze the input commands
* Passing a shell command to write

Thanks to the last point we launch the access system interface.

Connection interface
--------------------

Immediately after connecting to the access system, the console interface is launched.

--------

.. image:: /images/posts/pyrma-ili-kak-ia-pisal-sistemu-dostupa/cli.gif

--------

The |npyscreen|_ library was used to create the interface. At the time of writing, the |pyRMA|_ project was more active than it is now.

The library has great capabilities for creating a multi-window application, a huge number of widgets, as well as
the ability to create your own, allows you to create an interface for any taste.

Implemented functionality:

* List of nodes with the ability to search and filter elements
* Displaying node information
* Request access to connect to a node

File Transfer Interface
-----------------------

Clicking the "File Transfer" button in the console application launches the file transfer interface.

--------

.. image:: /images/posts/pyrma-ili-kak-ia-pisal-sistemu-dostupa/ft.gif

--------

The display interface is also written in |npyscreen|_. To list and transfer files I used `pysftp <https://pypi.org/project/pysftp/>`_.

.. note::

  To start data transfer, the user needs to upload the file to the access system via the SFTP protocol,
  after which it will become available in the interface.

One of the tasks was to store information about transferred files, both to the destination node and in the opposite direction.

This is implemented as follows:

1. The transferred file or directory is archived in ``tar.gz``
#. From the received archive we get the hash sum ``md5``
#. The presence of a given hash sum in the database is checked.
#. If the database contains a hash, a ``hard link`` to the found archive is created
#. If it is missing, the archive is transferred to the storage directory, and the corresponding entry is entered into the database.

By using ``hardlink`` and ``tar.gz`` we save space and do not duplicate data.

All transferred files are available in the "operator" interface and can be downloaded for analysis.

Connections
-----------

`Connection interface` returns a connection object (SSH, FTP, TELNET, etc.) on which the ``run()``, ``connection()``,
and ``close()`` functions are run.

* ``run()`` - starts the services required for the connection, enters connection information into the database, generates ``iptables`` rules.
* ``connection()`` - starts a connection directly, this can be either a child process or a separate console interface.
* ``close()`` - Closes all previously created services, connections and deletes ``iptables`` rules, updates connection information in the database.

When the connection is terminated, the TTY session record is also closed and is also available for viewing in the `operator` web interface.

SSH/TELNET
^^^^^^^^^^

Popular protocols for connection are implemented. Connection is performed by starting a child process, and if necessary,
a chain of ``Jump`` hosts is started.

SFTP
^^^^

A separate file transfer interface is launched and, if necessary, a connection chain is formed if the node is not directly accessible.

IPMI/iLo
^^^^^^^^

At the moment, viewing the recording is not available, but this type of connection is regulated by a separate set of user rights.
For the current connection, a recording of the user's network traffic will be launched, this dump will be available for
downloading through the `operator` interface.

Services
^^^^^^^^

Sometimes just connecting to the destination node is not enough, for example you need to connect to the database on
the node using locally installed software (e.g. `pgadmin <https://www.pgadmin.org/>`_).
The access system allows you to create and connect these services to nodes.

After connecting the service, the access system begins to register user traffic and becomes accessible from the operator's interface.

Database
--------

The database is used not only to store data but also to store the current state.

* Service Redirection Rules
* Network traffic recording rules

--------

.. image:: /images/posts/pyrma-ili-kak-ia-pisal-sistemu-dostupa/db.png

--------

To work with the database and access it, the ``ORM`` `SQLAlchemy <https://www.sqlalchemy.org/>`_ library is used.

.. note::

  Object–relational mapping (ORM, O/RM, and O/R mapping tool) in computer science is a programming technique
  for converting data between a relational database and the memory (usually the heap) of an object-oriented programming language.
  This creates, in effect, a virtual object database that can be used from within the programming language.

What I liked:

* Working with records/tables as objects
* Description of tables in code
* Integration with |alembic|_

The only thing I didn’t like was the high entry threshold.

For the initial filling of the database and update management, |alembic|_ is used, this is not a simple tool and also
requires learning, but it is worth it, the tool allows you to store the state of the database and when calling the
update |alembic|_ will automatically transfer the database to the current state.

Firewall
--------

One of the modules |pyRMA|_ is a network traffic management subsystem named after the
`iptables <https://linux.die.net/man/8/iptables>`_ rules management.

--------

.. image:: /images/posts/pyrma-ili-kak-ia-pisal-sistemu-dostupa/firewall.png

--------

This module runs as a system service. There is a separate table in the database where the current rules are entered,
the service collects these rules and updates the ``iptables`` rules.

This service also manages the recording of network traffic and the storage of information about it in the user session.

Web interface
-------------

Administration and viewing of the user session is carried out via the web interface. The web service is written in
`Flask <https://flask.palletsprojects.com/en/stable/>`_, the CSRF token mechanism is additionally integrated via
`Flask-WTF <https://pypi.org/project/Flask-WTF/>`_.

--------

.. image:: /images/posts/pyrma-ili-kak-ia-pisal-sistemu-dostupa/web_connection.png

--------

The web interface is available to all users, however access to information is only possible in accordance with the granted rights.

Since our system does not store authentication data and is completely tied to |Linux PAM|_, we also use this
authentication mechanism here. The |python-pam|_ module makes it easy to check authentication data

.. code-block:: python

  >>> import pam
  >>> p = pam.authenticate()
  >>> p.authenticate('user', 'correctpassword')
  True
  >>> p.authenticate('user', 'badpassword')
  False

The functions were also implemented through a web interface:

**monitoring**

Allows you to track the number of active connections, new users and pending connection requests.

.. code-block::

  in  > curl -u username:password -X GET http://pyrma:8080/api/monitor
  out > {
  out >     "active_connection": 0,
  out >     "new_user": 0,
  out >     "access_request": 0
  out > }

**Loading node data**

Creating nodes manually is fine, but if you have a lot of them, you can use upload, which requires a CSV file.

.. code-block::

  in  > curl -u username:password -X POST -H "Content-Type: multipart/form-data" -F 'file=@tests/eggs.csv' http://pyrma:8080/api/host/upload
  out > {
  out >     "status": "success",
  out >     "created host": 0,
  out >     "updated host": 1000,
  out >     "skipped host": 0
  out > }


User access rights
------------------

User rights are divided into 2 groups:

**connection:**

* Connecting to a node
* File transfer
* Connecting services together with connecting to a node
* Connecting services only
* Connecting to the server management interface

**Custom Actions:**

* View node information
* Editing node information
* Create/Edit Directories
* Moving nodes between directories
* Display login
* Display password
* View user session
* Access coordination
* Editing connection credentials

Rights are stored in the database as a single integer.

.. code-block::

  11100 = 28
  ││││└── Connecting to the server management interface
  │││└── Connecting services only
  ││└── Connecting services together with connecting to a node
  │└── File transfer
  └── Connecting to a node

This approach seemed more manageable to me, using logical addition for nested directories we get the final result of user rights

.. code-block::

  ROOT                                        00000
  └── Level1                                + 10000
      └── Level2                            + 01101
          └── Host1                         = 11101
                                              
In order for a user to be able to use the access system, a group to which the user belongs must be registered in the system.
For a registered group, you can set rights and grant access to all nodes or a group of nodes.

If the user does not have access to connect to the node, he can use the access system to generate an access request,
which the "operator" can accept or reject.

--------

.. image:: /images/posts/pyrma-ili-kak-ia-pisal-sistemu-dostupa/access_request.png

--------

Install
-------

For installation, an ``Ansible`` script was prepared, which completely performs the installation and startup of the access system.

Afterword
=========

The development of the current project lasted an indecently long time - 6 years, from 2016 to 2022.
Combining work for hire, family and solving everyday problems leaves no time for development.

That's why I decided to put the code on GitHub, maybe someone will be interested in these developments and start
contributing to the project or fork the repository.

--------

.. figure:: /images/posts/pyrma-ili-kak-ia-pisal-sistemu-dostupa/finish.webp
  :width: 40%
  :align: center
  
  ``Photo by ChatGPT``

--------

.. [1] The system itself does not have the entities “user”, “operator” and “administrator”, the division is carried out
       on the basis of the issued rights.
.. [2] Services in the access system are system software on the destination node that has a socket for connection via
       the TCP or UDP protocols.
