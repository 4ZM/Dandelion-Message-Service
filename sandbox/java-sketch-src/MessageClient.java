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

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.ArrayList;

public class MessageClient {
    private String server_;
    private int port_;
    
    private MessageDB db_;
    
    MessageClient(String server, int port, MessageDB db) {
         server_ = server;
         port_ = port;
         db_ = db;
    }
    
    String requestVersion() throws MessageClientException {
        return request("GET VER");
    }

    String requestId() throws MessageClientException {
        return request("GET ID");
    }
    
    int getMessages() throws MessageClientException {
        String msgList = request("GET LIST");
        String[] msgIds = msgList.split(";");
        ArrayList<String> newMsgIds = new ArrayList<String>();
        int newCnt = 0;
        for (String s : msgIds) {
            if (!db_.contains(s)) {
                newMsgIds.add(s);
                newCnt++;
            }
        }

        // Nothing new
        if (newCnt == 0)
            return newCnt;
        
        StringBuilder sb = new StringBuilder("GET MSGS");
    
        // We don't need all messages
        if (newCnt < msgIds.length) {
            sb.append(" ");
            sb.append(newMsgIds.get(0));
            for (int i = 1; i < newMsgIds.size(); ++i)
                sb.append(";").append(newMsgIds.get(i));
        }
        
        String newMsgs = request(sb.toString());
        String[] msgs = newMsgs.split(";");
        for (String m : msgs) {
            try {
                db_.addMessage(MessageDB.Message.parse(m));
            } catch (MessageDB.Message.MessageException e) {
                System.err.println("Unparsable");
            }
        }
        
        return newCnt;        
    }
    
    private String request(String q) throws MessageClientException {
        try {
            Socket socket = new Socket(server_, port_);

            PrintWriter out = null;
            BufferedReader in = null;

            out = new PrintWriter(socket.getOutputStream(), true);
            in = new BufferedReader(new InputStreamReader(socket.getInputStream()));

            out.println(q);
            return in.readLine(); // Don't wait forever

        } catch (UnknownHostException e) {
            throw new MessageClientException("Could not connect to server " + server_ + " on port " + port_);
        } catch (IOException e) {
            throw new MessageClientException("Error communicating with server: " + server_);
        }
    }
    
    public static class MessageClientException extends Exception {
        public MessageClientException(String msg) { super(msg); }
        private static final long serialVersionUID = 1L;
    }
}
