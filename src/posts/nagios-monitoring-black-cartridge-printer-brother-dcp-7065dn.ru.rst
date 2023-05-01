.. title: Nagios Monitoring Black Cartridge Printer Brother DCP-7065DN
.. slug: nagios-monitoring-black-cartridge-printer-brother-dcp-7065dn
.. date: 2013-05-21 12:00:00 UTC+03:00
.. tags: nagios, monitoring, linux
.. category: monitoring
.. link:
.. description: Плагин мониторинга принтера Brother DCP-7065DN
.. type: text
.. author: Sergey <DerNitro> Utkin
.. previewimage: /images/posts/nagios-monitoring-black-cartridge-printer-brother-dcp-7065dn/bank-phrom-Tzm3Oyu_6sk-unsplash.jpg


.. _Bank Phrom: https://unsplash.com/@bank_phrom?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText
.. _Unsplash: https://unsplash.com/s/photos/printer?utm_source=unsplash&amp;utm_medium=referral&amp;utm_content=creditCopyText

.. |PostImage| image:: /images/posts/nagios-monitoring-black-cartridge-printer-brother-dcp-7065dn/bank-phrom-Tzm3Oyu_6sk-unsplash.jpg
    :width: 40%
    :target: `Bank Phrom`_

.. |PostImageTitle| replace:: Photo by `Bank Phrom`_ on Unsplash_


|PostImage|

|PostImageTitle|

В хозяйстве имеется 4 принтера Brother DCP-7065DN, захотелось мониторить состояние картриджей, и столкнулся со следующими проблемами:
 1. Плагин для Nagios check_snmp_printer не подходит, возвращает не верное значение, хотя для мониторинга состояния барабана он отлично подходит.
 2. Не нашел в сети какой SNMP OID состояния картриджа, для этого принтера.

Написал в тех. поддержку Brother… И неожиданно для себя они ответили и сообщили мне OID для моего принтера.
Открыл любимый VIM и написал bash-скрипт для Nagios. И теперь делюсь им `check_snmp_brother <https://github.com/DerNitro/check_snmp_brother>`_.

Кладем данный скрипт в папку с плагинами Nagios, выставляем нужные права, и ставим флаг на выполнение.

Настройка в Nagios

.. code-block::

    define command{  
    command_name  check_snmp_brother  
    command_line  $USER1$/check_snmp_brother $ARG1$ $HOSTADDRESS$ $ARG2$ $ARG3$  
    }
    define service{  
            use                          default-service  
            host_name                    PRINTER  
            service_description          Toner Black  
            check_command                check_snmp_brother!public!20!10  
            }

**Скрипт корректно работает для модели Brother DCP-7065DN. Если будет работать для других моделей, буду рад если вы мне сообщите.**