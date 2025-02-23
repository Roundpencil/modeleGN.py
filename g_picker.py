import json
from flask import Flask, render_template_string, session, redirect, url_for

import lecteurGoogle

app = Flask(__name__)
app.secret_key = "VOTRE_APP_SECRET_KEY"  # Clé secrète pour sécuriser les sessions

def load_token():
    # Charge le token depuis un fichier JSON (assurez-vous que le chemin est correct)
    with open("token.json", "r") as f:
        return json.load(f)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Accueil</title>
      </head>
      <body>
        <h1>Bienvenue</h1>
        <a href="/picker"><button>Ouvrir Google Picker</button></a>
      </body>
    </html>
    '''

@app.route('/picker')
def picker():
    # Charge le token en session si ce n'est pas déjà fait
    if 'credentials' not in session:
        session['credentials'] = load_token()
    access_token = session['credentials']['token']  # Assurez-vous que votre JSON possède bien ce champ
    developer_key = "AIzaSyAXDZl_GdL1AzevK7yGCO7oIYuEQchnhCE"  # Remplacez par votre clé de développeur obtenue dans la Google Cloud Console

    template = '''
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Google Picker</title>
        <script type="text/javascript" src="https://apis.google.com/js/api.js"></script>
        <script type="text/javascript">
          function onApiLoad() {
            gapi.load('picker', {callback: onPickerApiLoad});
          }
          function onPickerApiLoad() {
            var docsView = new google.picker.DocsView()
              .setIncludeFolders(true)      // Inclut les dossiers dans la vue
              .setSelectFolderEnabled(true); // Permet de sélectionner des dossiers
        
            var picker = new google.picker.PickerBuilder()
              .addView(docsView)
              .setOAuthToken("{{ access_token }}")
              .setDeveloperKey("{{ developer_key }}")
              .setCallback(pickerCallback)
              .build();

            picker.setVisible(true);
          }
          function pickerCallback(data) {
            if (data[google.picker.Response.ACTION] === google.picker.Action.PICKED) {
              var fileId = data[google.picker.Response.DOCUMENTS][0][google.picker.Document.ID];
              console.log('File ID: ' + fileId);
              // Vous pouvez ici envoyer l'ID du fichier à votre backend si nécessaire
            }
          }
        </script>
      </head>
      <body onload="onApiLoad()">
        <h1>Choisissez vos fichiers Google</h1>
      </body>
    </html>
    '''
    return render_template_string(template, access_token=access_token, developer_key=developer_key)

if __name__ == '__main__':
    lecteurGoogle.creer_lecteurs_google_apis()
    app.run(debug=True)
