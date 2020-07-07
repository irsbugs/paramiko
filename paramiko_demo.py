#!/usr/bin//env python3
#
# paramiko_demo.py
# Demonstrates copying files from remote server and executing commands on a
# remote server.
#
# For installation of paramikp using apt.
# $ suro apt install python3-paramiko
#
# Ian Stewart 2020-0-08
#
# Warning: Confidential data regarding the remote server.
# Can be read from b64.data file as comma seperated values
# Changing all these from being empty strings will over-ride reading b64.data file.
SERVER = ""
PORT = 22
USERNAME = ""
PASSWORD = ""

TITLE = "Demo Paramiko"
WINDOW_WIDTH = 950
WINDOW_HEIGHT = 400
HEADING_MESSAGE = """
Welcome to the paramiko python module demo."

Paramiko will copy a file from a remote server as well as execute commands on
a remote server.

On launching this application four methods tested for the remote servers 
details. This is to retrieve confidential data. Thus it is not ideal to have
this data in the program or left in the command line history. However
as this is a demo, then it may be acceptable.

The four options used are:

1. At the top of this program edit in values for SERVER = "", PORT = 22
USERNAME = "" and PASSWORD = ""

2. At the bottom of this program uncomment
#create_b64_message()
#sys.exit()
...and start the program. When prompted enter something like this:

SERVER = "1.2.3.4",PORT = 2022,USERNAME = "aroha",PASSWORD = "my_password"

Re-insert the # to make the two lines of code comments again. Restart the
application. A file named b64.data will now be read to retrieve these remote 
server details. The contents of the b64.data file is something like this:
0gIjIxOS44OS4yMDUuMTAwIixQT1JUID0gMjAyMixVU0VSTkFNRSA9ICJpImRlY3RoYWlsYW5kIg==

3. Run the application with --help and observer the command line options 
available. i.e.

usage: paramiko_demo.py [-h] [-s SERVER] [-p PORT] [-u USERNAME] [-w PASSWORD]

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        Server domain name or IP address string.
  -p PORT, --port PORT  Port number for ssh
  -u USERNAME, --username USERNAME
                        Account name on remote server .
  -w PASSWORD, --password PASSWORD
                        Password to Account on remote server.

Start the application with something like this:

$ python paramiko_demo.py -s 1.2.3.4 -p2022 -u aroha -w my_password


4. Just start the application and you will prompted to enter these remote server 
details.

"""
REMOTE = "/var/log/wtmp"
LOCAL = "servers_wtmp"

# Labels for the buttons
BUTTON_LIST = ["Copy", "Command 1", "Command 2", "Command 3", "Command 4"]

PYTHON_VERSION_MIN = (3, 7, 0)

import paramiko
import base64
import os
import sys
import argparse
import subprocess

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GObject', '2.0')
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GLib', '2.0')
gi.require_version('Pango', '1.0')
from gi.repository import Gtk, Gst, Gdk  #, GObject, Gtk, Gdk, GLib, Pango


# subprocess.run() capture_output=True requires V3.7+
# sys.version_info(major=3, minor=8, micro=2, releaselevel='final', serial=0)
if sys.version_info < PYTHON_VERSION_MIN: 
    print("Python must be at Version {}.{} or higher."
        .format(PYTHON_VERSION_MIN[0], PYTHON_VERSION_MIN[1]))
    sys.exit("Exiting...")


#    /* CSS to set the font size for everything */
#    * {
#    font: 16px Mono;
#    }
# Use CSS as mothod of changing fonts and colours, etc.
# see: https://developer.gnome.org/gtk3/stable/chap-css-overview.html
CSS = """
    /* Theme all widgets with the style class text-button */
    .text-button {
    color: blue;
    font: 18px Sans;    
    }
    
    /* Theme any widget in the scrolledwindow. i.e. The textview */
    scrolledwindow * {
        color: black;
        background-color: #ddffff;
        font: 18px Mono; 
    }
"""

