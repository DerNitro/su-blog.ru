.. title: pyRegistryStore - Or how to create a register of objects
.. slug: pyregistrystore-or-how-to-create-a-register-of-objects
.. date: 2021-07-15 07:39:24 UTC+03:00
.. tags: linux, devops, python
.. category: utils
.. link:
.. description:
.. type: text
.. author: Sergey <DerNitro> Utkin
.. previewimage: /images/posts/pyregistrystore/alfons-morales-YLSwjSy7stw-unsplash.jpg


.. |ss| raw:: html

    <strike>

.. |se| raw:: html

    </strike>


.. _Alfons Morales: https://unsplash.com/@alfonsmc10?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText
.. _Unsplash: https://unsplash.com/s/photos/bookshelf?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText
.. _pyRegistryStore: https://github.com/DerNitro/pyRegistryStore
.. _PyYAML: https://pypi.org/project/PyYAML/
.. _Molecula: https://molecule.readthedocs.io/en/latest/

.. |PostImage| image:: /images/posts/pyregistrystore/alfons-morales-YLSwjSy7stw-unsplash.jpg
    :width: 40%
    :target: `Alfons Morales`_

.. |PostImageTitle| replace:: Photo by `Alfons Morales`_ on Unsplash_

|PostImage|

|PostImageTitle|

Good afternoon colleague!

The history of the creation of this post is very interesting, it all started with the fact that I planned to write
a little about the PyYAML library and how we domesticated it, but something went wrong, and all this resulted in
the creation of a utility pyRegistryStore_

Let's go...

.. TEASER_END

Starting...
===========
Any CI / CD automation has reference books, registries, test environments, analyzers, source code control systems,
and this is all controlled by the orchestrator.

Our small group prepares and tests images of virtual machines + development of Ansible roles for installing
the necessary software according to the role model.

**Task** - There is a set of "Roles" - testing automation is required when a new image of a virtual machine appears
and the test results successful / unsuccessful are written to the **registry**.

The task was completed, a script was written using PyYAML, and so far it copes with its task.

This solution seemed to me very interesting and I decided to tell a little about it, but since I am by nature more
practitioners than a theoretician, I realized that what examples would be needed, and then everything went wrong
as intended.

I could not use the script written at work, because there are quite a few letters on intellectual property in my
contract. Therefore, I started writing examples from scratch and only describing the topic of the planned article...

At some point in time when writing the code, I realized that it would be nice to have a utility for creating a registry
of objects, and objects should be dynamic, no hardcode, it should be possible for the user to create object templates
by himself, spending a minimum of effort.

The result was pyRegistryStore_.

Let's go...

PyYAML
======

`YAML <http://yaml.org/>`_ has grown from a markup language to a powerful data serialization tool.

::

    %YAML 1.2
    ---
    YAML: YAML Ain't Markup Language

    What It Is: YAML is a human friendly data serialization
    standard for all programming languages.

Data serialization is done through strict markup rules and the ability to specify tags, both global and local.

One of the frameworks for Python is PyYAML_, which, based on tags, can save Python classes as yaml files.

This is exactly the given serialization/deserialization of objects used in the utility pyRegistryStore_

Let's look at examples of using the utility.

Object "Image VM"
=================
This type of object will describe all existing VM images for which we need to develop.

We will determine the requirements that we need to store information:
 - Name
 - Distribution kit
 - Version
 - Kernel Linux
 - LTS

We describe the object in pyRegistryStore_

::

    import objects

    class Image(objects.RegistryStore):
        """
        Image Object

        Parameters
        ----------
        name: str
            Name image
        distr: str
            Distribution kit
        version: str
            Version distr
        kernel: str
            Kernel Linux
        lts: bool
            Long term support
        """
        uniq_key = ['name']
        desc = 'Object image VM'

        def __init__(self) -> None:
            super().__init__()

Object "Ansible role"
=====================
This object will describe successful tests of passing software rolling on VM images.

We will determine the requirements that we need to store information:
 - Name
 - Image VM
 - Commit GIT
 - State

The following code turned out

::

    import objects


    class Role(objects.RegistryStore):
        """
        Image Object

        Parameters
        ----------
        name: str
            Name role
        image: str
            Name image VM
        commit: str
            Commit GIT
        status: bool
            Success
        """
        uniq_key = ['name', 'image', 'status']
        desc = 'Object Ansible role'

        def __init__(self) -> None:
            super().__init__()

Pipeline
========
At the moment, we have an empty object registry, let's create 2 pipelines to work with this registry.

