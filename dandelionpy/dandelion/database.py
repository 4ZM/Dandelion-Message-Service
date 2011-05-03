"""
Copyright (c) 2011 Anders Sundman <anders@4zm.org>

This file is part of Dandelion Messaging System.

Dandelion is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Dandelion is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Dandelion.  If not, see <http://www.gnu.org/licenses/>.
"""
from dandelion.identity import Identity, DSA_key, RSA_key
from dandelion.message import Message
from dandelion.util import encode_b64_bytes, decode_b64_bytes, encode_b64_int, \
    decode_b64_int
import random
import sqlite3


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
    
    _DBID_LENGTH_BYTES = 12 
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

    def get_messages(self, msgids=None, time_cookie=None):
        """Get a list of all messages with specified message id.
    
        If the parameter is None, all messages are returned.
    
        If a time cookie is specified, all messages in the database after
        the time specified by the time cookie will be returned.  
        """

    def add_identities(self, identities):
        """Add a a list of identities to the data base.
        
        Will add all identities, not already in the data base to the data base and return a 
        time cookie (bytes) that represents the point in time after the identities have been added.
        If no identities were added, it just returns the current time cookie. 
        """

    def remove_identities(self, identities=None):
        """Removes identities from the data base.
        
        The specified list of identities will be removed from the data base. 
        If the identities parameter is omitted, all identities in the data base will be removed.
        """
        
    @property
    def identity_count(self):
        """Returns the number of identities currently in the data base (int)"""

    def contains_identity(self, fingerprint):
        """Returns true if the database contains the identity fingerprint"""

    def get_identities(self, fingerprints=None, time_cookie=None):
        """Get a list of all identities with specified fingerprints.

        If the parameter is None, all identities are returned.
    
        If a time cookie is specified, all identities in the database after
        the time specified by the time cookie will be returned.  
        """

    def get_last_time_cookie(self, dbfp=None):
        """Get the latest time cookie known in the data base for the remote 
        data base with fingerprint dbfp. 
        
        If there is no record of the remote data base, return None.
        
        If dbfp is None, get the latest time cookie for the own database.
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
        return encode_b64_bytes(id).decode()

    @classmethod
    def _decode_id(self, id):
        """Text to binary decoding of id's"""
        return decode_b64_bytes(id.encode())

