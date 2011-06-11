# -*- coding: utf-8 -*-
"""
simple GUI implementation
"""

import tkinter
from tkinter import *
import threading
import dandelion
from dandelion.util import *

class GUI(tkinter.Frame):
    
    def __init__(self, config_manager, db, id, server=None, content_synchronizer=None):
        
        print("initing GUI")
        self._server = server
        self._synchronizer = content_synchronizer
        self._config_manager = config_manager
        self._db = db
        self._identity = id
        
        # TKinter 
        master = None
        tkinter.Frame.__init__(self, master)
     

        self.master.config(
            borderwidth=0,
            background="black",
            )

        self.master.focus_set()

        
        self.processcheck = IntVar() #P
        self.processCheck = 1 #P
        
        self.master.title("Dandelion Message System") #P
        
        message_entry_area_height = message_area_height = 3
        
        row_pos = 2
    
        self.show_messages = tkinter.Button(master, 
                                            text="Get messages", bg="black", fg="green", 
                                            activebackground="black", 
                                            highlightbackground="black", 
                                            command=self._show_messages)
        self.show_messages.grid(row=row_pos, column=0, sticky=W, padx=8, pady=4)
        
        
        self.labelQuit = StringVar()
        self.labelQuit.set("x")
               
        self.QUIT = tkinter.Button(master, textvariable=self.labelQuit, 
                                   bg="black", fg="red", 
                                   activebackground="black", 
                                   highlightbackground="black", 
                                   command=self._quit)
        self.QUIT.grid(row=row_pos, column=2, sticky=E, padx=8)
          
        row_pos+=1 # new line?     
        self.labelMsgs = StringVar()
        self.labelMsgs.set("...looking for messages")   
       
        # Where messages are displayed
        self.message_area = tkinter.Text(master, bg="black", fg="green", height=12)
        self.message_area.insert(END, "Welcome to the Dandelion Message System.")
        self.message_area.config(state=DISABLED)
        self.message_area.grid(row=message_area_height, column=0, 
                          columnspan=3, 
                          rowspan=message_area_height, 
                          sticky=W, padx=8, pady=8)

        row_pos += message_area_height
        
        self.labelmsg = StringVar()
        self.labelmsg.set("Tell it like it is:")
         
        self.tilte = tkinter.Label(master, textvariable=self.labelmsg, bg="black", fg="green")  
        self.tilte.grid(row=row_pos, column=0, sticky=W, padx=8)
          
        row_pos+=1 # new line?
          
        #  Where messages are entered
        
        self.message_entry_area = tkinter.Text(master, bg="black", fg="green", height=1.5)
        #self.message_entry_area.insert(END, "hello there")
        self.message_entry_area.grid(row=row_pos, column=0, 
                                columnspan=3, 
                                rowspan=message_entry_area_height,
                                sticky=W, padx=8, pady=8)
        
        row_pos += message_entry_area_height
        
        self.sign_var = tkinter.IntVar()
        self.sign_checkbutton = tkinter.Checkbutton(master, 
                                                    text="Sign", 
                                                    bg="black", 
                                                    fg="green",  
                                                    activebackground="black", 
                                                    highlightbackground="black", 
                                                    borderwidth=0, 
                                                    variable=self.sign_var)
        
        self.sign_checkbutton.grid(row=row_pos, column=0, sticky=W, padx=8)
        
        self.send_button = tkinter.Button(master, text="Send", bg="black", fg="green", activebackground="black", highlightbackground="black", command=self._send_text)
        self.send_button.grid(row=row_pos, column=2, sticky=E, padx=8)
        
        row_pos+=1
        
        self.START_RESTART = tkinter.Button(master, text="Start", bg="black", fg="green", activebackground="black", highlightbackground="black", command=self._start_restart) # ►
        self.START_RESTART.grid(row=row_pos, column=0, sticky=W, padx=8, pady=8)

        self.STOP = tkinter.Button(master, text="Stop", bg="black", fg="green", activebackground="black", highlightbackground="black", command=self._stop)
        self.STOP.grid(row=row_pos, column=0)
        
        self.processText = StringVar()
        self.processText.set("Active...")
        self.processTextStart = tkinter.Label(master, bg="black", fg="green", textvariable=self.processText, height=4)       
        self.processTextStart.grid(row=row_pos, column=1, sticky=W, padx=8)
               
        self.HELP = tkinter.Button(master, text="?", bg="black", fg="green", activebackground="black", highlightbackground="black", command=self._help)
        self.HELP.grid(row=row_pos, column=2, sticky=E, padx=8, pady=8)
        
        self.mainloop()
     
    
        
    
    """
    def create_widgets(self):
        self.QUIT = tkinter.Button(self, 
                                   text="Quit", 
                                   command=self._quit
                                   )
        self.QUIT.pack({"side" : "left"})
        
    
        self.START = tkinter.Button(self,
                                    text="Start",
                                    command=self._start
                                    )
        self.START.pack({"side" : "left"})
 
        ###        ###        ###        ###
        self.STOP = tkinter.Button(self,
                                   text="Stop",
                                   command=self._stop
                            )
        self.STOP.pack({"side" : "left"})
    
    
        self.SAY = tkinter.Button(self,
                                  text="Say",
                                  command=self._say)
        self.SAY.pack({"side" : "left"})
        
    """    
    
    def _start_restart(self):
        print("starting things")
        self.labelStarted = ("Active...")
        self.processText.set(self.labelStarted)
        self.processCheck = 1
        self._synchronizer.start()
        
    def _stop(self):
        print("stopping things")
        self.labelStop = ("Peer Down..")
        self.processText.set(self.labelStop)
        self.processCheck = 0
        self._synchronizer.stop()
        
    def _quit(self):
        print("Quitting program")
        self.labelQuit = ("Quitting..")
        self.processText.set(self.labelQuit)
        self._stop()
        self.quit()
    
    def _send_text(self):
        msg = self.message_entry_area.get(1.0, END)
        print("checked: %s send_text: %s " % (self.sign_var.get(), msg))
        
        if self.processCheck == 0:
            self.labelNotRunning = ("To message pls press Start.")
            self.processText.set(self.labelNotRunning)
            print("To message the client must be running")
        else:    
            self._say(msg)
            self.message_entry_area.delete(1.0, END)

    #def _say(self, msg, sign=None, receiver_name=None):
    def _say(self, msg, sign=None, receiver_name=None):
        print("_say %s" % (msg))
        if receiver_name:
            receiver_ = dandelion.identity.generate() # Should look up id of receiver
        else:
            receiver_ = None
        
        if sign and receiver_:
            m = dandelion.message.create(msg, sender=self._identity, receiver=receiver_)
            self._db.add_messages([m])
        elif sign:
            m = dandelion.message.create(msg, sender=self._identity)
            self._db.add_messages([m])
        elif receiver_:
            m = dandelion.message.create(msg, receiver=receiver_)
            self._db.add_messages([m])
        else:
            m = dandelion.message.create(msg)
            self._db.add_messages([m])
            
    def _show_messages(self):
        # om du först definierar en stringvar
        self.all_msgs = StringVar()
        # sedan hämtar vi meddelandena från db
        (current_tc, self.all_msgs) = self._db.get_messages()
        self.message_area.config(state=NORMAL) 
        self.message_area.delete(1.0,END)  
        for m in self.all_msgs:   
                self.all_msgs = (' : '.join([encode_b64_bytes(m.id).decode(), 
                              m.text if not m.has_receiver else encode_b64_bytes(m.text).decode(), 
                              'N/A' if not m.has_receiver else encode_b64_bytes(m.receiver).decode(), 
                              'N/A' if not m.has_sender else encode_b64_bytes(m.sender).decode()]))           
                self.message_area.insert(END, self.all_msgs)
        
        self.message_area.config(state=DISABLED)
                
    def _help(self):
        pass
    
    def show_identities(self):
        _, identities = self._db.get_identities()
        print(' --- IDENTITIES BEGIN --- ')
        
        for id in identities:
            print(' : '.join([encode_b64_bytes(id.fingerprint).decode()]))

        print(' --- IDENTITIES END --- ')

    
    """
    def synchronizer_ctrl(self, op=""):
        self._service_ctrl(self._synchronizer, op)
        
    def _service_ctrl(self, service, op):
        if op == OP_START:
            service.start()
        elif op == OP_STOP:
            service.stop()
        elif op == OP_RESTART:
            service.restart()
        elif op == OP_STATUS:
            print(service.status)
        else:
            pass # Error
    """
