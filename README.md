** Welcome to OFAutomation !

-------------
Introduction
-------------
OFAutomation is a solution that aims to interact with and automate all 
components in the OpenFlow/SDN network.

OFAutomation is a end to end automation solution for automating tests 
run across various components in an OpenFlow topology. This solution 
aims to provide an automation framework, that is not just exhaustive in
coverage, but also makes it easy to debug and author scripts. 
It allows for authoring scripts in plain English and can be run standalone
from the command line.

------------
Test Launch
------------

In order to run OFAutomation, you must have:

* A Linux 2.6.26 or greater kernel compiled with network namespace support 
  enabled (see INSTALL for additional information.)

* python 2.6 or higher versions.

* Install python package configObj. It can be installed as :

     openflow@ETH-Tutorial:~$ sudo pip install configObj

* Finally ,launching of test must be from "bin" directory which
  resides into "OFAutomation-master" directory as following:

openflow@ETH-Tutorial:~/OFAutomation-master/bin$ ./launcher.py --test MininetTest

--------
Examples
--------
For more examples, refer 'examples' directory.
To launch of the given example run as:
Please find the below link for examples:
     https://github.com/OFAutomation/OFAutomation/tree/OFAutomation-0.0.1/examples

openflow@ETH-Tutorial:~/OFAutomation-master/bin$ ./launcher.py --example CaseParams   
     
     

---------
Documents
--------- 
* HTML_Document directory provided with auto generated Document 
  for the OFAutomation framework.
* index.html is the home page.

-------
 Note
-------
Corresponding logs for the executed test or example will be available in ~/logs/
