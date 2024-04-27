.. title: pyRegistryStore - Или как создать реестр объектов
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

Добрый день коллега!

История создания этого поста очень интересная, все начиналось с того что я планировал написать немного об библиотеке
PyYAML и как мы ее приручили у себя, но что то пошло не так, и все это вылилось в создание утилиты pyRegistryStore_

Итак поехали...

.. TEASER_END

Начало...
=========
Любая автоматизация CI/CD подразумевает наличие справочников, реестров, тестовых сред, анализаторов и систем
управления исходным кодом. А над этим всем |ss| ветер поднимал свой флаг |se| стоит оркестратор.
Вот как раз о справочниках и реестре хотелось бы поговорить сегодня.

Наша небольшая группа занимается подготовкой и тестированием образов виртуальных машин + разработка Ansible ролей 
по установке необходимого ПО согласно ролевой модели.

**Задача** - Есть набор "Ролей" - требуется автоматизация тестирования при появлении нового образа виртуальной машины
и результаты теста успешные/не успешные записать в **реестр**.

Задача была выполнена, с использование на коленке написанного скрипта с использованием
PyYAML_ , и пока что со своей задачей справляется.

Данное решение мне показалось очень интересным и я решил немного про него рассказать, но так как я по натуре
больше практик чем теоретик, понял что нужны будут какие примеры, и вот тут то все пошло не так как задумывалось.

Скрипт написанный на работе я не мог использовать, так как в моем договоре довольно много букв на интеллектуальную
собственность. По этому я начал писать примеры с нуля и только описывающие тему запланированной статьи...

В какой то момент времени при написании кода, я понял что было бы прикольно создать утилиту
для создания реестра объектов, при чем объекты должны быть динамическими, никакого hardcode,
должна быть возможность пользователю самому создавать шаблоны объектов, затратив минимум усилий.

Результатом стало pyRegistryStore_.

Поехали...

YAML: YAML Ain't Markup Language
================================

`YAML <http://yaml.org/>`_ вырос из языка разметки в мощный инструмент сериализации данных.

::

    %YAML 1.2
    ---
    YAML: YAML Ain't Markup Language

    What It Is: YAML is a human friendly data serialization
    standard for all programming languages.

Сериализация данных осуществляется за счет строгих правил разметки и возможности указывать теги,
как глобальные так и локальные.

Одним из framework для Python является PyYAML_, который как раз на основе тегов может сохранять классы Python
в виде yaml файлов.

Вот как раз данная сериализация/десериализация объектов применяется в утилите pyRegistryStore_

Разберем практическое применение утилиты.

Объект "Образ ВМ"
=================
Данный тип объекта будет у нас описывать все существующие образы ВМ для которых нам нужно вести разработку.

Определим требования которые нам нужны для хранения информации:
 - Имя
 - Дистрибутив
 - Версия
 - Ядро Linux
 - LTS

Описываем объект в pyRegistryStore_

::

    import objects

    class Image(objects.RegistryStore):
        """
        Image Object

        Parameters
        ----------
        name: str
            Имя образа
        distr: str
            Название дистрибутива
        version: str
            Версия дистрибутива
        kernel: str
            Версия ядра Linux
        lts: bool
            Long term support
        """
        uniq_key = ['name']
        desc = 'Объект образов ВМ'

        def __init__(self) -> None:
            super().__init__()

Объект "Ansible роль"
=====================
Данный объект будет описывать успешные тесты прохождения раскатки ПО на образах ВМ.

Как и с предыдущим объектом определим требования:
 - Имя
 - Образ ВМ
 - Commit GIT
 - Статус

Получился следующий код

::

    import objects


    class Role(objects.RegistryStore):
        """
        Image Object

        Parameters
        ----------
        name: str
            Name ansible role
        image: str
            Name image VM
        commit: str
            Commit GIT
        status: bool
            Successful passing of all tests
        """
        uniq_key = ['name', 'image', 'status']
        desc = 'Объект Ansible роль'

        def __init__(self) -> None:
            super().__init__()

Pipeline
========
На данный момент реестр объектов у нас пустой, давай те создадим 2 процесса для работы с данным реестром.

Создание реестра образов
------------------------
Создание образа процесс не хитрый, берем заготовку, обновляем пакеты, устанавливаем необходимое ПО и отправляем 
дальше по бизнес процессу.

Заполняем реестр:

::

    pyRegistryStore.py image set name=ubuntu_20.04_v0.image distr=ubuntu version=20.04 kernel=5.4.0-73-generic lts=true
    pyRegistryStore.py image set name=centos_7_v0.image distr=centos version=7 kernel=3.10.0-1160.el7.x86_64 lts=true

Итого у нас получилось 2 образа которые мы можем использовать дальше:

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

Создание реестра Ansible ролей
------------------------------
Напомню что в задачи нашего отдела так же входит разработка Ansible ролей, для раскатки на образы ВМ, и мы должны быть
полностью уверенными, что текущая версия роли успешно прошла раскатку и тесты.

Наш стек тестирования выглядит следующим образом:
 * Jenkins
 * Molecula_ - автоматизация создания ВМ, совместно с модулем molecule-openstack
 * `testinfra <https://testinfra.readthedocs.io/en/latest/>`_ - тестирование ВМ
 * Реестр образов и Ansible ролей.

Да я не ошибся написав реестр, а не pyRegistryStore_, так как я писал раннее, что данный проект появился спонтанно, но
в планы я ставлю перейти именно на pyRegistryStore.

И так допустим у нас есть небольшая роль для установки и настройки синхронизации времени с локальным NTP.
Назовем ее **ntp-client**

И так первое что нам нужно, это получить список всех доступных образов:

::

    pyRegistryStore.py image get | jq .[].name
    "ubuntu_20.04_v0.image"
    "centos_7_v0.image"

Итого у нас появилось 2 образа, а если быть точнее то **список образов**, на которых мы должны протестировать нашу роль.

А раз у нас есть список, то мы можем организовать цикл:

**проверим был ли тест для образа успешным для текущего commit**

::

    pyRegistryStore.py role get name=ntp-client image=ubuntu_20.04_v0.image commit=b312abbb05a9be4fe82abcb60d44b7bdd0220bdc status=true

как и ожидалось список оказался пустым, а значит нам нужно проверить данную роль на данном образе ВМ,
если у нас на вывод пришел список, то можем и пропустить тестирование.

**Запускаем молекулу прогоняем тесты, если словили успех, записываем информацию в реестр**

::

    pyRegistryStore.py role set name=ntp-client image=ubuntu_20.04_v0.image commit=b312abbb05a9be4fe82abcb60d44b7bdd0220bdc status=true

ну а если тесты прошли не успешно, то просто меняем ключ status=true на status=false

Допустим у нас тесты прошли так:

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

Выводы
======

И так у нас получилось следующее:
 - Есть список образов который, в который можем автоматически добавлять новые образы
 - Список прохождения тестов по ролям
 - Последний успешный commit для образа
 - Автоматизировать тестирование новых образов

**Что дальше?**

Дальше я планирую развивать утилиту, расширяя функционал. Если у данной утилиты появится свое сообщество буду очень рад.

Надеюсь я никого не утомил, и данный материал кому то будет полезен, а кто то почерпнет для себя какие то идеи для
вдохновения.

**Спасибо за то что прочитали данную статью.**
