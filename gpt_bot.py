import itchat
import requests
from bilibili_api import search, sync, user, favorite_list, video, comment
from datetime import datetime
from diffusion.diffusion import ai_draw
import random
import time
from chatgpt import chatgpt
import threading
from uuid import uuid1
import os
dj_imgs = []


for filepath,dirnames,filenames in os.walk(r'./repositories/yiyandingzhen'):
    for filename in filenames:
        if filename.split('.')[-1] in ["gif","jpg","jpeg","png","svg",'bmp']:
            dj_imgs.append(os.path.join(filepath,filename))


def download_cover(url):
    r = requests.get(url)
    p = "./covers/"+str(uuid1())+".jpg"
    with open(p, 'wb') as f:
        f.write(r.content)               
    return p
    
ai_painting_on = True
hard_mode_on = True


bili_favs = {
    'Yuanhou':'77439966',
    '薄荷冰皮蛋糕奶茶':'2027309228',
    '远渡':'2238175994'
}
bili_news = {}

for name,id in bili_favs.items():
    fav = favorite_list.FavoriteList(favorite_list.FavoriteListType.VIDEO,media_id=id)

    res = sync(fav.get_content())

    if (not res['medias']) or len(res['medias'])==0:
        bili_news[name] = 0
        continue
    
    bili_news[name] = res['medias'][0]['bvid']


room = None
def watch_bilibili():
    global room
    if not room:
        rooms = itchat.get_chatrooms()
        if len(rooms)==0:
            return
        room = rooms[0]
    for name,id in bili_favs.items():
        fav = favorite_list.FavoriteList(favorite_list.FavoriteListType.VIDEO,media_id=id)

        res = sync(fav.get_content())
        
        if (not res['medias']) or len(res['medias'])==0:
            continue
        
        
        if res['medias'][0]['bvid'] == bili_news[name]:
            continue
        
        print(bili_news)
        
        vid = res['medias'][0]
        bili_news[name] = vid['bvid']
        reps = sync(comment.get_comments(res['medias'][0]['id'],type_=comment.CommentResourceType.VIDEO,order=comment.OrderType.LIKE))['replies']
        com = [
            i['content']['message']
            for i in (reps if reps else [])
        ]
        b_com = "无"
        for c in com:
            b_com = c
            break
        room.send_image(download_cover(vid['cover']))
        m = "{}收藏了新视频\nhttps://www.bilibili.com/video/{}\n\n标题：{}\nUP：{}\n发布时间：{}\n热评：\n{}".format(name,vid['bvid'],vid['title'],vid['upper']['name'],datetime.utcfromtimestamp(vid['pubtime']).strftime("%Y-%m-%d %H:%M:%S"),b_com)
        room.send(m)
        print(m)
        chatgpt.history.append(
                {
                    'role': 'system',
                    'content': m
                }
            )
        

def watch_bili_loop():
    while True:
        watch_bilibili()
        time.sleep(20)

threading.Thread(target=watch_bili_loop).start()

@itchat.msg_register(itchat.content.TEXT)
def single_reply(msg):
    if ai_painting_on:
        msg.user.send_image(ai_draw(msg.text))
        return
    msg.user.send_image("120px-Taffy_top_2.png")
    return "关注永雏塔菲喵，关注永雏塔菲谢谢喵"

@itchat.msg_register(itchat.content.TEXT, isGroupChat = True)
def text_reply(msg):
    global history,sum,ai_painting_on,hard_mode_on
    
    if msg.actualNickName == 'Yuanhou' and msg.text == 'dif':
        ai_painting_on = not ai_painting_on
        if ai_painting_on:
            return "绘图已打开"
        else:
            return "看见Taffy再说吧"
    
    if msg.actualNickName == 'Yuanhou' and msg.text == 'har':
        hard_mode_on = not hard_mode_on
        if hard_mode_on:
            return "使用GPT3.5-turbo模型"
        else:
            return "davinci来咯~"
        
    if msg.text == "小小丁真":
        f = random.choice(dj_imgs)
        msg.user.send_image(f)
        print(f)
        return f.split("/")[-1].split('.')[0]
    
    
    if msg.text.startswith("小小告诉"):
        split = msg.text.find("：")
        if split == -1:
            split = msg.text.find(":")
        if split == -1:
            return "格式错误，应为：“小小告诉[角色名]：对话内容”"
        target = msg.text[4:split]
        content = msg.text[split+1:]
        print(target,content)
        res = requests.get("http://45.129.9.134:8081/tell",{"target":target,"content":content}).json()
        
        return res["target"]+" 的回复：\n\n"+res["content"]
    
    if msg.text.startswith("小小重置"):
        split = msg.text.find("：")
        target = msg.text[4:]
        print(target)
        res = requests.get("http://45.129.9.134:8081/restart",{"target":target},timeout=20).json()
        
        return res["target"]+" 的问好：\n\n"+res["content"]
    
    
    if(msg.text.startswith("小小画画")):
        if ai_painting_on:
            msg.user.send_image(ai_draw(msg.text[4:]))
            
            chatgpt.history.append(
                {
                    'role': 'system',
                    'content': msg.actualNickName+"想让你画画，他给了提示词："+msg.text[4:]+"。你已经画完了这幅画并把画发到了群里。"
                }
            )
            return "@"+msg.actualNickName+" 的 "+msg.text[4:]
        msg.user.send_image("120px-Taffy_top_2.png")
        return "关注永雏塔菲喵，关注永雏塔菲谢谢喵"
    
    chatgpt.ai_chat(msg,hard_mode_on)
    
itchat.auto_login(enableCmdQR=2,hotReload=True)
itchat.run()
itchat.dump_login_status()
