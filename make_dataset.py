import os
from multiprocessing import Pool, cpu_count
from os.path import basename, join
from time import time

import cv2 as cv
import numpy as np
from PIL import Image

import constants
from commons import make_dir


def get_bbox(image):
    """Функция определения границ маски.

    При формировании границ учитываются отступы, чтобы в дальнейшем трансформировать изображения.

    Args:
        image (PIL.Image): Маска изображения

    Returns:
        bbox (list): Координаты прямоугольной гранциы маски

    """
    PADDING = 50
    paddings = (-PADDING, -PADDING, PADDING, PADDING)
    bbox = image.getbbox()
    bbox = [box_coord + offset for (box_coord, offset) in zip(bbox, paddings)]
    return bbox


def get_bboxes(container_mask_path):
    """Функция определения границ изображений контейнеров.

    Args:
        container_mask_path (str): Маска контейнеров

    Returns:
        (tuple): Координаты прямоугольных границ изображений контейнеров

    """
    image = Image.open(container_mask_path)
    image = image.convert("L")  # Конвератция в черно-белое изображение

    bbox = get_bbox(image)
    offsets = [bbox[0], bbox[1]] * 2

    image = image.crop(bbox)
    spilt_index = image.size[0] // 2
    left_image = image.crop((0, 0, spilt_index, image.size[1]))
    right_image = image.crop((spilt_index, 0, image.size[0], image.size[1]))

    l_bbox = get_bbox(left_image)
    relative_r_bbox = get_bbox(right_image)

    r_bbox_offsets = [spilt_index, 0, spilt_index, 0]
    r_bbox = [box_coord + offset for box_coord, offset in zip(relative_r_bbox, r_bbox_offsets)]

    abs_l_bbox = [box_coord + offset for box_coord, offset in zip(l_bbox, offsets)]
    abs_r_bbox = [box_coord + offset for box_coord, offset in zip(r_bbox, offsets)]

    return abs_l_bbox, abs_r_bbox


def to_class_id(mask, class_id):
    """Функция преобразования значений маски в индексы класса.

    Args:
        mask (numpy.ndarray): Маска изображения
        class_id (int): Индекс класса

    Returns:
        (numpy.ndarray): Маска изображения со значениями индекса класса

    """
    return mask // 255 * class_id


def crop(image, bbox):
    """Функция кадрирования изображений в формате numpy.ndarray.

    Args:
        image (numpy.ndarray): Изображение
        bbox (tuple): Координты прямоугольных границ изображения

    Returns:
        (numpy.ndarray): Кадрированное изображение

    """
    left = bbox[0]
    right = bbox[2]
    upper = bbox[1]
    lower = bbox[3]
    return image[upper: lower, left: right]


def get_semantic_mask(oil_mask, water_mask, container_mask):
    """Функция создания семантической маски изображения.

    Функция возвращает одноканальное изображение с размеченными обласятми каждого из классов.
    Каждому классу соответсвует число.

    Args:
        oil_mask (numpy.ndarray): Маска фракции масла
        water_mask (numpy.ndarray): Маска фракции воды
        container_mask (numpy.ndarray): Маска изображенйи контейнеров

    Returns:
        (numpy.ndarray): Семантическая маска изображения

    """
    semantic_mask = np.full_like(container_mask, constants.BACKGROUND_ID)

    water_pixels = np.where(water_mask != 0)
    semantic_mask[water_pixels] = water_mask[water_pixels]

    oil_pixels = np.where(oil_mask != 0)
    semantic_mask[oil_pixels] = oil_mask[oil_pixels]

    emulsion_pixels = np.where(semantic_mask == 0)
    semantic_mask[emulsion_pixels] = constants.EMULSION_ID

    semantic_mask = cv.bitwise_and(semantic_mask, semantic_mask, mask=container_mask)

    return semantic_mask


def process_set(container_mask_path, oil_subdir, water_mask_path, photo_subdir):
    """Функция обработки набора изображений.

    Функция выполняет следующие операции:
    1. Загрузка исходных фотографий, масок фракций масла и воды, маски изображений контейнеров.
    2. Создание семантической маски для каждой из фотографий.
    3. Кадрирование изображений контейнеров для исходных фотографий и семантических масок.

    Args:
        container_mask_path (str): Путь до маски изображений контейнеров
        oil_subdir (str): Путь до директории, содержащей маски фракций масла
        water_mask_path (str): Путь до маски фракции воды
        photo_subdir (str): Путь до директории, содержащей исходные фотографии эксперимента

    Returns:
        (tuple): Списки кадрированных фотографий и кадрированных семантических масок

    """

    l_bbox, r_bbox = get_bboxes(container_mask_path)

    container_mask = cv.imread(container_mask_path, cv.IMREAD_GRAYSCALE)

    water_mask = cv.imread(water_mask_path, cv.IMREAD_GRAYSCALE)
    water_mask = to_class_id(water_mask, constants.WATER_ID)

    photos = []
    semantic_masks = []

    for photo_path in [entry.path for entry in list(os.scandir(photo_subdir)) if entry.is_file()]:
        photo = cv.imread(photo_path, cv.IMREAD_COLOR)
        photo = cv.cvtColor(photo, cv.COLOR_BGR2RGB)

        l_photo = crop(photo, l_bbox)
        r_photo = crop(photo, r_bbox)

        l_photo = cv.resize(l_photo, constants.IMAGE_SIZE)
        r_photo = cv.resize(r_photo, constants.IMAGE_SIZE)

        photos.extend((l_photo, r_photo))

    for oil_mask_path in [entry.path for entry in list(os.scandir(oil_subdir)) if entry.is_file()]:
        oil_mask = cv.imread(oil_mask_path, cv.IMREAD_GRAYSCALE)
        oil_mask = to_class_id(oil_mask, constants.OIL_ID)

        semantic_mask = get_semantic_mask(oil_mask, water_mask, container_mask)

        l_semantic_mask = crop(semantic_mask, l_bbox)
        r_semantic_mask = crop(semantic_mask, r_bbox)

        l_semantic_mask = cv.resize(l_semantic_mask, constants.IMAGE_SIZE)
        r_semantic_mask = cv.resize(r_semantic_mask, constants.IMAGE_SIZE)

        # Делаю здесь, т.к. cv.resize устраняет синглтоны.
        l_semantic_mask = np.expand_dims(l_semantic_mask, axis=-1)
        r_semantic_mask = np.expand_dims(r_semantic_mask, axis=-1)

        semantic_masks.extend((l_semantic_mask, r_semantic_mask))

    return photos, semantic_masks


