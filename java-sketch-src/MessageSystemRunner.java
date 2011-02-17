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

public class MessageSystemRunner {

    public static void main(String[] args) {
        System.out.println("Starting MessageSystemRunner");

        int serverPort = 1337;
        
        if (args.length == 1) {
            serverPort = Integer.parseInt(args[0]);
        }
        
        try {
            MessageDB db = new MessageDB();

            MessageServer server = new MessageServer(serverPort, db);
            server.start();

            CmdLineInterface cmdIf = new CmdLineInterface(server, db);
            cmdIf.run(); // Blocking call

            server.stopServer();
            server.join();
            
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        System.out.println("Bye");
    }

}
