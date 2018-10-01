import tensorflow as tf
import os
import sys
import math

############################################################################# Network Utils

def MLP_2_hidden(features, numInputFeatures, hidden1_units, hidden2_units, numOutFeatures, 
    layerName, keepProb, isTraining, useDropOut = False, useInitBN = True):
    """Method to create the graph of a MLP of two hidden layers.

    Args:
        features (nxm tensor): Input features.
        numInputFeatures (int): Number of input features.
        hidden1_units (int): Number of units in the first hidden layer.
        hidden2_units (int): Number of units in the second hidden layer.
        numOutFeatures (int): Number of output features.
        layerName (string): Name of the MLP.
        keepProb (tensor): Tensor with the probability to maintain a input in the MLP.
        isTraining (tensor): Tensor with a boolean that indicates if the MLP is executed
            in a training mode or not.
        useDropOut (bool): Boolean that indicates if dropout should be used in the MLP.
        useInitBN (bool): Boolean that indicates if an initial batch normalization should be used.
    """

    initializer = tf.contrib.layers.variance_scaling_initializer(factor=1.0, 
        mode='FAN_AVG', uniform=True)

    if useInitBN:
        features = tf.layers.batch_normalization(inputs = features, training = isTraining, name = layerName+"_BN_Init")
    
    # Hidden 1
    weights = tf.Variable(initializer([numInputFeatures, hidden1_units]), name='weights')
    tf.add_to_collection('weight_decay_loss', weights)
    biases = tf.Variable(tf.zeros([hidden1_units]), name='biases')
    mul1 = tf.matmul(features, weights) + biases
    mul1 = tf.layers.batch_normalization(inputs = mul1, training = isTraining, name = layerName+"_BN_h1")
    hidden1 = tf.nn.relu(mul1)
        
    # Hidden 2
    if useDropOut:
        hidden1 = tf.nn.dropout(hidden1, keepProb)
    weights = tf.Variable(initializer([hidden1_units, hidden2_units]), name='weights')
    tf.add_to_collection('weight_decay_loss', weights)
    biases = tf.Variable(tf.zeros([hidden2_units]), name='biases')
    mul2 = tf.matmul(hidden1, weights) + biases
    mul2 = tf.layers.batch_normalization(inputs = mul2, training = isTraining, name = layerName+"_BN_h2")
    hidden2 = tf.nn.relu(mul2)
        
    # Linear
    if useDropOut:
        hidden2 = tf.nn.dropout(hidden2, keepProb)
    weights = tf.Variable(initializer([hidden2_units, numOutFeatures]), name='weights')
    tf.add_to_collection('weight_decay_loss', weights)
    biases = tf.Variable(tf.zeros([numOutFeatures]), name='biases')
    logits = tf.matmul(hidden2, weights) + biases
    return logits


def MLP_1_hidden(features, numInputFeatures, hidden_units, numOutFeatures, layerName, 
    keepProb, isTraining, useDropOut = False):
    """Method to create the graph of a MLP of one hidden layers.

    Args:
        features (nxm tensor): Input features.
        numInputFeatures (int): Number of input features.
        hidden_units (int): Number of units in the hidden layer.
        numOutFeatures (int): Number of output features.
        layerName (string): Name of the MLP.
        keepProb (tensor): Tensor with the probability to maintain a input in the MLP.
        isTraining (tensor): Tensor with a boolean that indicates if the MLP is executed
            in a training mode or not.
        useDropOut (bool): Boolean that indicates if dropout should be used in the MLP.
    """

    initializer = tf.contrib.layers.variance_scaling_initializer(factor=1.0, mode='FAN_AVG', uniform=True)
    # Hidden 1
    weights = tf.Variable(initializer([numInputFeatures, hidden_units]), name='weights')
    tf.add_to_collection('weight_decay_loss', weights)
    biases = tf.Variable(tf.zeros([hidden_units]), name='biases')
    mul = tf.matmul(features, weights) + biases
    mul = tf.layers.batch_normalization(inputs = mul, training = isTraining, name = layerName+"_BN_h")
    hidden = tf.nn.relu(mul)
        
    # Linear
    if useDropOut:
        hidden = tf.nn.dropout(hidden, keepProb)
    weights = tf.Variable(initializer([hidden_units, numOutFeatures]), name='weights')
    tf.add_to_collection('weight_decay_loss', weights)
    biases = tf.Variable(tf.zeros([numOutFeatures]), name='biases')
    linear = tf.matmul(hidden, weights) + biases
    return linear


def conv_1x1(layerName, inputs, numInputs, numOutFeatures):
    """Method to create a fully connected layer to compute a new set of features
        by combining the input features.

    Args:
        layerName (string): Name of the layer.
        inputs (nxm tensor): Input features.
        numInputs (int): Number of input features.
        numOutFeatures (int): Number of output features.
    """

    initializer = tf.contrib.layers.variance_scaling_initializer(factor=1.0, mode='FAN_AVG', uniform=True)
    weights = tf.Variable(initializer([numInputs, numOutFeatures]), name='weights')
    tf.add_to_collection('weight_decay_loss', weights)
    biases = tf.Variable(tf.zeros([numOutFeatures]), name='biases')
    reducedOutput = tf.matmul(inputs, weights) + biases
    return reducedOutput


def batch_norm_RELU_drop_out(layerName, inFeatures, isTraining, usedDropOut, keepProb):
    """Method to create a combination of layers: Batch norm + RELU + Drop out.

    Args:
        layerName (string): Name of the layer.
        inFeatures (nxm tensor): Input features.
        isTraining (tensor): Tensor with a boolean that indicates if the MLP is executed
            in a training mode or not.
        useDropOut (bool): Boolean that indicates if dropout should be used in the MLP.
        keepProb (tensor): Tensor with the probability to maintain a input in the MLP.
    """
    inFeatures = tf.layers.batch_normalization(inputs = inFeatures, training = isTraining, name = layerName+"_BN")
    inFeatures = tf.nn.relu(inFeatures)
    if usedDropOut:
        inFeatures = tf.nn.dropout(inFeatures, keepProb)
    return inFeatures