def process_set_wrapper(args):
    """Обертка функции process_set для её параллельного использования.

    Args:
        args (tuple): Аргументы, необходимые для функции process_set

    Returns:
        (Any): Результат выполнения функции process_set

    """
    return process_set(*args)


def save_as_ndarray(data, filename, save_dir):
    """

    Args:
        data (list): Набор изображений
        filename (str): Название файла c указанием расширения .npy
        save_dir (str): Путь до директории сохранения

    """
    make_dir(save_dir)
    file_path = join(save_dir, filename)
    np.save(file_path, data)


def time_elapsed(func):
    def wrapper(*args, **kwargs):
        t_1 = time()
        res = func(*args, **kwargs)
        t_2 = time()
        print(f'(multiprocessing) Done in {t_2 - t_1} seconds')
        return res

    return wrapper


@time_elapsed
def pipeline(container_masks_dir, oil_masks_dir, water_masks_dir, photos_dir, save_dir):
    """Функия подготовки набора данных.

    Для ускорения работы функция использует максимально доступное число CPU,
    если число доступных CPU не превышает число возможных параллельных вычислений.

    Args:
        container_masks_dir (str): Путь до директории, содержащей маски изображений контейнеров
        oil_masks_dir (str): Путь до директории, содержащей поддиректории с масками фракций масла
        water_masks_dir (str): Путь до директории, содержащей маски фракций воды
        photos_dir (str): Путь до директории, содержащей поддиректории с исходными фотографиями
        save_dir (str): Путь до директории сохранения набора данных

    Returns:

    """
    container_mask_paths = [entry.path for entry in list(os.scandir(container_masks_dir))]
    oil_subdirs = [entry.path for entry in list(os.scandir(oil_masks_dir))]
    water_mask_paths = [entry.path for entry in list(os.scandir(water_masks_dir))]
    photo_subdirs = [entry.path for entry in list(os.scandir(photos_dir))]

    container_mask_paths.sort(key=basename)
    oil_subdirs.sort(key=basename)
    water_mask_paths.sort(key=basename)
    photo_subdirs.sort(key=basename)

    total = len(container_mask_paths)

    if cpu_count() > total:
        agents = total
    else:
        agents = cpu_count()
    chunk_size = total // agents

    args = zip(
        container_mask_paths,
        oil_subdirs,
        water_mask_paths,
        photo_subdirs,
    )

    with Pool(processes=agents) as pool:
        res = pool.map(process_set_wrapper, args, chunk_size)

    photos = []
    semantic_masks = []

    for photo_set, semantic_mask_set in res:
        photos.extend(photo_set)
        semantic_masks.extend(semantic_mask_set)

    save_as_ndarray(photos, constants.X_FILENAME, save_dir)
    save_as_ndarray(semantic_masks, constants.Y_FILENAME, save_dir)


if __name__ == '__main__':
    masks_dir = join(
        constants.PROJECT_DIRNAME,
        constants.DATA_DIRNAME,
        constants.ORIGINAL_DATA_DIRNAME,
        constants.MASK_DIRNAME
    )

    container_masks_dir = join(
        masks_dir,
        constants.CONTAINER_MASKS_DIRNAME
    )

    oil_masks_dir = join(
        masks_dir,
        constants.OIL_MASKS_DIRNAME
    )

    water_masks_dir = join(
        masks_dir,
        constants.WATER_MASKS_DIRNAME
    )

    photos_dir = join(
        constants.PROJECT_DIRNAME,
        constants.DATA_DIRNAME,
        constants.ORIGINAL_DATA_DIRNAME,
        constants.PHOTO_DIRNAME
    )

    processed_dir = join(
        constants.PROJECT_DIRNAME,
        constants.DATA_DIRNAME,
        constants.PROCESSED_DATA_DIRNAME
    )

    print(masks_dir)
    print(container_masks_dir)
    print(oil_masks_dir)
    print(water_masks_dir)
    print(photos_dir)

    pipeline(container_masks_dir, oil_masks_dir, water_masks_dir, photos_dir, processed_dir)
