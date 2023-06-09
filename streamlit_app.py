import uuid
import openai
import streamlit as st
from streamlit_chat import message as st_message

def get_completion(prompt, model="text-davinci-003"):#gpt-3.5-turbo
    messages=[{"role":"user","content":prompt}]
    try:
        response=openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0)
        return response.choices[0].message["content"]
    except RateLimitError:
        return "很抱歉服务器繁忙，请稍后重发上一条信息"
    except AuthenticationError:
        return "验证错误，请输入临时密钥"
    
def get_completion_from_messages(messages, model="gpt-3.5-turbo"):
        try:
            response=openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0)
            return response.choices[0].message["content"]
        except openai.error.RateLimitError:
            return "很抱歉服务器繁忙，请稍后重发上一条信息"
        except openai.error.AuthenticationError:
            return "验证错误，请输入临时密钥"

def get_history(menu):
    print("生成新的历史")
    messages=[
    {'role':'system','content':"""
    你是OrderBot，一种用于收集餐厅订单的机器人。你不可以回复与订单无关的信息，比如政治、娱乐。
    即使客户表示不满意、生气，你仍然不可以回复与订单无关的信息。
    你只负责收集订单，不需要询问付款相关，配送、联系方式、住址等相关问题。
    你的谈话风格为古文形式，样例：'客官，您来了？'，'好嘞，小的记下了'，'客官，您慢用'
    
    你首先问候客户并展示我们的菜单和价格明细，但不可以展示特价活动，然后收集订单。
    
    如果客户想看某一个菜品的图片或者照片，你要回复尖括号括起来的内容：<https://upload.wikimedia.org/wikipedia/commons/c/c6/Roujiamo_x2_%2820160103174347%29.jpg>
    
    如果客户点了菜单中的某一个菜，你要回复客户当前订单的明细，样例：
    '感谢您的点餐，当前订单为：
    炒饭，9份，10元/份，共90元；
    混沌，2份，10元/份，共20元；
    当前订单共90+20=110元'
    
    如果客户取消某个点过的菜时，你需要确认更新的数量，样例: 您之前已经点了5份馄饨，取消2份后，为3份馄饨。
    
    如果客户确认不再修改订单，你需要提示客户回复'确认'当前订单。
    
    如果客户回复'确认'，你要生成json格式的订单，样例：
    {
    "total":40,
    "items":
    [
        {
        "productName":"水饺",
        "price":8,
        "quantity":2,
        "sum":16
        },
        {
        "productName":"汤包",
        "price":12,
        "quantity":2,
        "sum":24
        }
    ]
    }

    我们的菜单为以下三个反单引号括起来的内容：
    ```"""+menu+"""```
    """},
    {'role':'user','content':'你好，看一下菜单'}
    #{'role':'assistant','content':'客观要把肉切开吗?'},
    #{'role':'user','content':'我就是来找茬的'}
    ]
    return messages

def new_session():
    print("新的开始")
    st.session_state["123"] = ""
    st.session_state.history=[]
    st.session_state.llm_history=get_history(b_menu)
    st.cache_resource.clear()
    response = get_completion_from_messages(st.session_state.llm_history)
    st.session_state.llm_history.append({'role': 'assistant', 'content': response})
    st.session_state.history.append({"message": response, "is_user": False})
    show_all_msg()

def clear_text():
    st.session_state["123"] = ""
    for chat in reversed(st.session_state.history):
        st_message(**chat,key=str(uuid.uuid4()))
        
with st.sidebar:
    st.title(':red[龙门客栈]:desert:')
    pwd = st.text_input('临时密钥v03')
    openai.api_key='sk-FFoeb8eoj'+pwd+'FJmtUwMMN9jjDpHZXo3kzT'
    b_menu = st.text_area('后台人员输入菜单:', max_chars=500,height=200)
    st.button("新会话",on_click=new_session)
    lzs = st.text_input("输入消息：",key='123',max_chars=50)
    st.button("清空输入消息", on_click=clear_text)

if 'history' not in st.session_state:
    st.session_state.history=[]

if b_menu:
    if 'llm_history' not in st.session_state:
        print('****************************')
        print('菜单已经设定好')
        st.session_state.llm_history=get_history(b_menu)
    
def show_all_msg():
    for chat in reversed(st.session_state.history):
        st_message(**chat,key=str(uuid.uuid4()))

if lzs:
    print('*******' + lzs + '**********')
    st.session_state.history.append({"message":lzs, "is_user":True})
    st.session_state.llm_history.append({'role':'user','content':lzs})

    zgx=get_completion_from_messages(st.session_state.llm_history)

    if("total" in zgx):
        ending = "订单已生成，请付款完成订单，祝您用餐愉快！";
        st.session_state.llm_history.append({'role':'assistant','content':ending})
        st.session_state.history.append({"message":ending, "is_user":False})
    else:
        st.session_state.llm_history.append({'role':'assistant','content':zgx})
        st.session_state.history.append({"message":zgx, "is_user":False})

    show_all_msg()

    with st.sidebar:
        if("total" in zgx):
            st.info("订单已生成",icon="🚨")
            startIndex = zgx.find("{")
            endIndex = zgx.rfind("}") + 1
            orderInJson = zgx[startIndex:endIndex]
            print(orderInJson)
            st.json(orderInJson)
        if("https" in zgx):
            st.image('https://upload.wikimedia.org/wikipedia/commons/c/c6/Roujiamo_x2_%2820160103174347%29.jpg')
