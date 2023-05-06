import requests
from PIL import Image
import io
import base64
import datetime

diff_api = ""

payload = {
    "prompt": "maltese puppy",
    "steps": 30,
    "negative_prompt":"((low quality)),((big breast)),((naked)),nude,no_cloth,lowres,bad anatomy,bad hands,text,error,missing fingers,extra digit,fewer digits,cropped,worst quality,low quality,normal quality,jpeg artifacts,signature,watermark,username,blurry,missing arms,long neck,Humpbacked,(((NSFW)))",
    "width": 512,
    "height": 768,
}
def ai_draw(prompt):
    print(prompt)
    payload['prompt'] = "((best quality)),((highly detailed)),"+prompt
    response = requests.post(url=diff_api, json=payload).json()
    for i in response['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
        filename = "imgs/"+str(datetime.datetime.now())+'.png'
        image.save(filename)
        return filename
