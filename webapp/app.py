#https://projects.raspberrypi.org/en/projects/python-web-server-with-flask/1
from flask import Flask
from flask import Flask, render_template, request
from fonctions import artist_data, artist_recommendation
app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def index():
    artist= artist_data()
    
    return render_template('index.html', artist = artist)

@app.route('/page2', methods = ['POST'])
def page2():
    #request.method == 'POST':
    selection_artists = request.form.getlist("listArtist")
    print(selection_artists)
    recom = artist_recommendation(selection_artists)[:10]
                
    return render_template('page2.html', recom=recom)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


  