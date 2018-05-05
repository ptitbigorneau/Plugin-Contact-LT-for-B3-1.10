# contactlt plugin
# Plugin for B3 (www.bigbrotherbot.net)
# www.ptitbigorneau.fr

need smtp server

contact plugin (v1.6-lt) for B3

Requirements
------------

* BigBortherBot(3) >= version 1.10

Installation:
-------------

1. Copy the 'contact' folder into 'b3/extplugins' and 'contact.ini' file into '/b3/extplugins/conf'.

2. Open your B3.ini or b3.xml file (default in b3/conf) and add the next line in the [plugins] section of the file:
    for b3.xml
        <plugin name="contact" config="@b3/extplugins/conf/contact.ini"/>
    for b3.ini
        contact: @b3/extplugins/conf/contact.ini

3. Open contact.ini

modify e_mail address for send message
modify e_mail address for receive message
modify server name
modify smtp server name  (localhost or smtp.exemple.com)
for smtp.gmail.com 
  modify gmailusername 
  modify gmailpwd  

4. Run the contact SQL script (contact.sql or contact_update.sql if you have contact v1.1) on your B3 database