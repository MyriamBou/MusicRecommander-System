import pandas as pd
import numpy as np
import time
from scipy.sparse import vstack
from scipy.sparse import csr_matrix
from lightfm import LightFM
from lightfm.evaluation import auc_score, precision_at_k, recall_at_k
from lightfm.cross_validation import random_train_test_split
from lightfm.data import Dataset


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

def artist_recommendation(artist):
    plays = pd.read_csv('data_lightfm/user_artists.dat', sep='\t')
    artists = pd.read_csv('data_lightfm/artists.dat', sep='\t', usecols=['id','name','url'])
    # Merge artist and user pref data
    ap = pd.merge(artists, plays, how="inner", left_on="id", right_on="artistID")
    ap = ap.rename(columns={"weight": "playCount"})
     
    # Group artist by name
    artist_rank = ap.groupby(['name']) \
        .agg({'userID' : 'count', 'playCount' : 'sum'}) \
        .rename(columns={"userID" : 'totalUsers', "playCount" : "totalPlays"}) \
        .sort_values(['totalPlays'], ascending=False)

    artist_rank['avgPlays'] = artist_rank['totalPlays'] / artist_rank['totalUsers']
    ap = ap.join(artist_rank, on="name", how="inner") \
        .sort_values(['playCount'], ascending=False)

    # Preprocessing
    pc = ap.playCount
    play_count_scaled = (pc - pc.min()) / (pc.max() - pc.min())
    ap = ap.assign(playCountScaled=play_count_scaled)

    # Build a user-artist rating matrix 
    ratings_df = ap.pivot(index='userID', columns='artistID', values='playCountScaled')
    ratings = ratings_df.fillna(0).values

    #rajout d'un nouvel utilisateur dans la base avec la cotation a 1 de son artist prefere dans ratings
    new_user_rating  = np.zeros(ratings.shape[1])
        
    artistID = artists[artists['name'].isin(artist)].id.unique()
    
    new_user_rating[artistID]+=1
    ratings = np.append(ratings, [new_user_rating], axis=0)
    
    X = csr_matrix(ratings)

    n_users, n_items = ratings_df.shape
    n_users += 1
    
    # user_ids = ratings_df.index.values
    
    artist_names = ap.sort_values('artistID')["name"].unique()
    # artist_lien = ap.sort_values('artistID')["url"].unique()
    
    # Build data references + train test
    Xcoo = X.tocoo()
    data = Dataset()
    data.fit(np.arange(n_users), np.arange(n_items))
    interactions, weights = data.build_interactions(zip(Xcoo.row, Xcoo.col, Xcoo.data)) 
    model = LightFM(learning_rate=0.05, loss='warp', learning_schedule='adadelta')
    model.fit(interactions, epochs=10, num_threads=2)

    scores = model.predict(n_users-1, np.arange(n_items))

    top_items = list(artist_names[np.argsort(-scores)])
    # top_lien = list(artist_lien[np.argsort(-scores)])
    # total = []
    # total.append([top_items, top_lien])
    # print(total)
    resultat_ =[]
    for z in top_items:
        if z not in artist:
            resultat_.append(z)
    
    return resultat_