class SQLiteContentDB(ContentDB):
    """A content database with a sqlite backend."""
     
    _CREATE_TABLE_DATABASES = """CREATE TABLE IF NOT EXISTS databases
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        fingerprint TEXT UNIQUE,
        alias TEXT)"""

    _CREATE_TABLE_TIME_COOKIES = """CREATE TABLE IF NOT EXISTS time_cookies
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        cookie TEXT NOT NULL)"""

    _CREATE_TABLE_REMOTE_TIME_COOKIES = """CREATE TABLE IF NOT EXISTS remote_time_cookies
        (cookie TEXT,
        dbid INTEGER REFERENCES databases (id), PRIMARY KEY (cookie, dbid))"""

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

    _QUERY_GET_LAST_TIME_COOKIE = """SELECT max(id), cookie FROM time_cookies"""
    _QUERY_REMOTE_GET_LAST_TIME_COOKIE = """SELECT cookie FROM remote_time_cookies WHERE dbfp=?"""
    _QUERY_GET_MESSAGE_COUNT = """SELECT count(*) FROM messages"""
    _QUERY_GET_IDENTITY_COUNT = """SELECT count(*) FROM identities"""

    
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
                             (self._encoded_id,)).fetchone()[0] != 1:
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
    
    def get_last_time_cookie(self, dbfp=None):
        """Get the latest time cookie known in the data base for the remote 
        data base with fingerprint dbfp. 
        
        If there is no record of the remote data base, return None.
        
        If dbfp is None, get the latest time cookie for the own database.
        """
        
        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()
            return self._get_last_time_cookie(c, dbfp)

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

            tcid = self._insert_new_tc(c)
            
            pre_msgs = self._get_message_count(c) # Count before insert
            
            try:
                for m in msgs:
                    # Add sender/receiver
                    c.execute("""INSERT OR IGNORE INTO messages (msgid, msg, receiver, sender, signature, cookieid) VALUES (?,?,?,?,?,?)""", 
                              (self._encode_id(m.id), 
                               m.text, 
                               None if not m.has_receiver else self._encode_id(m.receiver), 
                               None if not m.has_sender else self._encode_id(m.sender),
                               None if not m.has_sender else self._encode_id(m.signature),
                               tcid))
            except AttributeError: # Typically caused by types other than Message in list
                raise TypeError
            
            post_msgs = self._get_message_count(c) # Count after insert
            
            """No new messages? Rollback tc insert and use old value"""
            if (post_msgs - pre_msgs) == 0: 
                conn.rollback() 
            
            return self._get_last_time_cookie(c)

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
                              [(self._encode_id(m.id),) for m in msgs])

    @property
    def message_count(self):
        """Returns the number of messages currently in the data base (int)"""
        
        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()
            return self._get_message_count(c)

    def contains_message(self, msgid):
        """Returns true if the database contains the msgid"""
        
        if not isinstance(msgid, bytes):
            raise TypeError

        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()
            c.execute('SELECT msgid FROM messages WHERE msgid=?', (self._encode_id(msgid),)) 
            return c.fetchone() is not None

    def get_messages(self, msgids=None, time_cookie=None):
        """Get a list of all msg_rows with specified message id.
        
        If a time cookie is specified, all messages in the database from (and 
        including) the time specified by the time cookie will be returned.
        """

        if msgids is not None and not hasattr(msgids, '__iter__'):
            raise TypeError

        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()
            
            if time_cookie is not None:
                if not isinstance(time_cookie, bytes):
                    raise TypeError
                if len(time_cookie) == 0:
                    raise ValueError

                """Assert that time_cookie is a valid cookie"""
                if c.execute("SELECT count(*) FROM time_cookies WHERE cookie = ?", 
                          (self._encode_id(time_cookie),)).fetchone()[0] == 0:
                    raise ValueError 
                
                c.execute("""SELECT msg, receiver, sender, signature 
                             FROM messages JOIN time_cookies ON messages.cookieid = time_cookies.id
                             WHERE time_cookies.id > (SELECT id FROM time_cookies WHERE cookie = ?)""", 
                             (self._encode_id(time_cookie),)) 
            else: 
                c.execute("""SELECT msg, receiver, sender, signature FROM messages""")

            msgs = c.fetchall()
            current_tc = self._get_last_time_cookie(c)
            msgs = [Message(m[0], 
                    None if m[1] is None else self._decode_id(m[1]), 
                    None if m[2] is None else self._decode_id(m[2]), 
                    None if m[3] is None else self._decode_id(m[3])) for m in msgs 
                    if m is not None]

            if msgids is not None:
                msgs = [m for m in msgs if m.id in msgids]
            
            return (current_tc, msgs)

    def add_identities(self, identities):
        """Add a a list of identities to the data base.
        
        Will add all identities, not already in the data base to the data base and return a 
        time cookie (bytes) that represents the point in time after the identities have been added.
        If no identities were added, it just returns the current time cookie. 
        """

        if identities is None:
            raise ValueError
        
        if not hasattr(identities, '__iter__'):
            raise TypeError
        
        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()

            tcid = self._insert_new_tc(c)
            
            pre_msgs = self._get_identity_count(c) # Count before insert
            
            try:
                for id in identities:
                    c.execute("""INSERT OR IGNORE INTO identities (fingerprint, dsa_y, dsa_g, dsa_p, dsa_q, rsa_n, rsa_e, cookieid) VALUES (?,?,?,?,?,?,?,?)""", 
                              (self._encode_id(id.fingerprint), 
                               encode_b64_int(id.dsa_key.y),
                               encode_b64_int(id.dsa_key.g),
                               encode_b64_int(id.dsa_key.p),
                               encode_b64_int(id.dsa_key.q),
                               encode_b64_int(id.rsa_key.n),
                               encode_b64_int(id.rsa_key.e),
                               tcid))
            except AttributeError: # Typically caused by types other than Identity in list
                raise TypeError
            
            post_msgs = self._get_identity_count(c) # Count after insert
            
            """No new identities? Rollback tc insert and use old value"""
            if (post_msgs - pre_msgs) == 0: 
                conn.rollback() 
                
            return self._get_last_time_cookie(c)
        
    def remove_identities(self, identities=None):
        """Removes identities from the data base.
        
        The specified list of identities will be removed from the data base. 
        If the identities parameter is omitted, all identities in the data base will be removed.
        """
        
        if identities is not None and not hasattr(identities,'__iter__'):
            raise TypeError

        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()
            
            if identities is None:
                c.execute("""DELETE FROM identities""")
            else:
                c.executemany("""DELETE FROM identities WHERE fingerprint = ?""", 
                              [(self._encode_id(id.fingerprint),) for id in identities])

    @property
    def identity_count(self):
        """Returns the number of identities currently in the data base (int)"""
        
        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()
            return self._get_identity_count(c)

    def contains_identity(self, fingerprint):
        """Returns true if the database contains the identity fingerprint"""
        
        if not isinstance(fingerprint, bytes):
            raise TypeError

        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()
            c.execute('SELECT fingerprint FROM identities WHERE fingerprint = ?', 
                      (self._encode_id(fingerprint),)) 
            if c.fetchone() is None:
                return False
            else:
                return True
        

    def get_identities(self, fingerprints=None, time_cookie=None):
        """Get a list of all identities with specified fingerprints.
        
        If the parameter is None, all identities are returned.
        
        If a time cookie is specified, all identities in the database after
        the time specified by the time cookie will be returned.  
        """

        if fingerprints is not None and not hasattr(fingerprints, '__iter__'):
            raise TypeError

        with sqlite3.connect(self._db_file) as conn:
            c = conn.cursor()

            if time_cookie is not None:
                if not isinstance(time_cookie, bytes):
                    raise TypeError
                if len(time_cookie) == 0:
                    raise ValueError

                """Assert that time_cookie is a valid cookie"""
                if c.execute("SELECT count(*) FROM time_cookies WHERE cookie = ?", 
                          (self._encode_id(time_cookie),)).fetchone()[0] == 0:
                    raise ValueError 

                c.execute("""SELECT fingerprint, dsa_y, dsa_g, dsa_p, dsa_q, rsa_n, rsa_e 
                             FROM identities JOIN time_cookies ON identities.cookieid = time_cookies.id
                             WHERE time_cookies.id > (SELECT id FROM time_cookies WHERE cookie=?)""", 
                             (self._encode_id(time_cookie),)) 
            else:
                c.execute("""SELECT fingerprint, dsa_y, dsa_g, dsa_p, dsa_q, rsa_n, rsa_e FROM identities""")
            
            id_rows = c.fetchall()
            current_tc = self._get_last_time_cookie(c)

            ids = [Identity(DSA_key(decode_b64_int(id[1]), 
                                                  decode_b64_int(id[2]), 
                                                  decode_b64_int(id[3]), 
                                                  decode_b64_int(id[4])), 
                                          RSA_key(decode_b64_int(id[5]), 
                                                  decode_b64_int(id[6]))) for id in id_rows 
                                                  if id is not None]
            if fingerprints is not None:
                ids = [id for id in ids if id.fingerprint in fingerprints]
            
            return (current_tc, ids)
            

            
    def _create_tables(self, cursor):
        """Create the tables if they don't exist"""

        cursor.execute(self._CREATE_TABLE_DATABASES)
        cursor.execute(self._CREATE_TABLE_TIME_COOKIES)
        cursor.execute(self._CREATE_TABLE_REMOTE_TIME_COOKIES)
        cursor.execute(self._CREATE_TABLE_IDENTITIES)
        cursor.execute(self._CREATE_TABLE_PRIVATE_IDENTITIES)
        cursor.execute(self._CREATE_TABLE_MESSAGES)

        if cursor.execute("""SELECT count(*) FROM databases WHERE fingerprint=(?)""", (self._encoded_id,)).fetchone()[0] == 0:
            cursor.execute("""INSERT INTO databases (fingerprint) VALUES (?)""", (self._encoded_id,))

        if cursor.execute("""SELECT count(*) FROM time_cookies""").fetchone()[0] == 0:
            cursor.execute("""INSERT INTO time_cookies (cookie) VALUES (?)""", 
                           (self._encode_id(self._generate_random_tc_id()),))

    def _insert_new_tc(self, c):
        """Create a new time cookie and insert it in the database. Return the time cookie."""
        
        """Create a new, unused id"""
        while True:
            tc = self._encode_id(self._generate_random_tc_id())
            if c.execute("""SELECT count(*) FROM time_cookies WHERE cookie=?""", (tc,)).fetchone()[0] == 0:
                break
            
        """Insert the new time cookie"""
        tcid = c.execute("""INSERT INTO time_cookies (cookie) VALUES (?)""", (tc,)).lastrowid

        return tcid

    def _get_last_time_cookie(self, dbcursor, dbfp=None):
        """Get the last known time cookie (bytes) for the specified database (bytes). If no data base is specified, 
        the current time cookie for this data base is returned. If the data base is unknown, 
        None is returned.
        """

        if dbfp is None:
            row = dbcursor.execute(self._QUERY_GET_LAST_TIME_COOKIE).fetchone()
            return self._decode_id(row[1])
        else:
            row = dbcursor.execute("SELECT cookie FROM remote_time_cookies JOIN databases ON remote_time_cookies.dbid = databases.id WHERE databases.fingerprint = ?",(self._encode_id(dbfp),)).fetchone()
            return None if row is None else self._decode_id(row[0])

    def _get_message_count(self, dbcursor):
        """Return the total number of messages in the data base"""
        return dbcursor.execute(self._QUERY_GET_MESSAGE_COUNT).fetchone()[0]

    def _get_identity_count(self, dbcursor):
        """Return the total number of identities (public and private) in the data base"""
        return dbcursor.execute(self._QUERY_GET_IDENTITY_COUNT).fetchone()[0]
