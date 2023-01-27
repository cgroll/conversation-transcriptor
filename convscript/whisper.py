import whisper
import pandas as pd

def whisper_inference(filename, model_type='base', 
                      verbose=False):
    
    model = whisper.load_model(model_type)
    result = model.transcribe(filename, 
                              verbose=verbose)

    return result

def whisper_inference_with_segments_df(fname, model_type='base'):
    
    result = whisper_inference(fname, model_type=model_type)

    all_seg_df_list = []
    
    for this_seg in result['segments']:
        if 'tokens' in this_seg.keys():
            this_seg.pop('tokens')

        this_df = pd.DataFrame.from_dict({0: this_seg}, 
                                        orient='index')
        
        all_seg_df_list.append(this_df)
        
    all_seg_df = pd.concat(all_seg_df_list, axis=0)
    all_seg_df = all_seg_df.set_index('id')
    
    return all_seg_df


if __name__ == '__main__':

    model_type = 'base'
    filename = 'freakonomics_short.wav'

    output_text = whisper_inference(filename, model_type='base')
    print(output_text)
    
    seg_df = whisper_inference_with_segments_df(filename)

