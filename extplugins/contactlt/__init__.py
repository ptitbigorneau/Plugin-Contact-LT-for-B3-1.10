# -*- coding: utf-8 -*-
#
# ContactLT For Urban Terror plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2015 PtitBigorneau - www.ptitbigorneau.fr
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA


__author__  = 'PtitBigorneau www.ptitbigorneau.fr'
__version__ = '1.6-lt'

import b3
import b3.plugin
from b3 import clients
from b3.functions import getCmd

import smtplib
#from email.MIMEText import MIMEText
from email import *

import time, threading, thread
import calendar
from time import gmtime, strftime

def cdate():
        
    time_epoch = time.time() 
    time_struct = time.gmtime(time_epoch)
    date = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
    mysql_time_struct = time.strptime(date, '%Y-%m-%d %H:%M:%S') 
    cdate = calendar.timegm( mysql_time_struct)

    return cdate

class ContactltPlugin(b3.plugin.Plugin):

    _adminPlugin = None    
    _frommail = None
    _tomail = None
    _smtpserver = "localhost"
    _maxmessage = 5
    _tempmaxmessage = 60
    _tempmessage = 5
    _gmailusername = None
    _gmailpwd = None
	
    def onLoadConfig(self):
	
        self._frommail = self.getSetting('settings', 'frommail', b3.STRING, self._frommail)
        self._tomail = self.getSetting('settings', 'tomail', b3.STRING, self._tomail)
        self._smtpserver = self.getSetting('settings', 'smtpserver', b3.STRING, self._smtpserver)
        self._maxmessage = self.getSetting('settings', 'maxmessage', b3.INT, self._maxmessage)		
        self._tempmaxmessage = self.getSetting('settings', 'tempmaxmessage', b3.INT, self._tempmaxmessage)	
        self._tempmessage = self.getSetting('settings', 'tempmessage', b3.INT, self._tempmessage)
        self._gmailusername = self.getSetting('settings', 'gmailusername', b3.STRING, self._gmailusername)
        self._gmailpwd = self.getSetting('settings', 'gmailpwd', b3.STRING, self._gmailpwd)
    
    def onStartup(self):
        
        self._adminPlugin = self.console.getPlugin('admin')
        
        if not self._adminPlugin:

            self.error('Could not find admin plugin')
            return False

        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp

                func = getCmd(self, cmd)
                if func:
                    self._adminPlugin.registerCommand(self, cmd, level, func, alias)

    def cmd_contact(self, data, client, cmd=None):
        """\
        <message> - Message to administrator server
        """

        mdate = cdate() 
        
        cursor = self.console.storage.query("""
        SELECT *
        FROM contact n 
        WHERE n.client_id = '%s'
        """ % (client.id))
           
        if cursor.rowcount > 0:
            
            sr = cursor.getRow()
            cnenvois=sr['nenvois']
            cmdate=sr['date']
            cauthoriz=sr['authoriz']            
            maxmessage=self._maxmessage
            tempmaxmessage=self._tempmaxmessage*60
            tempmessage=self._tempmessage*60
            
            if mdate - tempmaxmessage > cmdate:
            
                cnenvois=0
                cursor = self.console.storage.query("""
                UPDATE contact
                SET nenvois= '%s'
                WHERE client_id = '%s'
                """ % (cnenvois, client.id))
                cursor.close()
            
            if cauthoriz==0:
                
                client.message('You are not authorized to send a message')
                return False

            if (cnenvois>=maxmessage) and (client.maxLevel<self._acontactlevel):
                     
                client.message('Your not authorized for the moment to send messages')
                return False            
            
            if (mdate - tempmessage < cmdate) and (client.maxLevel<self._bancontactlevel):
                
                client.message('Wait! You have already send a message')
                return False              
        
        cursor.close()

        if data:
            
            smessage = data
        
        else:
            
            client.message('!contact <message to admin>')
            return
        
        smessage = smessage.replace('. ', '.\r\n')
        smessage = smessage.replace('? ', '?\r\n')
        smessage = smessage.replace('! ', '!\r\n')
        
        if not smessage:
            
            client.message('!contact <message to admin>')
            return False
               
        if smessage:
            
            mto = self._tomail
            mfrom = self._frommail
            server = self.nameserver()
            smtpserver = self._smtpserver
            gmailusername = self._gmailusername
            gmailpwd = self._gmailpwd
            
            sujetmail = 'Message from B3 Plugin Contact from server: ' + server
            id =  str(client.id)
            message='Server : ' + server + ' - Message from : ' + client.name + ' - Guid : ' + client.guid + ' - Id Player : @' + id + ' - Ip : ' + client.ip + '\r\n\n ' + client.name + ' writes :\r\n\n' + smessage
                                          
            if smtpserver == 'smtp.gmail.com' :
            
                email = MIMEText.MIMEText(message) 
                email['From']=mfrom
                email['To']=mto 
                email['Subject']=sujetmail 
                server = smtplib.SMTP('smtp.gmail.com',587)
                #server.set_debuglevel(1)
                server.ehlo(gmailusername)
                server.starttls()
                server.ehlo()
                server.login(gmailusername, gmailpwd)
                server.sendmail(mfrom, mto, email.as_string())
                server.quit()

            else:
                
                email = MIMEText.MIMEText(message) 
                email['From']=mfrom
                email['To']=mto 
                email['Subject']=sujetmail 
                server = smtplib.SMTP(smtpserver) 
                server.sendmail(mfrom, mto, email.as_string())
                server.quit()
                
            client.message('Your message has been sent')
            client.message('Your nickname, ip, guid and id appear in the message sent')
            
            cursor = self.console.storage.query("""
            SELECT *
            FROM contact n 
            WHERE n.client_id = '%s'
            """ % (client.id))
            
            if cursor.rowcount > 0:
                
                sr = cursor.getRow()
                cnenvois=sr['nenvois']
                cnenvois = cnenvois + 1
                cursor = self.console.storage.query("""
                UPDATE contact
                SET nenvois= '%s', date= '%s' 
                WHERE client_id = '%s'
                """ % (cnenvois, mdate, client.id))
                cursor.close()
                return False
            
            cursor.close()
            
            cursor = self.console.storage.query("""
            INSERT INTO contact
            VALUES (%s, %s, %s, %s)
            """ % (client.id, 1, 1, mdate))

            cursor.close()
            
        else:
            return False
    
    def cmd_addmail(self, data, client, cmd=None):
        """\
        <message> - Register or change your mail address 
        """

        if data:

            input = self._adminPlugin.parseUserCmd(data)
        
        else:
            
            client.message('!addmail <your mail address>')
            return
        
        smail=input[0]
        test1= smail.count('@')
        test2 = smail.count('.')         
        
        if (test1==0) or (test2==0):
            client.message('Mail address is not valid')
            return False        
        
        if smail:
            
            cursor = self.console.storage.query("""
            SELECT *
            FROM adminmail n 
            WHERE n.client_id = '%s'
            """ % (client.id))

            if cursor.rowcount > 0:
                cursor = self.console.storage.query("""
                UPDATE adminmail
                SET mail='%s' 
                WHERE client_id = %s
                """ % (smail, client.id))
                client.message('Your new mail address : %s is now registered' %(smail))
                cursor.close()
                return False
            cursor.close()
            cursor = self.console.storage.query("""
            INSERT INTO adminmail
            VALUES (%s, '%s')
            """ % (client.id,  smail))

            cursor.close()
            client.message('Your mail address : %s is now registered' %(smail))
       
        else:
            return False
    
    def cmd_delmail(self, data, client, cmd=None):
        """\
        <message> - Delete your mail address 
        """

        cursor = self.console.storage.query("""
        SELECT n.client_id
        FROM adminmail n 
        WHERE n.client_id = '%s'
        """ % (client.id))
        
        if cursor.rowcount == 0:
            client.message("^7You don't have a registered mail address")
            return False
        
        cursor.close()
        
        cursor = self.console.storage.query("""
        DELETE FROM adminmail
        WHERE client_id = '%s'
        """ % (client.id))
        
        cursor.close()
        
        client.message("^7Your mail address has been deleted")
    
    def cmd_listmail(self, data, client, cmd=None):
        """\
        <message> - Admins list with an mail address registered 
        """
        
        thread.start_new_thread(self.listmail, (data, client))
        
    def listmail(self, data, client):
            
        cursor = self.console.storage.query("""
        SELECT *
        FROM adminmail
        """)
        c = 1
        
        if cursor.EOF:
          
            client.message('Admins list with an mail address registered is empty')
            cursor.close()            
            return False
        
        while not cursor.EOF:
            sr = cursor.getRow()
            cid = sr['client_id']
            scid= '@'+str(cid)
            sclient = self._adminPlugin.findClientPrompt(scid, client)
            client.message('^2%s^7 - id : ^2@%s^7 - level : (^1%s^7)' % (sclient.exactName, cid, sclient.maxLevel))
            cursor.moveNext()
            c += 1
            
        cursor.close()
    
    def cmd_bancontact(self, data, client, cmd=None):
        """\
        <message> - ban from Contact 
        """

        mdate = cdate() 
        
        if data:

            input = self._adminPlugin.parseUserCmd(data)

        else:
            
            client.message('!banacontact <name or id>')
            return
        
        sclient = self._adminPlugin.findClientPrompt(input[0], client)
        
        if sclient:
            
            if sclient.maxLevel>=self._bancontactlevel:
                
                client.message("%s can not be banned from Contact"%(sclient.exactName))
                return False
            
            cursor = self.console.storage.query("""
            SELECT *
            FROM contact n 
            WHERE n.client_id = '%s'
            """ % (sclient.id))

            if cursor.rowcount > 0:
                
                cursor = self.console.storage.query("""
                UPDATE contact
                SET authoriz="0" , date=%s
                WHERE client_id = %s
                """ % (sclient.id, mdate))
                
                client.message('%s is now ban from Contact' %(sclient.exactName))
                
                cursor.close()
                
                return False
            cursor.close()
            
            cursor = self.console.storage.query("""
            INSERT INTO contact
            VALUES (%s, %s, %s, %s)
            """ % (sclient.id, 0, 0, mdate))

            cursor.close()        
            
            client.message('%s is now ban from Contact' %(sclient.exactName))
       
        else:
            return False

    def cmd_unbancontact(self, data, client, cmd=None):
        """\
        <message> - unban from Contact
        """
        
        if data:
            
            input = self._adminPlugin.parseUserCmd(data)
        
        else:
            
            client.message('!unbanacontact <name or id>')
            return
        
        sclient = self._adminPlugin.findClientPrompt(input[0], client)
        
        if sclient:
            
            cursor = self.console.storage.query("""
            SELECT n.authoriz
            FROM contact n 
            WHERE n.client_id = %s
            """ % (sclient.id))
        
            if cursor.rowcount == 0:
                
                client.message("%s^7 not ban from Contact"%(sclient.exactName))
                return False
            
            cursor.close()
        
            cursor = self.console.storage.query("""
            UPDATE contact
            SET authoriz="1"
            WHERE client_id = %s
            """ % (sclient.id))
            
            cursor.close()
            
            client.message("%s^7 is unban from Contact"%(sclient.exactName))
    
    def cmd_listcontact(self, data, client, cmd=None):
        """\
        <message> - Send by e_mail the users list from Contact and see the last 10 users
        """
        thread.start_new_thread(self.listcontact, (data, client))

    def listcontact(self, data, client, cmd=None):
    
        cursor = self.console.storage.query("""
        SELECT *
        FROM contact
        ORDER BY date DESC LIMIT 0, 10
        """)
        c = 1
        
        if cursor.EOF:
          
            client.message('Users list from Contact is empty')
            cursor.close()            
        
        while not cursor.EOF:
        
            sr = cursor.getRow()
            cid = sr['client_id']
            cdate = time.strftime('%d-%m-%Y %H:%M',time.localtime(sr['date']))
            cauthoriz = sr['authoriz']
            scid= '@'+str(cid)
            
            if cauthoriz==0:
                cstatus='^1Banned'
            if cauthoriz==1:
                cstatus='^2Authorized'                   
            
            sclient = self._adminPlugin.findClientPrompt(scid, client)
            client.message('^2%s^7- ID : ^2@%s^7 - Date : ^2%s^7 - Status %s^7' %(sclient.name, sclient.id, cdate, cstatus))
            
            cursor.moveNext()
            
            c += 1
        
        cursor.close()
                
        cursor = self.console.storage.query("""
        SELECT *
        FROM contact
        """)

        c = 1

        message = '\r\n'
        
        if cursor.EOF:
          
            message='Users list from Contact is empty'
            cursor.close() 
            return False
            
        while not cursor.EOF:
        
            sr = cursor.getRow()
            cid = sr['client_id']
            cdate = time.strftime('%d-%m-%Y %H:%M',time.localtime(sr['date']))
            cauthoriz = sr['authoriz']
            scid= '@'+str(cid)

            if cauthoriz==0:
                cstatus='Banned'
            if cauthoriz==1:
                cstatus='Authorized'                   

            sclient = self._adminPlugin.findClientPrompt(scid, client)
            message= message + '%s - ID : @%s - Guid : %s - IP : %s - Date : %s - Status : %s\r\n' % (sclient.name, sclient.id, sclient.guid, sclient.ip, cdate, cstatus)
            
            cursor.moveNext()
            
            c += 1
            
        cursor.close()    
        
        mto = self._tomail
        mfrom = self._frommail
        server = self.nameserver()
        smtpserver = self._smtpserver
        sujetmail = 'Clients list from Contact Server : ' + server
                                                   
        email = MIMEText.MIMEText(message) 
        email['From']=mfrom
        email['To']=mto 
        email['Subject']=sujetmail 
        server = smtplib.SMTP(smtpserver) 
        server.sendmail(mfrom, mto, email.as_string())
        server.quit()
        client.message('Clients list from Contact has been sent by e_mail to %s'%(mto))
        
    def cmd_lookcontact(self, data, client, cmd=None):
        """\
        <message> - Look if player is in Contact list 
        """

        if data:
        
            input = self._adminPlugin.parseUserCmd(data)

        else:
            
            client.message('!lookcontact <name or id>')
            return
        
        sclient = self._adminPlugin.findClientPrompt(input[0], client)
        
        if sclient:        
        
            cursor = self.console.storage.query("""
            SELECT *
            FROM contact n 
            WHERE n.client_id = %s
            """ % (sclient.id))
        
            if cursor.rowcount == 0:
                client.message("%s^7 is not in Contact list"%(sclient.exactName))
                return False
            
        
            sr = cursor.getRow()
            cauthoriz = sr['authoriz']
            cdate = time.strftime('%d-%m-%Y %H:%M',time.localtime(sr['date']))
            
            if cauthoriz==0:
                cstatus='^1Banned'
            if cauthoriz==1:
                cstatus='^2authorized'                   
                        
            client.message('^2%s^7 - id : ^2@%s^7 - Date : ^2%s^7' % (sclient.exactName, sclient.id, cdate))
            client.message('^7Status : %s^7' % (cstatus))

            cursor.close()
        else:
            return False
			
    def nameserver(self):

        nameserver = self.console.stripColors(self.console.getCvar('sv_hostname').getString())
        return nameserver
        