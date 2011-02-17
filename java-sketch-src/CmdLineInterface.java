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

public class CmdLineInterface {

    private MessageServer server_;
    private MessageDB db_;

    public CmdLineInterface(MessageServer server, MessageDB db) {
        server_ = server;
        db_ = db;
    }

    public void run() {

        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));

        while (true) {
            String input = "";

            try {
                System.out.print("$ ");
                input = reader.readLine();
            } catch (IOException e) {
                System.err.println("Error reading input in cmd line interface, stoping.");
                break;
            }

            input = input.trim();

            if (input.equals("")) {
                continue;
            }

            else if (input.equals("/q"))
                break;

            else if (input.equals("/h")) {
                printHelp();
                continue;
            }

            else if (input.equals("/port")) {
                System.out.println(server_.getPort());
                continue;
            }

            else if (input.startsWith("/version")) {
                String parts[] = input.split(" ");

                if (parts.length == 1) {
                    System.out.println("local : " + server_.getServerVersion());
                } else if (parts.length == 3) {
                    try {
                        int port = Integer.parseInt(parts[2]);
                        MessageClient client = new MessageClient(parts[1], port, db_);
                        String remoteId = client.requestVersion();
                        System.out.println(parts[1] + ":" + port + " : " + remoteId);
                    } catch (NumberFormatException e) {
                        System.err.println("Error: Bad port format");
                    } catch (MessageClient.MessageClientException e) {
                        System.err.println("Error: " + e.getMessage());
                    }
                } else {
                    System.out.println("Syntax Error...");
                }

                continue;
            }

            else if (input.equals("/list")) {
                MessageDB.Message[] msgs = db_.getMessages();
                for (MessageDB.Message m : msgs) {
                    System.out.println(m);
                }
                continue;
            }

            else if (input.startsWith("/id")) {
                String parts[] = input.split(" ");

                try {

                    if (parts.length == 1) {
                        System.out.println("local : (" + db_.computeFingerprint(server_.getServerId()) + ") : "
                                + server_.getServerId());

                    } else if (parts.length == 3) {
                        try {
                            int port = Integer.parseInt(parts[2]);
                            MessageClient client = new MessageClient(parts[1], port, db_);
                            String remoteId = client.requestId();
                            System.out.println(parts[1] + ":" + port + " : (" + db_.computeFingerprint(remoteId) + ") : "
                                    + remoteId);
                        } catch (NumberFormatException e) {
                            System.err.println("Error: Bad port format");
                        } catch (MessageClient.MessageClientException e) {
                            System.err.println("Error: " + e.getMessage());
                        }
                    } else {
                        System.out.println("Syntax Error...");
                    }
                } catch (MessageDB.MessageDBException e) {
                    System.err.println("Error: " + e.getMessage());
                }
                continue;
            }

            else if (input.startsWith("/pull")) {
                String parts[] = input.split(" ");

                if (parts.length == 3) {
                    try {
                        int port = Integer.parseInt(parts[2]);
                        MessageClient client = new MessageClient(parts[1], port, db_);
                        int noNew = client.getMessages();
                        System.out.println(parts[1] + ":" + port + " : " + noNew + " new msgs");
                    } catch (NumberFormatException e) {
                        System.err.println("Error: Bad port format");
                    } catch (MessageClient.MessageClientException e) {
                        System.err.println("Error: " + e.getMessage());
                    }
                } else {
                    System.out.println("Syntax Error...");
                }

                continue;
            }

            else if (input.startsWith("/say ")) {
                input = input.substring("/say ".length());
                try {
                    db_.addMessage(input, false);
                } catch (MessageDB.Message.MessageException e) {
                    System.err.println("Error! Could not say that");
                }
                continue;
            } else if (input.startsWith("/isay ")) {
                input = input.substring("/isay ".length());
                try {
                    db_.addMessage(input, true);
                } catch (MessageDB.Message.MessageException e) {
                    System.err.println("Error! You could not say that");
                }
                continue;
            }

            System.out.println("Syntax Error...");
            printHelp();
        }
    }

    private void printHelp() {
        System.out.println("Messaging System command line");
        System.out.println("  /h                      : This help message");
        System.out.println("  /q                      : Quit");
        System.out.println("  /port                   : Show local server port");
        System.out.println("  /list                   : Show local messages");
        System.out.println("  /say msg                : Send message");
        System.out.println("  /isay msg               : Send signed message");
        System.out.println("  /version [server port]  : Show server version");
        System.out.println("  /pull server port       : Pull messages from server");
        System.out.println("  /id [server port]       : Print id");
    }

}
