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
        
        row_pos = 2
        message_entry_area_height = message_area_height = 3
        
        # Where messages are displayed
        self.message_area = tkinter.Text(master, height=8)
        #self.message_area.insert(END, 'pre pre')
        self.message_area.config(state=DISABLED)
        self.message_area.grid(row=message_area_height, column=0, 
                          columnspan=2, 
                          rowspan=message_area_height, 
                          sticky=W, padx=8, pady=8)

        row_pos += message_area_height

        #  Where messages are entered
        
        self.message_entry_area = tkinter.Text(master, height=4)
        #self.message_entry_area.insert(END, "hello there")
        self.message_entry_area.grid(row=row_pos, column=0, 
                                columnspan=2, 
                                rowspan=message_entry_area_height,
                                sticky=W, padx=8, pady=8)
        
        row_pos += message_entry_area_height
        
        self.sign_var = tkinter.IntVar()
        self.sign_checkbutton = tkinter.Checkbutton(master, text="Sign", variable=self.sign_var)
        self.sign_checkbutton.grid(row=row_pos, column=1, sticky=W, padx=8, pady=8)
        
        self.send_button = tkinter.Button(master, text="Send", command=self._send_text)
        self.send_button.grid(row=row_pos, column=1, sticky=E)
        
        row_pos+=1
        
        
        self.START_RESTART = tkinter.Button(master, text="Start", command=self._start_restart)
        self.START_RESTART.grid(row=row_pos, column=0, sticky=W)
        
        self.STOP = tkinter.Button(master, text="Stop", command=self._stop)
        self.STOP.grid(row=row_pos, column=0, sticky=E)
        
        self.QUIT = tkinter.Button(master, text="Quit", command=self._quit)
        self.QUIT.grid(row=row_pos, column=1, sticky=W)
        
        row_pos+=1
        self.server_status = tkinter.Label(master, text="Running")
        self.server_status.grid(row=row_pos, column=0, sticky=W)
        
        self.show_messages = tkinter.Button(master, text="Show messages", command=self._show_messages)
        self.show_messages.grid(row=row_pos, column=1, sticky=W)
        
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
        self._synchronizer.start()
        
    def _stop(self):
        print("stopping things")
        self._synchronizer.stop()
        
    def _quit(self):
        print("Quitting program")
        self._stop()
        self.quit()
    
    def _send_text(self):
        msg = self.message_entry_area.get(1.0, END)
        print("checked: %s send_text: %s " % (self.sign_var.get(), msg))
        self._say(msg)

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
        msgs = self._db.get_messages()
        print(' --- MESSAGES BEGIN --- ')
        
        for m in msgs:
            print(' : '.join([encode_b64_bytes(m.id).decode(), 
                              m.text if not m.has_receiver else encode_b64_bytes(m.text).decode(), 
                              'N/A' if not m.has_receiver else encode_b64_bytes(m.receiver).decode(), 
                              'N/A' if not m.has_sender else encode_b64_bytes(m.sender).decode()]))

        print(' --- MESSAGES END --- ')
        
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
