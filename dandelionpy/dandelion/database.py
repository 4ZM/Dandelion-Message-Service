"""
Copyright (c) 2011 Anders Sundman <anders@4zm.org>

This file is part of dandelionpy

dandelionpy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

dandelionpy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with dandelionpy.  If not, see <http://www.gnu.org/licenses/>.
"""

import random
import sqlite3
import dandelion.util

from dandelion.message import Message

class ContentDBException(Exception):
    pass

class ContentDB: 
    """Message data base for the Dandelion Message Service"""
    
    class _classproperty(property):
        """Class property (mix of classmethod and property)"""
        def __get__(self, obj, type_):
            return self.fget.__get__(None, type_)()
    
    _ID_LENGTH_BYTES = 18 # 144 bit id
    
    __instance = None # Singleton instance

    @classmethod
    def register(cls, db):
        """Register a database instance
        
        Can only register one database (available from the db property) 
        """
        
        if cls.__instance is not None:
            raise ContentDBException
        
        if db is None or not isinstance(db, ContentDB):
            raise ContentDBException
        
        cls.__instance = db

    @classmethod
    def unregister(cls):
        """Unregister currently registered db"""
        
        if cls.__instance is None:
            raise ContentDBException
        
        cls.__instance = None
            
    @_classproperty
    @classmethod
    def db(cls):
        """Access the registered database."""
        return cls.__instance
    
    @property
    def id(self):
        """The data base id (bytes)"""

    def add_messages(self, msgs):
        """Add a a list of messages to the data base.
        
        Will add all messages, not already in the data base to the data base and return a 
        time cookie (bytes) that represents the point in time after the messages have been added.
        If no messages were added, it just returns the current time cookie. 
        """

    def remove_messages(self, msgs=None):
        """Removes messages from the data base.
        
        The specified list of messages will be removed from the data base. 
        If the message parameter is omitted, all messages in the data base will be removed.
        """
    @property
    def message_count(self):
        """Returns the number of messages currently in the data base (int)"""

    def contains_message(self, msgid):
        """Returns true if the database contains the msgid"""

    def get_messages(self, msgids=None):
        """Get a list of all messages with specified message id"""

    def get_messages_since(self, time_cookie=None):
        """Get messages from the data base.
        
        If a time cookie is specified, all messages in the database from (and 
        including) the time specified by the time cookie will be returned.  
        If the time cookie parameter is omitted, all messages currently in the 
        data base will be returned.
        """
        
    def _generate_random_db_id(self):
        """Create a new db id"""
        return bytes([int(random.random() * 255) for _ in range(ContentDB._ID_LENGTH_BYTES)])

