.. title: Testinfra or how to automate infrastructure health checks after failure
.. slug: testinfra-ili-kak-avtomatizirovat-proverku-infrastruktury-posle-sboia
.. date: 2026-11-03 05:52:21 UTC+03:00
.. tags: testinfra, python, devops, linux, testing, sysadmin
.. category: devops, python
.. link: 
.. description: Automating infrastructure and service health checks after failures and reboots using Python and Testinfra.
.. type: text
.. author: Sergey <DerNitro> Utkin
.. previewimage: /images/posts/testinfra-ili-kak-avtomatizirovat-proverku-infrastruktury-posle-sboia/sergey-utkin--er_XtTx85s-unsplash.jpg

.. _Sergey Utkin: https://unsplash.com/@dernitro?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText
.. _Unsplash: https://unsplash.com/photos/-er_XtTx85s?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText

.. |PostImage| image:: /images/posts/testinfra-ili-kak-avtomatizirovat-proverku-infrastruktury-posle-sboia/sergey-utkin--er_XtTx85s-unsplash.jpg
    :width: 40%
    :target: `Sergey Utkin`_

.. |PostImageTitle| replace:: Photo by `Sergey Utkin`_ on Unsplash_


|PostImage|

|PostImageTitle|

Introduction
------------

After an outage, planned maintenance, or server reboot, an engineer always faces a classic task: ensuring that everything is running correctly.
Usually, this process comes down to manually executing a checklist of commands:

- Checking the status of systemd services (`nginx`, `postgresql`, `uwsgi`, etc.).
- Ensuring necessary ports are open and listening.
- Verifying the presence of configuration files, logs, and correct permissions.
- Performing basic HTTP requests or pings.

Manual checks using notepads or memory are slow, tedious, and prone to human error.
In this article, we will look at how to apply the **Infrastructure as Tests** approach using the **Testinfra** library, turning routine checks into a fast, reliable, and repeatable suite of pytest tests.

.. TEASER_END

What is Testinfra?
------------------

**Testinfra** is a Python library that allows you to write unit tests to check the actual state of servers, containers, or hosts.
Essentially, it is `pytest` for infrastructure. You can find detailed official documentation on the `Testinfra documentation website <https://testinfra.readthedocs.io/>`_.

Key benefits:

1. **Familiar pytest syntax:** If you know Python and pytest, mastering it takes minutes.
2. **Agentless operation:** Testinfra connects via SSH, Docker, WinRM, LXC, or runs locally. No additional software needs to be installed on target servers.
3. **Rich set of modules:** Out-of-the-box checks for packages (`package`), services (`service`), files (`file`), users, sockets, commands, and more.

Examples of post-failure checks
-------------------------------

Suppose our web server and database have restarted. We need to verify:

1. That `nginx` and `postgresql` services are running and enabled at startup.
2. That ports 80, 443, and 5432 are listening.
3. That the nginx configuration file exists and contains certain directives.

Here is what a set of Testinfra tests looks like (`test_infra.py`), including conditional skips (`pytest.skip`) for hosts not belonging to a specific Ansible group or lacking installed software:

.. code-block:: python

    import pytest

    def test_services(host):
        # Check systemd services
        for service_name in ["nginx", "postgresql"]:
            svc = host.service(service_name)
            assert svc.is_running
            assert svc.is_enabled

    def test_nginx_only_on_webservers(host):
        # Skip the test if host is not in the webservers group in Ansible
        ansible_vars = host.ansible.get_variables()
        if "webservers" not in ansible_vars.get("group_names", []):
            pytest.skip("Host is not part of the webservers group")
        
        # Alternatively, check package installation presence
        if not host.package("nginx").is_installed:
            pytest.skip("Nginx is not installed on this host")

        assert host.service("nginx").is_running

    def test_sockets(host):
        # Check open ports
        assert host.socket("tcp://0.0.0.0:80").is_listening
        assert host.socket("tcp://0.0.0.0:443").is_listening
        assert host.socket("tcp://127.0.0.1:5432").is_listening

    def test_config_files(host):
        # Check nginx configuration file
        nginx_conf = host.file("/etc/nginx/nginx.conf")
        assert nginx_conf.exists
        assert nginx_conf.is_file
        assert nginx_conf.user == "root"
        assert nginx_conf.group == "root"
        # Check file content
        assert "worker_processes" in nginx_conf.content_string

Running the tests
-----------------

Tests can be run locally on the server or remotely via SSH:

.. code-block:: bash

    # Local run
    pytest test_infra.py

    # Run via SSH on a remote server
    pytest --connection=ssh --hosts=root@my-server.example.com test_infra.py

    # Check a group of servers from a list
    pytest --connection=ssh --hosts=root@server1.example.com,root@server2.example.com test_infra.py

Ansible Integration
-------------------

If your infrastructure is managed with Ansible, Testinfra has a built-in backend for Ansible inventory. This allows you to run tests directly by host or group names from your `inventory.yml`:

.. code-block:: bash

    # Run tests for the entire webservers group from ansible inventory
    pytest --connection=ansible --ansible-inventory=inventory.yml --hosts=webservers

Testinfra automatically reads connection settings (SSH keys, ports, users) from your Ansible inventory, eliminating the need to duplicate connection parameters.

Integrating into the Recovery Process
-------------------------------------

Such tests can be:

- Added to post-outage recovery runbooks.
- Automatically executed via CI/CD after deployment or infrastructure restart in Docker/Ansible.
- Integrated into monitoring or orchestration systems.

Conclusion
----------

Using Testinfra allows you to formalize infrastructure state requirements and automate health checks after failures. Instead of manual command execution, we get a green or red pytest report that immediately shows which component failed to start.
