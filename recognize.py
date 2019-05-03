import face_recognition
import os
from app import Known


def compare(unknown):
    """
    Atpažinimo logika. Encodina nuotraukas iš katalogo,
    encodina vartotojo pateiktą nuotrauką, lygina tų encodingų rezultatus.
    atiduoda dict, kuriame k= nuotraukos pavadinimas,v = boolean reiksme.
    True jeigu sutampa veidai, False, jei nesutampa.
    Jeigu sutapusios nuotraukos path = path iš duombazės,
    atiduoda vardą pavardę iš tos pačios eilutės.
    jeigu atsakyme nera True reiksmes, atsakyma prilygina 'Unrecognized Person'
    """
    img_names = list(os.walk('./static/known'))[0][2]
    enc_list = []
    for pic in img_names:
        picture = face_recognition.load_image_file(f'./static/known/{pic}')
        picture_enc = face_recognition.face_encodings(picture)[0]
        enc_list.append(picture_enc)

    example = face_recognition.load_image_file(unknown)
    example_enc = face_recognition.face_encodings(example)[0]

    results = face_recognition.compare_faces(enc_list, example_enc)
    output = dict(zip(img_names, results))

    if any(results):
        for k, v in output.items():
            if v:
                match = k

        answer = Known.query.filter_by(image_file=f'{match}').all()

    else:
        answer = 'Unrecognized Person'

    return answer

def validate(file):
    """

    """
    try:
        image = face_recognition.load_image_file(file)
        face_recognition.face_encodings(image)[0]
        return True
    except IndexError:
        return False



