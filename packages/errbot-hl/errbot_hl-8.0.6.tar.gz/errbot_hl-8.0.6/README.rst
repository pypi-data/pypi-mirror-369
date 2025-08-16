.. image:: https://errbot.readthedocs.org/en/latest/_static/errbot.png
   :target: http://errbot.io

|

.. image:: https://github.com/errbotio/errbot/workflows/Python%20package/badge.svg
   :target: https://github.com/errbotio/errbot/actions


.. image:: https://img.shields.io/pypi/v/errbot.svg
   :target: https://pypi.python.org/pypi/errbot
   :alt: Latest Version

.. image:: https://img.shields.io/badge/License-GPLv3-green.svg
   :target: https://pypi.python.org/pypi/errbot
   :alt: License

.. image:: https://img.shields.io/badge/gitter-join%20chat%20%E2%86%92-brightgreen.svg
   :target: https://gitter.im/errbotio/errbot?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
   :alt: Join the chat at https://gitter.im/errbotio/errbot

|

Note: This is a forked version of Errbot. The main reason was, to be able to have an automated release process and release the
changes often. The base for this fork was version 6.1.9 (commit: 7609f6c) from June 2023. The first released version here is
7.0.0 and contains all unreleased changes up to commit 0080eff1324930207f021f55674d5240abae172d from 2023-10-30.

- Docker image: `ghcr.io/hapag-lloyd/errbot-hl <https://github.com/Hapag-Lloyd/errbot/pkgs/container/errbot>`__
- PyPi package: `errbot-hl <https://pypi.org/project/errbot-hl/>`__


Errbot
======

Errbot is a chatbot. It allows you to start scripts interactively from your chatrooms
for any reason: random humour, chatops, starting a build, monitoring commits, triggering
alerts...

It is written and easily extensible in Python.

Errbot is available as open-source software and released under the GPL v3 license.


Features
--------

Chat servers support
~~~~~~~~~~~~~~~~~~~~

**Built-in**

- IRC support
- `Telegram support <https://www.telegram.org/>`_
- `XMPP support <http://xmpp.org>`_

**With add-ons**

- `Slack support <https://slack.com/>`_ (See `instructions <https://github.com/errbotio/err-backend-slackv3>`__)
- `Discord <https://www.discordapp.com/>`_ (See `instructions <https://github.com/errbotio/err-backend-discord>`__)
- `Gitter support <https://gitter.im/>`_ (See `instructions <https://github.com/errbotio/err-backend-gitter>`__)
- `Webex <https://www.webex.com/>`_ (See `instructions <https://github.com/marksull/err-backend-cisco-webex-teams>`__)
- `Mattermost <https://about.mattermost.com/>`_ (See `instructions <https://github.com/Vaelor/errbot-mattermost-backend>`__)
- `RocketChat <https://rocket.chat/>`_ (See `instructions <https://github.com/cardoso/errbot-rocketchat>`__)
- `Skype <https://www.skype.com/>`_ (See `instructions <https://github.com/errbotio/errbot-backend-skype>`__)
- `TOX <https://tox.im/>`_ (See `instructions <https://github.com/errbotio/err-backend-tox>`__)
- `VK <https://vk.com/>`_ (See `instructions <https://github.com/Ax3Effect/errbot-vk>`__)
- `Zulip <https://zulipchat.com/>`_ (See `instructions <https://github.com/zulip/errbot-backend-zulip>`__)


Administration
~~~~~~~~~~~~~~

After the initial installation and security setup, Errbot can be administered by just chatting to the bot (chatops).

- install/uninstall/update/enable/disable private or public plugins hosted on git
- plugins can be configured from chat
- direct the bot to join/leave Multi User Chatrooms (MUC)
- Security: ACL control feature (admin/user rights per command)
- backup: an integrated command !backup creates a full export of persisted data.
- logs: can be inspected from chat or streamed to Sentry.

Developer features
~~~~~~~~~~~~~~~~~~

