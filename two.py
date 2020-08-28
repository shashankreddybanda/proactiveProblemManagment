def three():
    return "yes"

import numpy as np
import pandas as pd

# importing data
import json

# cleaning text function
import re
import string

# lda model
import gensim
import gensim.corpora as corpora

# stopwords list
import nltk
from nltk.corpus import stopwords

# pos tagging to remove proper nouns
import spacy
import en_core_web_sm

# finding best num_topics based on coherence
from gensim.models import CoherenceModel

def train(incidents, addStopwords, numTopics, businessService):

    def cleanText(text):
        text = text.lower()
        text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
        text = re.sub('\\n', ' ', text)
        return text
    
    def botText(text):
        start = "Additional Information"
        end   = "Loss is in percentile"
        if re.search('%s' % (start), text) != None:
            t1 = re.split(start,text,maxsplit=1)[0].rstrip()
            t2 = re.split(end,text,maxsplit=1)[1].rstrip()
            text = t1 + t2
        else:
            res = list(filter(None, text.splitlines()))
            t3 = '\n'.join(res)
            start = "Alright, I am starting a new conversation again."
            if re.search('%s' % (start), t3) != None:
                text = re.split(start,t3,maxsplit=1)[1].rstrip()
            else:
                del res[1]
                del res[3]
                del res[5]
                text = '\n'.join(res)
        return text
    
    incidentsList = []
    for i in range(len(incidents)):

        # Ignores bot, email, tech lounge and alert contact type incidents
        if ( incidents[i]['contact_type'] not in ['email', 'tech_lounge', 'alert', 'bot']):
            incident = {}
            incident['contact_type'] = incidents[i]['contact_type']
            incident['number'] = incidents[i]['number']
            incident['text'] = incidents[i]['short_description'] + incidents[i]['description'] + incidents[i]['assignment_group'] + incidents[i]['assignment_group'] + incidents[i]['assignment_group']
            incidentsList.append(incident)
            
        # Considers only bot contact type and prunes incidents with long discriptions  
        elif (incidents[i]['contact_type'] in ['bot']):
            text = incidents[i]['short_description'] + incidents[i]['description']
            if len(incidents[i]['description']) > 1500:
                text = incidents[i]['short_description'] + botText(incidents[i]['description'])
            incident = {}
            incident['contact_type'] = incidents[i]['contact_type']
            incident['number'] = incidents[i]['number']
            incident['text'] = text
            incidentsList.append(incident)
    
    incidentDf = pd.DataFrame(incidentsList)
    incidentDf = incidentDf.set_index('number')
    

    clean_func = lambda x: cleanText(x)
    cleanData = pd.DataFrame(incidentDf['text'].apply(clean_func))
                             
    nlp = en_core_web_sm.load()
                             
    stop_words = stopwords.words('english') + addStopwords
                             
    list_sentences = cleanData['text'].values.tolist()
    list_words = []
    
    for sentence in list_sentences:
        # simple_preprocess tokenizes the sentences into words
        list_words.append(gensim.utils.simple_preprocess(sentence.encode('utf-8')))
    # removing stopwords
    list_words = [[w for w in gensim.utils.simple_preprocess(str(d)) if w not in stop_words] for d in list_words]
    # lemmatize + pos filter
    lem_words = []
    # only allow these part of speech
    pos_tags = ['NOUN', 'VERB', 'ADJ', 'ADV']
    for s in list_words:
        doc = nlp(" ".join(s))
        lem_words.append([token.lemma_ for token in doc if token.pos_ in pos_tags])

    # gives unique id for each word
    id2word = corpora.Dictionary(lem_words)

    # maps a specific word_id to the frequency of that word
    corpus = [id2word.doc2bow(t) for t in lem_words]
                             
    lda_model = gensim.models.ldamodel.LdaModel(corpus = corpus, id2word = id2word, num_topics = numTopics, 
                                                 random_state = 42, per_word_topics = True, passes = 10)
                             

    lda_model.save(businessService+'LDA.model')
    
    result = {}
    inci = incidentDf.reset_index()
    prob = 1/numTopics + 0.001

    for i in range(len(corpus)):
        topics ={}
        t = lda_model.get_document_topics(corpus[i])
        for j in t:
            if j[1] > prob:
                topics[str(j[0])] = str(j[1])
        if len(topics) > 0:
            result[inci['number'][i]] = topics
        
    return json.dumps(result)

