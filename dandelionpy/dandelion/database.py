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

from dandelion.message import Message
import dandelion.util

class ContentDBException(Exception):
    pass

class ContentDB: 
    """Message data base for the Dandelion Message Service.
    
    Abstract base class and static singleton.
    """
    
    class _classproperty(property):
        """Class property (mix of classmethod and property)"""
        def __get__(self, obj, type_):
            return self.fget.__get__(None, type_)()
    
    _DBID_LENGTH_BYTES = 18 
    _TCID_LENGTH_BYTES = 9 
    
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

    @property
    def name(self):
        """The data base name (can be None)"""

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
    
    @classmethod
    def _generate_random_db_id(self):
        """Create a new db id"""
        return self._generate_random_id(ContentDB._DBID_LENGTH_BYTES)
    
    @classmethod
    def _generate_random_tc_id(self):
        """Create a new time_cookie id"""
        return self._generate_random_id(ContentDB._TCID_LENGTH_BYTES)

    @classmethod
    def _generate_random_id(self, length):
        """Create a new random binary id"""
        return bytes([int(random.random() * 255) for _ in range(length)])

    @classmethod
    def _encode_id(self, id):
        """Binary to text encoding of id's"""
        return dandelion.util.encode_b64_bytes(id).decode()

    @classmethod
    def _decode_id(self, id):
        """Text to binary decoding of id's"""
        return dandelion.util.decode_b64_bytes(id.encode())
    

