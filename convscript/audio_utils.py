# %%
import requests
import tempfile
from pydub import AudioSegment

def record_to_wav(RECORD_SECONDS, WAVE_OUTPUT_FILENAME):

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100


    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


def download_mp3(audio_url, fname=None):

    # download
    doc = requests.get(audio_url)

    if fname:
        this_temp_file_name = fname
        with open(fname, 'wb') as f:
            f.write(doc.content)

    else:
        # create temp file
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        this_temp_file_name = temp_file.name

        # write to file
        temp_file.write(doc.content)

    return this_temp_file_name

def transform_mp3_to_wav(mp3_fname, output_fname=None):
        
    sound = AudioSegment.from_mp3(mp3_fname) # load source

    if output_fname:
        this_temp_file_name = output_fname
        sound.export(output_fname, format="wav")

    else:
        # create temp file
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        this_temp_file_name = temp_file.name

        sound.export(this_temp_file_name, format="wav")

    return this_temp_file_name

def crop_wav(fname, output_fname, start_frame=0, n_frames=60000):
    
    sound = AudioSegment.from_wav(fname)

    sound = sound.set_channels(1) # mono
    sound = sound.set_frame_rate(16000) # 16000Hz

    # Extract the first frames (60000 equals 60 seconds)
    excerpt = sound[start_frame:(start_frame + n_frames)]

    # write to disk
    excerpt.export(output_fname, format="wav")


# %%

if __name__ == '__main__':

    # %% Record audio wave file and save to disk
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "voice.wav"
    record_to_wav(RECORD_SECONDS, WAVE_OUTPUT_FILENAME)
    
    # %% Download mp3 podcast episode

    audio_url = 'https://chtbl.com/track/736CG3/pdst.fm/e/stitcher.simplecastaudio.com/2be48404-a43c-4fa8-a32c-760a3216272e/episodes/413d1340-d75e-46ae-956c-3785e2b359b2/audio/128/default.mp3?aid=rss_feed&amp;awCollectionId=2be48404-a43c-4fa8-a32c-760a3216272e&amp;awEpisodeId=413d1340-d75e-46ae-956c-3785e2b359b2&amp;feed=Y8lFbOT4'
    tmp_fname = download_mp3(audio_url, 'freakonomics.mp3')

    # %% Transform mp3 file to wave file
    
    mp3_fname = 'freakonomics.mp3'
    wav_fname = 'freakonomics.wav'
    transform_mp3_to_wav(mp3_fname, output_fname=wav_fname)
    
    # %% Crop wave file
    
    wav_output_fname = 'freakonomics_short.wav'
    crop_wav(wav_fname, wav_output_fname, start_frame=60000, n_frames=60000)




    