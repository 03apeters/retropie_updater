#
# Anthony R Peters
#
# Sends terminal commands through SSH to automatically update retropie
# and install any new games found in roms folder

import paramiko
import PySimpleGUI as gui
import time
from threading import Thread
import os

queue = []
progress_update = []
login_info = []

def main():
    gui.theme("Dark Grey 11")
    layout = [[gui.Text('IP address', size=(26, 1)), gui.InputText()],
              [gui.Text('Hostname', size=(26, 1)), gui.InputText()],
              [gui.Text('Password', size=(26, 1)), gui.InputText()],
              [gui.Submit()]]
    window = gui.Window("RetroPie Updater", layout, margins=(200, 200))
    while True:
        event, values = window.read()
        if event == gui.WIN_CLOSED:
            break
        if event == "Submit":
            ip = values[0]
            host = values[1]
            password = values[2]
            login_info.append(ip)
            login_info.append(host)
            login_info.append(password)
            print(host + '@' + ip)
            print(password)
            window.close()
            load()


def load():
    gui.theme("Dark Grey 11")
    message = 'Connecting'
    layout = [[gui.Text(message, size=(26, 1), key='connect')]]
    window = gui.Window("RetroPie Updater", layout, margins=(200, 200))
    start = time.time()
    i = 0
    ssh_connect = Thread(name='connect', target=connect)
    ssh_connect.start()
    while ssh_connect.is_alive():
        event, values = window.read(timeout=10)
        if event == gui.WIN_CLOSED:
            break
        if time.time() - start > 0.5:
            start = time.time()
            i += 1
            message = "Connecting" + ("." * (i%4))
            window['connect'].update(message)
    if len(queue) == 0:
        error = "Error: Connection has failed. Please verify credentials and try again."
        response = gui.Popup(error, title='Connection Failed', custom_text=('Retry', 'Cancel'))
        window.close()
        if response == 'Retry':
            load()
        else:
            main()
    else:
        window.close()
        progress_bar()

def connect():
    ip = login_info[0]
    host = login_info[1]
    password = login_info[2]
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=host, password=password, timeout=10, port=22)
    queue.append(client)

def update():
    client = queue[0]
    stdin, stdout, stderr = client.exec_command('some really useful command')
    folders = stdout.readlines()
    print(''.join(folders))
    sftp = client.open_sftp()
    #sftp.put('test/test1', 'test/test1')
    for x in range(100):
        time.sleep(0.001)
        progress_update[0] += 1
    client.close()

def progress_bar():
    gui.theme("Dark Grey 11")
    updater = Thread(name='connect', target=update)
    updater.start()
    while updater.is_alive():
        gui.one_line_progress_meter(title='Updating Device', current_value=progress_update[0], max_value=101, no_button=True)



main()