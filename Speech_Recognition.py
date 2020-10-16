import pyttsx3
import speech_recognition as sr
import time
import wave
import pyaudio
import numpy as np
from scipy import fftpack
from playsound import playsound


def recording(filename, time, threshold=7000):
    """
    :param filename: 文件名
    :param time: 录音时间,如果指定时间，按时间来录音，默认为自动识别是否结束录音
    :param threshold: 判断录音结束的阈值
    :return:
    """
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = time
    WAVE_OUTPUT_FILENAME = filename
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    playsound('./ans_voice/answered_01.wav')
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
    time_start1 = time.time()

    recording('./Rec_voice/text_word.wav', time=3)
    f = wave.open('./Rec_voice/text_word.wav', "rb")
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

    energy = calEnergy(wave_data)
    with open("./energy/en.txt", "w") as f:
        for en in energy:
            f.write(str(en) + "\n")
    zeroCrossingRate = calZeroCrossingRate(wave_data)
    with open("./zeroCrossingRate/zero.txt", "w") as f:
        for zcr in zeroCrossingRate:
            f.write(str(zcr) + "\n")
    N = endPointDetect(energy, zeroCrossingRate)
    with open('./Rec_voice/text_word.pcm', "wb") as f:
        i = 0
        while i < len(N):
            for num in wave_data[N[i] * 256: N[i + 1] * 256]:
                f.write(num)
            i = i + 2

    with open('./Rec_voice/text_word.pcm', 'rb') as pcmfile:
        pcmdata = pcmfile.read()
    with wave.open('./Rec_voice/text.wav', 'wb') as wavfile:
        wavfile.setparams((1, 2, 16000, 0, 'NONE', 'NONE'))
        wavfile.writeframes(pcmdata)
        # 参数说明如下：声道数、量化位数、采样频率、采样点数、压缩类型、压缩类型描述
        # wave模块 只支持非压缩的数据，所以可以忽略后面两个信息
    time_end1 = time.time()
    print('音频采集已结束，一共用时：', time_end1-time_start1)

    time_start2 = time.time()
    PATH = './Rec_voice/text.wav'
    r = sr.Recognizer()
    with sr.AudioFile(PATH) as source:
        audio = r.record(source)
    try:
        c = r.recognize_sphinx(audio, language='zh-cn')
        time_end2 = time.time()
        print('识别已结束，一共用时：', time_end2 - time_start2)
        if c == '':
            playsound('./ans_voice/error_01.wav')
        else:
            print('你说了：' + c)
            if r.recognize_sphinx(audio, language='zh-cn') == '开门' or '西瓜开门':
                playsound('./ans_voice/answered_02.wav')
    except sr.UnknownValueError:
        print('Sphinx could not understand audio')
        playsound('./ans_voice/error_01.wav')
    except sr.RequestError as e:
        print('Sphinx error; {0}'.format(e))
        playsound('./ans_voice/error_02.wav')







