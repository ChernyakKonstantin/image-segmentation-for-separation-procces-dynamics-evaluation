# https://towardsdatascience.com/a-keras-pipeline-for-image-segmentation-part-1-6515a421157d

# https://www.tensorflow.org/api_docs/python/tf/keras/preprocessing/image/ImageDataGenerator

import tensorflow as tf
from tensorflow.keras import Model, Sequential
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import BatchNormalization, Concatenate, Conv2DTranspose, Dropout, Input, ReLU, Softmax
from tensorflow.keras.layers.experimental.preprocessing import Rescaling, Resizing


def preprocessing_layer(image_size):
    """Слой предобработки входных изображений.
    Слой выполняет следующие операции:
    1. Изменяет разрешение входных изображений.
    2. Нормализует входные изображения.

    Данный слой позволяет отказаться от предобработки входных данных
    на этапах обучения и использования модели.

    Args:
        image_size (tuple): Разрешение изображения семантической маски

    Returns:
        (tf.keras.Sequential): Слой предобработки изображений

    """
    preprocessing = Sequential(name='preprocessing_layer')
    preprocessing.add(Resizing(*image_size))
    preprocessing.add(Rescaling(1. / 255))
    return preprocessing


def deconvolutional_layer(filters, size, apply_dropout=False):
    """ Слой обратной сверки.

    Args:
        filters (int): Число фильтров
        size (int): Размер фильтра
        apply_dropout (bool): Флаг применения слоя Dropout

    Returns:
        (tf.keras.Sequential): Слой обратной сверки

    """
    initializer = tf.random_normal_initializer(0., 0.02)
    result = Sequential()
    result.add(Conv2DTranspose(
        filters,
        size,
        strides=2,
        padding='same',
        kernel_initializer=initializer,
        use_bias=False,
        )
    )
    result.add(BatchNormalization())
    if apply_dropout:
        result.add(Dropout(0.5))
    result.add(ReLU())
    return result


def make_model(image_size, output_channels, alpha=1.0):
    """Функция создания модели.

    Модель возвращает семантическую маску с действительными значениями классов.
    Модель самостоятельно уменьшает разрешение входного изображения.
    Модель самостоятельно нормализует входное изображение.

    Args:
        image_size (tuple): Разрешение изображения семантической маски
        output_channels (int): Число классов маски
        alpha (float): Регулятор настрйоки числа параметров модели

    Returns:
        (tf.keras.Model): Модель семантической сегментации изображений

    """
    # Encoder
    base_model = MobileNetV2(input_shape=[*image_size, 3], include_top=False, alpha=alpha)

    encoder_output_layer_names = [
        'block_1_expand_relu',  # 64x64
        'block_3_expand_relu',  # 32x32
        'block_6_expand_relu',  # 16x16
        'block_13_expand_relu',  # 8x8
        'block_16_project',  # 4x4
    ]
    output_layers = [base_model.get_layer(name).output for name in encoder_output_layer_names]

    encoder = Model(inputs=base_model.input, outputs=output_layers)
    encoder.trainable = False

    # Decoder
    deconv_stack = [
        deconvolutional_layer(512, 3),  # 4x4 -> 8x8
        deconvolutional_layer(256, 3),  # 8x8 -> 16x16
        deconvolutional_layer(128, 3),  # 16x16 -> 32x32
        deconvolutional_layer(64, 3),  # 32x32 -> 64x64
    ]

    inputs = Input(shape=[None, None, 3])
    preprocessed_input = preprocessing_layer(image_size)(inputs)

    # Downsampling through the model
    encoder_outputs = encoder(preprocessed_input)
    feature_vector = encoder_outputs[-1]
    skip_connections = reversed(encoder_outputs[:-1])

    # Upsampling and establishing the skip connections
    for deconv, skip in zip(deconv_stack, skip_connections):
        feature_vector = deconv(feature_vector)
        concat = Concatenate()
        feature_vector = concat([feature_vector, skip])

    output_layer = Conv2DTranspose(
        output_channels, 3, strides=2,
        padding='same'
    )  # 64x64 -> 128x128

    logits = output_layer(feature_vector)

    outputs = Softmax()(logits)

    return Model(inputs=inputs, outputs=outputs)