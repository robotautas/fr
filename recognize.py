import face_recognition
import os
from app import Known


def compare(unknown):
    """
    Apps'o razinka, atpažinimo logika.
    Encodina nuotraukas iš imgpaths() pateikto listo,
    encodina argumentuose gautą vartotojo pateiktą nuotrauką,
    lygina tų encodingų rezultatus.
    atiduoda dict, kuriame k= reliatyvus kelias iki nuotraukos folderyje,
    v = True jeigu sutampa veidai, False, jei nesutampa.
    Jeigu sutapusios nuotraukos path = path iš duombazės,
    atiduoda vardą pavardę iš tos pačios eilutės.

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

# def imgpaths():
#
#     """
#     Gražina path'us iki pažįstamų nuotraukų, kuriuos paskui naudos compare() funkcijoje
#     """
#
#     for file in os.walk('./static/known'):
#         root = file[0]
#         imglist = file[2]
#         pathlist = []
#         for i in imglist:
#             pathlist.append(f'{root}/{i}')
#     newlist = list(os.walk('./static/known'))[2]
#     print(newlist)
#     return pathlist
