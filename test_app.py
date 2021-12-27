from flask import Flask, request

app = Flask(__name__)

@app.route('/predict',methods = ['POST', 'GET'])
def login():
   # if request.method == 'POST':
   #    img = transforms(Image.open(request.files['image'])).unsqueeze(0)/255.0
   #    prediction = model(img)
   #    prediction = list(prediction.cpu().detach().numpy()[0])

   # output = f"Class Name : {prediction.index(max(prediction))} Accuracy : {max(prediction)}"
   # print(output, flush=True)
   # return output
   print(request.files)
   return "Done"

if __name__ == '__main__':
   app.run(debug=False)
