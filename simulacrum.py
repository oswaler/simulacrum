# https://www.youtube.com/watch?v=ic3__PoSq-4
# pyinstaller -F -w mailmidi.py

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
# import mimetypes
import email.mime.application
from tkinter import *
from tkinter import messagebox
from midiutil import MIDIFile  # midi creation module
from midi2audio import FluidSynth  # creates wav from midi
from playsound import playsound # mp3 in-app player module
from pydub import AudioSegment  # converts wav to mp3
import re  # regex used in validating email address

usesoundfont = '/home/eric/soundfonts/tubular_bells.sf2' # sound font used in creating sound file

class Application(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid()
        self.button_clicks = 0
        self.create_widgets()

    def create_widgets(self):

        self.instruction2 = Label(self, text="Enter email address: ")
        self.instruction2.grid(row=2, column=0, columnspan=1, sticky=W)

        self.email_address = Entry(self, width=50)
        self.email_address.grid(row=2, column=1, sticky=W)
        self.email_address.insert(END, 'eric@ericoswald.com')

        self.bademail = Label(self)
        self.bademail.grid(row=2, column=2, columnspan=1, sticky=W)

        self.submit_button = Button(self, text="Begin Data Capture", command=self.reveal)
        self.submit_button.grid(row=3, column=0, sticky=W)

        self.text = Text(self, width=35, height=5, wrap=WORD, state=DISABLED)
        self.text.grid(row=4, column=0, columnspan=2, sticky=W)

        self.email_sent = Label(self, text="")
        self.email_sent.grid(row=5, column=0, sticky=W)

    def reveal(self):
        # content = self.password.get()
        message = ""
        self.text.config(state=NORMAL)

        isvalid = self.mail_valid(self.email_address.get())

        if (isvalid):

            self.bademail.config(text=message)
            self.text.delete(0.0, END)
            f = open('datacap.txt')
            content_list = f.readlines()
            f.close()

            for i in range(len(content_list)):
                # content_list[i] = content_list[i].strip('\n')
                self.text.insert(0.0, content_list[i])
                self.text.mark_set("insert", "100.100")
                self.text.see("insert")
            # End FOR

            self.text.insert(END, "IMPORT COMPLETE.")
            self.make_midi(content_list)
            self.send_mail(self.email_address.get())
            self.text.mark_set("insert", "100.100")
            self.text.see("insert")
            self.email_sent.config(text="Email sent to: " + self.email_address.get())
        # End IF

        else:
            message = "<=- Invalid email address"
            messagebox.showinfo("Invalid Email Address", "Your email address must be in the form user@domain.ext")
            self.text.delete(0.0, END)
            self.bademail.config(text=message)
            self.email_sent.config(text="")
        # End ELSE

        # self.text.insert(END, "IMPORT COMPLETE.")
        # self.email_sent.config(text="Email sent to: " + self.email_address.get())
        self.text.config(state=DISABLED)


    def make_midi(self, data_list):
        degrees = []
        volume = []
        duration = []
        # channel = []
        track = []
        time = []

        for i in range(len(data_list)):
            data_list[i] = data_list[i].strip('\n')
            current = data_list[i].split(",")
            degrees.append(int(current[0]))
            volume.append(int(current[1]))
            duration.append(float(current[2]))
            track.append(int(current[3]))
            time.append(float(current[4]))

        """
        print(degrees)
        print(volume)
        print(duration)
        print(track)
        print(time)
        """

        # degrees  = [38, 42, 57, 38, 57, 42, 38]  # MIDI note number
        # track    = 0
        channel = 0
        # time = 1    # In beats
        # duration = [15, 15, 12, 13, 11, 13, 3]    # In beats
        tempo = 20  # In BPM
        # volume   = [110, 25, 100, 80, 40, 70, 120]  # 0-127, as per the MIDI standard
        program = 10

        MyMIDI = MIDIFile(3, deinterleave=False)  # One track, defaults to format 1 (tempo track is created
        # automatically)

        MyMIDI.addTempo(0, 1, tempo)
        MyMIDI.addTempo(1, 1, tempo)
        MyMIDI.addTempo(2, 1, tempo)
        MyMIDI.addProgramChange(0, channel, 1, program)
        MyMIDI.addProgramChange(1, channel, 1, program)
        MyMIDI.addProgramChange(2, channel, 1, program)

        for i, pitch in enumerate(degrees):
            MyMIDI.addNote(track[i], channel, pitch, time[i], duration[i], volume[i])

        with open("simulacrum.mid", "wb") as output_file:
            MyMIDI.writeFile(output_file)

        fs = FluidSynth(usesoundfont) # usesoundfont is defined at top of code

        fs.midi_to_audio('simulacrum.mid', 'simulacrum.wav')
        AudioSegment.from_wav("simulacrum.wav").export("simulacrum.mp3", format="mp3")
        # playsound('simulacrum.mp3') # Plays the mp3 after its created - not sure if want to do this or not

    def mail_valid(self, useraddress):

        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', useraddress)

        if match == None:
            return False

        else:
            return True


    def send_mail(self, to_address):

        email_user = "gentleechodesigns@gmail.com"
        email_pass = "90089008aA!"
        smtp_ssl_host = 'smtp.gmail.com'  # smtp.mail.yahoo.com
        smtp_ssl_port = 465
        s = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
        s.login(email_user, email_pass)

        msg = MIMEMultipart()
        msg['Subject'] = 'Data file attached'
        msg['From'] = email_user  # email_user
        msg['To'] = to_address

        txt = MIMEText('Here is Your Data File.')
        msg.attach(txt)

        filename = "simulacrum.mp3"
        fo = open(filename, 'rb')
        file = email.mime.application.MIMEApplication(fo.read(), _subtype=".mp3")
        fo.close()
        file.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(file)
        # msg.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(file)

        s.send_message(msg)
        s.quit()


root = Tk()
root.title("Simulacrum")
root.geometry("800x300")

app = Application(root)
root.mainloop()
