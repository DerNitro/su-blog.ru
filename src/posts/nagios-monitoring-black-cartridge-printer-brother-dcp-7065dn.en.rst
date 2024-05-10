.. title: Nagios Monitoring Black Cartridge Printer Brother DCP-7065DN
.. slug: nagios-monitoring-black-cartridge-printer-brother-dcp-7065dn
.. date: 2013-05-21 12:00:00 UTC+03:00
.. tags: nagios, monitoring, linux
.. category: monitoring
.. link:
.. description: Printer monitoring plugin for Brother DCP-7065DN
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

The IT farm has 4 Brother DCP-7065DN printers, I wanted to monitor the status of the cartridges, and ran into problems:
 1. The plugin for Nagios ``check_snmp_printer`` is not suitable, it returns the wrong value, although it is perfect for monitoring the state of the drum.
 2. I could not find on the network what SNMP OID of the cartridge status for this printer.

I wrote to Brother support ... And unexpectedly for themselves they answered and gave me the OID for my printer.
Opened my favorite VIM and wrote a bash script for Nagios. And now I share it `check_snmp_brother <https://github.com/DerNitro/check_snmp_brother>`_.

We put this script in the folder with Nagios plugins, set the necessary rights, and set the flag for execution.

Configuring Nagios

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

**The script works correctly for Brother DCP-7065DN model. If it works for other models, I will be glad if you let me know.**