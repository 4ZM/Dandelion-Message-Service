
# DANDELION MESSAGE SERVICE #
                    
Dandelion is robust, distributed message passing designed to leverage the power of self organizing networks. 

The message passing protocol can be implemented on any transport layer but we will start by implementing it utilizing Zeroconf service discovery and ad hoc wifi networks with link local addresses. Dandelion does not rely on any existing infrastructure like the Internet or mobile phone services - it is truly peer to peer. 

By running Dandelion you get access to a distributed stream of messages posted by other users. 

There are three types of messages:

1. The completely anonymous public announcement. This type does not have a sender or receiver and is readable by all. 
2. Signed messages with a specified sender. This type of communication gives your message credibility and is similar to a twitter feed. You can also establish secure trust relations with other users that allows you to make sure that the message is realy from who it says. 
3. Messages with a specific receiver. If you know the identity of a node, you can send a message specifically to that node. This type of message is automatically encrypted. This type of message can also be signed to specify a sender. 