class Demo_Window(Gtk.Window):
    'Launch the Demo window'
    def __init__(self):
        super(Demo_Window, self).__init__()
        
        self.setup_css()                   
        self.setup_main()
        
        # Start
        Gtk.main()

        # Shutdown actions
        self.destroy()
        sys.exit()

   
    def setup_main(self):

        # Get the path icon in a temp file.    
        #self.icon_path_file = self.get_icon_file_path_name()
        self.setup_window()
        self.setup_textview()
        self.setup_buttonbox()

        self.add(self.vbox)
        self.show_all()

        
    def setup_window(self):
        # Setup window
        self.set_title(TITLE)
        self.set_size_request(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.set_default_size(300, 200)
        self.connect("destroy", Gtk.main_quit, "WM destroy")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        #self.set_icon_from_file(self.icon_path_file)

        # Instantiate main container for the window   
        self.vbox = Gtk.VBox() 
        self.vbox.set_margin_start(10)
        self.vbox.set_margin_end(10) 
        #self.vbox.set_margin_top(MARGIN_SIZE)
        self.vbox.set_margin_bottom(10)
     

    def setup_css(self):
        # Apply css for font and colour changes, etc.
        css_provider = Gtk.CssProvider()
        # If css start with b for bytes: css = b'* { background-color: #f00; }'
        #css_provider.load_from_data(css)
        css_provider.load_from_data(bytes(CSS.encode()))
        context = Gtk.StyleContext()
        screen = Gdk.Screen.get_default()
        context.add_provider_for_screen(screen, 
                                        css_provider,
                                        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            

    def setup_textview(self):
        """
        Create a textview window to display return data from remote commands.
        Insert in a scrolled window.
        """
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_min_content_height(200)
   
        self.textview_1 = Gtk.TextView()
        self.textbuffer_1 = self.textview_1.get_buffer()
        self.textbuffer_1.set_text(HEADING_MESSAGE)

        # If not using the scrolled window, then word wrap.
        # Gtk.WrapMode.NONE Gtk.WrapMode.CHAR Gtk.WrapMode.WORD
        #self.textview_1.set_wrap_mode(Gtk.WrapMode.WORD)

        scrolled_window.add(self.textview_1)
        self.vbox.pack_start(scrolled_window, expand=True, fill=True, padding=0 )


    def setup_buttonbox(self):
        """
        Create a horizontal button box
        Add buttons to the ButtonBox and connect to a single callback function
        But get callback to pass an integer value for unique identification.
        """
        hbox = Gtk.ButtonBox.new(Gtk.Orientation.HORIZONTAL)
        hbox.set_spacing(5)
                   
        for i in range(len(BUTTON_LIST)):
            button = Gtk.Button(label=BUTTON_LIST[i])           
            button.set_can_focus(False)
            button.connect("clicked", self.button_clicked, i)
            hbox.add(button)

        self.vbox.pack_start(hbox, expand=False, fill=True, padding=0)    
    

    def button_clicked(self, widget, index):
        """
        Callback for buttons in the button box. value is index of button
        """
        if index == 0:
            #print("Index: 0. Copy?")
            # Perform copy operation
            self.textbuffer_1.set_text("Copy Remote File: " + REMOTE + "\n" +
                    "To Local File: " + LOCAL + "\n\n")
            
            copy_from_remote_server(args.server, args.port, args.username, 
                    args.password, REMOTE, LOCAL)
                    
            response = subprocess.run(["ls","-l", LOCAL], capture_output=True)
            string = response.stdout.decode("utf-8")
            self.textbuffer_1.set_text("Copy Remote File: " + REMOTE + "\n" +
                    "To Local File: " + LOCAL + "\n\n" + string)
       

        if index == 1:
            COMMAND = 'ls -l'
            return_string = execute_command_on_remote_server(args.server, 
                    args.port, args.username, args.password, COMMAND)
            self.textbuffer_1.set_text("Remote Command: " + COMMAND + "\n\n" 
                    + return_string)
            #print(return_string)
            

        if index == 2:
            COMMAND = 'ls -l /etc'
            return_string = execute_command_on_remote_server(args.server, 
                    args.port, args.username, args.password, COMMAND)
            self.textbuffer_1.set_text("Remote Command: " + COMMAND + "\n\n" 
                    + return_string)
            #print(return_string)
   
        if index == 3:
            COMMAND = 'uname -a'
            return_string = execute_command_on_remote_server(args.server, 
                    args.port, args.username, args.password, COMMAND)
            self.textbuffer_1.set_text("Remote Command: " + COMMAND + "\n\n" 
                    + return_string)
            #print(return_string)   

        if index == 4:
            COMMAND = 'cat /etc/debian_version'
            return_string = execute_command_on_remote_server(args.server, 
                    args.port, args.username, args.password, COMMAND)
            self.textbuffer_1.set_text("Remote Command: " + COMMAND + "\n\n" 
                    + return_string)
            #print(return_string)              


def copy_from_remote_server(server, port, username, password, remote, local):
    """
    Copy a file from a remote server.
    A previous ssh login should have been performed so ~/.ssh/known_hosts
    has the keys.
    """
    
    client = paramiko.SSHClient()
    client.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))

    try:
        client.connect(server, port, username, password)
    except Exception as e:
        print("Error: {}".format(e))
        # paramiko.ssh_exception.AuthenticationException: Authentication failed

    sftp = client.open_sftp()
    sftp.get(remote, local)
    sftp.close()
    client.close()
    
    
