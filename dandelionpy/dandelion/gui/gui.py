"""
simple GUI implementation
"""
import sqlite3
import tkinter
from tkinter import *
import threading
import dandelion
from dandelion.util import *
from dandelion.identity import IdentityInfo
from re import sub
#import time
from queue import Queue

class GUI(tkinter.Frame):

    def __init__(self, config_manager, db, id, server=None, content_synchronizer=None):

        self._server = server
        self._synchronizer = content_synchronizer
        self._config_manager = config_manager
        self._db = db
        self._identity = id

        # identity set

        # for threading..
        # self.has_been_run = False

        # welcome = self._db.add_search
        # print(welcome)

        # TKinter
        master = None
        tkinter.Frame.__init__(self, master)

        self.master.config(
            borderwidth=0,
            background=self._config_manager["bg_master"],
            )

        self.master.focus_set()

        self.processcheck = IntVar() #P
        self.processCheck = 1 #P
        self.MAX_TEXT_LENGTH = StringVar()
        self.MAX_TEXT_LENGTH = "Max 140 chars"

        # Message labels
        self.labelMsgs = StringVar()
        self.labelMsgs.set("...looking for messages")

        self.master.title("Dandelion Message System") #P

        message_entry_area_height = message_area_height = 3

        row_pos = 2

        # Insert text to search
        self.search_term_frame = tkinter.Frame(master,
                                               bg=self._config_manager["bg_frame"],
                                               borderwidth=self._config_manager["border"])
        self.search_term = tkinter.Text(self.search_term_frame,
                                        bg=self._config_manager["bg_window"],
                                        fg=self._config_manager["fg_window"],
                                        height=1,
                                        width=20)
        self.search_term.insert(END, self._config_manager["label_searchbox"])

        self.search_term_frame.grid(row=row_pos, column=1, sticky=W, padx=8, pady=8)
        self.search_term.grid(row=row_pos, column=1, sticky=W, padx=8, pady=8)

        # search message button
        self.search_messages = tkinter.Button(master,
                                              text=self._config_manager["label_search_m"],
                                              bg=self._config_manager["bg_button"],
                                              fg=self._config_manager["fg_button"],
                                              activebackground=self._config_manager["abg_button"],
                                              highlightbackground=self._config_manager["hbg_button"],
                                              command=self._search_messages)
        self.search_messages.grid(row=row_pos, column=1, sticky=E, padx=8, pady=8)

        # quit message button
        self.QUIT = tkinter.Button(master,
                                   text=self._config_manager["label_quit"],
                                   bg=self._config_manager["bg_button"],
                                   fg=self._config_manager["fg_button_a"],
                                   activebackground=self._config_manager["abg_button"],
                                   highlightbackground=self._config_manager["hbg_button"],
                                   command=self._quit)
        self.QUIT.grid(row=row_pos, column=3, sticky=E, padx=8)

        # get ids button
        self.UpdateNodes = tkinter.Button(master,
                                          text=self._config_manager["label_get_id"],
                                          bg=self._config_manager["bg_button"],
                                          fg=self._config_manager["fg_button"],
                                          activebackground=self._config_manager["abg_button"],
                                          highlightbackground=self._config_manager["hbg_button"],
                                          command=self.show_identities)
        self.UpdateNodes.grid(row=row_pos, column=4, sticky=E, padx=8)

        row_pos+=1 # linebrake+1

        # Messages display widget
        self.message_area_frame = tkinter.Frame(master,
                                               bg=self._config_manager["bg_frame"],
                                               borderwidth=self._config_manager["border"])

        self.message_area = tkinter.Text(self.message_area_frame,
                                         bg=self._config_manager["bg_window"],
                                         fg=self._config_manager["fg_window"],
                                         height=16)
        self.message_area.insert(END, self._config_manager["welcome_screen"])
        self.message_area.config(state=DISABLED)
        self.message_area_frame.grid(row=message_area_height,
                                     column=1,
                                     columnspan=3,
                                     rowspan=message_area_height,
                                     sticky=W,
                                     padx=8,
                                     pady=8)

        self.message_area.grid(row=message_area_height,
                               column=1,
                               columnspan=3,
                               rowspan=message_area_height,
                               sticky=W,
                               padx=8,
                               pady=8)

        self.yscroll = tkinter.Scrollbar(command=self.message_area.yview,
                                         orient=tkinter.VERTICAL)
        self.yscroll.grid(row=message_area_height, column=1,
                          columnspan=3,
                          rowspan=message_area_height,
                          sticky=tkinter.N+tkinter.S+tkinter.E, padx=8, pady=8)
        self.message_area.configure(yscrollcommand=self.yscroll.set)

        # Id display widget
        self.id_list_frame = tkinter.Frame(master,
                                               bg=self._config_manager["bg_frame"],
                                               borderwidth=self._config_manager["border"])

        self.id_list = tkinter.Listbox(self.id_list_frame,
                                       bg=self._config_manager["bg_window"],
                                       fg=self._config_manager["fg_window"],
                                       height=23,
                                       width=18)
        self.id_list_frame.grid(row=message_area_height,
                                column=4,
                                columnspan=1,
                                rowspan=6,
                                sticky=W,
                                padx=8,
                                pady=8)

        self.id_list.grid(row=message_area_height,
                          column=4,
                          columnspan=1,
                          rowspan=6,
                          sticky=W,
                          padx=8,
                          pady=8)

        row_pos += message_area_height

        # title over your message widget
        self.tilte = tkinter.Label(master,
                                   text=self._config_manager["your_m_title"],
                                   bg=self._config_manager["bg_window"],
                                   fg=self._config_manager["fg_window"])
        self.tilte.grid(row=row_pos, column=1, sticky=W, padx=8)


        # show message button
        self.show_messages = tkinter.Button(master,
                                            text=self._config_manager["label_show_m"],
                                            bg=self._config_manager["bg_button"],
                                            fg=self._config_manager["fg_button"],
                                            activebackground=self._config_manager["abg_button"],
                                            highlightbackground=self._config_manager["hbg_button"],
                                            command=self._show_messages)
        self.show_messages.grid(row=row_pos, column=1, columnspan=3, sticky=E, padx=8, pady=8)

        row_pos+=1 # new row

        #  widget where messages are entered
        self.message_entry_area_frame = tkinter.Frame(master,
                                               bg=self._config_manager["bg_frame"],
                                               borderwidth=self._config_manager["border"])

        self.message_entry_area = tkinter.Text(self.message_entry_area_frame,
                                               bg=self._config_manager["bg_window"],
                                               fg=self._config_manager["fg_window"],
                                               height=3)
        self.message_entry_area_frame.grid(row=row_pos, column=1,
                                           columnspan=3,
                                           rowspan=message_entry_area_height,
                                           sticky=W, padx=8, pady=8)

        self.message_entry_area.grid(row=row_pos, column=1,
                                columnspan=3,
                                rowspan=message_entry_area_height,
                                sticky=W, padx=8, pady=8)

        row_pos += message_entry_area_height
        self.message_entry_area.bind('<Return>', self._send_text) # TODO binds return to send msg?

        # Check this box to sign your message
        self.sign_var = tkinter.IntVar()
        self.sign_checkbutton = tkinter.Checkbutton(master,
                                                    text=self._config_manager["sign"],
                                                    bg=self._config_manager["bg_button"],
                                                    fg=self._config_manager["fg_button"],
                                                    activebackground=self._config_manager["abg_button"],
                                                    highlightbackground=self._config_manager["hbg_button"],
                                                    borderwidth=0,
                                                    variable=self.sign_var)
        self.sign_checkbutton.grid(row=row_pos, column=1, sticky=W, padx=8)

        # Process text
        self.processTextLen = StringVar()
        self.processTextLen.set(self.MAX_TEXT_LENGTH)
        self.processTextStartLen = tkinter.Label(master,
                                                 bg=self._config_manager["bg_window"],
                                                 fg=self._config_manager["fg_window"],
                                                 textvariable=self.processTextLen,
                                                 height=4)
        self.processTextStartLen.grid(row=row_pos, column=4, sticky=W, padx=8)

        # send message button
        self.send_button = tkinter.Button(master,
                                          text=self._config_manager["label_send"],
                                          bg=self._config_manager["bg_button"],
                                          fg=self._config_manager["fg_button"],
                                          activebackground=self._config_manager["abg_button"],
                                          highlightbackground=self._config_manager["hbg_button"],
                                          command=self._send_text)
        self.send_button.grid(row=row_pos, column=3, sticky=E, padx=8)

        # Widget to display/edit nick selection
        self.editnick_frame = tkinter.Frame(master,
                                            bg=self._config_manager["bg_frame"],
                                            borderwidth=self._config_manager["border"])
        
        self.editnick = tkinter.Entry(self.editnick_frame,
                                      width=18,
                                      bg=self._config_manager["bg_window"],
                                      fg=self._config_manager["fg_window"])
        self.editnick.insert(0, self._config_manager["label_nickbox"])
        self.editnick_frame.grid(row=row_pos, column=4, padx=8, pady=8)
        self.editnick.grid(row=row_pos, column=4, padx=8, pady=8)

        row_pos+=1 #new row

        # start and restart button
        self.START_RESTART = tkinter.Button(master,
                                            text=self._config_manager["label_start"],
                                            bg=self._config_manager["bg_button"],
                                            fg=self._config_manager["fg_button"],
                                            activebackground=self._config_manager["abg_button"],
                                            highlightbackground=self._config_manager["hbg_button"],
                                            command=self._start_restart)
        self.START_RESTART.grid(row=row_pos, column=2, sticky=W, padx=8, pady=8)

        # stop button
        self.STOP = tkinter.Button(master,
                                   text=self._config_manager["label_stop"],
                                   bg=self._config_manager["bg_button"],
                                   fg=self._config_manager["fg_button"],
                                   activebackground=self._config_manager["abg_button"],
                                   highlightbackground=self._config_manager["hbg_button"],
                                   command=self._stop)
        self.STOP.grid(row=row_pos, sticky=E, column=1)

        # process text
        self.processText = StringVar()
        self.processText.set("Active...")
        self.processTextStart = tkinter.Label(master,
                                              bg=self._config_manager["bg_window"],
                                              fg=self._config_manager["fg_window"],
                                              textvariable=self.processText,
                                              height=4)
        self.processTextStart.grid(row=row_pos, column=1, sticky=W, padx=8)

        # help button
        self.HELP = tkinter.Button(master,
                                   text=self._config_manager["label_help"],
                                   bg=self._config_manager["bg_button"],
                                   fg=self._config_manager["fg_button"],
                                   activebackground=self._config_manager["abg_button"],
                                   highlightbackground=self._config_manager["hbg_button"],
                                   command=self._help)
        self.HELP.grid(row=row_pos, column=3, sticky=E, padx=8, pady=8)


        self.save_nickname = tkinter.Button(master,
                                            text=self._config_manager["label_set_new_nick"],
                                            bg=self._config_manager["bg_button"],
                                            fg=self._config_manager["fg_button"],
                                            activebackground=self._config_manager["abg_button"],
                                            highlightbackground=self._config_manager["hbg_button"],
                                            borderwidth=0,
                                            command=self.set_nick)
        self.save_nickname.grid(row=row_pos, column=4, sticky=E, padx=8, pady=8)
        self.save_nickname.config(state=DISABLED)

        # pressing the return key will update edited line
        self.editnick.bind('<Return>', self.set_nick)

        # left mouse click on a list item to display selection
        self.id_list.bind('<ButtonRelease-1>', self.get_name)

        self.show_identities()

    #    self._start_restart()

        self._db.add_event_listener(self._message_listener)

        self._event_queue = Queue()

        self._check_queue()

        self.mainloop()

    def _message_listener(self, type, msgs):
        self._event_queue.put_nowait("newmessage")
