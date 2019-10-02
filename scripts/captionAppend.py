import requests,json
import pandas as pd
import re 
from translate import Translator
from langdetect import detect
"""
This script is for Caption, so append the text or append and translate the text of each video.
For use it you have to have Translate, langdetec
    pip install translate
    pip install langdetect
So you take the json File that normally you can easily download from pytheas and put it and run the code.
Have two function just Append the caption or Translate and Append the captions
Autor: Bertha Brenes
"""
#################################################################################################################""
###Append Function
def AppendCaption(EntryFile,OutputFile):
    data = json.load(EntryFile)
    lst = []
    print(len(data))
    for i in range(len(data)):
        text = ''
        if(data[i]['captions']):
            for j in range(len(data[i]['captions'])):
                caption = data[i]['captions'][j]['text']
                regex = re.search('(\[[a-zA-Z])',caption)
                print(regex)
                if(regex):
                    print('There is a sound or action')
                else: 
                    text+=str(caption)
                    text+=' '
            print(text)
            results_json = {
            'query_id':data[i]['query_id'],
            'videoId':data[i]['videoId'],
            'text': text
            }
            lst.append(results_json)
            
        else:
            print('There is no captions')
    json.dump(lst,OutputFile,sort_keys=True, indent=4, separators=(',', ': '))

#################################################################################################################""
####Translate and Append Function
def AppendTranslate(EntryFile,OutputFile,Lang):
    data = json.load(EntryFile)
    lst = []
    print(len(data))
    for i in range(len(data)):
        text = ''
        if(data[i]['captions']):
            for j in range(len(data[i]['captions'])):
                caption = data[i]['captions'][j]['text']
                regex = re.search('(\[[a-zA-Z])',caption)
                if(regex):
                    print('There is a sound')
                else: 
                    print(type(caption))
                    print(caption)
                    src = 'en'
                    try:
                        src = detect(caption)
                        print(src)
                    except:
                        pass
                    translator= Translator(to_lang=Lang,from_lang=src)
                    translation = translator.translate(caption)
                    print(translation)
                    text+=str(caption)
                    text+=' '
            print(text)
            results_json = {
            'query_id':data[i]['query_id'],
            'videoId':data[i]['videoId'],
            'text': text,
            'translatedText': translation
            }
            lst.append(results_json)
        
        else:
            print('There is no captions')

    json.dump(lst,OutputFile,sort_keys=True, indent=4, separators=(',', ': '))
        
            
#################################################################################################################""
with open('<PATH JSON>') as file:
    with open('<PATH JSON>','w') as output:
        AppendTranslate(file,output,'en') 