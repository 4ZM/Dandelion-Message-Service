// Copyright (c) 2011 Anders Sundman <anders@4zm.org>
//
// This file is part of the Riot Control Messaging System (RCMS).
//
// RCMS is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version. 
//
// The RCMS is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with the RCMS.  If not, see <http://www.gnu.org/licenses/>.

import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.security.Signature;
import java.util.ArrayList;

public class MessageDB {
    private SecureRandom rndGen_;
    private KeyPair keyPair_; // DSA keys - public key is server ID
    private ArrayList<Message> msgList_ = new ArrayList<Message>();

    public MessageDB() throws MessageDBException {
        try {
            rndGen_ = SecureRandom.getInstance("SHA1PRNG");
            KeyPairGenerator keyGen = KeyPairGenerator.getInstance("DSA");
            keyGen.initialize(1024, rndGen_);
            keyPair_ = keyGen.generateKeyPair();
        } catch (NoSuchAlgorithmException e) {
            throw new MessageDB.MessageDBException("Could not create keys");
        }
    }

    public void addMessage(Message msg) throws Message.MessageException {
        if (contains(msg.getId()))
            throw new Message.MessageException("Could not add message to DB");

        msgList_.add(msg);
    }
        

    public void addMessage(String text, boolean sign) throws Message.MessageException {
        Message msg = new Message(text);
        
        if (sign) {
            try {
                Signature dsa = Signature.getInstance("SHA1withDSA");
                dsa.initSign(keyPair_.getPrivate());
                dsa.update(text.getBytes("UTF-8"));
                dsa.update(getId().getBytes("UTF-8"));
                msg.sign(getPubKey(), dsa.sign());
            } catch (Exception e) {
                throw new Message.MessageException("Error creating signature");
            }
        }
        
        addMessage(msg);        
    }

    public boolean contains(String s) {
        for (Message m : msgList_) {
            if (m.getId().equals(s))
                return true;
        }
        return false;
    }

    public Message[] getMessages() {
        return getMessages(null);
    }

    public Message getMessage(String id) {
        for (Message m : msgList_) {
            if (m.getId().equals(id))
                return m;
        }
        return null;
    }

    
    public Message[] getMessages(String[] msgIds) {
        if (msgIds == null) {
            Message[] msgs = new Message[msgList_.size()];
            return msgList_.toArray(msgs);
        }
        
        ArrayList<Message> msglist = new ArrayList<Message>();
        for (String msgId : msgIds) {
            Message m = getMessage(msgId);
            if (m != null)
                msglist.add(m);
        }
        Message[] msgs = new Message[msglist.size()];
        return msglist.toArray(msgs);
    }

    public String getId() {
        return HexFormater.toHex(keyPair_.getPublic().getEncoded());
    }

    public byte[] getPubKey() {
        return keyPair_.getPublic().getEncoded();
    }

    public String computeFingerprint(String id) throws MessageDBException {
        byte[] bytes = null;

        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            digest.reset();
            bytes = digest.digest(id.getBytes("UTF-8"));
        } catch (Exception e) {
            throw new MessageDBException("Could not create fingerprint");
        }

        return HexFormater.toHex(bytes, " ").substring(0, 8 * 3 - 1); // first 8 of
                                                                  // 64 bytes
    }

    public static class MessageDBException extends Exception {
        public MessageDBException(String msg) {
            super(msg);
        }

        private static final long serialVersionUID = 1L;
    }

    public static class Message {
        public final int MAX_LENGTH = 160;
        private byte[] hash_;
        private String msgText_;

        private byte[] senderId_;
        private byte[] senderSignature_;

        // + FROM
        // + SIGN

        public Message(String msg) throws MessageException {
            if (msg.length() > MAX_LENGTH)
                throw new MessageException("Message text too long (max: " + MAX_LENGTH + ")");

            msgText_ = msg;
            msgText_ = String.format("%-" + MAX_LENGTH + "s", msgText_);

            hash_ = computeHash();
        }

        public Message(String msg, byte[] sender, byte[] signature) throws MessageException {
            if (msg.length() > MAX_LENGTH)
                throw new MessageException("Message text too long (max: " + MAX_LENGTH + ")");

            msgText_ = msg;
            msgText_ = String.format("%-" + MAX_LENGTH + "s", msgText_);
            
            senderId_ = sender;
            senderSignature_ = signature;

            hash_ = computeHash();
        }

        public void sign(byte[] sender, byte[] signature) throws MessageException {
            senderId_ = sender;
            senderSignature_ = signature;
            hash_ = computeHash();
        }

        public String getText() {
            return msgText_;
        }

        public String getId() {
            return HexFormater.toHex(hash_);
        }

        public boolean hasSender() {
            return senderId_ != null && senderSignature_ != null;
        }

        private byte[] computeHash() throws MessageException {
            byte[] bytes = null;

            try {
                MessageDigest digest = MessageDigest.getInstance("SHA-256");
                digest.reset();
                digest.update(msgText_.getBytes("UTF-8"));
                if (hasSender()) {
                    digest.update(HexFormater.toHex(senderId_).getBytes("UTF-8"));
                    digest.update(HexFormater.toHex(senderSignature_).getBytes("UTF-8"));
                }
                bytes = digest.digest();
            } catch (Exception e) {
                throw new MessageException("Message creation failed, could not create hash");
            }

            return bytes;
        }

        public String toString() {
            StringBuilder sb = new StringBuilder();
            sb.append(HexFormater.toHex(hash_));
            sb.append("|");
            sb.append(msgText_);
            if (hasSender()) {
                sb.append("|");
                sb.append(HexFormater.toHex(senderId_));
                sb.append("|");
                sb.append(HexFormater.toHex(senderSignature_));
            }

            return sb.toString();
        }

        public static Message parse(String str) throws MessageException {
            String[] parts = str.split("\\|");
            if (parts.length == 2) {
                return new Message(parts[1]);
            }
            else if (parts.length == 4) {
                return new Message(parts[1], HexFormater.fromHex(parts[2]), HexFormater.fromHex(parts[3]));  
            }
            else {
                throw new MessageException("Invalid msg format");
            }
        }
        
        public int equals(Message other) {
            for (int i = 0; i < hash_.length; ++i) {
                if (other.hash_[i] != hash_[i])
                    return -1;
            }
            return 0;
        }

        public static class MessageException extends Exception {
            public MessageException(String msg) {
                super(msg);
            }

            private static final long serialVersionUID = 1L;
        }

    }

}