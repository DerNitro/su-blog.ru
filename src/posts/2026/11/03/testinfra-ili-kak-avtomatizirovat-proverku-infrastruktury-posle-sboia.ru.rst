.. title: Testinfra или как автоматизировать проверку инфраструктуры после сбоя
.. slug: testinfra-ili-kak-avtomatizirovat-proverku-infrastruktury-posle-sboia
.. date: 2026-11-03 05:52:21 UTC+03:00
.. tags: testinfra, python, devops, linux, testing, sysadmin
.. category: devops, python
.. link: 
.. description: Автоматизация проверки состояния инфраструктуры и сервисов после сбоев и перезагрузок с помощью Python и Testinfra.
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

Введение
--------

После аварии, планового обслуживания или перезагрузки серверов перед инженером всегда встает классическая задача: убедиться, что всё работает корректно. 
Обычно этот процесс сводится к ручному выполнению списка команд:

- Проверить статус systemd-служб (`nginx`, `postgresql`, `uwsgi` и т.д.).
- Убедиться, что нужные порты открыты и слушают интерфейсы.
- Проверить наличие конфигурационных файлов, логов и правильность прав доступа.
- Выполнить базовые HTTP-запросы или пинги.

Ручные проверки по блокноту или памяти — это долго, утомительно и чревато человеческой ошибкой (что-то забыли проверить). 
В этой статье мы рассмотрим, как применить подход **Infrastructure as Tests** с помощью библиотеки **Testinfra**, превратив рутину в быстрый, надежный и повторяемый набор pytest-тестов.

.. TEASER_END

Что такое Testinfra?
--------------------

**Testinfra** (Test Infrastructure) — это Python-библиотека, которая позволяет писать юнит-тесты для проверки реального состояния серверов, контейнеров или хостов. 
Фактически, это `pytest` для инфраструктуры. Подробную официальную документацию можно найти на `сайте Testinfra <https://testinfra.readthedocs.io/>`_.

Основные преимущества:

1. **Знакомый синтаксис pytest:** если вы знакомы с Python и pytest, освоение займет минуты.
2. **Работа без агентов:** Testinfra подключается по SSH, Docker, WinRM, LXC или работает локально. Никакого дополнительного ПО на целевых серверах устанавливать не нужно.
3. **Богатый набор модулей:** из коробки доступны проверки пакетов (`package`), служб (`service`), файлов (`file`), пользователей, сокетов, команд и т.д.

Примеры проверок после сбоя
---------------------------

Представим, что у нас упал и поднялся веб-сервер с базой данных. Нам нужно проверить:

1. Что службы `nginx` и `postgresql` запущены и включены в автозагрузку.
2. Что порты 80, 443 и 5432 прослушиваются.
3. Что конфигурационный файл nginx существует и содержит определенные директивы.

Вот как выглядит набор тестов на Testinfra (`test_infra.py`), включая условный пропуск (`pytest.skip`) для хостов, не входящих в определенную Ansible-группу или не имеющих установленного ПО:

.. code-block:: python

    import pytest

    def test_services(host):
        # Проверяем systemd службы
        for service_name in ["nginx", "postgresql"]:
            svc = host.service(service_name)
            assert svc.is_running
            assert svc.is_enabled

    def test_nginx_only_on_webservers(host):
        # Пропускаем тест, если хост не входит в группу webservers в Ansible
        ansible_vars = host.ansible.get_variables()
        if "webservers" not in ansible_vars.get("group_names", []):
            pytest.skip("Хост не входит в группу webservers")
        
        # Или альтернативно проверка наличия пакета
        if not host.package("nginx").is_installed:
            pytest.skip("Nginx не установлен на этом хосте")

        assert host.service("nginx").is_running

    def test_sockets(host):
        # Проверяем открытые порты
        assert host.socket("tcp://0.0.0.0:80").is_listening
        assert host.socket("tcp://0.0.0.0:443").is_listening
        assert host.socket("tcp://127.0.0.1:5432").is_listening

    def test_config_files(host):
        # Проверяем конфигурационный файл nginx
        nginx_conf = host.file("/etc/nginx/nginx.conf")
        assert nginx_conf.exists
        assert nginx_conf.is_file
        assert nginx_conf.user == "root"
        assert nginx_conf.group == "root"
        # Проверяем содержимое файла
        assert "worker_processes" in nginx_conf.content_string

Как запустить тесты
-------------------

Запустить тесты можно как локально на самом сервере, так и удаленно по SSH:

.. code-block:: bash

    # Локальный запуск
    pytest test_infra.py

    # Запуск по SSH на удаленном сервере
    pytest --connection=ssh --hosts=root@my-server.example.com test_infra.py

    # Проверка группы серверов из inventory / списка
    pytest --connection=ssh --hosts=root@server1.example.com,root@server2.example.com test_infra.py

Интеграция с Ansible
--------------------

Если ваша инфраструктура управляется с помощью Ansible, у Testinfra есть встроенный бэкенд для работы с Ansible-инвентарем. Это позволяет запускать тесты прямо по именам хостов или групп из вашего `inventory.yml`:

.. code-block:: bash

    # Запуск тестов для всей группы веб-серверов из ansible inventory
    pytest --connection=ansible --ansible-inventory=inventory.yml --hosts=webservers

Testinfra автоматически прочитает настройки подключения (SSH-ключи, порты, пользователей) из вашего инвентаря Ansible, что избавляет от необходимости дублировать параметры подключения.

Интеграция в процесс восстановления
-----------------------------------

Такие тесты можно:

- Добавить в скрипты восстановления (runbook) после аварии.
- Запускать автоматически через CI/CD после деплоя или рестарта инфраструктуры в Docker/Ansible.
- Интегрировать в системы мониторинга или оркестрации.

Заключение
----------

Использование Testinfra позволяет формализовать требования к состоянию инфраструктуры и автоматизировать проверку работоспособности после сбоев. Вместо ручного перебора команд мы получаем зеленый или красный отчет pytest, где сразу видно, какой именно компонент не поднялся.

