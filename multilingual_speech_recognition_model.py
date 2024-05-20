# -*- coding: utf-8 -*-
"""Multilingual Speech Recognition Model.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1eVuG37_zSz5f26QB0h6n6JL7W8EKzcbg
"""

!pip install transformers torch librosa moviepy

!pip install datasets

!pip install datasets faiss

!pip install faiss-cpu

import torch
import librosa
from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer, BartForConditionalGeneration, BartTokenizer
import moviepy.editor as mp

wav2vec_tokenizer = Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-large-960h")
wav2vec_model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")

bart_tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
bart_model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")

def transcribe_audio(file_path):

    speech, rate = librosa.load(file_path, sr=16000)

    input_values = wav2vec_tokenizer(speech, return_tensors="pt").input_values

    with torch.no_grad():
        logits = wav2vec_model(input_values).logits

    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = wav2vec_tokenizer.decode(predicted_ids[0])

    return transcription

def generate_response(input_text, task="summarize"):

    inputs = bart_tokenizer([input_text], max_length=1024, return_tensors="pt", truncation=True)

    if task == "translate":
        summary_ids = bart_model.generate(inputs["input_ids"], num_beams=4, max_length=50, early_stopping=True)
    else:

        summary_ids = bart_model.generate(inputs["input_ids"], num_beams=4, max_length=150, early_stopping=True)

    response = bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return response

def extract_audio(video_path, audio_output_path="extracted_audio.wav"):

    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_output_path)
    return audio_output_path

def process_file(file_path):

    if file_path.endswith(('.mp4', '.mkv', '.avi')):
        audio_path = extract_audio(file_path)
    else:
        audio_path = file_path

    transcription = transcribe_audio(audio_path)
    translation = generate_response(transcription, task="translate")
    summary = generate_response(transcription, task="summarize")

    return transcription, translation, summary

if __name__ == "__main__":
    file_path = "/content/1714121853870.mp4"

    transcription, translation, summary = process_file(file_path)

    print("Transcription:", transcription)
    print("Translation:", translation)
    print("Summary:", summary)