#        print(type, msgs)

    def _check_queue(self):
        while self._event_queue.qsize():
            msg = self._event_queue.get(0)
            self._show_messages()
            self.show_identities()
        self.master.after(100, self._check_queue)

    #def _msgloop(self):
    #    while not self._stop_requested:
    #        self._show_messages()
    #        time.sleep(1)

    #def _idloop(self):
    #    while not self._stop_requested:
    #        self.show_identities()
    #        time.sleep(10)

    def _start_restart(self):
        print("starting things")
        self.labelStarted = ("Active...")
        self.processText.set(self.labelStarted)
        self.processCheck = 1
        self._synchronizer.start()
        self._stop_requested = False

        # Thread for checking new messages
        # self._stop_requested = False
        #self._msgthread = threading.Thread(target=self._msgloop)
        # self._msgthread.start()

        # Thread for checking id list
        # self._idthread = threading.Thread(target=self._idloop)
        # self._idthread.start()

    def _stop(self):
        #self._stop_requested = True
        #if self._msgthread is not None:
        #    self._msgthread.join(2)
        #    if self._msgthread.is_alive():
        #        print("msgthread is alive")
        #        raise Exception # timeout
        #if self._idthread is not None:
        #    self._idthread.join(11)
        #    if self._idthread.is_alive():
        #        print("idthread is alive")
        #        raise Exception # timeout

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

    def _send_text(self, *event):
        msg = self.message_entry_area.get(1.0, END)
        msg = sub("\n"," ",msg)
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
            self.labelToLong = ("Message too long.")
            self.processTextLen.set(self.labelToLong)
        self._show_messages()

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
            sender = 'anon' if not m.has_sender else encode_b64_bytes(m.sender).decode()
            if  m.has_receiver:
                msg = "%s to %s> %s\n" % (sender,
                                        'N/A' if not m.has_sender else encode_b64_bytes(m.sender).decode(),
                                        encode_b64_bytes(m.text).decode())
            else:
                msg = "%s> %s\n" % (sender, m.text)
                self.message_area.insert(END, msg)

        self.message_area.config(state=DISABLED)
        self.message_area.see(tkinter.END)

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
        _, newidentities = self._db.get_identities()

        selindices = self.id_list.curselection()
        if selindices:
            selindex = int(selindices[0])
            selection = self.identities[selindex]
            self.id_list.selection_clear(selindex)

        self.id_list.delete(0, END)

        for id in newidentities:
            id_info = IdentityInfo(self._db, id)
            if id_info.nick is None:
                thisname = encode_b64_bytes(id.fingerprint).decode()
                thisnick = "Anon_"+thisname[12:16]
            else:
                thisnick = id_info.nick

            self.id_list.insert(END, thisnick)

        if selindices:
            try:
                selindex = newidentities.index(selection)
                self.id_list.selection_set(selindex)
                self.id_list.activate(selindex)
            except ValueError:
                pass

        self.identities = newidentities

        self.save_nickname.config(state=DISABLED)

    def get_name(self, event):
        """
        function to read the listbox selection
        and put the result in an entry widget
        """
        # get selected line index. i set a class-wide variable here instead /plan
        self.index = self.id_list.curselection()[0]
        # get the line's text
        seltext = self.id_list.get(self.index)
        # delete previous text in editnick
        self.editnick.delete(0, 50)
        # now display the selected text
        self.editnick.insert(0, seltext)
        self.save_nickname.config(state=NORMAL)

    def set_nick(self, *event):
        """
        insert an edited line from the entry widget
        back into the listbox
        """

        selindices = self.id_list.curselection()
        if selindices:
            selindex = int(selindices[0])
            selection = self.identities[selindex]
            id_info = IdentityInfo(self._db, selection)
            newnick = self.editnick.get()
            id_info.nick = newnick
            
            self.show_identities()

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
