import pandas as pd
import numpy as np
import time
from scipy.sparse import vstack
from scipy.sparse import csr_matrix
from lightfm import LightFM
from lightfm.evaluation import auc_score, precision_at_k, recall_at_k
from lightfm.cross_validation import random_train_test_split
from lightfm.data import Dataset

# import Datas
plays = pd.read_csv('data_lightfm/user_artists.dat', sep='\t')
artists = pd.read_csv('data_lightfm/artists.dat', sep='\t', usecols=['id','name'])
ap1 = pd.merge(artists, plays, how="inner", left_on="id", right_on="artistID")
ap = ap1.rename(columns={"weight": "playCount"})
artist = artists.name


# création fonction
def artist_data ():
    # Merge artist and user pref data
    artist = artists.name
    return artist

def recuperer_X():
    ap1 = pd.merge(artists, plays, how="inner", left_on="id", right_on="artistID")
    ap = ap1.rename(columns={"weight": "playCount"})
    # Group artist by name
    artist_rank = ap.groupby(['name']) \
    .agg({'userID' : 'count', 'playCount' : 'sum'}) \
    .rename(columns={"userID" : 'totalUsers', "playCount" : "totalPlays"}) \
    .sort_values(['totalPlays'], ascending=False)

    artist_rank['avgPlays'] = artist_rank['totalPlays'] / artist_rank['totalUsers']
   
    # Merge into ap matrix
    ap = ap.join(artist_rank, on="name", how="inner") \
    .sort_values(['playCount'], ascending=False)

    # Preprocessing
    pc = ap.playCount
    play_count_scaled = (pc - pc.min()) / (pc.max() - pc.min())
    ap = ap.assign(playCountScaled=play_count_scaled)
    # Build a user-artist rating matrix 
    ratings_df = ap.pivot(index='userID', columns='artistID', values='playCountScaled')
    ratings = ratings_df.fillna(0).values
    # Build a sparse matrix
    X = csr_matrix(ratings)
    return X



def artist_recommendation(artists):
    X = recuperer_X()
    user = np.zeros(X.shape[1]) #shape[1]: nombre de colonnes, Shape[0]: nbre de lignes
    for a in artists:
        i = list(artists.name).index(a)
        user[i] = X[:,i].mean()
    X = vstack([X,user]) # creation d'une nouvelle matrice en stackant mon user

    model = LightFM(loss = 'warp')
    model.fit(X, epochs=30, num_threads=2)
    n_users, n_items = X.shape
    rating = X.ratings_df
    user_id = rating.index.values
    scores = model.predict(user_id-1, np.arange(n_items))
    #artist_names = ap.sort_values("artistID")["name"].unique() #récupérer la dernière ligne de ap
    #artist_names = ap.['artistID'][:-1]
    top_items = artist_names[np.argsort(-scores)][:10]
    reco =[]
    for x in top_items:
        if i not in x:
            reco.append(i)   
    return reco
       
