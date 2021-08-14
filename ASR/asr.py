import time

import numpy
import pyaudio
import deepspeech

# https://github.com/mozilla/DeepSpeech-examples/tree/r0.9/mic_vad_streaming
# load pretrained model
ds = deepspeech.Model('model/deepspeech-0.9.3-models.pbmm')
ds.enableExternalScorer('model/deepspeech-0.9.3-models.scorer')

SAMPLE_RATE = 16000
# duration of signal frame, seconds
FRAME_LEN = 1.0
# number of audio channels (expect mono signal)
CHANNELS = 1

CHUNK_SIZE = int(FRAME_LEN * SAMPLE_RATE)

crnt_sentence = ""
stt = ""

p = pyaudio.PyAudio()
fullsignal = numpy.array([], dtype=numpy.int16)
crnt_signal = numpy.array([], dtype=numpy.int16)
context = ds.createStream()
empty = 0


def callback(in_data, frame_count, time_info, status):
    global empty, crnt_sentence, stt, fullsignal, crnt_signal
    signal = numpy.frombuffer(in_data, dtype=numpy.int16)
    crnt_signal = numpy.append(crnt_signal, signal)
    transcription = ds.stt(signal)
    # context.feedAudioContent(signal)
    # print('Intermidate: ' + context.intermediateDecode())
    if len(transcription):
        print(transcription, end=' ')
        stt += transcription
        crnt_sentence += transcription
        empty = 5
    elif len(transcription) == 0:
        if empty != 0:
            empty -= 1
            if empty == 1:
                print('.', end='\n')
                # NLP here
                stt += '.\n'
                crnt_sentence = ""
                # print('Final prediction: ' + ds.stt(crnt_signal))
                fullsignal = numpy.append(fullsignal, crnt_signal)
                crnt_signal = numpy.array([], dtype=numpy.int16)
                empty = 0
    return (in_data, pyaudio.paContinue)


stream = p.open(format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                stream_callback=callback,
                frames_per_buffer=CHUNK_SIZE)

print('Listening...')

stream.start_stream()

# Interrupt kernel and then speak for a few more words to exit the pyaudio loop !
try:
    while stream.is_active():
        time.sleep(0.1)
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()

    print()
    print("PyAudio stopped")
    print(stt)
    print('Final prediction: ' + ds.stt(fullsignal))
