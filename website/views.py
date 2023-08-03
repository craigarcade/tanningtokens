from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
import requests

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    note = Note.query.filter_by(user_id=current_user.id).first()
    current_note = int(note.data) if note else 0  # Get the current note value or set it to 0 if no note exists

    if request.method == 'POST':
        note_value = request.form.get('note')
        action = request.form.get('action')
        
        try:
            if action == 'redeem':
                note_value = int(note_value)  # Convert the user input to an integer
                note_value = note_value*-1
                current_note += note_value  # Perform addition or subtraction
                data_to_send = {'token_count': note_value, 'user_id': current_user.id}
                print(data_to_send)
                # Make the POST request to the other Flask server
                response = requests.post('http://192.168.1.144:80/', json=data_to_send)
                #print(response.status_code)  # Print the response status code
                #print(response.json())  # Print the JSON response from the server
                if current_note < 0:
                    current_note = 0  # Ensure the note cannot go below 0
                if note:
                    note.data = current_note  # Update the existing note's data
                else:
                    new_note = Note(data=current_note, user_id=current_user.id)
                    db.session.add(new_note)  # Create a new note with the calculated value
            elif action == 'purchase':
                note_value = int(note_value)  # Convert the user input to an integer
                current_note += note_value  # Perform addition or subtraction
                if current_note < 0:
                    current_note = 0  # Ensure the note cannot go below 0
                if note:
                    note.data = current_note  # Update the existing note's data
                else:
                    new_note = Note(data=current_note, user_id=current_user.id)
                    db.session.add(new_note)  # Create a new note with the calculated value

            db.session.commit()
            flash('Tokens Adjusted!', category='success')
        except ValueError:
            flash('Invalid input! Please enter a valid number.', category='error')

    return render_template("home.html", user=current_user, note=current_note)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
