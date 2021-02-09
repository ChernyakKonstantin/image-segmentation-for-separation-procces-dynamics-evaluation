from tensorflow.keras.losses import SparseCategoricalCrossentropy

from commons import UpdatedMeanIoU


PROJECT_DIRNAME = r'C:\Users\zvfrf\Documents\PyCharmProjects\diploma_prj'
DATA_DIRNAME = 'data'

ORIGINAL_DATA_DIRNAME = 'original'
PROCESSED_DATA_DIRNAME = 'processed'

PHOTO_DIRNAME = 'photos'

MASK_DIRNAME = 'masks'
CONTAINER_MASKS_DIRNAME = 'container_masks'
OIL_MASKS_DIRNAME = 'oil_masks'
WATER_MASKS_DIRNAME = 'water_masks'

X_FILENAME = 'X.npy'
Y_FILENAME = 'y.npy'

MODEL_DIR = 'model'
OPTIMIZED_MODEL_DIR = 'optimized_model'

# Параметры семантической маски
BACKGROUND_ID = 0
WATER_ID = 1
EMULSION_ID = 2
OIL_ID = 3
TOTAL_CLASSES = 4
IMAGE_SIZE = (128, 128)

# Параметры обучения модели

SEED = 489

COMMON_DATAGEN_PARAMS = dict(
        rotation_range=90,
        width_shift_range=0.1,
        height_shift_range=0.1,
        zoom_range=0.2,
        vertical_flip=True,
        validation_split=0.2,
    )

TRAIN_DATAGEN_PARAMS = dict()

FLOW_PARAMS = dict(
        batch_size=32,
        shuffle=True,
        seed=SEED,
    )

MODEL_PARAMS = dict(
    image_size=IMAGE_SIZE,
    output_channels=TOTAL_CLASSES,
    alpha=0.35,
)

COMPILE_PARAMS = dict(
    optimizer='adam',
    loss=SparseCategoricalCrossentropy(from_logits=False),
    metrics=[UpdatedMeanIoU(num_classes=TOTAL_CLASSES, name='mean_iou')],
)

FIT_PARAMS = dict(
    steps_per_epoch=10,
    epochs=5,
    verbose=1,
    validation_steps=10,
)

# Параметры приложения

DEVICE_ID = 0
CAMERA_RESOLUTION = (1280, 720)

LOG_DIR = 'log'
LOG_FILENAME = 'log.csv'

PERIOD = 0.03  # Период срабатывания приложения (секунды)
