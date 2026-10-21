import pytest
import os.path
import os
from convscript.model_parakeet import parakeet_inference_df
from convscript.model_sortformer import sortformer_inference_df
from convscript.audio_utils import download_mp3, \
    transform_mp3_to_wav, crop_wav

@pytest.fixture(scope='session', autouse=True)
def test_download_transform_and_crop():
    
    test_url = 'https://chtbl.com/track/736CG3/pdst.fm/e/stitcher.simplecastaudio.com/2be48404-a43c-4fa8-a32c-760a3216272e/episodes/413d1340-d75e-46ae-956c-3785e2b359b2/audio/128/default.mp3?aid=rss_feed&amp;awCollectionId=2be48404-a43c-4fa8-a32c-760a3216272e&amp;awEpisodeId=413d1340-d75e-46ae-956c-3785e2b359b2&amp;feed=Y8lFbOT4'
    test_download_data_path = './test/data/freakonomics.mp3'
    test_wav_path = './test/data/tiny.wav'
    
    # cleanup before download
    if os.path.isfile(test_download_data_path):
        os.remove(test_download_data_path)
    
    mp3_fname = download_mp3(test_url, test_download_data_path)
    
    assert mp3_fname == test_download_data_path
    assert os.path.isfile(mp3_fname)
    
    wav_fname = transform_mp3_to_wav(mp3_fname)
    assert os.path.isfile(wav_fname)
    
    crop_wav(wav_fname, test_wav_path, start_frame=100000, n_frames=60000)
    
    yield test_wav_path
    
    os.remove(mp3_fname)
    os.remove(test_wav_path)
    

def test_parakeet(test_download_transform_and_crop):
    
    test_file_path = test_download_transform_and_crop
    
    text_df = parakeet_inference_df(test_file_path)
    print(text_df)
    
def test_sortformer(test_download_transform_and_crop):
    
    test_file_path = test_download_transform_and_crop
    
    speaker_df = sortformer_inference_df(test_file_path)
    print(speaker_df)
    
    
def wav_to_transcript(test_download_transform_and_crop):
    
    test_file_path = test_download_transform_and_crop

    output_str = wav_to_transcript(test_file_path)
    
    print(output_str)

    



if __name__ == '__main__':
    
    test_download_transform_and_crop()
    
    
    