class SQLiteContentDB(ContentDB):
    """A content database with a sqlite backend."""
     
    _CREATE_TABLE_DATABASES = """CREATE TABLE IF NOT EXISTS databases
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        fingerprint TEXT UNIQUE,
        alias TEXT)"""

    _CREATE_TABLE_TIME_COOKIES = """CREATE TABLE IF NOT EXISTS time_cookies
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        cookie TEXT NOT NULL,
        dbid INTEGER NOT NULL REFERENCES databases (id))"""

    _CREATE_TABLE_IDENTITIES = """CREATE TABLE IF NOT EXISTS identities
        (fingerprint TEXT PRIMARY KEY,
        dsa_y INTEGER NOT NULL,
        dsa_g INTEGER NOT NULL,
        dsa_p INTEGER NOT NULL,
        dsa_q INTEGER NOT NULL,
        rsa_n INTEGER NOT NULL,
        rsa_e INTEGER NOT NULL,
        cookieid INTEGER NOT NULL REFERENCES time_cookies (id))"""

    _CREATE_TABLE_PRIVATE_IDENTITIES = """CREATE TABLE IF NOT EXISTS
        private_identities
        (fingerprint TEXT PRIMARY KEY REFERENCES identities (fingerprint),
        dsa_x INTEGER NOT NULL,
        rsa_d INTEGER NOT NULL)"""

    _CREATE_TABLE_MESSAGES = """CREATE TABLE IF NOT EXISTS messages
        (msgid TEXT PRIMARY KEY,
        msg TEXT NOT NULL,
        receiver TEXT REFERENCES identities (fingerprint),
        sender TEXT REFERENCES identities (fingerprint),
        signature TEXT,
        cookieid INTEGER NOT NULL REFERENCES time_cookies (id))"""

    _CREATE_VIEW_TCDB = """CREATE VIEW IF NOT EXISTS time_cookies_db AS 
        SELECT time_cookies.id AS id, time_cookies.cookie AS cookie, databases.fingerprint AS dbfp 
        FROM time_cookies JOIN databases ON time_cookies.dbid=databases.id"""

    def __init__(self, db_file, id=None):
        """Create a SQLite backed data base."""
        super().__init__()
        
        if db_file is None or not isinstance(db_file, str):
            raise ContentDBException
        
        self._db_file = db_file
        
        if id is None:
            self._id = ContentDB._generate_random_db_id()
            self._encoded_id = ContentDB._encode_id(self._id)
        else:
            self._id = id
            self._encoded_id = ContentDB._encode_id(self._id)
            
            """Check existence of specified id"""
            with sqlite3.connect(self._db_file) as conn:  
                c = conn.cursor()
                if c.execute("""SELECT count(*) FROM databases WHERE fingerprint=?""", 
                             (self._decoded_id,)).fetchone()[0] != 1:
                    raise ValueError
        
        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()
            self._create_tables(c)

    @property
    def id(self):
        """The data base id (bytes)"""
        return self._id
    
    @property
    def name(self):
        """The data base name (can be None)"""
        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()
            return c.execute("""SELECT name FROM databases WHERE fingerprint=?""", 
                             (self._decoded_id,)).fetchone()[0]
    

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
        
        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()

            """Create a new, unused id"""
            while True:
                tc = self._encode_id(self._generate_random_tc_id())
                if c.execute("""SELECT count(*) FROM time_cookies_db WHERE cookie=? and dbfp=?""", (tc, self._encoded_id)).fetchone()[0] == 0:
                    break
                
            """Insert the new time cookie"""
            tcid = c.execute("""INSERT INTO time_cookies (cookie, dbid) VALUES (?, (SELECT id FROM databases WHERE fingerprint=?))""", (tc, self._encoded_id)).lastrowid

            pre_msgs = c.execute("""SELECT count(*) FROM messages""").fetchone()[0] # Count before insert
            
            try:
                for m in msgs:
                    # Add sender/receiver
                    c.execute("""INSERT OR IGNORE INTO messages (msgid, msg, receiver, sender, signature, cookieid) VALUES (?,?,?,?,?,?)""", 
                              (dandelion.util.encode_b64_bytes(m.id).decode(), 
                               m.text, 
                               None if not m.has_receiver else dandelion.util.encode_b64_bytes(m.receiver).decode(), 
                               None if not m.has_sender else dandelion.util.encode_b64_bytes(m.sender).decode(),
                               None if not m.has_sender else dandelion.util.encode_b64_bytes(m.signature).decode(),
                               tcid))
            except AttributeError: # Typically caused by types other than Message in list
                raise TypeError
            
            post_msgs = c.execute("""SELECT count(*) FROM messages""").fetchone()[0] # Count after insert
            
            """No new messages? Rollback tc insert and use old value"""
            if (post_msgs - pre_msgs) == 0: 
                conn.rollback() 
                tc = c.execute("""SELECT max(id), cookie FROM time_cookies_db WHERE dbfp=?""", (self._encoded_id,)).fetchone()[1]
                
            return self._decode_id(tc)

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
                c.executemany("""DELETE FROM messages WHERE msgid=?""", 
                              [(dandelion.util.encode_b64_bytes(m.id).decode(),) for m in msgs])

    @property
    def message_count(self):
        """Returns the number of messages currently in the data base (int)"""
        
        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()
            return c.execute("""SELECT count(*) 
                                FROM messages JOIN time_cookies_db ON messages.cookieid = time_cookies_db.id 
                                WHERE time_cookies_db.dbfp=?""", (self._encoded_id,)).fetchone()[0]

    def contains_message(self, msgid):
        """Returns true if the database contains the msgid"""
        
        if not isinstance(msgid, bytes):
            raise TypeError

        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()
            c.execute('SELECT msgid FROM messages WHERE msgid=?', (dandelion.util.encode_b64_bytes(msgid).decode(),)) 
            if c.fetchone() is None:
                return False
            else:
                return True

    def get_messages(self, msgids=None):
        """Get a list of all msg_rows with specified message id"""

        if msgids is not None and not hasattr(msgids, '__iter__'):
            raise TypeError

        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()
            
            if msgids is None:
                c.execute("""SELECT msg, receiver, sender, signature 
                             FROM messages JOIN time_cookies_db ON messages.cookieid = time_cookies_db.id 
                             WHERE time_cookies_db.dbfp = ?""", (self._encoded_id,))
                msg_rows = c.fetchall()
            else:
                msg_rows = []
                try:
                    for m in msgids: 
                        c.execute("""SELECT msg, receiver, sender, signature 
                                     FROM messages JOIN time_cookies_db ON messages.cookieid = time_cookies_db.id 
                                     WHERE msgid = ? AND dbfp = ?""", (dandelion.util.encode_b64_bytes(m).decode(), self._encoded_id))
                        msg_rows.extend([c.fetchone()])
                except AttributeError:
                    raise TypeError
                
            return [Message(m[0], m[1], m[2], m[3]) for m in msg_rows] 


    def get_messages_since(self, time_cookie=None):
        """Get messages from the data base.
        
        If a time cookie is specified, all messages in the database from (and 
        including) the time specified by the time cookie will be returned.  
        If the time cookie parameter is omitted, all messages currently in the 
        data base will be returned.
        """

        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()
            
            if time_cookie is None:
                c.execute("""SELECT msg, sender, receiver 
                             FROM messages JOIN time_cookies_db ON messages.cookiedb = time_cookies_db.id 
                             WHERE time_cookies_db.dbfp = ?""", (self._encoded_id,))
            else:
                if not isinstance(time_cookie, bytes):
                    raise TypeError
                if len(time_cookie) == 0:
                    raise ValueError
                
                c.execute("""CREATE TEMPORARY VIEW new_cookies AS 
                             SELECT tc1.id AS tcid, tc1.cookie AS new_cookie, tc2.cookie AS old_cookie, tc1.dbfp AS dbfp FROM time_cookies_db AS tc1 JOIN time_cookies_db AS tc2 
                             WHERE tc1.id > tc2.id""")

                # Is it a valid cookie?
                if c.execute("""SELECT count(*) FROM time_cookies_db WHERE cookie=? AND dbfp=?""", 
                          (dandelion.util.encode_b64_bytes(time_cookie).decode(), self._encoded_id)).fetchone()[0] == 0:
                    raise ValueError 
                
                c.execute("""SELECT msg, receiver, sender 
                             FROM messages JOIN new_cookies ON messages.cookieid = new_cookies.tcid
                             WHERE new_cookies.old_cookie=? AND new_cookies.dbfp=?""", 
                             (dandelion.util.encode_b64_bytes(time_cookie).decode(), self._encoded_id)) 

            msgs = [Message(row[0], row[1], row[2]) for row in c.fetchall()]
            
            current_tc = c.execute("""SELECT new_cookie, max(tcid) FROM new_cookies WHERE dbfp=?""", (self._encoded_id,)).fetchone()[0] 

            return (dandelion.util.decode_b64_bytes(current_tc.encode()), msgs)

    def _create_tables(self, cursor):
        """Create the tables if they don't exist"""

        cursor.execute(self._CREATE_TABLE_DATABASES)
        cursor.execute(self._CREATE_TABLE_TIME_COOKIES)
        cursor.execute(self._CREATE_TABLE_IDENTITIES)
        cursor.execute(self._CREATE_TABLE_PRIVATE_IDENTITIES)
        cursor.execute(self._CREATE_TABLE_MESSAGES)
        cursor.execute(self._CREATE_VIEW_TCDB)

        if cursor.execute("""SELECT count(*) FROM databases WHERE fingerprint=(?)""", (self._encoded_id,)).fetchone()[0] == 0:
            cursor.execute("""INSERT INTO databases (fingerprint) VALUES (?)""", (self._encoded_id,))

        if cursor.execute("""SELECT count(*) FROM time_cookies_db WHERE dbfp=(?)""", (self._encoded_id,)).fetchone()[0] == 0:
            cursor.execute("""INSERT INTO time_cookies (cookie, dbid) VALUES (?, (SELECT id FROM databases WHERE fingerprint=(?)))""", 
                           (self._encode_id(self._generate_random_tc_id()), self._encoded_id))

class InMemoryContentDB(ContentDB): 
    """A naive in memory data base for the Dandelion Message Service"""
    
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
    
    @property
    def name(self):
        """The data base name (can be None)"""
        return None
    
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
    