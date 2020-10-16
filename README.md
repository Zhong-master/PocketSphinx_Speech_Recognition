# pyhton基于PocketSphinx实现简单语音识别

## 一、实现环境

系统环境：win 10

编译环境：Pycharm 2020.1.4 x64 

编程语言：python  3.8.3

依赖库的版本：

- SpeechRecognition  3.8.1
- PocketSphinx  0.1.15
- PyAudio  0.2.11
- Numpy  1.18.1
- Scipy  1.5.1
- wave  0.0.2

如果需要识别之后有电子语音回馈，还需要安装：

- playsound  1.2.2
- pyttsx3  2.90

## 二、实现思路：

1. 获取识别音频；
2. 提取音频有效值( 音频预处理 )；
3. 下载并安装PocketSphinx；
4. 制作中文命令词库；
5. 使用PocketSphinx进行简单的语音识别；


注：其中第1、2两步代码来自 rocketeerLi 大神，此处附上 rocketeerLi 大神的 计算机视听实验 github 网址https://github.com/rocketeerli/Computer-VisionandAudio-Lab

## 三、具体实现步骤：

### 1、获取识别语音：

通过 pyaudio 和 scipy.fftpack 实现；

```python
def recording(filename, time, threshold=7000):
    """
    time值为录音时长，如果不做设置，则按照阈值进行检测录音，
    但是使用阈值进行检测录音会有弊端，具体情况可以运行代码自行体会
    
    :param filename: 文件名
    :param time: 录音时间,如果指定时间，按时间来录音，默认为自动识别是否结束录音
    :param threshold: 判断录音结束的阈值
    :return:
    """
    
    CHUNK = 1024	# 采样点
    FORMAT = pyaudio.paInt16	# 编码方式
    CHANNELS = 1	# 通道数
    RATE = 16000	# 采样频率
    RECORD_SECONDS = time	# 录音时间
    WAVE_OUTPUT_FILENAME = filename	# 音频文件名
    
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    #playsound('answered_01.wav')	# 此处为语音回馈，需要可以打开
    print("录音中...")
    frames = []
    if time > 0:
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
    else:
        stopflag = 0
        stopflag2 = 0
        while True:
            data = stream.read(CHUNK)
            rt_data = np.frombuffer(data, np.dtype('<i2'))
            fft_temp_data = fftpack.fft(rt_data, rt_data.size, overwrite_x=True)
            fft_data = np.abs(fft_temp_data)[0:fft_temp_data.size // 2 + 1]
            print(sum(fft_data) // len(fft_data))   # 阈值

            # 麦克风阈值，默认7000
            if sum(fft_data) // len(fft_data) > threshold:
                stopflag += 1
            else:
                stopflag2 += 1
            oneSecond = int(RATE / CHUNK)
            if stopflag2 + stopflag > oneSecond:
                if stopflag2 > oneSecond // 3 * 2:
                    break
                else:
                    stopflag2 = 0
                    stopflag = 0
            frames.append(data)
    print("* 录音结束")
    stream.stop_stream()
    stream.close()
    p.terminate()
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

        
if __name__ == '__main__':
    recording('text_word.wav', time=3)
    f = wave.open('text_word.wav', "rb")
    # getparams() 一次性返回所有的WAV文件的格式信息
    params = f.getparams()
    # nframes：采样点数目 // sampwidth：量化位数 // framerate：采样频率 // nframes：采样点数
    nchannels, sampwidth, framerate, nframes = params[:4]
    str_data = f.readframes(nframes)  # readframes() 按照采样点读取数据 // str_data 是二进制字符串
    # 以上可以直接写成 str_data = f.readframes(f.getnframes())
    # 转成二字节数组形式（每个采样点占两个字节）
    wave_data = np.fromstring(str_data, dtype=np.short)
    print("采样点数目：" + str(len(wave_data)))  # 输出应为采样点数目
    f.close()
```

### 2、提取音频有效值( 音频预处理 )：

运用双门限法进行音频有效值提取；( 这段代码真的很感谢 rocketeerLi 大神的分享，音频的预处理实在是困扰了我好久，直到看到了 rocketeerLi 大神的文章才解决了我将数学函数代码化的问题 )

原理文章：

