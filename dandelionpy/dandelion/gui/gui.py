"""
simple GUI implementation
"""
import sqlite3
import tkinter
from tkinter import *
import threading # vad använd detta till? 
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
        

        # identity set
        self.has_been_run = False
        # welcome = self._db.add_search
        # print(welcome)
        
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
        self.MAX_TEXT_LENGTH = StringVar()
        self.MAX_TEXT_LENGTH = "Max 140 chars"
        
        # styling --------------------------------
        # button 
        bg_button = "black" # background color 
        fg_button = "green" # foreground color 
        abg_button = "yellow" # activebackground
        hbg_button = "yellow" # highlightbackground
        # windows widgets
        bg_window = "black" # background color 
        fg_window = "green" # foreground color
        
        # button alert 
        fg_button_a = "red" # foreground color
        
        # Lables for buttons
        lable_search_m = "Search" # search_messages label text
        lable_show_m = "Get messages" # get_messages label text
        lable_quit = "x" # quit label text
        lable_get_id = "Get ids" # get ids label text
        lable_stop = "Stop" # stop label text
        lable_start = "Start" # start label text,  ► sign could be used 
        lable_send = "Send" # send label text
        lable_help = "?" # help lable text

        # Lables mics       
        your_m_title = "What on your mind?" # title over write message box
        sign = "Sign" # checkbox if sign
        lable_nickbox = "Rename nick" # remane nick label text       
        lable_set_new_nick = "Set new nick"
        lable_searchbox = "Search"
        
        # Message lables
        self.labelMsgs = StringVar()
        self.labelMsgs.set("...looking for messages")   
        
        # Messages 
        welcome_screen = """  
  Welcome to the Dandelion Message System  
  --------------------------------------------------  
  Dandelion is robust, distributed message passing   
  designed to leverage the power of self organizing 
  networks. The message passing protocol can be     
  implemented on any transport layer but we will     
  start by implementing it utilizing Zeroconf       
  service discovery and ad hoc wifi networks with    
  link local addresses. Dandelion does not rely on   
  any existing infrastructure like the Internet or   
  mobile phone services - it is truly peer to peer. 
        """
        
        self.master.title("Dandelion Message System") #P
        
        message_entry_area_height = message_area_height = 3
        
        row_pos = 2
       
        # Insert text to search
        self.search_term = tkinter.Text(master, bg=bg_window, fg=fg_window, height=1, width=20)
        self.search_term.insert(END, "Search messages")
        self.search_term.grid(row=row_pos, column=1, sticky=W, padx=8, pady=8)
        
        # search message button 
        self.search_messages = tkinter.Button(master, text=lable_search_m, bg=bg_button, fg=fg_button, 
                                            activebackground=abg_button, highlightbackground=hbg_button, 
                                            command=self._search_messages)
        self.search_messages.grid(row=row_pos, column=1, sticky=E, padx=8, pady=8)

        # quit message button        
        self.QUIT = tkinter.Button(master, text=lable_quit, bg=bg_button, fg=fg_button_a, 
                                            activebackground=abg_button, highlightbackground=hbg_button,
                                            command=self._quit)
        self.QUIT.grid(row=row_pos, column=3, sticky=E, padx=8)
        
        # get ids button         
        self.UpdateNodes = tkinter.Button(master, text=lable_get_id,  bg=bg_button, fg=fg_button, 
                                            activebackground=abg_button, highlightbackground=hbg_button,
                                            command=self.show_identities)
        self.UpdateNodes.grid(row=row_pos, column=4, sticky=E, padx=8)
        
        row_pos+=1 # linebrake+1         
         
        # Messages display widget
        self.message_area = tkinter.Text(master, bg=bg_window, fg=fg_window, height=16)
        self.message_area.insert(END, welcome_screen)
        self.message_area.config(state=DISABLED)
        self.message_area.grid(row=message_area_height, column=1, 
                          columnspan=3, 
                          rowspan=message_area_height, 
                          sticky=W, padx=8, pady=8)
        self.yscroll = tkinter.Scrollbar(command=self.message_area.yview, orient=tkinter.VERTICAL)
        self.yscroll.grid(row=message_area_height, column=1, 
                          columnspan=3, 
                          rowspan=message_area_height, 
                          sticky=tkinter.N+tkinter.S+tkinter.E, padx=8, pady=8)
        self.message_area.configure(yscrollcommand=self.yscroll.set)
        
        # Id display widget
        self.id_list = tkinter.Listbox(master, bg=bg_window, fg=fg_window, height=23, width=18)
        self.id_list.grid(row=message_area_height, column=4, columnspan=1,
                          rowspan=6, 
                          sticky=W, padx=8, pady=8)        
  
        row_pos += message_area_height
        
        # title over your message widget    
        self.tilte = tkinter.Label(master, text=your_m_title, bg=bg_window, fg=fg_window)  
        self.tilte.grid(row=row_pos, column=1, sticky=W, padx=8)
        
         
        # show message button 
        self.show_messages = tkinter.Button(master, text=lable_show_m, bg=bg_button, fg=fg_button, 
                                            activebackground=abg_button, highlightbackground=hbg_button, 
                                            command=self._show_messages)
        self.show_messages.grid(row=row_pos, column=1, columnspan=3, sticky=E, padx=8, pady=8)
          
        row_pos+=1 # new row
          
        #  widget where messages are entered
        self.message_entry_area = tkinter.Text(master, bg=bg_window, fg=fg_window, height=3)
        self.message_entry_area.grid(row=row_pos, column=1, 
                                columnspan=3, 
                                rowspan=message_entry_area_height,
                                sticky=W, padx=8, pady=8)

        row_pos += message_entry_area_height
        
        # Check this box to sign your message 
        self.sign_var = tkinter.IntVar()
        self.sign_checkbutton = tkinter.Checkbutton(master, text=sign, bg=bg_button, fg=fg_button, 
                                                    activebackground="black", highlightbackground="black",
                                                    borderwidth=0, variable=self.sign_var)
        self.sign_checkbutton.grid(row=row_pos, column=1, sticky=W, padx=8)
        
        # Process text
        self.processTextLen = StringVar()
        self.processTextLen.set(self.MAX_TEXT_LENGTH)
        self.processTextStartLen = tkinter.Label(master, bg=bg_window, fg=fg_window, textvariable=self.processTextLen, height=4)       
        self.processTextStartLen.grid(row=row_pos, column=4, sticky=W, padx=8)
        
        # send message button 
        self.send_button = tkinter.Button(master, text=lable_send, bg=bg_button, fg=fg_button, 
                                          activebackground=abg_button, highlightbackground=hbg_button,
                                          command=self._send_text)
        self.send_button.grid(row=row_pos, column=3, sticky=E, padx=8)
        
        # Widget to display/edit nick selection
        self.editnick = tkinter.Entry(master, width=18, bg=bg_window, fg=fg_window)
        self.editnick.insert(0, lable_nickbox)
        self.editnick.grid(row=row_pos, column=4, padx=8, pady=8)
        
        row_pos+=1 #new row
        
        # start and restart button 
        self.START_RESTART = tkinter.Button(master, text=lable_start, bg=bg_button, fg=fg_button, 
                                          activebackground=abg_button, highlightbackground=hbg_button,
                                          command=self._start_restart) 
        self.START_RESTART.grid(row=row_pos, column=2, sticky=W, padx=8, pady=8)

        # stop button
        self.STOP = tkinter.Button(master, text=lable_stop, bg=bg_button, fg=fg_button, 
                                   activebackground=abg_button, highlightbackground=hbg_button,
                                   command=self._stop)
        self.STOP.grid(row=row_pos, sticky=E, column=1)
        
        # process text 
        self.processText = StringVar()
        self.processText.set("Active...")
        self.processTextStart = tkinter.Label(master, bg=bg_window, fg=fg_window, textvariable=self.processText, height=4)       
        self.processTextStart.grid(row=row_pos, column=1, sticky=W, padx=8)

        # help button                
        self.HELP = tkinter.Button(master, text=lable_help, bg=bg_button, fg=fg_button, 
                                   activebackground=abg_button, highlightbackground=hbg_button,
                                   command=self._help)
        self.HELP.grid(row=row_pos, column=3, sticky=E, padx=8, pady=8)
        
        
        self.save_nickname = tkinter.Button(master, text=lable_set_new_nick, bg=bg_button, fg=fg_button, 
                                            activebackground=abg_button, highlightbackground=hbg_button,
                                            borderwidth=0, command=self.set_nick)
        self.save_nickname.grid(row=row_pos, column=4, sticky=E, padx=8, pady=8)              
        self.save_nickname.config(state=DISABLED)
        
        # pressing the return key will update edited line
        self.editnick.bind('<Return>', self.set_nick)
        
        # left mouse click on a list item to display selection
        self.id_list.bind('<ButtonRelease-1>', self.get_name)
        
        self.set_identities_nick()
        
        self.mainloop()

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
        
        self.toLong = IntVar()    
        self.toLong = len(msg)
        if self.toLong > 140:
            self.labelToLong = ("To message to long.")
            self.processTextLen.set(self.labelToLong)           

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
        message_screen = """  
 Dandelion Messages                                    
 -------------------------------------------------
        """

        self.all_msgs = StringVar()
        (current_tc, self.all_msgs) = self._db.get_messages()
        self.message_area.config(state=NORMAL) 
        self.message_area.delete(1.0,END)
        self.message_area.insert(END, message_screen)
        for m in self.all_msgs:   
                self.all_msgs = (' : '.join([encode_b64_bytes(m.id).decode(), 
                            m.text if not m.has_receiver else encode_b64_bytes(m.text).decode(), 
                            'N/A' if not m.has_receiver else encode_b64_bytes(m.receiver).decode(), 
                            'N/A' if not m.has_sender else encode_b64_bytes(m.sender).decode()])) 
                self.message_area.insert(END, self.all_msgs)
        
        self.message_area.config(state=DISABLED)
                
    def _help(self):
        help_screen = """  
 Dandelion Help                                    
 -------------------------------------------------  
 * Help                                        
        """
        self.message_area.config(state=NORMAL) 
        self.message_area.delete(1.0,END)
        self.message_area.insert(END, help_screen) 
        self.message_area.config(state=DISABLED) 
          
    def validatecommand(self, *args):
        return len(self.get()) < self.Message.MAX_TEXT_LENGTH 
    
    def show_identities(self):
        _, self.identities = self._db.get_identities() 
        self.id_list.delete(0, END) 
        #id = db.select(sql)
        for id in self.identities:
            thisname = encode_b64_bytes(id.fingerprint).decode()
            thisnick = "Anon_"+thisname[12:16]
            # later get all nicks, if nick None set nick 
            self.id_list.insert(END, thisnick)     
                    
        self.save_nickname.config(state=DISABLED)
           
    def set_identities_nick(self):
        _, self.identities = self._db.get_identities() 
        self.id_list.delete(0, END) 
        
        for id in self.identities:
            thisname = encode_b64_bytes(id.fingerprint).decode()
            thisnick = "Anon_"+thisname[12:16]
            self._db.set_nick(thisnick, thisname)
            self.id_list.insert(END, thisnick)            
        self.save_nickname.config(state=DISABLED) 
              
    def get_name(self, event):
        """
        function to read the listbox selection
        and put the result in an entry widget
        """
        # get selected line index
        index = self.id_list.curselection()[0]
        # get the line's text
        seltext = self.id_list.get(index)
        # delete previous text in editnick
        self.editnick.delete(0, 50)
        # now display the selected text
        self.editnick.insert(0, seltext)
        self.save_nickname.config(state=NORMAL)
        
    def set_nick(self, event):
        """
        insert an edited line from the entry widget
        back into the listbox
        """
        
        try:
            index = self.id_list.curselection()[0]
            oldnick = self.id_list.get(index)
            print(oldnick)
            # delete old listbox line
            self.id_list.delete(index)
        except IndexError:
            index = tkinter.END
        # insert edited item back into listbox1 at index
    
        self.id_list.insert(index, self.editnick.get())
        newnick = self.id_list.get(index)
        print(newnick)
        self._db.set_nick(newnick, oldnick)
        self.save_nickname.config(state=DISABLED) 
            
    def _search_messages(self):
        search_screen = """  
 Dandelion Search:  """
        self.message_area.config(state=NORMAL) 
        self.message_area.delete(1.0,END)
        self.message_area.insert(END, search_screen)
        term = self.search_term.get(1.0, END)
        self.message_area.insert(END, term)  
        self.message_area.insert(END, " ------------------------------------------------- \n")
        self.message_area.insert(END, " ")   
        result = self._db.search_messages(term) # needs FIX  
        for row in result:
            self.message_area.insert(END, row)  
        self.message_area.insert(END, " ------------------------------------------------- \n")
        self.message_area.insert(END, " Result for: ") 
        self.message_area.insert(END, term)         
        self.message_area.config(state=DISABLED) 
        
    def save_list(self):
        """
        save the current listbox contents to a file
        """
        pass
    
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