def execute_command_on_remote_server(server, port, username, password, command):
    """
    Connect to the server, execute command and grab the results.
    """
    client = paramiko.SSHClient()
    #client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))    

    try:
        client.connect(server, port, username, password)
    except Exception as e:
        print("Error: {}".format(e))       
   
    stdin, stdout, stderr = client.exec_command(command)

    #print(type(string))  # <class 'paramiko.channel.ChannelFile'>

    # Because type is <class 'paramiko.channel.ChannelFile'> read each line???
    string = ""
    for line in stdout:
        string += line

    client.close()
    return string
    

def create_b64_message():
    """
    Convert the confidential remote server data to be a b64 string
    """
    message = input("Enter a message you want converted to base64: ")
    message_bytes = message.encode('utf-8')
    base64_bytes = base64.b64encode(message_bytes)
    #print("Encoded message in bytes:{}".format(base64_bytes))
    message_b64_ascii = base64_bytes.decode('utf-8')
    print("Encoded message in utf-8:{}".format(message_b64_ascii))

    # Check decoding: 
    base64_bytes = message_b64_ascii.encode('utf-8')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('utf-8')    
    print("Original message decoded:{}".format(message))
    
    # Write b64 data to file
    with open("b64.data", "w") as fout:
        fout.write(message_b64_ascii)
        
    # Open file and check it decodes OK:
    with open("b64.data", "r") as fin:
        message_b64_ascii = fin.read()
        base64_bytes = message_b64_ascii.encode('utf-8')
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode('ascii')    
        print("Original message from file decoded:{}".format(message))             
        

if __name__=="__main__":
    pass

# One-time code to create a base64 message:
# Run the create_b64_message() utility and add four parameters as follows:
# SERVER = "1.2.3.4",PORT = 2022,USERNAME = "aroha",PASSWORD = "my_password"
#create_b64_message()
#sys.exit()

# If not set in constants section at the top of the program, 
# then try for b64.data file to load constants.
if SERVER == "" or USERNAME == "" or PASSWORD == "":

    try: 
        with open("b64.data", "r") as fin:
            message_b64_ascii = fin.read()
            base64_bytes = message_b64_ascii.encode('utf-8')
            message_bytes = base64.b64decode(base64_bytes)
            message = message_bytes.decode('ascii')
            #print(message)
            constant_list = message.split(",")
            #print(data_list)
            for constant in constant_list:
                exec(constant)            
            
    except FileNotFoundError as e:
        print("b64.data file not found")
        print("Continuing...")
        #print("No server, port, username or password details")
        #sys.exit("exiting...")
        
#print(SERVER, PORT, USERNAME, PASSWORD)        
        
# Allow command line to load constants
# Use argparse for: server, port, username and passwrod
parser = argparse.ArgumentParser()


parser.add_argument("-s", "--server", 
                    type = str, 
                    default = SERVER,
                    help = "Server domain name or IP address string.")
                    
parser.add_argument("-p", "--port", 
                    type = int, 
                    default = PORT,
                    help = "Port number for ssh")                        
                 
parser.add_argument("-u", "--username", 
                    type = str, 
                    default = USERNAME,
                    help = "Account name on remote server .")

# Password for development only. Removes need for first screen. TODO: Comment out.
parser.add_argument("-w", "--password", 
                    type = str, 
                    default = PASSWORD,
                    help = "Password to Account on remote server.")


# Prompt for the server, port, username and password.                   
args = parser.parse_args()

if args.server == "":
    args.server = input("\nEnter the name or ip address of the server: ")
    
if args.port == 22:
    args.port = int(input("\nEnter the ssh port number: "))       

if args.username == "":
    args.username = input("\nEnter the Account name on the remote server: ")

# Password for development only. Removes need for first screen. TODO: Comment out.
if args.password == "":
    args.password = input("\nEnter the password for the account on the remote server: ")


# Launch Gtk GUI
# GObject.threads_init()  # <-- Deprecated since V3.11
Gst.init(None)
Demo_Window()