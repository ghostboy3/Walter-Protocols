import requests


def send_command_to_raspberry_pi(command):
    url = "http://10.197.116.85:5000/command"
    data = {"command": command}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print(f"{command} command sent successfully")
    else:
        print(f"Failed to send {command} command")
send_command_to_raspberry_pi("stop_vacuum")