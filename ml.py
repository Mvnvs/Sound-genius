import pandas as pd
import lyricsgenius
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.stem.porter import PorterStemmer
import re

token  = "2bwyevsei2GLQ5B7yp_T5RcmlF061C5J0tG2V7TIn_9qcgtEI8mNOzqSRTiFsvCP"
genius = lyricsgenius.Genius(token)


def tokenization(txt):
    stemmer = PorterStemmer()
    tokens = nltk.word_tokenize(txt)
    stemming = [stemmer.stem(w) for w in tokens]  # racine du mot
    return " ".join(stemming)

def load_clean_procces_data():

    df = pd.read_csv("spotify_millsongdata.csv")
    df =df.sample(1000).drop('link', axis=1).reset_index(drop=True)
    df['text'] = df['text'].str.lower().replace(r'^\w\s', ' ').replace(r'\n', ' ', regex = True)
    df['text'] = df['text'].apply(lambda x: tokenization(x))

    return df

def cos_sim(df):

    tfidvector = TfidfVectorizer(analyzer='word', stop_words='english')
    matrix = tfidvector.fit_transform(df['text'])  # matrice compte les mots
    similarity = cosine_similarity(matrix)

    return similarity


def recommendation(df,similarity,song_df):
    idx = df[df['song'] == song_df].index[0]
    distances = sorted(list(enumerate(similarity[idx])), reverse=True, key=lambda x: x[1])
    songs = []
    for m_id in distances[1:6]:
       # print(m_id,df.iloc[m_id[0]].artist,",",df.iloc[m_id[0]].song)
        songs.append(df.iloc[m_id[0]].artist + "|" +df.iloc[m_id[0]].song)

    return songs



def get_text(title,artist):
    attempts = 0
    while attempts < 10:
        try:
            song = genius.search_song(title, artist)
            if song is not None:
                print(song.lyrics)
                return song.lyrics
        except requests.exceptions.Timeout as e:
            print("Request timed out (attempt {}/{}):".format(attempts + 1, 10), e)
        except Exception as e:
            print("An error occurred (attempt {}/{}):".format(attempts + 1, 10), e)
        attempts += 1
    print("Unable to find the song after {} attempts.".format(10))
    return None

def add_song(df, title, artist, lyrics):
    # Convert the lyrics to lowercase
    lyrics = lyrics.lower()

    # Replace patterns using regular expression
    lyrics = re.sub(r'^\w\s', ' ', lyrics)
    lyrics = lyrics.replace('\n', ' ')

    # Perform tokenization as needed
    lyrics = tokenization(lyrics)

    # Create a new DataFrame for the song
    new_row = pd.DataFrame({'artist': [artist], 'song': [title], 'text': [lyrics]})

    # Concatenate the original DataFrame with the new DataFrame
    df = pd.concat([df, new_row], ignore_index=True)  # Reassign the result back to 'df'

    return df




def song_exists(df, title, artist):
    # Check if a row with the same title and artist exists in the DataFrame
    exists = not df[(df['song'] == title) & (df['artist'] == artist)].empty
    return exists



def analyse(title, artist):
    pd.set_option('display.max_columns', None)
    df = load_clean_procces_data()
    if not song_exists(df, title, artist):
        lyrics = get_text(title, artist)
        df = add_song(df, title, artist, lyrics)
        print("song added in the database")
    else:
        print("song already in database")


    similarity = cos_sim(df)
    sugg = recommendation(df,similarity,title)
    return sugg