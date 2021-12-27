from flask import Flask, request

app = Flask(__name__)

@app.route('/predict',methods = ['POST', 'GET'])
def login():
   print(request.files)
   return "Done"

if __name__ == '__main__':
   app.run(debug=True)