class SQLiteContentDB(ContentDB):
    """A content database with a sqlite backend""" 
    
    def __init__(self, db_file):
        super().__init__()
        
        if db_file is None or not isinstance(db_file, str):
            raise ContentDBException
        
        self._db_file = db_file
        
        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()
            self._create_tables(c)
            self._id = self._create_id(c)
    
    @property
    def id(self):
        """The data base id (bytes)"""
        return self._id

    def add_messages(self, msgs):
        """Add a a list of messages to the data base.
        
        Will add all messages, not already in the data base to the data base and return a 
        time cookie (bytes) that represents the point in time after the messages have been added.
        If no messages were added, it just returns the current time cookie. 
        """
    
        if msgs is None:
            raise ValueError
        
        if not hasattr(msgs, '__iter__'):
            raise TypeError
        
        """Make sure the list only contains messages"""
        if not all([isinstance(m, Message) for m in msgs]):
            raise TypeError

        
        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()

            tc = self._current_tc(c)

            no_added = 0
            for m in msgs:
                c.execute('SELECT count(*) FROM messages WHERE id IS (?)',
                          (dandelion.util.encode_b64_bytes(m.id).decode(),))
                
                if c.fetchone()[0] == 1: # Allready contains msg
                    continue

                c.execute("""INSERT INTO messages VALUES (?,?,?)""", 
                          (dandelion.util.encode_b64_bytes(m.id).decode(), m.text, tc))
                
                no_added += 1

            if no_added == 0:
                return bytes([tc]) # Did't add anything, no new tc

            tc_int = c.execute("""INSERT INTO time_cookies (time) VALUES (datetime('now'))""").lastrowid
            return bytes([tc_int])
            
            
            
    def remove_messages(self, msgs=None):
        """Removes messages from the data base.
        
        The specified list of messages will be removed from the data base. 
        If the message parameter is omitted, all messages in the data base will be removed.
        """

        if msgs is not None and not hasattr(msgs,'__iter__'):
            raise TypeError

        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()
            
            if msgs is None:
                c.execute("""DELETE FROM messages""")
            else:
                c.executemany("""DELETE FROM messages WHERE id IS (?)""", 
                              [(dandelion.util.encode_b64_bytes(m.id).decode(),) for m in msgs])

    @property
    def message_count(self):
        """Returns the number of messages currently in the data base (int)"""
        
        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()
            return c.execute("""SELECT count(*) FROM messages""").fetchone()[0]

    def contains_message(self, msgid):
        """Returns true if the database contains the msgid"""
        
        if not isinstance(msgid, bytes):
            raise TypeError

        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()
            c.execute('SELECT count(*) FROM messages WHERE id IS (?)',
                      (dandelion.util.encode_b64_bytes(msgid).decode(),))
            cnt = c.fetchone()[0] 
            if cnt == 0:
                return False
            elif cnt == 1:
                return True
            else:
                raise ContentDBException # Duplicate id should never happen

    def get_messages(self, msgids=None):
        """Get a list of all msg_rows with specified message id"""

        if msgids is not None and not hasattr(msgids, '__iter__'):
            raise TypeError

        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()
            
            if msgids is None:
                c.execute('SELECT * FROM messages')
                msg_rows = c.fetchall()
            else:
                msg_rows = []
                for m in msgids: 
                    # TODO There has to be some way of geting a list into the IN clause
                    c.execute('SELECT * FROM messages WHERE id IN (?)', (dandelion.util.encode_b64_bytes(m).decode(),))
                    msg_rows.extend([c.fetchone()])
                    
            return [Message(m[1]) for m in msg_rows]


    def get_messages_since(self, time_cookie=None):
        """Get messages from the data base.
        
        If a time cookie is specified, all messages in the database from (and 
        including) the time specified by the time cookie will be returned.  
        If the time cookie parameter is omitted, all messages currently in the 
        data base will be returned.
        """
        
        if time_cookie is not None and not isinstance(time_cookie, bytes):
            raise TypeError 

        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()
            
            if time_cookie is None:
                c.execute('SELECT msg FROM messages')
            else:
                tc = dandelion.util.decode_int(time_cookie)
                if c.execute('SELECT count(*) FROM time_cookies WHERE tc == ?', (tc,)).fetchone()[0] == 0:
                    raise ValueError

                c.execute('SELECT msg FROM messages WHERE tc >= ?', (tc,))
                
            msgs = [Message(row[0]) for row in c.fetchall()]
            
            return (dandelion.util.encode_int(self._current_tc(c)), msgs)

    def _create_id(self, cursor):        
        cursor.execute("""SELECT count(id) FROM self_db""")
        if cursor.fetchone()[0] == 0:
            newid = dandelion.util.encode_b64_bytes(self._generate_random_db_id()).decode()
            cursor.execute("""INSERT INTO self_db (id) values (?)""", (newid,))
        cursor.execute("""SELECT id FROM self_db""")
        return dandelion.util.decode_b64_bytes(cursor.fetchone()[0].encode())

    def _create_tables(self, cursor):
        """Create the tables if they don't exist"""
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS time_cookies 
            (tc INTEGER PRIMARY KEY AUTOINCREMENT, time INTEGER)''')
        
        if cursor.execute('''SELECT count(*) FROM time_cookies''').fetchone()[0] == 0:
            cursor.execute("""INSERT INTO time_cookies (time) VALUES (datetime('now'))""")
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY, msg TEXT NOT NULL, 
            tc INTEGER NOT NULL REFERENCES time_cookies (tc))''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS remote_databases 
            (id TEXT PRIMARY KEY, time_cookie TEXT)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS self_db (id TEXT PRIMARY KEY)''')

    def _current_tc(self, cursor):
        return cursor.execute('''SELECT max(tc) FROM time_cookies''').fetchone()[0]