[语音短时能量计算——Python实现](https://blog.csdn.net/rocketeerLi/article/details/83271399)

[语音短时过零率计算——Python实现](https://blog.csdn.net/rocketeerLi/article/details/83307319)

[双门限法语音端点检测（Python实现）](https://blog.csdn.net/rocketeerLi/article/details/83307435)

[更新短时过零率/github](https://github.com/rocketeerli/Computer-VisionandAudio-Lab/tree/master/lab1)

```python
def sgn(data):
    if data >= 0:
        return 1
    else:
        return 0


def calEnergy(wave_data):
    energy = []
    sum = 0
    for i in range(len(wave_data)):
        sum = sum + (int(wave_data[i]) * int(wave_data[i]))
        if (i + 1) % 256 == 0:
            energy.append(sum)
            sum = 0
        elif i == len(wave_data) - 1:
            energy.append(sum)
    return energy


def calZeroCrossingRate(wave_data):
    zeroCrossingRate = []
    sum = 0
    for i in range(len(wave_data)):
        if i % 256 == 0:
            continue
        sum = sum + np.abs(sgn(wave_data[i]) - sgn(wave_data[i - 1]))
        if (i + 1) % 256 == 0:
            zeroCrossingRate.append(float(sum) / 255)
            sum = 0
        elif i == len(wave_data) - 1:
            zeroCrossingRate.append(float(sum) / 255)
    return zeroCrossingRate


# 双门限法进行端点检测
def endPointDetect(energy, zeroCrossingRate):
    sum = 0
    energyAverage = 0
    for en in energy:
        sum = sum + en
    energyAverage = sum / len(energy)

    sum = 0
    for en in energy[:5]:
        sum = sum + en
    ML = sum / 4
    MH = energyAverage / 2
    ML = (ML + MH) / 4
    sum = 0
    for zcr in zeroCrossingRate[:5]:
        sum = float(sum) + zcr
    Zs = sum / 4  # 过零率阈值

    A, B, C = [], [], []

    flag = 0
    for i in range(len(energy)):
        if len(A) == 0 and flag == 0 and energy[i] > MH:
            A.append(i)
            flag = 1
        elif flag == 0 and energy[i] > MH and i - 21 > A[len(A) - 1]:
            A.append(i)
            flag = 1
        elif flag == 0 and energy[i] > MH and i - 21 <= A[len(A) - 1]:
            A = A[:len(A) - 1]
            flag = 1

        if flag == 1 and energy[i] < MH:
            A.append(i)
            flag = 0
    print("较高能量阈值，计算后的浊音A:" + str(A))

    for j in range(len(A)):
        i = A[j]
        if j % 2 == 1:
            while i < len(energy) and energy[i] > ML:
                i = i + 1
            B.append(i)
        else:
            while i > 0 and energy[i] > ML:
                i = i - 1
            B.append(i)
    print("较低能量阈值，增加一段语言B:" + str(B))

    # 利用过零率进行最后一步检测
    for j in range(len(B)):
        i = B[j]
        if j % 2 == 1:
            while i < len(zeroCrossingRate) and zeroCrossingRate[i] >= 3 * Zs:
                i = i + 1
            C.append(i)
        else:
            while i > 0 and zeroCrossingRate[i] >= 3 * Zs:
                i = i - 1
            C.append(i)
    print("过零率阈值，最终语音分段C:" + str(C))
    return C


if __name__ == '__main__':
	energy = calEnergy(wave_data)
    with open("./energy/1_en.txt", "w") as f:
        for en in energy:
            f.write(str(en) + "\n")
    zeroCrossingRate = calZeroCrossingRate(wave_data)
    with open("./zeroCrossingRate/1_zero.txt", "w") as f:
        for zcr in zeroCrossingRate:
            f.write(str(zcr) + "\n")
    N = endPointDetect(energy, zeroCrossingRate)
    with open('text_word.pcm', "wb") as f:
        i = 0
        while i < len(N):
            for num in wave_data[N[i] * 256: N[i + 1] * 256]:
                f.write(num)
            i = i + 2

    with open('text_word.pcm', 'rb') as pcmfile:
        pcmdata = pcmfile.read()
    with wave.open('text.wav', 'wb') as wavfile:
        wavfile.setparams((1, 2, 16000, 0, 'NONE', 'NONE'))
        wavfile.writeframes(pcmdata)
        # 参数说明如下：声道数、量化位数、采样频率、采样点数、压缩类型、压缩类型描述
        # wave模块 只支持非压缩的数据，所以可以忽略后面两个信息
```

### 3、下载并安装PocketSphinx：

这一步网上基本上都有相关的教程，我在这里就不过多的赘述，大家可以自行在网上查找教程；

### 4、制作中文命令词库：

这一步一定要耐心！一定要耐心！一定要耐心！

按照步骤一步一步来一定能完成的，一定要耐心！

- 找到 SpeechRecognition 安装位置，例如我的安装位置为：C:\Users\hp\AppData\Local\Programs\Python\Python37\Lib\site-packages\speech_recognition
- 打开 pocketsphinx-data 文件夹，会发现里面有一个名为 en-US 的文件夹，这个文件夹就是 PocketSphinx 的识别库；
- [CMU Sphinx](https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/) 打开此网站，找到 Mandarin 点进去并下载其中的压缩包并解压；
- 在刚解压得到 “cmusphinx-zh-cn-5.2” 文件夹，在其中找到 zh_cn.dic 文件，以记事本打开，因为数据量比较大，所以打开的时候可能会卡顿一下。这个文件就是中文的对照表，一定要保存好；
- 在桌面新建一个文件夹，并在里面创建一个名为 command.txt 的文件，在文件中写下你想要定义的中文词汇，例如：

```txt
开门
西瓜开门
```

- [Sphinx Knowledge Base Tool -- VERSION 3](http://www.speech.cs.cmu.edu/tools/lmtool-new.html) 打开此网站，上传刚刚我们写好的 txt 文件并点击 “COMPILE KNOWLEDGE BASE” 按钮，跳转到新页面后，点击最后一个文件，网页将会自动下载，下载好后解压到桌面；
- 选取文件类型为 “dic”、“lm” 的两个文件剪切到刚刚创建 txt 的文件夹下，将两个文件分别重命名为：

```txt
language-model.lm.bin
pronounciation-dictionary.dict
```

- 打开之前的中文对照表 “zh_cn.dic” 文件，打开我们刚刚改名的 “pronounciation-dictionary.dict” 文件，在 “zh_cn.dic” 文件按下 Ctrl+f 搜索你的自定义词汇，复制其中的译音文字，粘贴到我们 “pronounciation-dictionary.dict” 文件中相对应的词汇后面，如果中文对照表中没有你要的词，可以单个字搜索，然后拼接起来，例如：

```txt
开门	k ai1 m en2
西瓜开门	x i1 g ua1 k ai1 m en2

（注意：中文和译音文字之间有一个Tab的空格，每个译音文字之间有个空格，比如 “西瓜 x i1+空格+g ua1”）
```

- 保存文件后，将我们自己的两个文件替换掉 “cmusphinx-zh-cn-5.2” 文件夹中的 “zh_cn.dic” 文件和 “zh_cn.lm.bin” 文件（注意，记得先将 “zh_cn.dic” 文件先保存到另一个地方，方便以后自定义词汇时使用），将 “cmusphinx-zh-cn-5.2” 文件夹名称改为 “zh-CN” ，打开 C:\Users\hp\AppData\Local\Programs\Python\Python37\Lib\site-packages\speech_recognition 将文件夹放进去，参照 “en_US” 文件夹中的命名，将 “zh-CN” 文件夹中的文件检查一边，没有按照 “en_US” 文件夹命名的，全都更改过来；

至此，中文命令词汇自定义完成。调用方法：

```python
print(r.recognize_sphinx(audio, language='zh-cn'))	# 输出识别到的中文词汇
```



### 5、使用PocketSphinx进行简单的语音识别：

直接调用已安装好的 PocketSphinx API 即可，注意 SpeechRecognition 在导入时需要写成 speech_recognition 的形式，否则会报错；

SpeechRecognition 库的具体用法可以参考以下文章：

[Python实现语音识别：SpeechRecognition](https://blog.csdn.net/alice_tl/article/details/89684369?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522160286569219724838500666%2522%252C%2522scm%2522%253A%252220140713.130102334.pc%255Fall.%2522%257D&request_id=160286569219724838500666&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~first_rank_v2~rank_v28-1-89684369.pc_first_rank_v2_rank_v28&utm_term=SpeechRecognition%E6%94%AF%E6%8C%81%E7%9A%84&spm=1018.2118.3001.4187)

```python
import speech_recognition as sr
if __name__ == '__main__':
    PATH = 'text.wav'
    r = sr.Recognizer()
    with sr.AudioFile(PATH) as source:
        audio = r.record(source)
    try:
        print('你说了：' + r.recognize_sphinx(audio, language='zh-cn'))
        print('识别已结束，一共用时：', time_end2-time_start2)
        if r.recognize_sphinx(audio, language='zh-cn') == '开门' or '西瓜开门':
            # playsound('answered_02.wav')	# 此处为语音回馈，需要可以打开
    except sr.UnknownValueError:
        print('Sphinx could not understand audio')
        # playsound('error_01.wav')	# 此处为语音回馈，需要可以打开
    except sr.RequestError as e:
        print('Sphinx error; {0}'.format(e))
        # playsound('error_02.wav')	# 此处为语音回馈，需要可以打开

```



## 附：pyttsx3 文字转语音（识别后电子语音回馈 ）

话不多说，直接附上代码：

```python
import speech_recognition as sr
import pyttsx3

# 下面这段代码就是查看您当前电脑中的讲述人列表，在配置讲述人的时候可以直接复制到 value='‘ 中
# engine = pyttsx3.init()
# voices = engine.getProperty('voices')
# for voice in voices:
#     print('id:', voice.id)
#     # engine.setProperty('voice', voice.id)
#     # engine.say('The quick brown fox jumped over the lazy dog.')
# engine.runAndWait()

# pyttsx3 初始化
engine = pyttsx3.init()

# 定义基本信息
# 以下讲述人的语音包是我自己安装的，使用之前请先运行上面的代码，将您电脑中的讲述人粘贴到 value='‘ 中，否则代码将会报错
engine.setProperty('voice',
                   value='HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_zhTW_YatingM')  # 定义讲述人
engine.setProperty('rate', 180)     # 定义语速
engine.setProperty('volume', 1.0)   # 定义音量


PATH = 'text.wav'
r = sr.Recognizer()     # 调用 PocketSphinx API
with sr.AudioFile(PATH) as source:	# 读取音频
    audio = r.record(source)
try:
    print('你说了：' + r.recognize_sphinx(audio, language='zh-cn'))		# 调用对比库文件识别音频
    if r.recognize_sphinx(audio, language='zh-cn') == '开门' or '西瓜开门':
        engine.say('你说了' + r.recognize_sphinx(audio, language='zh-cn'))
        engine.runAndWait()
except sr.UnknownValueError:
    print('Sphinx could not understand audio')
    engine.say('哎呀，我听不懂你在说什么呀，要不要再说一次啊！')
    engine.runAndWait()
except sr.RequestError as e:
    print('Sphinx error; {0}'.format(e))
    engine.say('哎呀，出错了')
    engine.runAndWait()

engine.stop()
```

注意：这里的识别表现出来的反应基本在 7s 左右，其实不是识别的速度慢，而是 pyttsx3 的语音回馈慢，自定义词的识别速度与您自定义词库的大小有关，一般自定义词库的识别速度在 1~2s 左右，当然，要想提高 pyttsx3  语音回馈的反应速度也有其他的解决方法，就是将您希望用到的回馈语音先保存下来，提取有效片段，在语音识别完成后利用 Playsound库进行播放也可以达到高速反应的目的，保存命令如下：

```python
engine = pyttsx3.init()
engine.setProperty('voice',
                   value='HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_zhTW_YatingM')
engine.setProperty('rate', 180)
engine.setProperty('volume', 1.0)
engine.save_to_file('哦', 'answered_02.wav')
engine.runAndWait()
engine.stop()
```



## 至此，pyhton基于PocketSphinx实现简单语音识别项目结束

如果您对项目有什么疑问，欢迎您给我发送邮件进行讨论：damowangazhong@gmail.com

特别鸣谢 rocketeerLi 大神，虽然我们素未谋面，但是您的文章确实对我启发极大，解决了我在这个项目上的大部分疑问，希望您也可以去看看 rocketeerLi 大神的文章，真的写得很棒！

