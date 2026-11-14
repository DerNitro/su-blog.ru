.. title: Развиваем функционал блога: реакции, подсветка и защита от накрутки
.. slug: razvivaem-funktsional-bloga-reaktsii-podsvetka-i-zashchita-ot-nakrutki
.. date: 2026-11-14 03:00:00 UTC+03:00
.. tags: python, fastapi, sqlalchemy, blog, development, ux
.. category: python, devops
.. link: 
.. description: Добавляем новый функционал в блог: микросервис реакций и просмотров на FastAPI с защитой от накрутки, подсветкой выбранной реакции, а также поддержкой переключения и отмены оценок.
.. type: text
.. author: Sergey <DerNitro> Utkin
.. previewimage: /images/posts/razvivaem-funktsional-bloga-reaktsii-podsvetka-i-zashchita-ot-nakrutki/planet-volumes-hgEiaquas5U-unsplash.jpg

.. _Planet Volumes: https://unsplash.com/@planetvolumes?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText
.. _Unsplash: https://unsplash.com/photos/a-row-of-different-colored-eggs-with-faces-painted-on-them-hgEiaquas5U?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText

.. |PostImage| image:: /images/posts/razvivaem-funktsional-bloga-reaktsii-podsvetka-i-zashchita-ot-nakrutki/planet-volumes-hgEiaquas5U-unsplash.jpg
    :width: 40%
    :target: `Planet Volumes`_

.. |PostImageTitle| replace:: Photo by `Planet Volumes`_ on Unsplash_


|PostImage|

|PostImageTitle|

Введение
--------

Захотелось сделать блог чуть более живым и интерактивным — добавить возможность оставлять реакции на статьи и видеть счетчик просмотров. В этой статье расскажу, как устроен микросервис на FastAPI: от защиты счетчиков от накруток до фронтенд-подсветки выбора читателя и страницы общей статистики.

.. TEASER_END

Схема взаимодействия (Архитектура решения)
------------------------------------------

Прежде чем углубляться в код, давайте посмотрим на общую схему того, как устроено взаимодействие между статическими страницами блога, клиентским JS-виджетом и бэкенд-микросервисом:

.. code-block:: text

    +-------------------+       HTTP (fetch /api/*)       +------------------------+
    |  Браузер читателя | ------------------------------> | FastAPI Микросервис    |
    |  (Статика Nikola  | <------------------------------ | (Реакции и Просмотры)  |
    |   + JS-виджет)    |                                 +------------------------+
    +-------------------+                                              |
                                                                SQLAlchemy ORM
                                                                       v
                                                          +------------------------+
                                                          |      SQLite База       |
                                                          |  - reactions           |
                                                          |  - user_views          |
                                                          |  - user_reactions      |
                                                          +------------------------+

Как видно из схемы, статический движок Nikola выдает готовые HTML-страницы со встроенным скриптом. При открытии статьи или клике на реакцию браузер шлет запросы на эндпоинты FastAPI, который проверяет уникальность через хэш клиента и обновляет данные в SQLite.

Архитектура и реализация бэкенда (FastAPI + SQLAlchemy)
-------------------------------------------------------

Микросервис реакций и просмотров написан на **FastAPI**, а данные хранятся в SQLite через **SQLAlchemy**. Чтобы всё работало честно и без сюрпризов при параллельных запросах, потребовалось продумать пару простых таблиц и эндпоинтов.

1. Защита просмотров от накрутки
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Чтобы счетчик просмотров не накручивался при каждом обновлении страницы или повторном заходе одного и того же человека, была сделана модель `UserViewModel` (`user_views`):

.. code-block:: python

    class UserViewModel(Base):
        __tablename__ = "user_views"

        id = Column(Integer, primary_key=True, autoincrement=True)
        slug = Column(String, index=True)
        client_id = Column(String, index=True)

При запросе к `/api/views` вычисляется уникальный идентификатор клиента (`client_id`, формируемый хэшированием IP-адреса и User-Agent через SHA-256). Первый визит на статью создает запись в `user_views` и увеличивает счетчик просмотров на 1. Повторные заходы от того же клиента учитываются как уникальные, но счетчик больше не дергается.

2. Хранение реакций и поддержка смены/отмены
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Для реакций используется таблица `reactions` с колонками под эмоции (`likes`, `heart`, `fire`, `clap`, `poop`). А чтобы каждый пользователь мог оставить ровно один голос и видеть свой выбор, заведена таблица `user_reactions`:

.. code-block:: python

    class UserReactionModel(Base):
        __tablename__ = "user_reactions"

        id = Column(Integer, primary_key=True, autoincrement=True)
        slug = Column(String, index=True)
        client_id = Column(String, index=True)
        reaction_type = Column(String, index=True)

Эндпоинт `/api/reactions` отрабатывает три сценария:
- **Новая реакция:** Если голос первый, пишем запись в `user_reactions` с нужным `reaction_type` и плюсуем счетчик в `reactions`.
- **Отмена (Toggle off):** Клик по той же самой реакции удаляет голос из базы, уменьшает счетчик и сбрасывает выбор.
- **Смена оценки (Switch):** Если читатель передумал (например, сменил лайк на огонь), старый счетчик уменьшается, новый увеличивается, а тип реакции в `user_reactions` обновляется на лету.

Фронтенд и пользовательский интерфейс (UX)
------------------------------------------

В шаблоне `post.tmpl` появился небольшой JS-виджет. Функция `updateStatsUI` на клиенте синхронизирует цифры и подсвечивает активную кнопку реакции, которую ранее выбрал пользователь.

Пример клиентской логики подсветки активной кнопки:

.. code-block:: javascript

    const types = ['likes', 'heart', 'fire', 'clap', 'poop'];
    types.forEach(t => {
        const btn = document.getElementById('btn-' + t);
        if (!btn) return;
        if (data.user_reaction === t) {
            btn.style.background = '#e3f2fd';
            btn.style.borderColor = '#2196f3';
            btn.style.boxShadow = '0 0 5px rgba(33, 150, 243, 0.5)';
        } else {
            btn.style.background = 'white';
            btn.style.borderColor = '#ddd';
            btn.style.boxShadow = 'none';
        }
    });

Глобальная статистика блога
---------------------------

Помимо реакций на страницах статей, появился эндпоинт `/stats` и публичная страница статистики (`/pages/stats/`). Она выводит аккуратную табличку со всеми просмотрами и типами реакций по каждой статье блога. Ссылка также прописана в навигационном меню (`src/conf.py`).

Заключение
----------

В итоге фича полностью встроена в инфраструктуру блога. Получился простой и честный механизм обратной связи: читатели могут выражать эмоции и менять свое мнение, а авторы видят честную статистику без накруток.
