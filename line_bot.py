from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from github import Github
import warnings
import requests
import uuid
from line_notify import line_notify, user

# Example usage
user_ids = [
    "U2af4cd23ba057030837e401ab488cf02",  # Ton
    "U4db9f375da2e63997f8e2a03000bba8d",  # Nack
    "U9f00eaf78bbd70b7c8ad7a741ef72b84",  # Pun
    "U0ceb0cba8da60c75125db0c9305dff18",  # Mook
    "Udc06fb08562413d3a0a4ba12973c7238",  # K
]
access_token = "H01BF+FEExRChKZwwf9VDkavRldgHer6UynWdEalU12Db1HPAoAv9vToEqWl0Ij8fqb4Z7gwGC3GJxHm3jw4NEw8P0SsWhlr+cEen6HweDPFy911euOyRx08CXm11vicIdZVNlSUe1v/yiONdz+GKwdB04t89/1O/w1cDnyilFU="
github_token = "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" 
repo_name = "LE402" 
date = datetime.now() - timedelta(days=1)
message = "%s's %s Data" % (user, date.strftime("%d-%m-%Y"))
hr_message = "%s's %s Heart Rate" % (user, date.strftime("%d-%m-%Y"))

# Generate the Matplotlib Plot
def generate_plot(data:dict, hr:dict):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        labels = data.keys()
        values = data.values()
        
        fig, ax = plt.subplots()
        ax.bar(labels, values)
        ax.set_title(message)
        ax.set_xlabel('Time (hr)')
        ax.set_ylabel('Distance (m)')
        
        plt.savefig("image.jpg", format='jpg')

        labels = hr.keys()
        values = hr.values()
        
        fig, ax = plt.subplots()
        ax.bar(labels, values)
        ax.set_title(hr_message)
        ax.set_xlabel('Time (hr)')
        ax.set_ylabel('Distance (m)')
        
        plt.savefig("hr_image.jpg", format='jpg')
    
# Upload Image to GitHub
def upload_image_to_github(user_id, image):
    random_name = str(uuid.uuid4())
    file_path = 'images/%s.jpg' % random_name
    g = Github(github_token)
    repo = g.get_repo("ChutiponTri/LE402")
    try:
        repo.create_file(file_path, "Add plot image", bytes(image), branch='main')
        print("Uploaded Image")

        raw_url = f"https://raw.githubusercontent.com/{repo.full_name}/main/{file_path}"
        send_image_message(user_id, raw_url)
    except:
        print("Error")
    finally:
        content = repo.get_contents("images/%s.jpg" % random_name)
        repo.delete_file(content.path, "Delete File", content.sha, branch="main")

# Send the Image in a Message via LINE
def send_image_message(message, image_url):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {
        "to": user_ids[0],
        "messages": [
            {
                "type": "text",
                "text": message
            },
            {
                "type": "image",
                "originalContentUrl": image_url,
                "previewImageUrl": image_url
            },
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Bot message sent successfully")
    else:
        # print(f"Failed to send image message: {response.status_code} {response.text}")
        line_notify(message, image_url)

# Main function to send plot as image message
def send_plot_to_line(data, hr, message):
    generate_plot(data, hr)
    with open("image.jpg", "rb") as file:
        image = file.read()
        image = bytearray(image)
    with open("hr_image.jpg", "rb") as file:
        hr_image = file.read()
        hr_image = bytearray(hr_image)
    upload_image_to_github(message, image)
    upload_image_to_github("Heart Rate Data", hr_image)

def line_bot(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {
        "to": user_ids[0],
        "messages": [
            {
                "type": "text",
                "text": message
            },

        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Bot message sent successfully")
    else:
        # print(f"Failed to send messages: {response.status_code} {response.text}")
        line_notify(message, None)

if __name__ == '__main__':
    line_bot(user_ids[0])
