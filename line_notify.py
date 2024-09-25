import requests

user = "Nack Bonus"
notify_token = "TtK9sTE06I8itQbl75gFdcwjdYertYmIbQEhTr7V0Mg"   # Group Token
notify_token = "b15ajPr1mhglSe58uxBzngKqgvVxx1DAvaYE5mIlQtS"   # My Token

# Send the Image in a Message via LINE
def line_notify(message, image_url):
    # Define the endpoint URL
    url = "https://notify-api.line.me/api/notify"
    token = "TtK9sTE06I8itQbl75gFdcwjdYertYmIbQEhTr7V0Mg"   # Group Token
    token = "b15ajPr1mhglSe58uxBzngKqgvVxx1DAvaYE5mIlQtS"   # My Token

    # Define the headers
    header = {"content-type": "application/x-www-form-urlencoded", "Authorization": "Bearer " + token}

    data = {"message": message, "imageThumbnail":image_url, "imageFullsize":image_url}
    response = requests.post(url, headers=header, data=data)
    if response.status_code == 200:
        print("Notify message sent successfully")
    else:
        print(f"Failed to send image message: {response.status_code} {response.text}")