import bz2

with open('shape_predictor_68_face_landmarks_GTX.dat.bz2', 'rb') as f_in:
    with open('shape_predictor_68_face_landmarks_GTX.dat', 'wb') as f_out:
        decompressor = bz2.BZ2Decompressor()
        for data in iter(lambda: f_in.read(100 * 1024), b''):
            f_out.write(decompressor.decompress(data))