- Very easy to extend in Python! (see below)
- Presetup storage for every plugin i.e. ``self['foo'] = 'bar'`` persists the value.
- Conversation flows to track conversation states from users.
- Webhook callbacks support
- supports `markdown extras <https://markdown-extra.readthedocs.io/>`_ formatting with tables, embedded images, links etc.
- configuration helper to allow your plugin to be configured by chat
- Text development/debug consoles
- Self-documenting: your docstrings become help automatically
- subcommands and various arg parsing options are available (re, command line type)
- polling support: your can setup a plugin to periodically do something
- end to end test backend
- card rendering under Slack

Community and support
---------------------

If you have:

- a quick question feel free to join us on chat at `errbotio/errbot on Gitter <https://gitter.im/errbotio/errbot>`_.
- a plugin development question please use `Stackoverflow <http://stackoverflow.com/questions/tagged/errbot>`_ with the tags `errbot` and `python`.
- a bug to report or a feature request, please use our `GitHub project page <https://github.com/errbotio/errbot/issues>`_.

You can also ping us on Twitter with the hashtag ``#errbot``.


Installation
------------

Prerequisites
~~~~~~~~~~~~~

Errbot runs under Python 3.6+ on Linux, Windows and Mac. For some chatting systems you'll need a key or a login for your bot to access it.

Quickstart
~~~~~~~~~~

We recommend to setup a `virtualenv <https://pypi.python.org/pypi/virtualenv>`_.

1. Install `errbot` from pip
2. Make a directory somewhere (here called `errbot`) to host Errbot's data files
3. Initialize the directory
4. Try out Errbot in text mode

.. code:: bash

    $ pip install errbot
    $ mkdir errbot; cd errbot
    $ errbot --init
    $ errbot

It will show you a prompt `>>>` so you can talk to your bot directly! Try `!help` to get started.

Adding support for a chat system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the built-ins, just use one of those options `telegram, IRC, XMPP` with pip, you can still do it
after the initial installation to add the missing support for example ::

   $ pip install "errbot[irc]"

For the external ones (Slack, Discord, Gitter, Skype, etc ...), please follow their respective github pages for instructions.

Configuration
~~~~~~~~~~~~~

In order to configure Errbot to connect to one of those chat systems you'll need to tweak the `config.py` file generated
by `errbot --init`.

To help you, we have a documented template available here: `config-template.py <https://raw.githubusercontent.com/errbotio/errbot/master/errbot/config-template.py>`_.

Note: even if you changed the BACKEND from the configuration, you can still use `errbot -T` to test
out your instance locally in text mode.

Starting Errbot as a daemon
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If all that worked, you can now use the -d (or --daemon) parameter to run it in a
detached mode:

.. code:: bash

    errbot --daemon

Interacting with the Bot
------------------------

After starting Errbot, you should add the bot to your buddy list if you haven't already.
You'll need to invite the bot explicitly to chatrooms on some chat systems too.
You can now send commands directly to the bot!

To get a list of all available commands, you can issue:

.. code:: bash

    !help

If you just wish to know more about a specific command you can issue:

.. code:: bash

    !help command

Managing plugins
~~~~~~~~~~~~~~~~

You can administer the bot in a one-on-one chat if your handle is in the BOT_ADMINS list in `config.py`.

For example to keyword search in the public plugin repos you can issue:

.. code:: bash

    !repos search jira

To install a plugin from this list, issue:

.. code:: bash

    !repos install <name of repo>


For example `!repos install errbotio/err-imagebot`.

Writing plugins
---------------

Writing your own plugins is extremely simple. `errbot --init` will have installed in the `plugins` subdirectory a plugin
called `err-example` you can use as a base.

As an example, this is all it takes to create a "Hello, world!" plugin for Errbot:

.. code:: python

    from errbot import BotPlugin, botcmd

    class Hello(BotPlugin):
        """Example 'Hello, world!' plugin for Errbot"""

        @botcmd
        def hello(self, msg, args):
            """Return the phrase "Hello, world!" to you"""
            return "Hello, world!"

This plugin will create the command "!hello" which, when issued, returns "Hello, world!"
to you. For more info on everything you can do with plugins, see the
`plugin development guide <https://errbot.io/en/latest/user_guide/plugin_development/>`_.

Contribution to Errbot itself
-----------------------------

Feel free to fork and propose changes on `github <https://www.github.com/errbotio/errbot>`_
