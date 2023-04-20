from youtube_transcript_api import YouTubeTranscriptApi
import requests,json,os,sys


openaiToken=os.environ.get('openaiToken')

if openaiToken is None:
    print("openaiToken Required as env var, syntax : export openaiToken='xxxx' ")
    raise SystemExit(2)

if (args_count := len(sys.argv)) < 2:
    print(f"Toggle Video expected as 1st argument \nsyntax : python ytsum.py <toggle>\nwhere toggle is the value of the v parameter in the youtube link\ne.g : https://www.youtube.com/watch?v=MpSvyWLEu8M , toggle would be : MpSvyWLEu8M")
    raise SystemExit(2)

else : toggle=sys.argv[1]

print(f'Video summarization for the youtube Toggle : {toggle}')

# assume language is english, can be changed to an other language like 'fr' 
language='en'
transcript_list = YouTubeTranscriptApi.list_transcripts(toggle)

transcript = transcript_list.find_transcript([language])  
#print(transcript.video_id)

data=transcript.fetch()
text=''.join([elem['text'] for elem in data])

# DEbug ONLY
# print('initial youtube transcript size : ',len(text.split(' ')),text.split(' ')[0:20])
# print(transcript.translate('en').fetch())
# print(transcript_list[0])

def summarizeMe(prompt,openaiToken,nbbullets,language):
    baseurl='https://api.openai.com'
    cmd='/v1/chat/completions'
    headers={ 'Content-Type':'application/json' ,'Authorization':'Bearer ' + openaiToken}
    if language=='en': myprompt="Summarize the key parts of the following text as {} sentences, get sure the idea of each new sentence is unique, and do not repeat across the summary: \n\n".format(nbbullets)+str(prompt)
    if language=='fr': myprompt="Fais un resume des moments cles du texte suivant: \n\n"+str(prompt)
    payload={
      "model": "gpt-3.5-turbo",#text-davinci-003",
      "messages": [{"role": "user", "content": myprompt}],
      "temperature": 0.7      }
    try:
        result=requests.post(baseurl + cmd,headers=headers,verify=True,json=payload)
    except Exception as e:
        return 'could not process API call ',str(e)
    if result.status_code>199 and result.status_code<300:
        #print('debug',result.status_code)
        resultjson=result.text
        #print('debug',resultjson)
        resultjson=json.loads(result.text)
        #print('debug',resultjson)
        return resultjson['choices'][0]['message']['content']
    else:
        return str(result.status_code)+result.text    


def titleMe(text):
    baseurl='https://api.openai.com'
    cmd='/v1/chat/completions'
    headers={ 'Content-Type':'application/json' ,'Authorization':'Bearer ' + openaiToken}
    if language=='en': myprompt="Create a title out of this text: \n\n"+str(text)
    if language=='fr': myprompt="Genere un titre a partir du texte suivant : \n\n"+str(text)
    payload={
      "model": "gpt-3.5-turbo",#text-davinci-003",
      "messages": [{"role": "user", "content": myprompt}],
      "temperature": 0.7      }
    try:
        result=requests.post(baseurl + cmd,headers=headers,verify=True,json=payload)
    except Exception as e:
        return 'could not process API call ',str(e)
    if result.status_code>199 and result.status_code<300:
        #print('debug',result.status_code)
        resultjson=result.text
        #print('debug',resultjson)
        resultjson=json.loads(result.text)
        #print('debug',resultjson)
        return resultjson['choices'][0]['message']['content']
    else:
        return str(result.status_code)+result.text  

#
#main
#

nbchar=4000
textsplit=text.split(' ')
textlist=[ textsplit[x:x+nbchar] for x in range(0,len(textsplit),nbchar ) ]

finalSummary=[]
#print(len(textlist))


print("Processing the video please wait...")
for x in range(0,len(textlist)):
    #print('processing part ',x,len(textlist)-1)#textlist[x][0:20])
    result=summarizeMe(''.join(textlist[x]),openaiToken,10,language)
    title=titleMe(result)
    print(title)
    print(result)
    finalSummary.append(result)

textsplit=''.join(finalSummary).split(' ')
textlist=[ textsplit[x:x+nbchar] for x in range(0,len(textsplit),nbchar ) ]


# This is in case of bigger video, it is designed to handle it as a summary of summary.

if len(finalSummary) > 3 :
    print("### finalSummary")
    print(finalSummary)
    for x in range(0,len(textlist)):
        #debug#print('processing part ',x,len(textlist)-1)#textlist[x][0:20])
        result=summarizeMe(''.join(textlist[x]),openaiToken,5,language)
        title=titleMe(result)
        print(title)
        print(result)

