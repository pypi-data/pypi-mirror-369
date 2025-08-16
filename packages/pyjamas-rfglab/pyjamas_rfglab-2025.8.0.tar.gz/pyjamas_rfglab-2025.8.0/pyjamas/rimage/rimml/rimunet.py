"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
from typing import Optional, Tuple

import matplotlib.pyplot as plt
import skimage.io as sio
import skimage.morphology as sm
import skimage.segmentation as ss
import skimage.transform as st
import tensorflow as tf
import tensorflow.keras.backend as kb
import tensorflow.keras.layers as kl
import tensorflow.keras.models as km
import tensorflow.keras.optimizers as ko
import tensorflow.keras.utils as ku
import numpy

import pyjamas.pjscore
from pyjamas.rimage.rimutils import rimutils
from pyjamas.rimage.rimml.rimneuralnet import rimneuralnet
from pyjamas.rutils import RUtils
from pyjamas.rimage.rimml.classifier_types import classifier_types


class UNet(rimneuralnet):

    CLASSIFIER_TYPE: str = classifier_types.UNET.value
    VALIDATION_SPLIT: float = 0.1

    def __init__(self, parameters: Optional[dict] = None):
        super().__init__(parameters)

    def build_network(self, input_shape: Tuple, n_classes: int) -> km.Model:
        _epsilon = tf.convert_to_tensor(kb.epsilon(), numpy.float32)

        # two inputs, one for the image and one for the weight maps
        ip = tf.keras.Input(shape=input_shape, name="image_input")
        # the shape of the weight maps has to be such that it can be element-wise
        # multiplied to the softmax output.
        weight_ip = tf.keras.Input(shape=input_shape[:2] + (n_classes,))

        # adding the layers
        conv1 = kl.Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(ip)
        conv1 = kl.Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv1)
        conv1 = kl.Dropout(0.1)(conv1)
        mpool1 = kl.MaxPool2D()(conv1)

        conv2 = kl.Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(mpool1)
        conv2 = kl.Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv2)
        conv2 = kl.Dropout(0.2)(conv2)
        mpool2 = kl.MaxPool2D()(conv2)

        conv3 = kl.Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(mpool2)
        conv3 = kl.Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv3)
        conv3 = kl.Dropout(0.3)(conv3)
        mpool3 = kl.MaxPool2D()(conv3)

        conv4 = kl.Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(mpool3)
        conv4 = kl.Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv4)
        conv4 = kl.Dropout(0.4)(conv4)
        mpool4 = kl.MaxPool2D()(conv4)

        conv5 = kl.Conv2D(1024, 3, activation='relu', padding='same', kernel_initializer='he_normal')(mpool4)
        conv5 = kl.Conv2D(1024, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv5)
        conv5 = kl.Dropout(0.5)(conv5)

        up6 = kl.Conv2DTranspose(512, 2, strides=2, kernel_initializer='he_normal', padding='same')(conv5)
        conv6 = kl.Concatenate()([up6, conv4])
        conv6 = kl.Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv6)
        conv6 = kl.Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv6)
        conv6 = kl.Dropout(0.4)(conv6)

        up7 = kl.Conv2DTranspose(256, 2, strides=2, kernel_initializer='he_normal', padding='same')(conv6)
        conv7 = kl.Concatenate()([up7, conv3])
        conv7 = kl.Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv7)
        conv7 = kl.Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv7)
        conv7 = kl.Dropout(0.3)(conv7)

        up8 = kl.Conv2DTranspose(128, 2, strides=2, kernel_initializer='he_normal', padding='same')(conv7)
        conv8 = kl.Concatenate()([up8, conv2])
        conv8 = kl.Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv8)
        conv8 = kl.Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv8)
        conv8 = kl.Dropout(0.2)(conv8)

        up9 = kl.Conv2DTranspose(64, 2, strides=2, kernel_initializer='he_normal', padding='same')(conv8)
        conv9 = kl.Concatenate()([up9, conv1])
        conv9 = kl.Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv9)
        conv9 = kl.Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv9)
        conv9 = kl.Dropout(0.1)(conv9)

        c10 = kl.Conv2D(n_classes, 1, activation='softmax', kernel_initializer='he_normal', name="unet-activation")(
            conv9)

        # Add a few non trainable layers to mimic the computation of the crossentropy
        # loss, so that the actual loss function just has to perform the
        # aggregation.
        c11 = kl.Lambda(lambda x: x / tf.reduce_sum(x, len(x.get_shape()) - 1, True))(c10)
        c11 = kl.Lambda(lambda x: tf.clip_by_value(x, _epsilon, 1. - _epsilon))(c11)
        c11 = kl.Lambda(lambda x: kb.log(x))(c11)
        weighted_sm = kl.multiply([c11, weight_ip])

        return km.Model(inputs=[ip, weight_ip], outputs=[weighted_sm])

    def predict(self, image: numpy.ndarray) -> (numpy.ndarray, numpy.ndarray):
        if image is None or image is False:
            return False

        if image.ndim == 3:
            image = image[0, :, :]

        testImage = image / self.scaler

        image_input = self.classifier.get_layer('image_input').input
        softmax_output = self.classifier.get_layer('unet-activation').output
        predictor = kb.function([image_input], [softmax_output])

        testLabel = numpy.zeros(testImage.shape, dtype=bool)
        testProb = numpy.zeros(testImage.shape, dtype=bool)
        half_width = int(self.train_image_size[1] / 2)
        half_height = int(self.train_image_size[0] / 2)

        for animage, therow, thecol in rimutils.generate_subimages(testImage, self.train_image_size[0:2],
                                                                   self.step_sz, True):
            yhat = predictor([numpy.expand_dims(animage, axis=0)])[0]
            yhat = numpy.argmax(yhat[0], axis=-1)
            p = numpy.amax(yhat[0], axis=-1)

            testLabel[(therow - half_height):(therow + half_height),
            (thecol - half_width):(thecol + half_width)] = numpy.logical_or(
                testLabel[(therow - half_height):(therow + half_height), (thecol - half_width):(thecol + half_width)],
                yhat)
            testProb[(therow - half_height):(therow + half_height),
            (thecol - half_width):(thecol + half_width)] = p  # This is not really correct: one should select the probability that makes the pixel get its final value (or an average of those).

        if self.erosion_width is not None and self.erosion_width != 0:
            self.object_array = numpy.asarray(rimutils.extract_contours(
                sm.dilation(sm.label(sm.binary_erosion(testLabel, sm.square(self.erosion_width)), connectivity=1),
                            sm.square(self.erosion_width))), dtype=object)
        else:
            self.object_array = numpy.asarray(rimutils.extract_contours(sm.label(testLabel, connectivity=1)),
                                              dtype=object)
        self.prob_array = testProb

        return self.object_array.copy(), self.prob_array.copy()

    def save(self, filename: str) -> bool:
        self.save_dict.update({
            'classifier_type': UNet.CLASSIFIER_TYPE
        })
        return super().save(filename)