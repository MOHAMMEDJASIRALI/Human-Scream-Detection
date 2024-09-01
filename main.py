import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import pyaudio
import numpy as np
from scipy.fftpack import fft
from twilio.rest import Client
import geocoder


# Configuration
TWILIO_SID = 'AC329b7fb4a94119925e977f43af9f3f71'
TWILIO_AUTH_TOKEN = '5ec5766d34331a1dd97a918f8b0c8316'
POLICE_NUMBER = '+918124527116'  # Replace with the police contact number
TWILIO_PHONE_NUMBER = '+12568264437'  # Replace with your Twilio phone number
THRESHOLD = 500000  # Adjust based on environment and testing

# Audio streaming setup
class AudioStream:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

    def read_audio(self):
        return self.stream.read(1024)

# Feature extraction (simple energy thresholding)
def is_scream(audio_data):
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    energy = np.sum(np.abs(fft(audio_array)))
    return energy > THRESHOLD

# Obtain location
def get_location():
    g = geocoder.ip('me')  # Obtain location based on IP address
    return g.latlng

# Send alert message to police with location
def send_alert(twilio_sid, auth_token, twilio_phone_number, police_number, location):
    client = Client(twilio_sid, auth_token)
    message = client.messages.create(
        body=f"Emergency! A danger scream has been detected. Location: {location}",
        from_=twilio_phone_number,
        to=police_number
    )
    return message.sid

# Kivy App
class ScreamDetectionApp(App):
    def build(self):
        self.stream = AudioStream()

        # Kivy UI
        self.layout = BoxLayout(orientation='vertical')
        self.status_label = Label(text="Listening for screams...")
        self.alert_button = Button(text="Send Test Alert", on_press=self.send_test_alert)

        self.layout.add_widget(self.status_label)
        self.layout.add_widget(self.alert_button)

        Clock.schedule_interval(self.detect_scream, 1.0 / 1.0)  # Check 30 times per second
        return self.layout

    def detect_scream(self, dt):
        audio_data = self.stream.read_audio()
        if is_scream(audio_data):
            self.status_label.text = "Danger scream detected!"
            location = get_location()
            send_alert(TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, POLICE_NUMBER, location)
            Clock.unschedule(self.detect_scream)

    def send_test_alert(self, instance):
        location = get_location()
        send_alert(TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, POLICE_NUMBER, location)
        self.status_label.text = "Test alert sent!"

if __name__ == '__main__':
    ScreamDetectionApp().run()
