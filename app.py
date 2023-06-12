import cv2
import time
import requests
import numpy as np
from tkinter import *
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode

COUNT = 0
COUNT_UPLOAD = 0
STATE = 'LANDING'
BOOKS = []
CHECKOUT_TYPE = ""
BASE_URL = "http://localhost:3000"
USN = ""
USER_DATA = {}
TRANSACTION_DATA = {}

# >> 0. Top Level Functions
def is_usn(data):
    if len(data) == 7 and data[0:2].isdigit():
        return True

def upload_image(data):
    global COUNT_UPLOAD

    # Upload the Image to the API Endpoint
    if COUNT_UPLOAD == 0:
        retval, buffer = cv2.imencode('.png', data)
        files=[('image',('Pirate.png',buffer,'image/png'))]
        headers = {}
        payload = {}
        response = requests.post(f"{BASE_URL}/auth", headers=headers, data=payload, files=files)
        print(response.text)
        COUNT_UPLOAD = 1

def trigger_action(data=''):
    global STATE
    global BOOKS
    global USN
    global USER_DATA

    if STATE == 'AUTH':
        if is_usn(data):
            USN = data
            help_text.config(
                text="Authentication Successful",
                fg="Green"
                )
            cta.config(text=f"Continue as {data}")
            cta.pack(fill=X, expand=True)
    elif STATE == 'CHECKOUT':
        if data not in BOOKS:
            # Check Book Info from DB
            if CHECKOUT_TYPE == "Issue":
                response = requests.get(f"{BASE_URL}/books/{data}")
                try:
                    if response.json():
                        book = response.json()
                        BOOKS.append(data)
                        Label(top_half, text=f"{len(BOOKS)}. {book['title']}", font=('Arial',15)).pack()
                        Label(top_half, text=f" By: {book['author']}", font=('Arial',10)).pack()
                except:
                    pass
            elif CHECKOUT_TYPE == "Return":
                if data in USER_DATA['books']:
                    response = requests.get(f"{BASE_URL}/books/{data}")
                    try:
                        if response.json():
                            book = response.json()
                            BOOKS.append(data)
                            Label(top_half, text=f"{len(BOOKS)}. {book['title']}", font=('Arial',15)).pack()
                            Label(top_half, text=f" By: {book['author']}", font=('Arial',10)).pack()
                    except:
                        pass

                else:
                    pass

            # End

    elif STATE == 'FACEDETECTION':
        upload_image(data)

def transact():
    # Send Transaction Data
    payload = {
        "transactionType": CHECKOUT_TYPE,
        "from": USN,
        "books": BOOKS
    }
    response = requests.post(f"{BASE_URL}/transactions", json = payload)
    try:
        if response.json():
            complete_transaction_btn.pack(fill=X, expand=True)
            return response.json()
    except:
        pass


def switch_frames(options=''):
    global STATE
    global CHECKOUT_TYPE
    global BOOKS
    global COUNT
    global USN
    global USER_DATA
    global TRANSACTION_DATA

    if STATE == 'LANDING':
        STATE = 'AUTH'
        landing_frame.pack_forget()
        auth_frame.pack(pady=50)

    elif STATE == 'AUTH':
        # Check User in DB
        response = requests.get(f"{BASE_URL}/users/{USN}")
        try:
            if response.json():
                USER_DATA = response.json()
        except:
            response = requests.post(f"{BASE_URL}/users", json = {'usn':USN})
            USER_DATA = response.json()
        # End
        auth_frame.pack_forget()
        choose_actions_frame.pack(pady=50)
        STATE = 'CHOOSE'
        COUNT = 0

    elif STATE == 'CHOOSE':
        STATE = 'CHECKOUT'
        CHECKOUT_TYPE = options
        choose_actions_frame.pack_forget()
        checkout_frame.pack(pady=50)
        checkout_heading.config(text=f"Checkout - {CHECKOUT_TYPE}")

    elif STATE == 'CHECKOUT':
        STATE = 'FACEDETECTION'
        checkout_frame.pack_forget()
        face_detection_frame.pack(pady=50)
        TRANSACTION_DATA = transact()

    elif STATE == 'FACEDETECTION':
        # print(upload_image())
        STATE = 'STATUS'
        face_detection_frame.pack_forget()
        status_frame.pack()
        # Temp Variables
        fbooks = TRANSACTION_DATA['books']
        ftime = TRANSACTION_DATA['transactedOn']
        ftxnid = TRANSACTION_DATA['transactionId']
        # End
        transaction_details.config(text=f"Transaction ID: {ftxnid}\nBooks: {fbooks}\nTime: {ftime}")
    
    elif STATE == 'STATUS':
        # Start - Clear variables and Session Data
        BOOKS = []
        CHECKOUT_TYPE = ""
        # .. Unpack the Labels consisting barcode Ids
        # End
        STATE = 'LANDING'
        status_frame.pack_forget()
        landing_frame.pack(pady=200)
        help_text.config(text='Scan the Barcode on your ID Card', font=('Arial',20), fg='Gray')
        cta.pack_forget()

