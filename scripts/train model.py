# Idk where to place it correctly. If it is here, all works. If it under import it works. If in __main__ block - doesnt.
import tensorflow as tf
physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

from os.path import join

import numpy as np
from keras.preprocessing.image import ImageDataGenerator

import constants
from commons import make_dir
from make_model import make_model


def train_model(X_path, y_path, save_dir):
    """Функция обучения и сохранения модели.

    Args:
        X_path (str): Путь до входных данных
        y_path (str): Путь до истинных меток
        save_dir (str): Директория сохранения модели

    Returns:
        model_history (?): Информация о процессе обучения модели

    """

    X = np.load(X_path)
    y = np.load(y_path)

    print(f'X shape: {X.shape}')
    print(f'y shape: {y.shape}')

    X_datagen = ImageDataGenerator(
        **constants.COMMON_DATAGEN_PARAMS,
        **constants.TRAIN_DATAGEN_PARAMS
    )
    X_datagen.fit(X)

    y_datagen = ImageDataGenerator(**constants.COMMON_DATAGEN_PARAMS)

    train_generator = zip(
        X_datagen.flow(X, **constants.FLOW_PARAMS, subset='training'),
        y_datagen.flow(y, **constants.FLOW_PARAMS, subset='training')
    )

    validation_generator = zip(
        X_datagen.flow(X, **constants.FLOW_PARAMS, subset='validation'),
        y_datagen.flow(y, **constants.FLOW_PARAMS, subset='validation')
    )

    model = make_model(**constants.MODEL_PARAMS)
    model.compile(**constants.COMPILE_PARAMS)
    model_history = model.fit(
        x=train_generator,
        validation_data=validation_generator,
        **constants.FIT_PARAMS
    )
    model.save(save_dir)
    return model_history


if __name__ == '__main__':
    processed_dir = join(
        constants.PROJECT_DIRNAME,
        constants.DATA_DIRNAME,
        constants.PROCESSED_DATA_DIRNAME,
    )

    model_save_dir = join(constants.PROJECT_DIRNAME, constants.MODEL_DIR)
    make_dir(model_save_dir)

    path_to_X = join(processed_dir, constants.X_FILENAME)
    path_to_y = join(processed_dir, constants.Y_FILENAME)

    train_history = train_model(path_to_X, path_to_y, model_save_dir)
