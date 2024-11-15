import requests
import urllib.request
import urllib.parse
import json



# def send_command_to_raspberry_pi(command):
#     url = "http://10.197.116.132:5000/command"
#     data = {"command": command}
#     response = requests.post(url, json=data)
#     if response.status_code == 200:
#         print(f"{command} command sent successfully")
#     else:
#         print(f"Failed to send {command} command")
# send_command_to_raspberry_pi("stop_vacuum")

def send_email(msg):
    url = "http://NicoTo.pythonanywhere.com/send-email"
    data = {
        # "subject": "Test Subject",
        "body": msg,
        "to_email": "nico.luu.to@gmail.com"
    }
    data_encoded = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=data_encoded, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print(" command sent successfully")
            else:
                print(f"Failed to send command")
    except urllib.error.URLError as e:
        print(f"Failed to send  command. Error: {e.reason}")
send_email("HII FROM WALT")