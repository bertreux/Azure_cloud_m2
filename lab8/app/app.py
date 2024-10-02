import requests
import json

# Paramètres de l'API (remplacez avec vos informations)
endpoint = "https://superchatgpt.cognitiveservices.azure.com/"
key = "66e7bb8ac2604c559cc0c71cc9c6a8c6"

# Texte à analyser
text = "WHYYYYYYY ?"

# Fonction pour analyser le sentiment
def analyze_sentiment(text):
    url = f"{endpoint}/text/analytics/v3.1/sentiment"
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/json"
    }
    body = {
        "documents": [
            {"id": "1", "language": "fr", "text": text}
        ]
    }
    response = requests.post(url, headers=headers, json=body)
    return response.json()

# Fonction pour extraire les phrases clés
def analyze_key_phrases(text):
    url = f"{endpoint}/text/analytics/v3.1/keyPhrases"
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/json"
    }
    body = {
        "documents": [
            {"id": "1", "language": "fr", "text": text}
        ]
    }
    response = requests.post(url, headers=headers, json=body)
    return response.json()

# Exécution des analyses
sentiment_result = analyze_sentiment(text)
key_phrases_result = analyze_key_phrases(text)

# Affichage des résultats
print("Résultat de l'analyse de sentiment :", json.dumps(sentiment_result, indent=2, ensure_ascii=False))
print("Résultat de l'extraction des phrases clés :", json.dumps(key_phrases_result, indent=2, ensure_ascii=False))
