import unittest
import binascii
import message
import database

class DatabaseTest(unittest.TestCase):
    
    def test_id(self):
        '''Test data base id'''
        
        db = database.DataBase()
        id = db.GetId()
        self.assertNotEqual(id, None)
        self.assertEqual(len(id), database.DataBase.ID_LENGTH_BYTES)
        
        # Another data base gets another id
        self.assertNotEqual(id, database.DataBase().GetId())
        
    def test_single_message_interface(self):
        '''Test functions relating to storing and recovering single messages'''
        db = database.DataBase()
        
        firstMsg = message.Message('A Single Message')

        # Try to add junk
        self.assertRaises(ValueError, db.AddMessage, None)
        self.assertRaises(ValueError, db.AddMessage, 23)
        self.assertRaises(ValueError, db.AddMessage, [None])

        # Add a single message        
        db.AddMessage(firstMsg)
        self.assertNotEqual(db.MessageCount, None)
        self.assertEqual(db.MessageCount(), 1)
        self.assertTrue(db.ContainsMessage(firstMsg))

        # And for another message? 
        secondMsg = message.Message("A new message")
        self.assertFalse(db.ContainsMessage(secondMsg))
        
        # Adding a second message
        db.AddMessage(secondMsg)
        self.assertEqual(db.MessageCount(), 2)
        self.assertTrue(db.ContainsMessage(firstMsg))
        self.assertTrue(db.ContainsMessage(secondMsg))

        # Nothing special about the particular instances (it's the id that counts)
        self.assertTrue(db.ContainsMessage(message.Message("A new message")))

        # Remove a single message
        db.RemoveMessage(firstMsg)
        self.assertEqual(db.MessageCount(), 1)
        self.assertFalse(db.ContainsMessage(firstMsg))

        # Remove same single message
        db.RemoveMessage(firstMsg)
        self.assertEqual(db.MessageCount(), 1)
        self.assertFalse(db.ContainsMessage(firstMsg))
        
        # Remove all messages
        db.RemoveMessage()
        self.assertEqual(db.MessageCount(), 0)
        self.assertFalse(db.ContainsMessage(firstMsg))
        self.assertFalse(db.ContainsMessage(secondMsg))
        
    def test_list_message_interface(self):
        '''Test functions relating to storing and recovering single messages'''
        db = database.DataBase()
        
        firstMsgList = [message.Message('A'), message.Message('B')]

        # Add a message list        
        db.AddMessage(firstMsgList)
        self.assertNotEqual(db.MessageCount, None)
        self.assertEqual(db.MessageCount(), len(firstMsgList))
        self.assertEqual(db.ContainsMessage(firstMsgList), [True, True])

        # And for another message list? 
        secondMsgList = [message.Message('C'), message.Message('A')]
        self.assertEqual(db.ContainsMessage(secondMsgList), [False, True])
        
        # Adding the second message list
        db.AddMessage(secondMsgList)
        self.assertEqual(db.MessageCount(), 3)
        self.assertEqual(db.ContainsMessage(firstMsgList), [True, True])
        self.assertEqual(db.ContainsMessage(secondMsgList), [True, True])

        # Remove a list
        db.RemoveMessage(firstMsgList)
        self.assertEqual(db.MessageCount(), 1)
        self.assertEqual(db.ContainsMessage(firstMsgList), [False, False])
        self.assertEqual(db.ContainsMessage(secondMsgList), [True, False])

        # Remove same message list 
        db.RemoveMessage(firstMsgList)
        self.assertEqual(db.MessageCount(), 1)
        self.assertEqual(db.ContainsMessage(firstMsgList), [False, False])
        self.assertEqual(db.ContainsMessage(secondMsgList), [True, False])
        
        # Remove all messages
        db.RemoveMessage()
        self.assertEqual(db.MessageCount(), 0)
        self.assertEqual(db.ContainsMessage(firstMsgList), [False, False])
        self.assertEqual(db.ContainsMessage(secondMsgList), [False, False])

    def test_uid_storage(self):
        '''Test function relating to storing and recovering user identities'''
        
    def test_time_cookies(self):
        '''Test the time cookies functionality''' 
        db = database.DataBase()

        # Adding a message        
        firstMsg = message.Message('A Single Message')
        firstCookie = db.AddMessage(firstMsg)
        self.assertNotEqual(firstCookie, None)

        # Same message again
        self.assertEqual(firstCookie, db.AddMessage(firstMsg))

        # New message, new cookie
        secondMsg = message.Message('Another Single Message')
        secondCookie = db.AddMessage(secondMsg)
        self.assertNotEqual(secondCookie, None)
        self.assertNotEqual(secondCookie, firstCookie)

        # Since first should only be second
        someMessages = db.MessagesSince(firstCookie)
        self.assertNotEqual(someMessages, None)
        self.assertEqual(len(someMessages), 1)
        self.assertEqual(someMessages[0], secondMsg)
        
        # Nothing new since last message was added
        lastMessages = db.MessagesSince(secondCookie)
        self.assertNotEqual(lastMessages, None)
        self.assertEqual(len(lastMessages), 0)

if __name__ == '__main__':
    unittest.main()