# payload = {"incidents":[{"number":"INC0440586","short_description":"Fuel 50 Access Request","description":"Hi IT Support,Please provide Michael Wang Fuel 50 access.Thanks,ChristinaChristina L. OliveiraHR Business PartnerCustomer OutcomesDesk: 408.450.7280Cell: 408.674.9020","contact_type":"email"},{"number":"INC0472429","short_description":"Mac | MS Team | Norway","description":"I am working together with partners and customer on teams. can I please get this on my computer?","contact_type":"email"},{"number":"INC0439101","short_description":"Issue with: Outlook","description":"When I open up Office 365 I am missing the Microsoft Teams application. Can you fix this asap? I need to build a Sharepoint site for my team. Thank you, +++Cynthia","contact_type":"self-service"},{"number":"INC0498639","short_description":"Message from --CVP_11_5_1_0_ (+16028204006)","description":"Translation from Watson: ","contact_type":"phone"},{"number":"INC0503909","short_description":"Camtasia | Installation | Hyderabad, India","description":"Need to install Camtasia on my Macbook.    I have the Camtasia software request approved and per the notification, it should automatically install when I connect to VPN.  However this has not happened.https://surf.service-now.com/nav_to.do?uri=sc_req_item.dosys_id%3D2fdfe7e9dbccdc50bb412b6913961919sysparm_stack%3Dsc_req_item_list.dosysparm_query%3Dactive%3Dtrue","contact_type":"portal"},{"number":"INC0498657","short_description":"Message from Unknown sender (+14083323540)","description":"Translation from Watson: ","contact_type":"phone"},{"number":"INC0473774","short_description":"(Duplicate of INC0473771):  Mobile | iPhone Setup | Munich","description":"Translation from Watson: hello this is  my cuts are speaking about setting up my work I  if you could please call me five S. zero zero four nine one seven three six five nine five two zero one thank you goodbye ","contact_type":"phone"},{"number":"INC0435633","short_description":"Issue with: Computer Applications","description":"Windows 7 End of Life Notification: I received a Windows 7 End of Life Notification and wanted to reach out to see what my next step should be. Also, could this be why I’ve gotten two blue screens in the last couple of months?","contact_type":"self-service"},{"number":"INC0477191","short_description":"Computer Applications | Intellij License Issue | Kirkland, WA","description":"Looks like my Intellij license didnt auto-renew. Last year I got a new license key ahead of the expiry (in email, IRCC - its been since purged). Went to do some work just now and was told the current license has expired. I have an all-access license (Idea, PyCharm, CLion, etc.). Please look into ASAP. Thanks!Update: I was able to click Evaluate so Im able to use the product temporarily in evaluation model. Wasnt sure it would let me do that since Ive evaluated it before.","contact_type":"portal"},{"number":"INC0456591","short_description":"Screenflow | Audio Recording not Working | San Diego, CA, USA","description":"Having an issue with Screenflow.   The audio recording function is no longer working and am receiving a runtime error.  *** Cant add nil AVCaptureinput .    The application continues to crash","contact_type":"portal"},{"number":"INC0444085","short_description":"Issue with: Computer Applications","description":"Per Ken Harveys request, I need to have access to DocuSign as we member of the Orders to Cash team.","contact_type":"self-service"},{"number":"INC0455659","short_description":"Computer Applications | Telestream ScreenFlow License | Staines, United Kingdom","description":"Hiya! :)I have a new Mac sy my previous one can get fixed (which I will bring in next week). I am using specific recording software, Screenflow. I have a license for version 8, i forgot to grab it off the old one. Do you perhaps keep a list of license keys?Thanks in advance!Tanya","contact_type":"portal"},{"number":"INC0459367","short_description":"Computer Applications | Skype for Business | Staines, UK","description":"Skype for business has stopped working over the weekend. If I try to log in I get the following error:That Microsoft account doesnt exist. Enter a different account or get a new one.I need Skype for both the projects Im working on at the moment.","contact_type":"portal"},{"number":"INC0452895","short_description":"Computer Applications | keychain and application issues  |Australia","description":"I am unable to access MS Applications as I am continually being asked to Log in and when I do, the process just repeats itself.","contact_type":"portal"},{"number":"INC0504047","short_description":"Duplicate of SCTASK0449347 | Duplicate of SCTASK0449347 | San Diego, CA, USA","description":"Liz: No","contact_type":"bot"}],"addStopWords":["tech","lounge","need","break","install","start","update","try","customer","support"],"numTopic":10,"businessService":"test"}
def apiCall(payload):
    return train(payload["Incidents"], payload["addStopWords"], payload['numTopic'], payload["businessService"])