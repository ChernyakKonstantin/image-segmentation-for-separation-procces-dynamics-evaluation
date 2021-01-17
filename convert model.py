"""На данный момент недоступно на Windows.

   https://www.tensorflow.org/api_docs/python/tf/experimental/tensorrt/Converter

"""
import numpy as np
from tensorflow.experimental.tensorrt import ConversionParams, Converter

import constants
from os.path import join

def input_fn():
    """Функция, возвращающая примеры данных для оптимизации модели..

    Функция возвращает примеры изображений для оптимизации модели.
    Размеры изображений соответсвуют планируемым при работе модели.
    Оптимизация на текущем этапе позволяет избежать ее при первом запуске модели,
    что сокращает время первого запуска.

    Returns:
        (list): Список массивов заданной формы.

    """
    shapes = [[*constants.IMAGE_SIZE, 3], ] # Размер входных данных, под которые оптимизируется
    yield [np.zeros([1, *shape], dtype='float32') for shape in shapes]

if __name__ == '__main__':
    input_saved_model_dir = join(constants.PROJECT_DIRNAME, constants.MODEL_DIR)
    output_saved_model_dir = join(constants.PROJECT_DIRNAME, constants.OPTIMIZED_MODEL_DIR)

    params = ConversionParams(precision_mode='FP16')

    converter = Converter(input_saved_model_dir, conversion_params=params)
    converter.convert()
    converter.build(input_fn)
    converter.save(output_saved_model_dir)
