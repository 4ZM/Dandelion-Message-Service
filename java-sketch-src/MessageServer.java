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
import java.net.BindException;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketTimeoutException;

public class MessageServer extends Thread {

    private int port_; // Port to listen to

    private MessageDB db_;

    private boolean running_;
    private ServerSocket serverSocket_;

    public MessageServer(int port, MessageDB db) throws MessageServerException {
        super("ServerThread");
        port_ = port;
        db_ = db;
    }

    public void run() {
        running_ = true;

        try {
            serverSocket_ = new ServerSocket(port_);
            serverSocket_.setSoTimeout(500);

            while (running_) {
                try {
                    new ServerSessionThread(serverSocket_.accept(), db_).start();
                } catch (SocketTimeoutException e) { /*
                                                      * Normal and expected.
                                                      * Check: should we
                                                      * continue running?
                                                      */
                }
            }

            serverSocket_.close(); // Will close before all threads done, sync.
        } catch (BindException e) {
            System.err
                    .println("Server error, can't bind to port, perhaps it is bussy? Note: only priviliged users can typically bind to ports 1-1024");
        } catch (IOException e) {
            System.err.println("Server error. Shutting down.");
        }

        running_ = false;
    }

    public void stopServer() {
        running_ = false;
    }

    public String getServerId() {
        return db_.getId();
    }

    public String getServerVersion() {
        return "0.1";
    }

    public int getPort() {
        return port_;
    }

    private class ServerSessionThread extends Thread {
        private Socket socket_ = null;
        private MessageDB db_;

        public ServerSessionThread(Socket socket, MessageDB db) {
            super("ServerSessionThread");
            socket_ = socket;
            db_ = db;
        }

        public void run() {
            try {
                PrintWriter out = new PrintWriter(socket_.getOutputStream(), true);
                BufferedReader in = new BufferedReader(new InputStreamReader(socket_.getInputStream()));

                String inputLine = in.readLine();

                if (inputLine.equals("GET VER"))
                    out.println(getServerVersion());
                else if (inputLine.equals("GET ID"))
                    out.println(getServerId());
                else if (inputLine.startsWith("GET LIST"))
                    sendList(out);
                else if (inputLine.startsWith("GET MSGS"))
                    sendMsg(out);
                else
                    out.println("SYNTAX ERROR");

                out.close();
                in.close();
                socket_.close();

            } catch (IOException e) {
                System.err.println("Error in message server session thread. Session thread bails out.");
            }
        }

        private void sendList(PrintWriter out) {
            MessageDB.Message[] msgs = db_.getMessages();
            out.print(msgs[0].getId());
            for (int i = 1; i < msgs.length; ++i)
                out.print(";" + msgs[i].getId());
        }
    }

    private void sendMsg(PrintWriter out) {
        MessageDB.Message[] msgs = db_.getMessages();
        out.print(msgs[0].toString());
        for (int i = 1; i < msgs.length; ++i) {
            out.print(";" + msgs[i].toString());
        }
    }

    public static class MessageServerException extends Exception {
        public MessageServerException(String msg) {
            super(msg);
        }

        private static final long serialVersionUID = 1L;
    }

}
