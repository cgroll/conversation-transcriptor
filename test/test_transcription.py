import os
from dotenv import load_dotenv
from convscript.path import ProjPaths
from convscript.conversation_transcription import url_to_transcript


def test_url_transcription():
    
    test_url = 'https://chtbl.com/track/736CG3/pdst.fm/e/stitcher.simplecastaudio.com/2be48404-a43c-4fa8-a32c-760a3216272e/episodes/413d1340-d75e-46ae-956c-3785e2b359b2/audio/128/default.mp3?aid=rss_feed&amp;awCollectionId=2be48404-a43c-4fa8-a32c-760a3216272e&amp;awEpisodeId=413d1340-d75e-46ae-956c-3785e2b359b2&amp;feed=Y8lFbOT4'
    
    dotenv_path = ProjPaths.env_variables_path
    load_dotenv(dotenv_path)
    pyannote_token = os.environ.get('PYANNOTE_ACCESS_TOKEN')
    
    output_str = url_to_transcript(test_url, 'base', pyannote_token)
    
    print(output_str)
    
if __name__ == '__main__':
    
    test_url_transcription()

    
    
    
    