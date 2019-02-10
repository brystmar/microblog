# when connecting from a web browser, show the Breadsheet Central page
from app import app

# map the top-level URL to this function
@app.route('/')
# also map the /index URL to this same function
@app.route('/index')

# specify what to return
def index():
    text = '<p>'
    text += '<h1><b>Breadsheet Central</b></h1>'
    text += 'Determine the right schedule for FWSY recipes'
    text += '</br></p>'
    text += '<div label="recipelist"><p>'
    text += '<ul>'
    text += '<li>Country Sourdough: <i>Pain de Campagne</i></li>'
    text += '<li>Overnight Poolish</li>'
    text += '</ul>'
    text += '</p></div>'
    return text