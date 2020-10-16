import speech_recognition as sr
import pyttsx3

'''

音源
id: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ZH-CN_HUIHUI_11.0
id: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_zhTW_YatingM
id: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0
id: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0
id: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_zhHK_DannyM
id: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ZH-HK_TRACY_11.0
id: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ZH-TW_HANHAN_11.0

'''

# 下面这段代码就是查看你当前电脑中的讲述人列表，在配置讲述人的时候可以直接复制到 value='‘ 中
# engine = pyttsx3.init()
# voices = engine.getProperty('voices')
# for voice in voices:
#     print('id:', voice.id)
#     # engine.setProperty('voice', voice.id)
#     # engine.say('The quick brown fox jumped over the lazy dog.')
# engine.runAndWait()

# 下面这段代码是保存pyttsx3语音的
engine = pyttsx3.init()   # 初始化
engine.setProperty('voice', value='HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_zhTW_YatingM')
engine.setProperty('rate', 220)
engine.setProperty('volume', 1.0)
# engine.say('有什么可以帮到你的？听到一声，滴，之后在三秒内告诉我！')
engine.save_to_file('听不懂你说啥', './ans_voice/error_01.wav')
engine.runAndWait()


# pyttsx3 初始化
engine = pyttsx3.init()

# 定义基本信息
# 以下讲述人的语音包是我自己安装的，使用之前请先运行上面的代码，将您电脑中的讲述人粘贴到 value='‘ 中，否则代码将会报错
# engine.setProperty('voice',
#                    value='HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_zhTW_YatingM')  # 定义讲述人
# engine.setProperty('rate', 180)     # 定义语速
# engine.setProperty('volume', 1.0)   # 定义音量
#
#
# PATH = 'text.wav'
# r = sr.Recognizer()     # 调用 PocketSphinx API
# with sr.AudioFile(PATH) as source:
#     audio = r.record(source)
# try:
#     print('你说了：' + r.recognize_sphinx(audio, language='zh-cn'))
#     if r.recognize_sphinx(audio, language='zh-cn') == '开门' or '西瓜开门':
#         engine.say('你说了' + r.recognize_sphinx(audio, language='zh-cn'))
#         engine.runAndWait()
# except sr.UnknownValueError:
#     print('Sphinx could not understand audio')
#     engine.say('哎呀，我听不懂你在说什么呀，要不要再说一次啊！')
#     engine.runAndWait()
# except sr.RequestError as e:
#     print('Sphinx error; {0}'.format(e))
#     engine.say('哎呀，出错了')
#     engine.runAndWait()
#
# engine.stop()
