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

from typing import Optional, Tuple
from abc import abstractmethod

import os
import numpy
import gzip
import pickle
import matplotlib.pyplot as plt
import skimage.io as sio
import skimage.morphology as sm
import skimage.segmentation as ss
import skimage.transform as st

import tensorflow as tf
import tensorflow.keras.backend as kb
import tensorflow.keras.models as km
import tensorflow.keras.optimizers as ko
import tensorflow.keras.utils as ku
import tensorflow.keras.callbacks as kc

import pyjamas.pjscore
from pyjamas.rimage.rimml.rimml import rimml
from pyjamas.rutils import RUtils


class rimneuralnet(rimml):
    OUTPUT_CLASSES: int = 2
    BATCH_SIZE: int = 1
    EPOCHS: int = 100
    LEARNING_RATE: float = 0.01
    STEP_SIZE: Tuple[int, int] = (rimml.TRAIN_IMAGE_SIZE[0]//8, rimml.TRAIN_IMAGE_SIZE[1]//8)
    EROSION_WIDTH: int = 0

    VALIDATION_SPLIT: float = 0.1
    EARLY_STOPPER: dict = {'active': True, 'kwargs': {'patience': 5}}
    LR_SCHEDULER: dict = {'active': True, 'kwargs': {'patience': 5}}  # ReduceLROnPlateau callback
    MODEL_CHECKPOINT: dict = {'active': True, 'kwargs': {'save_best_only': True}}
    LOGGING: dict = {'active': True, 'kwargs': {}}

    def __init__(self, parameters: Optional[dict] = None):
        super().__init__(parameters)

        self.positive_training_folder: str = parameters.get('positive_training_folder')
        self.save_folder: str = parameters.get('save_folder')

        # Size of training images (rows, columns).
        self.train_image_size: Tuple[int, int] = parameters.get('train_image_size', rimneuralnet.TRAIN_IMAGE_SIZE)  # (row, col)
        self.step_sz: Tuple[int, int] = parameters.get('step_sz', rimneuralnet.STEP_SIZE)

        self.scaler: int = parameters.get('scaler', 1)  # max pixel value of the training set.

        self.X_train: numpy.ndarray = None
        self.Y_train: numpy.ndarray = None
        self.W_train: numpy.ndarray = None

        self.save_dict: dict = {}

        self.object_array: numpy.ndarray = None
        self.prob_array: numpy.ndarray = None

        self.output_classes: int = parameters.get('output_classes', rimneuralnet.OUTPUT_CLASSES)
        self.learning_rate: float = parameters.get('learning_rate', rimneuralnet.LEARNING_RATE)
        self.input_size: Tuple[int, int, int] = parameters.get('train_image_size', rimneuralnet.TRAIN_IMAGE_SIZE)
        self.epochs: int = parameters.get('epochs', rimneuralnet.EPOCHS)
        self.mini_batch_size: int = parameters.get('mini_batch_size', rimneuralnet.BATCH_SIZE)
        self.erosion_width: int = parameters.get('erosion_width', rimneuralnet.EROSION_WIDTH)
        self.step_sz = parameters.get('step_sz', rimneuralnet.STEP_SIZE)
        self.validation_split = parameters.get('validation_split', rimneuralnet.VALIDATION_SPLIT)

        self.early_stopper = parameters.get('early_stopper', rimneuralnet.EARLY_STOPPER)
        self.lr_scheduler = parameters.get('lr_scheduler', rimneuralnet.LR_SCHEDULER)
        self.model_checkpoint = parameters.get('model_checkpoint', rimneuralnet.MODEL_CHECKPOINT)
        self.logging = parameters.get('logging', rimneuralnet.LOGGING)

        classifier_representation = parameters.get('classifier')
        if type(classifier_representation) is km.Model:
            self.classifier = classifier_representation
        else:
            if len(self.input_size) == 2:
                self.input_size = self.input_size + (1,)

        self.classifier = self.build_network(self.input_size, self.output_classes)
        adam = ko.Adam(learning_rate=self.learning_rate)
        self.classifier.compile(adam, loss=self.pixelwise_loss)
        if type(classifier_representation) is list:
            self.classifier.set_weights(classifier_representation)

    @abstractmethod
    def build_network(self, input_shape: Tuple, n_classes: int) -> km.Model:
        pass

    @staticmethod
    def pixelwise_loss(target, output):
        """
        A custom function defined to simply sum the pixelwise loss.
        This function doesn't compute the crossentropy loss, since that is made a
        part of the model's computational graph itself.
        Parameters
        ----------
        target : tf.tensor
            A tensor corresponding to the true labels of an image.
        output : tf.tensor
            Model output
        Returns
        -------
        tf.tensor
            A tensor holding the aggregated loss.
        """
        return - tf.reduce_sum(target * output,
                               len(output.get_shape()) - 1)

    def fit(self):
        self._process_training_data()
        inputs = self._get_training_inputs()
        callbacks = self._build_callbacks()

        self.classifier.fit(inputs, self.Y_train, batch_size=self.mini_batch_size, epochs=self.epochs,
                            validation_split=self.validation_split, callbacks=callbacks if callbacks else None)
        return True

    def _process_training_data(self) -> bool:
        """
        Loads and scales training data and calculates weight maps.
        :return:
        """
        train_ids = next(os.walk(self.positive_training_folder))[1]

        # Get and resize train images and masks
        self.X_train = numpy.zeros((len(train_ids), self.train_image_size[0], self.train_image_size[1], 1), dtype=numpy.uint16)
        self.Y_train = numpy.zeros((len(train_ids), self.train_image_size[0], self.train_image_size[1], 1), dtype=bool)
        self.W_train = numpy.zeros((len(train_ids), self.train_image_size[0], self.train_image_size[1], 1), dtype=float)
        print('Getting and resizing train images and masks ... ')

        for n, id_ in enumerate(train_ids):
            path = os.path.join(self.positive_training_folder, id_)
            im_file = os.path.join(path, "image", os.listdir(os.path.join(path, "image"))[0])
            img = sio.imread(im_file)
            if img.ndim == 3:
                img = img[0, :, :]
            img = numpy.expand_dims(st.resize(img, (self.train_image_size[0], self.train_image_size[1]), order=3,
                                              mode='constant', preserve_range=True), axis=-1)
            self.X_train[n] = img
            msk_file = os.path.join(path, "mask", os.listdir(os.path.join(path, "mask"))[0])
            mask = numpy.zeros((self.train_image_size[0], self.train_image_size[1], 1), dtype=bool)
            mask_ = sio.imread(msk_file)
            mask_ = numpy.expand_dims(st.resize(mask_, (self.train_image_size[0], self.train_image_size[1]), order=0,
                                                mode='constant', preserve_range=True), axis=-1)
            mask = numpy.maximum(mask, mask_)
            weights = self.weight_map(mask)
            self.Y_train[n] = mask
            self.W_train[n, :, :, 0] = weights

        self.scaler = numpy.amax(self.X_train)
        self.X_train = self.X_train / self.scaler

        wmap = numpy.zeros((self.X_train.shape[0], self.train_image_size[0], self.train_image_size[1], 2),
                           dtype=numpy.float32)
        wmap[..., 0] = self.W_train.squeeze()
        wmap[..., 1] = self.W_train.squeeze()
        self.W_train = wmap

        self.Y_train = ku.to_categorical(self.Y_train)
        return True

    @staticmethod
    def weight_map(binmasks: numpy.ndarray, w0: float = 10., sigma: float = 5., show: bool = False):
        """Compute the weight map for a given mask, as described in Ronneberger et al.
        (https://arxiv.org/pdf/1505.04597.pdf)
        """

        labmasks = sm.label(binmasks)
        n_objs = numpy.amax(labmasks)

        nrows, ncols = labmasks.shape[:2]
        masks = numpy.zeros((n_objs, nrows, ncols))
        distMap = numpy.zeros((nrows * ncols, n_objs))
        X1, Y1 = numpy.meshgrid(numpy.arange(nrows), numpy.arange(ncols))
        X1, Y1 = numpy.c_[X1.ravel(), Y1.ravel()].T
        for i in range(n_objs):
            mask = numpy.squeeze(labmasks == i + 1)
            bounds = ss.find_boundaries(mask, mode='inner')
            X2, Y2 = numpy.nonzero(bounds)
            xSum = (X2.reshape(-1, 1) - X1.reshape(1, -1)) ** 2
            ySum = (Y2.reshape(-1, 1) - Y1.reshape(1, -1)) ** 2
            distMap[:, i] = numpy.sqrt(xSum + ySum).min(axis=0)
            masks[i] = mask
        ix = numpy.arange(distMap.shape[0])
        if distMap.shape[1] == 1:
            d1 = distMap.ravel()
            border_loss_map = w0 * numpy.exp((-1 * (d1) ** 2) / (2 * (sigma ** 2)))
        else:
            if distMap.shape[1] == 2:
                d1_ix, d2_ix = numpy.argpartition(distMap, 1, axis=1)[:, :2].T
            else:
                d1_ix, d2_ix = numpy.argpartition(distMap, 2, axis=1)[:, :2].T
            d1 = distMap[ix, d1_ix]
            d2 = distMap[ix, d2_ix]
            border_loss_map = w0 * numpy.exp((-1 * (d1 + d2) ** 2) / (2 * (sigma ** 2)))
        xBLoss = numpy.zeros((nrows, ncols))
        xBLoss[X1, Y1] = border_loss_map
        # class weight map
        loss = numpy.zeros((nrows, ncols))
        w_1 = 1 - masks.sum() / loss.size
        w_0 = 1 - w_1
        loss[masks.sum(0) == 1] = w_1
        loss[masks.sum(0) == 0] = w_0
        ZZ = xBLoss + loss
        # ZZ = resize(ZZ, outsize, preserve_range=True)
        if show:
            plt.imshow(ZZ)
            plt.colorbar()
            plt.axis('off')
        return ZZ

    def _get_training_inputs(self):
        return [self.X_train, self.W_train]

    def _build_callbacks(self):
        callbacks = []
        if self.early_stopper['active']:
            if self.validation_split > 0:
                monitor = 'val_loss'
            else:
                raise Warning("Using early stopping without a validation split is not recommended. "
                              "Setting early stopping to monitor train loss.")
                monitor = 'train_loss'
            callbacks.append(kc.EarlyStopping(monitor, restore_best_weights=True, **self.early_stopper['kwargs']))
        if self.lr_scheduler['active']:
            callbacks.append(kc.ReduceLROnPlateau(monitor='val_loss' if self.validation_split > 0 else 'train_loss',
                                                  **self.lr_scheduler['kwargs']))
        if self.logging['active']:
            log_dir = os.path.join(self.save_folder, 'logs')
            os.makedirs(log_dir, exist_ok=True)
            callbacks.append(kc.TensorBoard(log_dir, **self.logging['kwargs']))
        if self.model_checkpoint['active']:  # add saving last so that it occurs after all other callback operations
            callbacks.append(SaveCallback(self, monitor='val_loss' if self.validation_split > 0 else 'train_loss',
                                          **self.model_checkpoint['kwargs']))

        return callbacks

    def build_save_dict(self) -> bool:
        self.save_dict.update({
            'positive_training_folder': self.positive_training_folder,
            'train_image_size': self.train_image_size,
            'scaler': self.scaler,
            'epochs': self.epochs,
            'mini_batch_size': self.mini_batch_size,
            'learning_rate': kb.eval(self.classifier.optimizer.lr),
            'classifier': self.classifier.get_weights(),
            'step_sz': self.step_sz,
            'erosion_width': self.erosion_width,
            'early_stopper': self.early_stopper,
            'lr_scheduler': self.lr_scheduler,
            'model_checkpoint': self.model_checkpoint,
            'logging': self.logging,
        })
        return True

    def save(self, filename: str) -> bool:
        self.build_save_dict()
        return RUtils.pickle_this(self.save_dict, RUtils.set_extension(filename, pyjamas.pjscore.PyJAMAS.classifier_extension))


class SaveCallback(kc.Callback):
    """This is quite slow, use the ModelCheckpoint callback and implement a "load model weights" in the IO menu?"""

    def __init__(self, neuralnet: rimneuralnet, save_best_only: bool = True, monitor: str = 'val_loss'):
        super().__init__()

        if neuralnet.save_folder is None or neuralnet.save_folder == "" or neuralnet.save_folder is False:
            self.save_folder = os.getcwd()
        else:
            self.save_folder = neuralnet.save_folder

        self.neuralnet = neuralnet
        self.save_best_only = save_best_only
        self.monitor = monitor
        if save_best_only:
            self.best_loss = numpy.inf

    def on_epoch_end(self, epoch, logs=None):
        if self.save_best_only and logs[self.monitor] < self.best_loss:
            self.neuralnet.save(os.path.join(self.save_folder, "ckpt_best.cfr"))
            self.best_loss = logs[self.monitor]
        elif not self.save_best_only:
            self.neuralnet.save(os.path.join(self.save_folder, f"ckpt_epoch{epoch:03d}.cfr"))
        return {"epoch": epoch, "logs": logs}

    def on_train_end(self, logs):
        if self.save_best_only:
            fh = gzip.open(os.path.join(self.save_folder, "ckpt_best.cfr"), "rb")
            best_cfr = pickle.load(fh)
            fh.close()
            self.neuralnet.classifier.set_weights(best_cfr["classifier"])
        self.neuralnet.save(os.path.join(self.save_folder, "ckpt_final.cfr"))
