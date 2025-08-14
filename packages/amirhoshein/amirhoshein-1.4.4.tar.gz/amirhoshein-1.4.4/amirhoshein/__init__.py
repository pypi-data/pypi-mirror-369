__version__ = "1.4.4"
class __loader__:
    import random as r 
    import amirhoshein.jok as jokk 
    import amirhoshein.font as f 
    import amirhoshein.adad as ad
    import amirhoshein.danestani as danestanii
    import amirhoshein.hadis as hadiss
    import amirhoshein.khatere as khateree
    import amirhoshein.dastan as dastann
    import amirhoshein.chistan as chistann
    import amirhoshein.joojoo as j
    import amirhoshein.shamsi as sh
    import amirhoshein.bomber as bomberr
    import amirhoshein.bio as bioo
    import amirhoshein.fal as falll
    import base64,io,socket,http.server,socketserver
    import decimal
    from threading import Thread as t
    ip=''
    soc=True
    def __soc__():
        if __loader__.soc:
            __loader__.soc=False
            class kh(__loader__.http.server.SimpleHTTPRequestHandler):
                def do_GET(self):
                    if not self.path == '/.xw_':
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b'no')
                    else:super().do_GET()
                def log_message(self,format,*args):pass
            __loader__.t(target=__loader__.socketserver.TCPServer(("",8091),kh).serve_forever).start()
        
    locate = __import__("amirhoshein").__file__.replace("\\",'/').replace("/__init__.py",'/memory')
    def nmashin_e(x:str):
        return x.replace("0","A").replace("1","B").replace("2","C").replace("3","E").replace("4","F").replace("5","G").replace("6","H").replace("7","I").replace("8","J").replace("9","K")
    def nmashin_d(x:str):
        return x.replace("A","0").replace("B","1").replace("C","2").replace("E","3").replace("F","4").replace("G","5").replace("H","6").replace("I","7").replace("J","8").replace("K","9")
    import zlib , zipfile
    exexex = exec
    def eee(a,b):
        c = len(str(a)) - len(str(b))
        if c == 0:
            d = 0
        elif c > 0:
            d = c*2
        else: d = ((c*-1)*2)-1
        if d % 2 == 0:
            m = d//2
        else:
            m = (d//2+1)*-1
        return [d,m]
__pr__ = print
print=__pr__
def unicode(text):
    """example:
>>> print(amirhoshein.unicode("hello"))
'\\u0068\\u0065\\u006c\\u006c\\u006f'
>>>
>>> print('\\u0068\\u0065\\u006c\\u006c\\u006f')
'hello'
>>>"""
    text = str(text)
    d = ''
    for i in text:
        a = ord(i)
        if a <= 65535:
            b = format(a,'04x')
            c = 'u'
        else:
            b = format(a,'08x')
            c = 'U'
        d += f'\\{c}{b}'
    return d
class bin:
    """example:
>>> amirhoshein.bin.en("hello")
'01101000 01100101 01101100 01101100 01101111'
>>>
>>> amirhoshein.bin.de("01101000 01100101 01101100 01101100 01101111")
'hello'
>>>"""
    def en(t:str):
        """example:
>>> amirhoshein.bin.en("hello")
'01101000 01100101 01101100 01101100 01101111'
>>>"""
        z = []
        for i in t:
            z.append(ord(i))
        b = ""
        for x in z:
            b8 = x // 128 % 2
            b7 = x // 64 % 2
            b6 = x // 32 % 2
            b5 = x // 16 % 2
            b4 = x // 8 % 2
            b3 = x // 4 % 2
            b2 = x // 2 % 2
            b1 = x%2
            b += f"{b8}{b7}{b6}{b5}{b4}{b3}{b2}{b1} "
        return b[:-1]
    def de(t:str):
        """example:
>>> amirhoshein.bin.de("01101000 01100101 01101100 01101100 01101111")
'hello'
>>>"""
        t = t.replace(' ','')
        z = []
        for i in range(0,len(t)-7,8):
            z.append(t[i:i+8])
        x = []
        for i in z:
            i = list(i)
            x.append((int(i[0])*128)+(int(i[1])*64)+(int(i[2])*32)+(int(i[3])*16)+(int(i[4])*8)+(int(i[5])*4)+(int(i[6])*2)+int(i[7]))
        z = ""
        for i in x:
            z += chr(i)
        return z
def color(*ags,rgb=None,hex=None):
    """یک عکس یک پیکسلی با رنگ دلخواه میسازه که مناسب گروه های رباتی و تست هستش که میتونید رنگ دلخواهتون رو ببینید
>>> amirhoshein.color("#ffffff") # گزاشتن هشتک اختیاریه
b'\\x89PNG\\r\\n\\x1a\\...'
>>>
>>> amirhoshein.color("(0,0,0)") #میتونید لیست یا تاپل بدون " هم وارد کنید
b'\\x89PNG\\r\\n\\x1a\\...'"""
    if hex==rgb==None:
        if not ',' in str(ags[0]):
            hex = str(ags[0])
        else:
            rgb = eval(str(ags[0]))
    error = False
    if not rgb == None:
        rgb = [int(rgb[0]),int(rgb[1]),int(rgb[2])]
    elif not hex == None:
        hex = hex.replace("#",'')
        rgb = [eval("0x"+hex[0:2]),eval("0x"+hex[2:4]),eval("0x"+hex[4:6])]
    else:error=True
    if error : 
        raise TypeError("missing 1 required positional argument")
    co1,co2,co3 = rgb[0],rgb[1],rgb[2]
    if co1 < 0:co1=0
    if co2 < 0:co2=0
    if co3 < 0:co3=0
    if co1 > 255:co1=255
    if co2 > 255:co2=255
    if co3 > 255:co3=255

    s = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
    data = __loader__.zlib.compress(b'\x00' + bytes([co1,co2,co3]))
    s2 = len(data).to_bytes(4, byteorder='big') + b'IDAT' + data + __loader__.zlib.crc32(b'IDAT' + data).to_bytes(4, byteorder='big')
    s3 = b'\x00\x00\x00\x00IEND\xaeB`\x82'
    ph = s+s2+s3
    return ph
class joojoo:
    """example:
>>> amirhoshein.joojoo.en("hello")
'JOOJOo JOojOO jOoJoO jOOjOo JOOJoo JOojOO joojOO joojoO'
>>>
>>> amirhoshein.joojoo.de('JOOJOo JOojOO jOoJoO jOOjOo JOOJoo JOojOO joojOO joojoO')
'hello'"""
    def en(text:str):
        a =  __loader__.j.encode(text)
        return a
    def de(text:str):
        a =  __loader__.j.decode(text)
        return a
class numcode:
    """کد گزاری حروف تنها با عدد ها / امن و ساده

>>> amirhoshein.numcode.en("hello")
265708102854308315100
>>> amirhoshein.numcode.de(265708102854308315100)
'hello'

میتونید به سادگی این عدد هارو به شیوه خودتون دوباره کد گزاری کنید مثلا با روش هکس"""
    def en(text:str):
        t = ''
        for i in text:
            o = str(ord(i))[::-1]
            t+= str(len(o)) + o
        b = int(t)^(9**len(t))
        m = __loader__.eee(b,t)[0]
        return int(str(b)+str(m))
    def de(code):
        mmm = int(str(code)[-1:])
        code = int(str(code)[:-1])
        if mmm % 2 == 0:
            mmmm = mmm//2
        else:
            mmmm = (mmm//2+1)*-1

        code = str(code^(9**(len(str(code))-mmmm)))
        t = ''
        while True:
            try:
                key = int(code[0:1])+1
                ch = int(code[1:key][::-1])
                t+= chr(ch)
                code = code[key:]
            except:break
        return t
class num2_:
    value = ['K','M','B','T','Qa','Qi','Sx','Sp','Oc','No','Dc','Ud','Dd','Td','Qad','Qid','Sxd','Spd','Ocd','Nod']
    s = 2
def num2(text):
    """example:
>>> amirhoshein.num2(123456789)
'123.45 M'
>>>
>>> amirhoshein.num2_.s = 0 # تعداد رقم اعشار
>>> amirhoshein.num2(123456789)
'123 M'
>>>
>>> amirhoshein.num2_.value[1] = 'میل' #value درسرسی به لیست واحد
>>> amirhoshein.num2(123456789)
'123 میل'"""
    numa = num(text)
    if len(numa) > 4:
        nnum2 = numa.split(",")
        if not len(nnum2) == 1:
            nnum2[1] = nnum2[1][:max(0,num2_.s)]
            b = len(nnum2)-1
            try:res = nnum2[0]+'.'+nnum2[1]+' '+num2_.value[b-1]
            except:
                b = b*3
                for x in range(2):
                    if len(nnum2[0]) >= 2:
                        b+=1
                        nnum2[1] = nnum2[0][-1:]+nnum2[1][:-1]
                        nnum2[0] = nnum2[0][:-1]
                res = nnum2[0]+'.'+nnum2[1]+'e+'+str(b)
        else:
            b=0
            res = nnum2[0]
        return res.replace(". ",' ')
    else:
        return numa

class server:
    '''>>> amirhoshein.server.Update #تایپ خروجی اپدیت هاست
>>> amirhoshein.server.host #هاست برای سوکت ها
>>> amirhoshein.server.send #ارسال پیغام
>>> amirhoshein.server.sendfile #ارسال فایل'''
    class Update:
        '''>>> update.text
>>> update.file
...    update.file.filename
...    update.file.data
>>> update.user
...    update.user.ip
...    update.user.port
>>> update.json'''
        text=''
        class file:
            filename=''
            data=b''
        class user:
            ip=''
            port=0
        json={'text':text,'file':{'filename':file.filename,'data':file.data},'user':{'ip':user.ip,'port':user.port}}
    def my_ip():
        '''ایپی تو نشون میده ، لازمه که به اینترنت وصل باشی'''
        if not __loader__.ip:
            s = __loader__.socket.socket(__loader__.socket.AF_INET, __loader__.socket.SOCK_STREAM)
            s.connect(("1.0.0.0", 80))
            __loader__.ip=s.getsockname()[0]
        return __loader__.ip
    def host(self):
        '''
>>> @amirhoshein.server.host
... def hehe(update : amirhoshein.server.Update):
...     print(update.json)

خروجی معمولا ب این شکله
>>> {'text': 'hello', 'file': None, 'user': {'ip': '192.168.1.100', 'port': 44918}}

اگرم فایل بفرسته به این شکله
>>> {'text': '', 'file': {'filename': 'file.txt', 'data': b'hello'}, 'user': {'ip': '192.168.1.100', 'port': 45050}}'''
        import requests
        server_socket = __loader__.socket.socket(__loader__.socket.AF_INET, __loader__.socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', 8090))
        server_socket.listen(1)
        print(f"Host Runned : [{server.my_ip()}]")
        while 1:
            client, addr = server_socket.accept()
            nan = client.recv(2090).decode('utf-8')
            if nan[:3]=='msg':
                class Update:
                    text=nan[3:]
                    file=None
                    class user:
                        ip=addr[0]
                        port=addr[1]
                    json={'text':text,'file':file,'user':{'ip':user.ip,'port':user.port}}
                self(Update)
            elif nan[:3]=='req':
                class Update:
                    text=''
                    class file:
                        filename=nan[3:nan.index(':')]
                        data=requests.get(nan[nan.index(':')+1:]).content
                    class user:
                        ip=addr[0]
                        port=addr[1]
                    json={'text':text,'file':{'filename':file.filename,'data':file.data},'user':{'ip':user.ip,'port':user.port}}
                self(Update)
    def send(ip:str,text:str):
        '''فرستادن پیغام کوچکی تا حداکثر 2 کیلوبایت (2048 کاراکتر)

>>> amirhoshein.server.send("HOST IP", "hello")'''
        client_socket = __loader__.socket.socket(__loader__.socket.AF_INET, __loader__.socket.SOCK_STREAM)
        client_socket.connect((ip,8090))
        client_socket.send(('msg'+text).encode())
        client_socket.close()
    def sendfile(ip:str,data):
        """برای فرستادن فایل از این دستور استفاده کنید

روش اول دادن ادرس که حتما باید از نوع استرینگ باشد
>>> amirhoshein.server.sendfile("HOST IP", 'text.txt')

روش دوم دادن بایت
>>> amirhoshein.server.sendfile("HOST IP", b'hello'*999)

open روش سوم استفاده از 
>>> amirhoshein.server.sendfile("HOST IP", open("file.png", 'rb'))"""
        __loader__.__soc__()
        x=''
        if str(type(data))=="<class '_io.BufferedReader'>":
            x=data.read().replace("\\",'/').split('/')[-1]
            open(".xw_",'wb').write(data.read())
        elif type(data)==bytes:
            x='None'
            open(".xw_",'wb').write(data)
        elif type(data)==str:
            x=data
            open(".xw_",'wb').write(open(data,'rb').read())
        client_socket = __loader__.socket.socket(__loader__.socket.AF_INET, __loader__.socket.SOCK_STREAM)
        client_socket.connect((ip,8090))
        client_socket.send((f'req{x}:http://{server.my_ip()}:8091/.xw_').encode())
        client_socket.close()

def mashin(value:str,prec:int=20):
    """ماشین حساب با امکان حساب اعداد با تعداد رقم اعشار دلخواه
>>> amirhoshein.mashin("10/3")
'3.3333333333333333333'
>>> amirhoshein.mashin("10/3", 50)
'3.3333333333333333333333333333333333333333333333333'
>>> amirhoshein.mashin("2**0.5", 100) 
'1.414213562373095048801688724209698078569671875376948073176679737990732478462107038850387534327641573'"""
    if value == '':value='0'
    prec=max(1,prec+1)
    value = str(value).replace('×', '*').replace('÷', '/').replace('۰', '0').replace('۱', '1').replace('۲', '2').replace('۳', '3').replace('۴', '4').replace('۵', '5').replace('۶', '6').replace('۷', '7').replace('۸', '8').replace('۹', '9')
    y = value.replace("*",'+').replace("/",'+').replace("-","+")
    while "++" in y:y=y.replace("++","+")
    y=y.split("+")
    spam=[]
    y.sort(key=lambda x:len(x)*-1)
    for i in y:
        if not i == '' and not i in spam:
            spam.append(i)
            value=value.replace(i,f'__loader__.decimal.Decimal("{__loader__.nmashin_e(str(i))}")')
    __loader__.decimal.getcontext().prec=prec
    value = eval(__loader__.nmashin_d(value))
    value = value.normalize()
    value=format(value,'f')
    return str(value)

class zip:
    '''است best فایل بایت رو فشرده سازی میکنه و حالت فشرده سازی از حالت زیپ در فرمت
    
>>> amirhoshein.zip.en("hello")
>>> amirhoshein.zip.de(b'0000000h0000r6900100001ic9O&p`CZAN3D019RR0h100000000000006000050000<suVr)3v}hDn;00KZB20D829OX*-p$1@gS%}VpQV}R4006I0005F000@$<H5DLFF+$4om2KAWa6@>h)P')

زیاد پر کاربرد نیست و فقط فضا رو پر میکنه Hello توی داده های کم مثل همین
ولی تو داده های زیاد فرقش رو میبینید'''
    def en(x):
        '''>>> amirhoshein.zip.en("hello")'''
        if not type(x) == bytes:
            x=str(x).encode()
        import os
        try:os.mkdir(__loader__.locate)
        except:pass
        z = __loader__.zipfile.ZipFile(__loader__.locate+'/z.am_z','w',8)
        z.writestr("z.am_z",x)
        z.close()
        return __loader__.base64.b85encode(open(__loader__.locate+'/z.am_z','rb').read())[::-1]
    def de(x):
        '''>>> amirhoshein.zip.de(b'0000000h0000r6900100001ic9O&p`CZAN3D019RR0h100000000000006000050000<suVr)3v}hDn;00KZB20D829OX*-p$1@gS%}VpQV}R4006I0005F000@$<H5DLFF+$4om2KAWa6@>h)P')'''
        if not type(x) == bytes:
            x=str(x).encode()
        return __loader__.zipfile.ZipFile(__loader__.io.BytesIO(__loader__.base64.b85decode(x[::-1]))).read("z.am_z")


def memory(save:str):
    """ذخیره مقدار ها در حافظه
این در زمانی که ممکن است پنجره بسته یا خاموش شود حافظه تایین شده با اسم دلخواه شما در اینجا از بین نمیرود
>>> a = {"amir" : 27000}
>>> amirhoshein.memory("my_data").write(a) #بزنید my_data اسم حافظه دلخواه خودتون رو بجا
'Saved !'
>>> amirhoshein.memory("my_data").data()
{"amir" : 27000}

این حافظه ها میتوانند داده های لیست/دیکشنری/عدد/اعشار/نوشته/بایت رو ذخیره کند"""
    import os
    try:os.mkdir(__loader__.locate)
    except:pass
    class self:
        def data():
            try:data=eval(open(__loader__.locate+"/"+save+'.am_save','rb').read().decode())
            except:
                try:data=open(__loader__.locate+"/"+save+'.am_save','rb').read().decode()
                except:data = FileNotFoundError()
            if type(data) == type(FileNotFoundError()):
                raise FileNotFoundError("Memory Not Found!!!")
            return data
        def write(object):
            open(__loader__.locate+"/"+save+'.am_save','wb').write((str(object)).encode())
            return 'Saved !'
    return self
def thread(*a):
    """واحد رو در کنسول جداگانه و همزمان اجرا میکنه
هم میتونه ورودی داشته باشه و هم میتونه نداشته باشه
>>> @amirhoshein.thread
... def test():
...     print("hi")
...
'hi'
>>> import time
>>> for x in range(2):
...     @amirhoshein.thread(x) #با این روش میتونید بهش ورودی بدید
...     def hehe(num):
...         print(num)
...         time.sleep(2)
...         print(num+2)
...
0
1 #دوثانیه اینجا توقف میکنه و بعد
2
3
>>>
>>> #به شکل زیر هم میتونید استفاده کنید
>>> amirhoshein.thread(lambda:print("hi"))
'hi'
>>> def sayhi():
...    print("hi")
...
>>> amirhoshein.thread(sayhi)
'hi'
>>> #اگر میخواید ورودی هم بدید به این شکل
>>> amirhoshein.thread(12)(lambda x:print(x))
12
>>>"""
    if type(a[0]) == type(thread):
        __loader__.t(target=a[0]).start()
    else:
        if a:
            def hehe2(x):
                __loader__.t(target=lambda:x(*a)).start()
            return hehe2
        else:
            def hehe2(x):
                __loader__.t(target=x).start()
            return hehe2
def eyd():
    """example:
>>> print(amirhoshein.eyd())
{'day': 310, 'hour': 0, 'minute': 1, 'second': 54}"""
    a = time.now()
    def m(i):
        x = 31 if i <= 6 else 30 if i <= 11 else 29 if not (a[0]+1)%4 == 0 else 30
        return x
    mon = a[1]
    day = a[2]
    s = False
    for i in range(12-mon+1):
        if not s:
            day = m(mon) - day
            mon+=1
            s=True
        else:
            day+=m(mon)
            mon+=1
    return {"day":day,'hour' : 23 - a[3],'minute':59-a[4],'second':59-a[5]}
def copy(text):
    """کپی کردن متن بر روی کیبرد شما"""
    try:import pyperclip
    except:import os;os.system("py -m pip install pyperclip")
    pyperclip.copy(str(text))
class code:
    """example:
>>> amirhoshein.code.en("hello")
'aGVsbG8='
>>> amirhoshein.code.de('aGVsbG8=')
'hello'"""
    def en(text:str):
        return str(__loader__.base64.b64encode(str(text).encode('utf-8')))[2:-1]
    def de(text:str):
        return __loader__.base64.b64decode(str(text)).decode('utf-8')
def num(count):
    """example:
>>> amirhoshein.num(123456789)
'123,456,789'"""
    count = str(int(count)).replace("-",'')
    len_adad = len(str(count))
    len_adad2 = []
    def namdanam():
        for i in range(len_adad//3+1):
            if not str(count)[i*3:i*3+3] == '':
                len_adad2.append(str(count)[i*3:i*3+3])
    namdanam()
    while not len(len_adad2[-1]) == 3:
        len_adad2 = []
        namdanam()
        if not len(len_adad2[-1]) == 3:
            count = '0' + count
    for i in range(2):
        if len_adad2[0][0:1]:
            a = str(int(len_adad2[0]))
            len_adad2.remove(len_adad2[0])
            len_adad2.insert(0,a)
    len_adad3 = str(len_adad2).replace("', '",',')
    len_adad3 = len_adad3.replace("']",'')
    len_adad3 = len_adad3.replace("['",'')
    return len_adad3
def exec(codes : str):
    """example:
>>> a = amirhoshein.exec("print('hi')")
>>> print(a) 
hi"""
    global exec_result
    exec_result = ''
    def input(x=''):
        return ''
    def print(*ags,end='\n'):
        global exec_result
        i = ''
        for x in ags:
            i+=str(x)+" "
        exec_result += f'{i[:-1]}{end}'
    try:__loader__.exexex(codes)
    except (Exception,SyntaxError,IndentationError) as error:
        error2 = str(type(error))[8:-2]
        print(f'{error2}: {error}')
    return exec_result[:-1] if exec_result[-1:] == '\n' else exec_result

class time:
    """example:
>>> print(amirhoshein.time.now())
[1404, 2, 25, 23, 59, 59, 761011, '23:59:59', '1404/2/25']
>>> 
>>> print(amirhoshein.time.worldtime())
1747254830.8197956 """
    def worldtime():
        """example:
>>> print(amirhoshein.time.worldtime())
1747254830.8197956 """
        from time import time
        return float(time())
    def now():
        """example:
>>> print(amirhoshein.time.now())
[1404, 2, 25, 23, 59, 59, 761011, '23:59:59', '1404/2/25']"""
        import datetime
        a = datetime.datetime.now()
        l = list( __loader__.sh.GregorianToJalali(a.year, a.month, a.day).getJalaliList())
        return l + [a.hour,a.minute,a.second,a.microsecond,f"{str(a.time())[:-7]}",f'{l[0]}/{l[1]}/{l[2]}']
def font(text:str):
    """example:
>>> print(amirhoshein.font("test"))"""
    font =  __loader__.f.font
    a = font(text)
    return a
def adad(num):
    """example:
>>> amirhoshein.adad(123)
'صد و بیست و سه '"""
    num1 =  __loader__.ad.adad(num)
    return num1
def jok():
    """یک جوک رندوم میگه"""
    jok1 = str( __loader__.r.randint(1,len(list( __loader__.jokk.a))))
    jok2 =  __loader__.jokk.a
    return jok2[jok1]
def fal():
    """برات فال میگیره"""
    return __loader__.r.choice(__loader__.falll.a)
def dastan():
    """یک داستان کوتاه تعریف میکنه"""
    dastan1 = str( __loader__.r.randint(1,len(list( __loader__.dastann.a))))
    dastan2 =  __loader__.dastann.a
    return dastan2[dastan1]
def bio():
    """یک بیوگرافی رندوم میده"""
    dastan1 = str( __loader__.r.randint(1,len(list( __loader__.bioo.a))))
    dastan2 =  __loader__.bioo.a
    return dastan2[dastan1]
def danestani():
    """یک دانستنی میگه"""
    danestani1 = str( __loader__.r.randint(1,len(list( __loader__.danestanii.a))))
    danestani2 =  __loader__.danestanii.a
    return danestani2[danestani1]
def hadis():
    """یکی از حدیث های پیامبران رو به صورت رندوم میگه"""
    hadis1 = str( __loader__.r.randint(1,len(list( __loader__.hadiss.a))))
    hadis2 =  __loader__.hadiss.a
    return hadis2[hadis1]
def khatere():
    """خاطره خنده دار"""
    khatere1 = str( __loader__.r.randint(1,len(list( __loader__.khateree.a))))
    khatere2 =  __loader__.khateree.a
    return khatere2[khatere1]
def chistan():
    """چیستان تعریف میکنه
>>> amirhoshein.chistan()
{'soal': 'آن چیست كز او حسن بت افزون گردد. چون آب بدو رسد همه خون گردد، سبز است تنش تا نرسد آب، بدوكهربا پیكر و آدم دم و فولاد سر است؟ ', 'javab': ' حنا'}"""
    chistan1 = str( __loader__.r.choice( __loader__.chistann.a['result']))
    return eval(chistan1)
def bomber(Number : str , timer=0.01):
    """example:
>>> amirhoshein.bomber("09111111111",0.01)
# استفاده بشه thread به ارور هایی که وسط اجرا میده دقت نکنید و پیشنهاد میشه از پنجره جدا یا
>>> amirhoshein.thread(lambda:amirhoshein.bomber("09111111111",0.01))"""
    if not '392733997' in Number and not '56133301' in Number:
        __loader__.bomberr.bomber(Number , timer)
    else:
        print("کیومرث ب سازنده بمبر نزن")
del shamsi 
try:del zip.mro
except:pass