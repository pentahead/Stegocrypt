from flask import Flask, request, send_file, render_template, jsonify
from PIL import Image
import os
import base64

app = Flask(__name__)

def xor_encrypt_decrypt(key, message):
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(message))

def hide_message(image_path, message, output_path):
    img = Image.open(image_path)
    encoded = img.copy()
    width, height = img.size
    index = 0

    message += chr(0)  # Null-terminate the message

    for row in range(height):
        for col in range(width):
            if index < len(message):
                r, g, b = img.getpixel((col, row))
                char = message[index]
                encoded.putpixel((col, row), (r, g, ord(char)))
                index += 1
            else:
                break
    encoded.save(output_path)

def reveal_message(image_path):
    img = Image.open(image_path)
    width, height = img.size
    message = ''
    
    for row in range(height):
        for col in range(width):
            r, g, b = img.getpixel((col, row))
            if b == 0:  # Null-terminator found
                return message
            message += chr(b)

    return message

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hide', methods=['GET'])
def hide_page():
    return render_template('hide_message.html')

@app.route('/reveal', methods=['GET'])
def reveal_page():
    return render_template('reveal_message.html')

@app.route('/hide', methods=['POST'])
def hide():
    try:
        image = request.files['image']
        message = request.form['message']
        key = request.form.get('key')

        if key:
            message = xor_encrypt_decrypt(key, message)
        
        output_path = os.path.join('output', 'hidden.png')
        image.save(output_path)
        hide_message(output_path, message, output_path)
        
        return send_file(output_path, mimetype='image/png')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/reveal', methods=['POST'])
def reveal():
    try:
        image = request.files['image']
        key = request.form.get('key')
        
        image_path = os.path.join('output', 'reveal.png')
        image.save(image_path)
        message = reveal_message(image_path)
        
        if key:
            message = xor_encrypt_decrypt(key, message)
        
        return jsonify({'message': message})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists('output'):
        os.makedirs('output')
    app.run(debug=True)