class InMemoryContentDB(ContentDB): 
    """A naive in memory data base for the Dandelion Message Service"""
    
    _ID_LENGTH_BYTES = 18 # 144 bit id
    
    def __init__(self):
        """Create a new data base with a random id"""
        super().__init__()        
        
        self._messages = []
        self._id = self._generate_random_db_id()
        self._rev = 0

    @property
    def id(self):
        """The data base id (bytes)"""
        return self._id
    
    def add_messages(self, msgs):
        """Add a a list of messages to the data base.
        
        Will add all messages, not already in the data base to the data base and return a 
        time cookie (bytes) that represents the point in time after the messages have been added.
        If no messages were added, it just returns the current time cookie. 
        
        """
        
        if msgs is None:
            raise ValueError
        
        if not hasattr(msgs, '__iter__'):
            raise TypeError
        
        """Make sure the list only contains messages"""
        if not all([isinstance(m, Message) for m in msgs]):
            raise TypeError
        
        """Add the messages not already present to the data base"""
        untagged_messages = [m for (_, m) in self._messages]
        new_msgs = [(self._rev, m) for m in msgs if m not in untagged_messages]
        
        if len(new_msgs) > 0:
            self._messages.extend(new_msgs)
            self._rev += 1
            
        return dandelion.util.encode_int(self._rev)
    
    def remove_messages(self, msgs=None):
        """Removes messages from the data base.
        
        The specified list of messages will be removed from the data base. 
        If the message parameter is omitted, all messages in the data base will be removed.
        """
        
        if msgs is None:
            self._messages = []
            return
        
        if not hasattr(msgs,'__iter__'):
            raise TypeError
        
        to_delete = [(tc,m) for tc, m in self._messages if m in msgs]
                        
        for m in to_delete:
            self._messages.remove(m)
            
    @property
    def message_count(self):
        """Returns the number of messages currently in the data base (int)"""
        
        return len(self._messages)
        
    def contains_message(self, msgid):
        """Returns true if the database contains the msgid"""
        
        if not isinstance(msgid, bytes):
            raise TypeError
            
        return len([m for (_, m) in self._messages if m.id == msgid]) > 0

    def get_messages(self, msgids=None):
        """Get a list of all messages with specified message id"""
        
        if msgids is None:
            return [m for _, m in self._messages]
        
        if not hasattr(msgids, '__iter__'):
            raise TypeError
               
        return [m for _, m in self._messages if m.id in msgids]

    def get_messages_since(self, time_cookie=None):
        """Get messages from the data base.
        
        If a time cookie is specified, all messages in the database from (and 
        including) the time specified by the time cookie will be returned.  
        If the time cookie parameter is omitted, all messages currently in the 
        data base will be returned.
        """
        
        if time_cookie is None:
            return (dandelion.util.encode_int(self._rev), [m for (_, m) in self._messages])
        
        if not isinstance(time_cookie, bytes):
            raise TypeError 
        
        tc_num = dandelion.util.decode_int(time_cookie)
        
        if not (0 <= tc_num <= self._rev):
            raise ValueError
        
        msgs = []
        for tc, m in self._messages:
            if tc >= tc_num:
                msgs.append(m)
        
        return (dandelion.util.encode_int(self._rev), msgs)
    