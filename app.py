from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def hello_world():
    return "<p>Hello, World! viju</p>"

@app.route('/armstrong/<int:n>')
def armstrong(n):
    sum = 0
    # Find the number of digits (the power to raise each digit to)
    order = len(str(n))
    copy_n = n
    
    while(n > 0):
        digit = n % 10
        sum += digit ** order
        n = n // 10
        
    if(sum == copy_n):
        print(f"{copy_n} is an armstrong number")
        result = {
             "Number":copy_n,
             "Armstrong" : True
             }
        return jsonify(result)
    else:
        print(f"{copy_n} is NOT an armstrong number")
        result = {
                 "Number":copy_n,
                 "Armstrong" : False
                }
        return jsonify(result)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
