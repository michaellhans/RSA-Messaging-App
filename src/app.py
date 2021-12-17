# app.py

# Required imports
import os
import re
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app
from Message import *
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Initialize Firestore DB
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
message_ref = db.collection('messages')
user_ref = db.collection('users')
verified_user_ref = db.collection('verified_users')

@app.route('/generate-key', methods=['POST'])
def generate_key():
    try:
        user = request.get_json()['user']
        public_key, private_key = generate_rsa_key()
        public_key = ','.join(str(x) for x in public_key)
        private_key = ','.join(str(x) for x in private_key)

        # Save the public key into the repository
        user_ref.document(user).set({'username': user, 'public_key': public_key})

        # Save the private key on the device
        with open("private_key/" + user + ".pri", "w") as f:
            f.write(private_key)

        return jsonify({
            "public_key": public_key,
            "private_key": private_key,
        }), 200

    except Exception as e:
        print(e)
        return f"An Error Occured: {e}"

@app.route('/generate-signature-key', methods=['POST'])
def generate_signature_key():
    try:
        user = request.get_json()['user']
        private_key, public_key = generate_rsa_key()
        public_key = ','.join(str(x) for x in public_key)
        private_key = ','.join(str(x) for x in private_key)

        # Save the public key into the repository
        verified_user_ref.document(user).set({'username': user, 'public_key': public_key})

        # Save the private key on the device
        with open("private_key/" + user + "-sign.pri", "w") as f:
            f.write(private_key)

        return jsonify({
            "public_key": public_key,
            "private_key": private_key,
        }), 200

    except Exception as e:
        print(e)
        return f"An Error Occured: {e}"

@app.route('/add', methods=['POST'])
def create():
    """
        create() : Add document to Firestore collection with request body.
    """
    try:
        sender = request.get_json()['sender']
        receiver = request.get_json()['receiver']
        message = request.get_json()['message']
        public_key = user_ref.document(receiver).get().to_dict()['public_key']
        print(public_key)
        public_key = list(map(int, public_key.split(',')))

        try:
            with open('private_key/' + sender + "-sign.pri", "r") as f:
                signing_private_key = f.read()
            print(signing_private_key)
            signing_private_key = list(map(int, signing_private_key.split(',')))

        except:
            signing_private_key = ""

        messageDict = Message(message, sender, receiver, public_key, signing_private_key)
        print(messageDict.message)
        timestamp = str(messageDict.timestamp)
        message_ref.document(timestamp).set(messageDict.to_json())
        return jsonify({"success": True}), 200

    except Exception as e:
        print(e)
        return f"An Error Occured: {e}"

@app.route('/messages', methods=['GET'])
def read():
    """
        read() : Fetches documents from Firestore collection as JSON.
        todo : Return document that matches query ID.
        all_todos : Return all documents.
    """
    receiver = request.args.get('receiver')
    print(receiver)
    assert(receiver)
    f = open("private_key/"+ receiver + ".pri", "r")
    private_key = f.read()
    print("Private key receiver: ", private_key)
    private_key = list(map(int, private_key.split(',')))
    all_messages = [doc.to_dict() for doc in message_ref.where(u'receiver', u'==', receiver).stream()]
    print(all_messages[0]['sender'])
    public_key_verifying = verified_user_ref.document(all_messages[0]['sender']).get().to_dict()['public_key']
    print("Public key verifying: ", public_key_verifying)
    if (public_key_verifying != None):
        public_key_verifying = list(map(int, public_key_verifying.split(',')))

    for message in all_messages:
        plaintext = rsa_decryption(message['message'], private_key)
        try:
            text, signature = re.findall(r"^(.*)<ds>(.*)</ds>$", plaintext, re.DOTALL)[0]
        except:
            text = plaintext
            signature = ''
        message['message'] = text
        message['verify'] = verify(text, signature, public_key_verifying)
    try:

        return jsonify(all_messages), 200

    except Exception as e:
        return f"An Error Occured: {e}"

@app.route('/raw-messages', methods=['GET'])
def read_raw():
    """
        read_raw() : Fetches messages documents from Firestore collection as JSON.
        param: receiver
    """
    try:
        receiver = request.args.get('receiver')
        all_messages = [doc.to_dict() for doc in message_ref.where(u'receiver', u'==', receiver).stream()]
        return jsonify(all_messages), 200

    except Exception as e:
        return f"An Error Occured: {e}"

port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port, debug=True)