Creating an image registry
--------------------------
Creating an image is not a tricky process, we take a blank, update packages, install the necessary software and send
it further along the business process.

We fill in the register:

::

    pyRegistryStore.py image set name=ubuntu_20.04_v0.image distr=ubuntu version=20.04 kernel=5.4.0-73-generic lts=true
    pyRegistryStore.py image set name=centos_7_v0.image distr=centos version=7 kernel=3.10.0-1160.el7.x86_64 lts=true

In total, we got 2 images that we can use further:

::

    pyRegistryStore.py image get | jq
    [
        {
            "_meta": {
                "create_time": "2021-05-27 06:07:19.950055",
                "update_time": "2021-05-27 06:07:19.950064",
                "version": 1,
                "uuid": "95abb4e1-ed8f-42a0-b0b0-5496e91a7b58"
            },
            "distr": "ubuntu",
            "kernel": "5.4.0-73-generic",
            "lts": true,
            "name": "ubuntu_20.04_v0.image",
            "version": "20.04"
        },
        {
            "_meta": {
                "create_time": "2021-05-27 06:25:26.587628",
                "update_time": "2021-05-27 06:25:26.587637",
                "version": 1,
                "uuid": "ab2fba4b-b9d0-4c05-8860-50f14580395a"
            },
            "distr": "centos",
            "kernel": "3.10.0-1160.el7.x86_64",
            "lts": true,
            "name": "centos_7_v0.image",
            "version": 7
        }
    ]

Create Ansible Role Registry
----------------------------
Let me remind you that the tasks of our group also include the development of Ansible roles for rolling out to VM
images, and we must be completely sure that the current version of the role has successfully passed the rolling out and
all synthetic tests.

Our testing stack looks like this:
 * Jenkins
 * Molecula_
 * `testinfra <https://testinfra.readthedocs.io/en/latest/>`_
 * Registry of images VM and Ansible roles.

Yes, I was not mistaken in writing the registry, and not pyRegistryStore_, since I wrote earlier that this project
appeared spontaneously, but I plan to switch to pyRegistryStore.

And so let's say we have a small role to set up and configure time synchronization with local NTP.
Let's call it **ntp-client**

The first thing we need is to get a list of all available images:
::

    pyRegistryStore.py image get | jq .[].name
    "ubuntu_20.04_v0.image"
    "centos_7_v0.image"

In total, we have 2 images, or to be more precise, **a list of images** on which we must test our role.

And since we have a list, we can organize a loop:

**check if the test for the image was successful for the current commit**
::

    pyRegistryStore.py role get name=ntp-client image=ubuntu_20.04_v0.image commit=b312abbb05a9be4fe82abcb60d44b7bdd0220bdc status=true

as expected, the list turned out to be empty, which means we need to check this role on this VM image,
if we received a list for the output, then we can skip testing.

**We run the Molecula, we run the tests, if we catch success, we write the information to the registry**
::

    pyRegistryStore.py role set name=ntp-client image=ubuntu_20.04_v0.image commit=b312abbb05a9be4fe82abcb60d44b7bdd0220bdc status=true

well, if the tests were not successful, then just change the status = true key to status = false

Let's say our tests passed like this:
::

    pyRegistryStore.py role get name=ntp-client | jq
    [
    {
        "_meta": {
            "create_time": "2021-05-28 07:01:01.470657",
            "update_time": "2021-05-28 07:01:01.470665",
            "version": 1,
            "uuid": "2fc0dabb-ea56-4eba-92de-75eea562f383"
        },
        "commit": "b312abbb05a9be4fe82abcb60d44b7bdd0220bdc",
        "image": "ubuntu_20.04_v0.image",
        "name": "ntp-client",
        "status": true
    },
    {
        "_meta": {
            "create_time": "2021-05-28 07:05:38.572570",
            "update_time": "2021-05-28 07:05:38.572578",
            "version": 1,
            "uuid": "c13a5266-8949-4d07-9c4e-8955d1cb3a8a"
        },
        "commit": "b312abbb05a9be4fe82abcb60d44b7bdd0220bdc",
        "image": "centos_7_v0.image",
        "name": "ntp-client",
        "status": false
    }
    ]

Conclusion
==========

And so we got the following:
 - There is a list of images to which we can automatically add new images
 - List of passing tests by role
 - Last successful commit for the image
 - Automate testing of new images

**What's next?**

Further, I plan to develop the utility, expanding the functionality. If this utility has its own community,
I will be very happy.

I hope I haven't bored anyone, and this material will be useful to someone, and someone will get some ideas for
themselves for inspiration.

**Thank you for reading this article.**
