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


### 2、提取音频有效值( 音频预处理 )：

运用双门限法进行音频有效值提取；( 这段代码真的很感谢 rocketeerLi 大神的分享，音频的预处理实在是困扰了我好久，直到看到了 rocketeerLi 大神的文章才解决了我将数学函数代码化的问题 )

原理文章：

[语音短时能量计算——Python实现](https://blog.csdn.net/rocketeerLi/article/details/83271399)

[语音短时过零率计算——Python实现](https://blog.csdn.net/rocketeerLi/article/details/83307319)

[双门限法语音端点检测（Python实现）](https://blog.csdn.net/rocketeerLi/article/details/83307435)

[更新短时过零率/github](https://github.com/rocketeerli/Computer-VisionandAudio-Lab/tree/master/lab1)


### 3、下载并安装PocketSphinx：

这一步网上基本上都有相关的教程，我在这里就不过多的赘述，大家可以自行在网上查找教程；

### 4、制作中文命令词库：

这一步一定要耐心！一定要耐心！一定要耐心！

按照步骤一步一步来一定能完成的，一定要耐心！

- 找到 SpeechRecognition 安装位置，例如我的安装位置为：C:\Users\hp\AppData\Local\Programs\Python\Python37\Lib\site-packages\speech_recognition
- 打开 pocketsphinx-data 文件夹，会发现里面有一个名为 en-US 的文件夹，这个文件夹就是 PocketSphinx 的识别库；
- [CMU Sphinx](https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/) 打开此网站，找到 Mandarin 点进去并下载其中的压缩包并解压；
- 解压并得到 “cmusphinx-zh-cn-5.2” 文件夹，在其中找到 zh_cn.dic 文件，以记事本打开，因为数据量比较大，所以打开的时候可能会卡顿一下。这个文件就是中文的对照表，一定要保存好；
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

注意：这里的识别表现出来的反应基本在 7s 左右，其实不是识别的速度慢，而是 pyttsx3 的语音回馈慢，自定义词的识别速度与您自定义词库的大小有关，一般自定义词库的识别速度在 1~2s 左右，当然，要想提高 pyttsx3  语音回馈的反应速度也有其他的解决方法，就是将您希望用到的回馈语音先保存下来，提取有效片段，在语音识别完成后利用 Playsound库进行播放也可以达到高速反应的目的，保存命令如下：


## 至此，pyhton基于PocketSphinx实现简单语音识别项目结束

如果您对项目有什么疑问，欢迎您给我发送邮件进行讨论：damowangazhong@gmail.com

特别鸣谢 rocketeerLi 大神，虽然我们素未谋面，但是您的文章确实对我启发极大，解决了我在这个项目上的大部分疑问，希望您也可以去看看 rocketeerLi 大神的文章，真的写得很棒！

