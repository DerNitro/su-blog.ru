.. title: Expanding Blog Functionality: Reactions, Highlighting, and View Protection
.. slug: razvivaem-funktsional-bloga-reaktsii-podsvetka-i-zashchita-ot-nakrutki
.. date: 2026-11-14 03:00:00 UTC+03:00
.. tags: python, fastapi, sqlalchemy, blog, development, ux
.. category: python, devops
.. link: 
.. description: Adding new features to the blog: a FastAPI reactions and views microservice with view protection, reaction highlighting, toggle/switching support, and global statistics.
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

Introduction
------------

I wanted to make the blog a bit more alive and interactive by adding reactions to articles and a view counter. In this post, I'll walk through how the FastAPI microservice is built: from anti-fraud view protection to frontend reaction highlighting and the global statistics page.

.. TEASER_END

Interaction Diagram (Architecture Overview)
-------------------------------------------

Before diving into the code, let's look at the high-level architecture overview showing how static blog pages, the client-side JS widget, and the backend microservice interact:

.. code-block:: text

    +-------------------+       HTTP (fetch /api/*)       +------------------------+
    |  Reader Browser   | ------------------------------> | FastAPI Microservice   |
    |  (Nikola Static   | <------------------------------ | (Reactions & Views)    |
    |   + JS Widget)    |                                 +------------------------+
    +-------------------+                                              |
                                                                SQLAlchemy ORM
                                                                       v
                                                          +------------------------+
                                                          |      SQLite DB         |
                                                          |  - reactions           |
                                                          |  - user_views          |
                                                          |  - user_reactions      |
                                                          +------------------------+

As illustrated in the diagram, the Nikola static generator serves pre-built HTML pages with embedded scripts. When visiting an article or clicking a reaction, the browser sends requests to FastAPI endpoints, which verify uniqueness via client hashing and update the SQLite database.

Backend Architecture and Implementation (FastAPI + SQLAlchemy)
--------------------------------------------------------------

The reactions and views microservice is built on **FastAPI** with SQLite storage via **SQLAlchemy**. To keep things fair and reliable under concurrent requests, I designed a couple of simple database tables and endpoints.

1. View Protection Against Fraud
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To prevent article view counters from incrementing on every page reload or repeat visit by the same reader, we introduced the `UserViewModel` (`user_views`):

.. code-block:: python

    class UserViewModel(Base):
        __tablename__ = "user_views"

        id = Column(Integer, primary_key=True, autoincrement=True)
        slug = Column(String, index=True)
        client_id = Column(String, index=True)

When requesting `/api/views`, a unique client identifier (`client_id`, formed by hashing the IP address and User-Agent via SHA-256) is computed. The first visit creates a record in `user_views` and increments the view counter by 1. Subsequent visits from the same client are logged as unique visits, but the counter is not incremented again.

2. Reaction Storage and Toggle/Switch Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Reactions use the `reactions` table with columns for each emotion type (`likes`, `heart`, `fire`, `clap`, `poop`). To allow each user to cast a single vote and see their selection, we added the `user_reactions` table:

.. code-block:: python

    class UserReactionModel(Base):
        __tablename__ = "user_reactions"

        id = Column(Integer, primary_key=True, autoincrement=True)
        slug = Column(String, index=True)
        client_id = Column(String, index=True)
        reaction_type = Column(String, index=True)

The `/api/reactions` endpoint handles three scenarios:
- **New Reaction:** If it's the first vote, a record is created in `user_reactions` with the `reaction_type`, and the corresponding counter in `reactions` is incremented.
- **Toggle Off:** Clicking the same reaction again removes the vote from the database, decrements the counter, and clears the selection.
- **Switch Reaction:** If the reader changes their mind (e.g. switching from like to fire), the old counter is decremented, the new one is incremented, and the reaction type in `user_reactions` is updated on the fly.

Frontend and User Experience (UX)
---------------------------------

An interactive JS widget was added to `post.tmpl`. On the client side, the `updateStatsUI` function syncs the numbers and highlights the reaction button previously chosen by the user.

Example client-side highlighting logic:

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

Global Blog Statistics
----------------------

In addition to reactions on individual article pages, we added the `/stats` endpoint and a public statistics page (`/pages/stats/`). It renders a clean table showing total views and reaction types across all blog posts. The link was also added to the navigation menu (`src/conf.py`).

Conclusion
----------

The new feature is fully integrated into the blog infrastructure. We now have a simple, honest feedback mechanism: readers can express emotions and change their minds, while authors get accurate view statistics without artificial padding.