# << End of TLF

window = Tk()
window.title('Sicily')
window.geometry("1280x1024")

Icon = PhotoImage(file='res/logo.png')
cascade_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# {{ FRAMES }} -- Landing, Auth, Choose Action, Action [Issue/Return] and Transaction

# >> 0. Landing Screen Start
landing_frame = Frame(window)

Label(
    landing_frame,
    text='Sicily',
    font=('Arial',40,'bold')
).grid(row=0, column=0, pady=(50,5))

Label(
    landing_frame,
    text='The Library Management System we Never had!',
    font=('Arial',10,'bold')
).grid(row=1, column=0, pady=(0,20))

Button(
    landing_frame,
    text='Authenticate with ID Card',
    font=('Arial',25),
    bg='Blue',
    fg='White',
    command=switch_frames
).grid(row=2, column=0)

Label(
    landing_frame,
    text="Built with Python, Tkinter, NodeJS. Hosted on Linux. Tested on Postman. And other things I've forgot to mention",
    font=('Arial',10),
    padx=20,
    pady=30
).grid(row=3, column=0, pady=(50,5))

landing_frame.pack(pady=200)
# << 1. Landing Screen End

# >> 2. Auth Screen Start
auth_frame = Frame(window)

Icon_Label2 = Label(
    auth_frame,
    image=Icon
)
Icon_Label2.pack(pady=30)

help_text = Label(
    auth_frame,
    text='Scan the Barcode on your ID Card',
    font=('Arial',30,'bold'),
    fg='Gray'
)
help_text.pack()

F1 = LabelFrame(auth_frame)
F1.pack()

L1 = Label(auth_frame)
L1.pack()

cta = Button(
    auth_frame,
    font=('Arial',25),
    bg='Blue',
    fg='White',
    command=switch_frames
)

# auth_frame.pack(pady=50)

# << >> 3. Auth Screen End. Functions Start

def get_barcodes(image):
    try:
        return decode(image)
    except:
        return []

