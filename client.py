import socket
import threading
import time
import pyotp
import qrcode

nickname = input("choose a nickname :   ")
key = pyotp.random_base32()

totp = pyotp.TOTP(key)
print(totp.now())
qrcode.make(totp.now()).save("qr.png")
input_code = input("Enter a 2FA Code : ")

if totp.verify(input_code):

    if nickname == 'admin': 
        password = input("enter password for admin : ")
else:
    print("wrong code operation canceled")
       

    

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

stop_thread = False

if totp.verify(input_code)==False: 
    stop_thread=True

client.connect(('127.0.0.1',8080))

def receive():
    while True: 
        global stop_thread
        if stop_thread:
            break
        try: 
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
                next_message = client.recv(1024).decode('ascii')
                if next_message == "PASS":
                    client.send(password.encode('ascii'))
                    if client.recv(1024).decode('ascii') == 'REFUSE':
                        print("connection was refused : Wrong Password")
                        stop_thread = True
                elif next_message == 'BAN':
                    print('Connection refused because of ban! ')
                    client.close()
                    stop_thread = True 
            else:
                print(message)
        except:
            print("An error occured ! ")
            client.close()
            break


def write():
    while True:
        if stop_thread:
            break
        message = f'{nickname}: {input("")}'
        if message[len(nickname)+2:].startswith('/'):
            if nickname == "admin":
                if message[len(nickname)+2].startswith('/kick'):
                    client.send(f'KICK{message[len(nickname)+2+6:]}'.encode('ascii'))
                elif message[len(nickname)+2].startswith('/ban'):
                    client.send(f'BAN{message[len(nickname)+2+5:]}'.encode('ascii'))
            else:
                print("Commands can only be executed by the admin ! ")
        else:
            client.send(message.encode('ascii'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

