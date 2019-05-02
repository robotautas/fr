import face_recognition

# ('./static/known/ingrida_simonyte.jpg')
# ('./static/known/0.jpg')





def validate(file):
    try:
        image = face_recognition.load_image_file(file)
        face_recognition.face_encodings(image)[0]
        return True
    except IndexError:
        return False


print(validate('./static/known/vl.jpeg'))