def draw_polygon(image, barcodes):
    global COUNT
    if len(barcodes) == 0:
        if STATE != 'FACEDETECTION':
            return image
        else:
            # Redundancy (Should be removed OR written as a function)
            frame = cv2.cvtColor(image, 0)
            detections = cascade_classifier.detectMultiScale(frame)
            if (len(detections) > 0):
                (x,y,w,h) = detections[0]
                frame = cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)
                trigger_action(frame)
                return frame
            else:
                return image
    else:
        if STATE != 'FACEDETECTION':
            for barcode in barcodes:
                x, y, w, h = barcode.rect
                cv2.rectangle(image, (x,y), (x+w, y+h), (0,0,255), 4)
                bdata = barcode.data.decode("utf-8")
                cv2.putText(image, bdata, (x, y-1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
                if STATE == "AUTH" and COUNT == 0:
                    trigger_action(bdata)
                    COUNT += 1
                elif STATE == "CHECKOUT":
                    trigger_action(bdata)
                return image
        elif STATE == 'FACEDETECTION':
            frame = cv2.cvtColor(image, 0)
            detections = cascade_classifier.detectMultiScale(frame)
            if (len(detections) > 0):
                (x,y,w,h) = detections[0]
                frame = cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)
                trigger_action(frame)
                return frame
            else:
                return image

        
# << 4. Functions End

# >> 5. Choose Actions Frame Start
choose_actions_frame = Frame(window)

Icon_Label = Label(
    choose_actions_frame,
    image=Icon
)
Icon_Label.pack(pady=50)

Button(
    choose_actions_frame,
    text="Issue Books",
    font=('Arial',30),
    command=lambda: switch_frames('Issue'),
    padx=100,
    pady=50
).pack(pady=10)

Button(
    choose_actions_frame,
    text="Return Books",
    font=('Arial',30),
    command=lambda: switch_frames('Return'),
    padx=88,
    pady=50
).pack(pady=10)

Button(
    choose_actions_frame,
    text="Get Info",
    font=('Arial',30),
    padx=138,
    pady=50
).pack(pady=10)

# << 6. Choose Actions Frame End


# >> 7. Issue / Return. Checkout Screen Start
checkout_frame = Frame(window)

Icon_Label = Label(
    checkout_frame,
    image=Icon
)
Icon_Label.pack(pady=50)

checkout_heading = Label(
    checkout_frame,
    text="",
    font=('Arial',30,'bold'),
    pady=20
)
checkout_heading.pack(side=TOP)

# >> 7.1 Left Half Start
left_half = Frame(checkout_frame)
F2 = LabelFrame(left_half)
F2.pack()

L2 = Label(left_half)
L2.pack()
left_half.pack(side=LEFT)
# << 7.2 Left Half End

# >> 7.3 Right Half Start
right_half = Frame(checkout_frame, padx=35)

# >> 7.3.1 Top Half Start
top_half = Frame(right_half)
Label(
    top_half,
    text='Books',
    font=('Arial',30)
).pack()
top_half.pack()
# << 7.3.2 Top Half End

# >> 7.3.3 Bottom Half Start
bottom_half = Frame(right_half)
Button(
    bottom_half,
    text='Checkout',
    bg='Blue',
    fg='White',
    command=switch_frames
).pack()
bottom_half.pack(side=BOTTOM)
# << 7.3.4 Bottom Half End

right_half.pack(side=RIGHT)
# << 7.4 Right Half End

# << 8. Checkout Screen End

# >> 9. Face Detection - Authorization Screen Start
face_detection_frame = Frame(window)

Icon_Label = Label(
    face_detection_frame,
    image=Icon
)
Icon_Label.pack(pady=50)

Label(
    face_detection_frame,
    text="Face Detection Screen",
    font=('Arial',30,'bold'),
    pady=20
).pack()

F3 = LabelFrame(face_detection_frame)
F3.pack()

L3 = Label(face_detection_frame)
L3.pack()

complete_transaction_btn = Button(
    face_detection_frame,
    text="Complete Transaction",
    font=('Arial',25),
    bg='Blue',
    fg='White',
    command=switch_frames
)
# << 10. Face Detection Screen End


# >> 11. Status Screen Start
status_frame = Frame(window)

Icon_Label = Label(
    status_frame,
    image=Icon
)
Icon_Label.pack(pady=50)

Label(
    status_frame,
    text="Your Transaction is Successful",
    font=('Arial',25,'bold'),
    pady=30
).pack()

transaction_details = Label(
    status_frame,
    text="",
    font=('Arial',20),
    pady=20
)
transaction_details.pack()

Button(
    status_frame,
    text="Return to Home",
    font=('Arial',25),
    bg='Blue',
    fg='White',
    command=switch_frames
).pack()
# << 12. Status Screen End

cap = cv2.VideoCapture(0)


while True:
    _, image = cap.read()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    barcodes = get_barcodes(image)
    image = draw_polygon(image, barcodes)
    img = ImageTk.PhotoImage(Image.fromarray(image))
    if STATE == 'AUTH':
        L1['image'] = img
    elif STATE == 'CHECKOUT':
        L2['image'] = img
    elif STATE == 'FACEDETECTION':
        L3['image'] = img
    window.update()
