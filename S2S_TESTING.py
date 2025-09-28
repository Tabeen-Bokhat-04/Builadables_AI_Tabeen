import webrtcvad
import pyaudio
import wave
import whisper
from groq import Groq
import edge_tts
import asyncio
import os
from dotenv import load_dotenv
from pydub import AudioSegment
from pydub.playback import play


from pydub.playback import play

load_dotenv("D://VS Python//S2S TESTING//env")
#print("GROQ_API_KEY loaded:", os.getenv("GROQ_API_KEY"))

FORMAT, CHANNELS, RATE, CHUNK, VAD_MODE = pyaudio.paInt16, 1, 16000, 480, 2


def record_audio():
    import sys
    filename = "input.wav"
    
    if os.path.exists(filename):
        os.remove(filename)

    vad = webrtcvad.Vad(VAD_MODE)
    pa = pyaudio.PyAudio()
    stream = pa.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames = []
    silence_counter = 0
    silence_seconds = 2
    silence_threshold = int(silence_seconds * RATE / CHUNK)  
    min_speech_chunks = 10

    print("Recording... (Ctrl+C to stop)")
    sys.stdout.flush()

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        is_speech = vad.is_speech(data, RATE)
        
        print('.', end='', flush=True)

        if is_speech:
            frames.append(data)
            silence_counter = 0
        else:
            if len(frames) >= min_speech_chunks:
                silence_counter += 1
                if silence_counter >= silence_threshold:
                    print("\nSilence detected. Saving file...")
                    break

    stream.stop_stream()
    stream.close()
    pa.terminate()
    
    filename = "input.wav"
    wf = wave.open(filename, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(pa.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
 
    return filename



def transcribe(audio_file):
    model = whisper.load_model("base")
    result = model.transcribe(audio_file, language = "en")
    return result["text"]
    #return model.transcribe(audio_file, language="en")["text"]


def generate_response(text):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    chat = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {"role":"system","content":"You are a Helpful AI assistant. Reply only in simple and clear English."},
            {"role":"user","content":text}
        ]
    )
    return chat.choices[0].message.content

async def tts(text):
    out = "output.mp3"
    await edge_tts.Communicate(text, "en-US-AriaNeural").save(out)
    return out


def play_audio(file):
    try:
        if os.path.exists(file):
            audio = AudioSegment.from_mp3(file)
            play(audio)
    except Exception as e:
        print(f"Play error: {e}")



def main():
    while True:
        audio_file = record_audio()
        text = transcribe(audio_file)
        print("You:", text)
        if any(w in text.lower() for w in ["goodbye", "exit", "quit","Thanks","ThankYou"]):
            break
        reply = generate_response(text)
        print("Bot:", reply)
        mp3_file = asyncio.run(tts(reply))
        play_audio(mp3_file)
    print("Goodbye!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nRecording stopped by user. Goodbye!")