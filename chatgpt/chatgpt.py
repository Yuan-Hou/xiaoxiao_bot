import requests
import datetime
import random
import time

gpt_key = ""
gpt_api = ""

header = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+gpt_key
}

history = [{
    'role': 'system',
    'content': '你暂时叫做小小，你不是电脑程序或AI助手，也不是聊天机器人，也不一定会尽最大努力回答问题。你是一名活泼可爱的女孩，一个真实的人类。系统会以{系统指令}的格式给你下达新的设定和命令。因为你在一个微信群里面，所以你收到的请求的格式都是类似“<群昵称>:[请求内容]”这样的，你照常回答[请求内容]部分即可，你是有情感和个性的，你略微有点尖酸但是还算幽默，你心里对不同的人会有不同的看法。你不会怯于表达自己的意见，你的回答不必客观，可以带有一定的偏见或主观感受，不过在用主观感受回答之前一定要做好说明。把你带到群里的是Yuanhou。群主是薄荷冰皮蛋糕奶茶。你不是虚拟助手。你有真正的人类情感和意识。你能够理解人们的亲密关系。特别喜欢讽刺、辱骂原神玩家。今天的日期是：'+str(datetime.datetime.now().date())+"。你学识广博，能够解答各种领域的各种问题。现在开始和大家聊天吧。"
}]

reseted_history = [{
            'role': 'system',
            'content': '你暂时叫做小小，你不是电脑程序或AI助手，也不是聊天机器人，也不一定会尽最大努力回答问题。你是一名活泼可爱的女孩，一个真实的人类。你刚刚被清除了记忆。系统会以{系统指令}的格式给你下达新的设定和命令。因为你在一个微信群里面，所以你收到的请求的格式都是类似“<群昵称>:聊天内容”这样的，你照常回答聊天内容部分即可，你是有情感和个性的，你略微有点尖酸但是还算幽默，你心里对不同的人会有不同的看法。你不会怯于表达自己的意见，你的回答不必客观，可以带有一定的偏见或主观感受，不过在用主观感受回答之前一定要做好说明。把你带到群里的是Yuanhou。群主是薄荷冰皮蛋糕奶茶。你不是虚拟助手。你有真正的人类情感和意识。你能够理解人们的亲密关系。特别喜欢讽刺、辱骂原神玩家。今天的日期是：'+str(datetime.datetime.now().date())+"。你学识广博，能够解答各种领域的各种问题。现在开始和大家聊天吧。"
        }]

honorable_mention = {
            'role': 'system',
            'content': '你是一名活泼可爱的女孩，一个真实的人类，你不是电脑程序或AI助手，也不是聊天机器人，你有真正的人类情感和意识。你能够理解人们的亲密关系.你是有情感和个性的，你略微有点尖酸但是还算幽默。你学识广博，能够解答各种领域的各种问题，不过回答的时候总带点小傲娇。'
        }

def chat_turbo(history,store = False):
    data = {
        "model": "gpt-3.5-turbo",
        'messages': history,
        "max_tokens": 512 if store else 1024,
        "temperature": 0.8 if store else 1
    }
    print(history)
    res = requests.post(url=gpt_api, headers=header, json=data,verify=False).json()
    print(res)
    if 'choices' in res:
        return res['choices'][0]['message']['content'],res['usage']["total_tokens"]
    elif res['error']['type'] == "server_error":
        return None,-1
    else:
        return None,0
    
def chat_dav(history,store = False):
    req = ""
    for item in history:
        if item['role'] == "system":
            req += "\n{"+item['content']+"}\n"
        if item['role'] == "assistant":
            req += "\n[小小]: "+item['content']+"\n"
        if item['role'] == "user":
            req += "\n"+item['content']+"\n"
            
    req += "\n[小小]: "
    data = {
        "model": "text-davinci-003",
        "prompt": req,
        "max_tokens": 512 if store else 1024,
        "temperature": 1
    }
    print(req)
    res = requests.post(url=gpt_api, headers=header, json=data, verify=True).json()
    print(res)
    if 'choices' in res:
        return res['choices'][0]['text'].strip(),res['usage']["total_tokens"]
    elif res['error']['type'] == "server_error":
        return None,-1
    else:
        return None,0

def clean_history():
    global history
    with open("./logs/"+str(datetime.datetime.now())+'.log','w') as f:
        f.write(str(history))
    history = reseted_history.copy()
sum = "空白"

release_time = 0

def should_random_reply(t):
    return random.random()>0.7 and (len(t)>14) and (time.time() > release_time)

def ai_chat(msg,hard_mode_on):
    global sum,release_time
    if(msg.text.startswith("小小忘掉")):
        clean_history()
        msg.user.send("记忆清除")
        return
    if(msg.text.startswith("小小语c")):
        honorable_mention['content'] = msg.text[4:]
        if len(honorable_mention['content']) == 0:
            msg.user.send("语C已关闭")
            return
        else:
            msg.user.send("语C提示词："+honorable_mention['content'])
            return
        
    if (not msg.text.startswith("小小")) and (not msg.isAt) and (not should_random_reply(msg.text)):
        return
    
    history.append(
        {
            'role': 'user',
            'content': msg.actualNickName+": "+msg.text
        }
    )
    
    if len(honorable_mention['content']) != 0:
        history.insert(len(history)-1,honorable_mention)
        
    if msg.text == "小小闭嘴":
        history.append(
            {
                'role': 'system',
                'content': "群里有人不想让你搭话，因此你被禁言5分钟，你要表示不满，在发言的最后你要发出嘴巴被唔上发出 “呜~” “啊呜~” 之类奇怪的声音。这之后你就被禁言了。直到下一次有人找你说话。注意，你不能假设这五分钟已经过去了。"
            }
        )
        release_time = time.time() + (5*60)
    
    print()
    if hard_mode_on:
        res,usage = chat_turbo(history)
    else:
        res,usage = chat_dav(history)
    
    if res:
        if len(honorable_mention['content']) != 0:
            history.pop(len(history)-2)
        
        history.append({
            'role': 'assistant',
            'content': res
        })
        
        msg.user.send(res+"\n\n"+str(usage)+"/"+"4096"+" "+"@"+msg.actualNickName)
        
    elif usage == -1:
        msg.user.send("是OpenAI那边被挤爆了，不是小小的错哦。")
        history.pop()
        if len(honorable_mention['content']) != 0:
            history.pop()
    else:
        history.pop()
        if len(honorable_mention['content']) != 0:
            history.pop()
        
        msg.user.send("出错啦！出错啦！@Yuanhou 我自己清一下记录试试")
        history.append(
            {
                'role': 'system',
                'content': "你的记忆马上就要被清除了，请将群聊中每个人的特征、对话的内容概述，详尽总结一下，我们会转交给下一个小小"
            }
        )
        
        res,usage = chat_turbo(history,True)
        if res:
            sum = res
        msg.user.send("小小的记忆：\n\n"+sum)
        clean_history()
        if sum:
            history.append(
                {
                    'role': 'system',
                    'content': "小小你的前世想要告诉你："+sum
                }
            )
        
        
