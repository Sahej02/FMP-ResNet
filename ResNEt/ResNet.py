#import required packages
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import datetime as dt
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import time
# dataset loading
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
y_train = to_categorical(y_train)
y_test = to_categorical(y_test)
train_dataset = tf.data.Dataset.from_tensor_slices(
    (x_train, y_train)).batch(64).shuffle(50000)
train_dataset = train_dataset.map(
    lambda x, y: (tf.cast(x, tf.float32) / 255.0, y))
train_dataset = train_dataset.repeat()
valid_dataset = tf.data.Dataset.from_tensor_slices(
    (x_test, y_test)).batch(5000).shuffle(10000)
valid_dataset = valid_dataset.map(
    lambda x, y: (tf.cast(x, tf.float32) / 255.0, y))
valid_dataset = valid_dataset.repeat()

#defining residual block
def res_net_block(input_data, filters, conv_size):
    x = layers.Conv2D(filters, conv_size, activation='relu',
                      padding='same')(input_data)
    x = layers.BatchNormalization(axis=-1)(x)
    x = layers.Conv2D(filters, conv_size, activation=None, padding='same')(x)
    x = layers.BatchNormalization(axis=-1)(x)
    x = layers.Add()([x, input_data])
    x = layers.Activation('relu')(x)
    return x


def non_res_block(input_data, filters, conv_size):
    x = layers.Conv2D(filters, conv_size, activation='relu',
                      padding='same')(input_data)
    x = layers.BatchNormalization()(x)
    x = layers.Conv2D(filters, conv_size,
                      activation='relu', padding='same')(x)
    x = layers.BatchNormalization()(x)
    return x

# creating the model - input blocks + residual blocks
inputs = keras.Input(shape=(32, 32, 3))
x = layers.Conv2D(32, 3, activation='relu')(inputs)
x = layers.Conv2D(64, 3, activation='relu')(x)
x = layers.MaxPooling2D(3)(x)

num_res_net_blocks = 20

for i in range(num_res_net_blocks):
    x = res_net_block(x, 64, 3)
    
x = layers.Conv2D(64, 3, activation='relu')(x)
x = layers.MaxPooling2D(3)(x)
x = layers.Flatten()(x)
x = layers.Dense(256, activation='relu')(x)
outputs = layers.Dense(10, activation='softmax')(x)
res_net_model = keras.Model(inputs, outputs)

#compilation and fitting
res_net_model.compile(optimizer=keras.optimizers.Adam(),
                      loss='categorical_crossentropy',
                      metrics=['acc'])

print(res_net_model.summary())

checkpoint = ModelCheckpoint(
    'Model.hdf5', monitor='val_loss', save_best_only=True, verbose=1, mode='min')

callbacks_list = [checkpoint]

results = res_net_model.fit(train_dataset, epochs=50, steps_per_epoch=100,
                            validation_data=valid_dataset,
                            validation_steps=3, callbacks=callbacks_list)


# plot epoch vs accuracy
plt.plot(results.history['acc'])
plt.plot(results.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

plt.plot(results.history['loss'])
plt.plot(results.history['val_loss'])
plt.title('loss history')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
