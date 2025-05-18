import threading
from socket import *
from customtkinter import *


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        set_appearance_mode("System") 
        set_default_color_theme("blue")

        self.geometry('600x400')
        self.minsize(400, 300)
        self.label = None

        self.menu_frame = CTkFrame(self, width=30, height=400)
        self.menu_frame.place(x=0, y=0)
        self.menu_frame.pack_propagate(False)

        self.is_show_menu = False
        self.speed_animate_menu = -5
        self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)

        self.chat_field = CTkTextbox(self, font=('Arial', 14, 'bold'), state='disabled')
        self.chat_field.place(x=30, y=0)

        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:', height=40)
        self.message_entry.bind('<Return>', lambda event: self.send_message())
        self.message_entry.place(x=30, y=360)

        self.send_button = CTkButton(self, text='>', width=50, height=40, command=self.send_message)
        self.send_button.place(x=550, y=360)

        self.username = 'Лопата'
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('4.tcp.eu.ngrok.io', 12565))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")

        self.after_idle(self.adaptive_ui)  

    def toggle_show_menu(self):
        if self.is_show_menu:
            new_name = self.entry.get().strip()
            if new_name:
                self.username = new_name

            self.is_show_menu = False
            self.speed_animate_menu = -abs(self.speed_animate_menu)
            self.btn.configure(text='▶️')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu = abs(self.speed_animate_menu)
            self.btn.configure(text='◀️')
            self.show_menu()

            self.label = CTkLabel(self.menu_frame, text='Імʼя')
            self.label.pack(pady=30)
            self.entry = CTkEntry(self.menu_frame)
            self.entry.pack()
            self.entry.insert(0, self.username)

    def show_menu(self):
        new_width = self.menu_frame.winfo_width() + self.speed_animate_menu
        self.menu_frame.configure(width=new_width)
        self.update_idletasks()

        if self.is_show_menu and new_width < 200:
            self.after(10, self.show_menu)
        elif not self.is_show_menu and new_width > 30:
            self.after(10, self.show_menu)
        else:
            if not self.is_show_menu and self.label and self.entry:
                self.label.destroy()
                self.entry.destroy()

    def adaptive_ui(self):
        self.update_idletasks()

        width = self.winfo_width()
        height = self.winfo_height()
        menu_width = self.menu_frame.winfo_width()

        self.menu_frame.configure(height=height)

        self.chat_field.place(x=menu_width, y=0)
        self.chat_field.configure(width=width - menu_width, height=height - 40)

        self.send_button.place(x=width - 50, y=height - 40)
        self.message_entry.place(x=menu_width, y=height - 40)
        self.message_entry.configure(width=width - menu_width - 50)

        self.after(100, self.adaptive_ui)

    def add_message(self, text):
        self.chat_field.configure(state='normal')
        self.chat_field.insert(END, text + '\n')
        self.chat_field.configure(state='disabled')
        self.chat_field.see(END)


    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_message(f"{self.username}: {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                self.add_message("[SYSTEM] Помилка при надсиланні повідомлення.")
        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]
                self.add_message(f"{author}: {message}")
        else:
            self.add_message(line)


win = MainWindow()
win.mainloop()
