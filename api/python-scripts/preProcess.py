from pycontractions import Contractions
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import nltk
from nltk import word_tokenize,sent_tokenize 
import string
import re

# use for text preprocessing
STOP_WORDS = stopwords = list(stopwords.words('english'))
PUNCTUATION = string.punctuation
porter_stemmer = PorterStemmer() # replace with lemmatizer
#cont = Contractions('C:\\Users\\arao6\\Desktop\\Search Engine Demo\\api\\data\\Word Vectors\\GoogleNews-vectors-negative300.bin.gz') #Used to expand contractions

contractions = { 
"ain't": " are not",
"aren't": "are not",
"can't": "cannot",
"can't've": "cannot have",
"'cause": "because",
"could've": "could have",
"couldn't": "could not",
"couldn't've": "could not have",
"didn't": "did not",
"doesn't": "does not",
"don't": "do not",
"hadn't": "had not",
"hadn't've": "had not have",
"hasn't": "has not",
"haven't": "have not",
"he'd": "he had he would",
"he'd've": "he would have",
"he'll": "he shall he will",
"he'll've": "he shall have he will have",
"he's": "he has",
"how'd": "how did",
"how'd'y": "how do you",
"how'll": "how will",
"how's": "how has",
"I'd": "I had I would",
"I'd've": "I would have",
"I'll": "I will",
"I'll've": "I will have",
"I'm": "I am",
"I've": "I have",
"isn't": "is not",
"it'd": "it would",
"it'd've": "it would have",
"it'll": "it will",
"it'll've": "it will have",
"it's": "it is",
"let's": "let us",
"ma'am": "madam",
"mayn't": "may not",
"might've": "might have",
"mightn't": "might not",
"mightn't've": "might not have",
"must've": "must have",
"mustn't": "must not",
"mustn't've": "must not have",
"needn't": "need not",
"needn't've": "need not have",
"o'clock": "of the clock",
"oughtn't": "ought not",
"oughtn't've": "ought not have",
"shan't": "shall not",
"sha'n't": "shall not",
"shan't've": "shall not have",
"she'd": "she would",
"she'd've": "she would have",
"she'll": "she will",
"she'll've": "she will have",
"she's": "she is",
"should've": "should have",
"shouldn't": "should not",
"shouldn't've": "should not have",
"so've": "so have",
"so's": "so is",
"that'd": "that had",
"that'd've": "that would have",
"that's": " that is",
"there'd": "there would",
"there'd've": "there would have",
"there's": "there is",
"they'd": " they would",
"they'd've": "they would have",
"they'll": " they will",
"they'll've": " they will have",
"they're": "they are",
"they've": "they have",
"to've": "to have",
"wasn't": "was not",
"we'd": "we had / we would",
"we'd've": "we would have",
"we'll": "we will",
"we'll've": "we will have",
"we're": "we are",
"we've": "we have",
"weren't": "were not",
"what'll": "what will",
"what'll've": " what will have",
"what're": "what are",
"what's": "what is",
"what've": "what have",
"when's": "when is",
"when've": "when have",
"where'd": "where did",
"where's": "where is",
"where've": "where have",
"who'll": "who shall",
"who'll've": "who shall have",
"who's": "who has",
"who've": "who have",
"why's": "why has",
"why've": "why have",
"will've": "will have",
"won't": "will not",
"won't've": "will not have",
"would've": "would have",
"wouldn't": "would not",
"wouldn't've": "would not have",
"y'all": "you all",
"y'all'd": "you all would",
"y'all'd've": "you all would have",
"y'all're": "you all are",
"y'all've": "you all have",
"you'd": "you would",
"you'd've": "you would have",
"you'll": "you will",
"you'll've": "you shall have",
"you're": "you are",
"you've": "you have"
}

def preProcessUrl(url,punctuation=PUNCTUATION):
    tokens = re.split(r'[;,-_+/\s]\s*', url)
    processed_tokens =[]
    for token in tokens:
        if token not in punctuation and token not in ["http", "https","com","org","www"]: #update list to include more url parameters in future releases
            processed_tokens.append(porter_stemmer.stem(token))


    return processed_tokens
    
def preProcess(doc,isUrl=False,stopwords = STOP_WORDS,punctuation=PUNCTUATION):
    #replace fullstop between two sentences with whitespace when there is no whitespace follwing the fullstop
    # For Example  
    # doc = "The quick brown fox jumped over the lazy dog.The dog barked"
    #expanded_doc = "The quick brown fox jumped over the lazy dog  The dog barked"
    # This is done to prevent word_tokenize from generating the token "dog.The", as is generally done for acronyms such as U.S.A    
    expanded_doc = ""
    for i in range(len(doc)):
        if i != len(doc)-1:
            if doc[i] == '.' and doc[i+1].isupper() and not doc[i-1].isupper():
                expanded_doc += '. '
                pass
        expanded_doc +=doc[i]
    
    tokens = word_tokenize(expanded_doc) #tokenize docs 
    #flags set to true when certain stopwords/punctuation need to be retained
    #such as a title or an article that is used in conjuction with a proper noun like 'The Batman'
    quotation = False
    ignoreStopWords = False
    processed_tokens = []
    for i in range(len(tokens)):
        #set flags to true if phrase is in quotes
        if tokens[i] == '"' or tokens[i]=="'":
            if(quotation):
                quotation = False
                ignoreStopWords = False
            else:
                quotation = True
                ignoreStopWords = True
        if tokens[i] in punctuation:
            pass
        elif i!=len(tokens)-1 and tokens[i].lower() in stopwords:
            if tokens[i][0] == "'": #if token begins with an apostrophe do nothing, for example 'ill
                pass

            elif i != len(tokens) and tokens[i+1][0] == "'": #if the next token has an apostrophe, current token is a contraction
                if tokens[i+2][0].isupper() or ignoreStopWords==True: #save the contraction only is the token after it is a proper Nown
                    processed_tokens.append(porter_stemmer.stem((tokens[i]+tokens[i+1]).lower()))
                else:
                    pass
            else:
                if tokens[i+1][0].isupper() or ignoreStopWords == True: # keep stopwords if they occur in a title or before a proper nown like The Batman
                    processed_tokens.append(porter_stemmer.stem(tokens[i].lower()))                   
                else:
                    pass

        else:
            processed_tokens.append(porter_stemmer.stem(tokens[i].lower()))
    return processed_tokens
        