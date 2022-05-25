from threading import Thread
from datetime import datetime
import socket
import pandas
import os


def main():

    # server's IP address
    config = {
        "SERVER_HOST": "127.72.1.1",
        "SERVER_PORT": 6052,  # port we want to use
        "separator_token": "<SEP>",  # we will use this to separate the client name & message
    }

    # initialize list/set of all connected client's sockets
    client_sockets = set()
    # create a TCP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # make the port as reusable port
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind the socket to the address we specified
    s.bind((config["SERVER_HOST"], config["SERVER_PORT"]))
    # listen for upcoming connections
    s.listen(2)

    print(f"[*] Listening as {config['SERVER_HOST']}:{config['SERVER_PORT']}")

    def create_file():
        if os.path.exists("db.csv"):
            return
        else:
            data = [
                ["Time Stamp", "Image Box", "People"],
            ]
            dataframe = pandas.DataFrame(data)
            dataframe.to_csv("db.csv", index=False, mode="a", header=False)

    def append_to_file(image_box, people):
        data = []
        data.append([])
        data[0].append(datetime.now().strftime("%x %X"))
        data[0].append(image_box)
        data[0].append(people)

        dataframe = pandas.DataFrame(data)
        dataframe.to_csv("db.csv", index=False, mode="a", header=False)

    create_file()

    def listen_for_client(cs):
        """
        This function keep listening for a message from `cs` socket
        Whenever a message is received, broadcast it to all other connected clients
        """
        try:
            # keep listening for a message from `cs` socket
            fragments = []
            while True:
                chunk = cs.recv(8192)
                if not chunk:
                    break
                fragments.append(chunk)

            data = b" ".join(fragments)
            data = data.decode()

            cs.close()
            print(f"[-] {client_address} disconnected.")
            client_sockets.remove(cs)

            data = data.split("<image-box-end>")
            append_to_file(data[0], data[1])
            print(data[0])
            print(data[1])
        except Exception as e:
            # client no longer connected
            # remove it from the set
            print(f"[!] Error: {e}")
            client_sockets.remove(cs)

    while True:
        # we keep listening for new connections all the time
        client_socket, client_address = s.accept()
        print(f"[+] {client_address} connected.")
        # add the new connected client to connected sockets
        client_sockets.add(client_socket)
        # start a new thread that listens for each client's messages
        t = Thread(target=listen_for_client, args=(client_socket,))
        # make the thread daemon so it ends whenever the main thread ends
        t.daemon = True
        # start the thread
        t.start()


if __name__ == "__main__":
    main()
