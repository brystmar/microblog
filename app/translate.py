import json
import requests
from flask_babel import _
from app import app


def translate(text, source_language, dest_language):
    # uses the Azure Text Translation API to translate text
    # returns a byte string in utf-8 _with a signature prefix_
    # Ex: b'\xef\xbb\xbf"Hi, how are you?"'

    if 'MS_TRANSLATOR_KEY' not in app.config or not app.config['MS_TRANSLATOR_KEY']:
        return _('Error: Translation service is not configured.')

    endpoint = 'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0'
    args = '&from={}&to={}'.format(source_language, dest_language)
    full_url = endpoint + args

    headers = {'Ocp-Apim-Subscription-Key': app.config['MS_TRANSLATOR_KEY']}
    data = [{'Text': text}]

    r = requests.post(full_url, headers=headers, json=data)

    if r.status_code != 200:
        return _('Error: Translation service failed. ' + r.text)
    else:
        # print('Success!')
        decoded = r.content.decode('utf-8-sig')
        result = json.loads(decoded)[0]['translations'][0]['text']
        return result
