"""A convolutional neural network for CIFAR-10 classification.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import cifar
import tensorflow as tf


def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.05)
    return tf.Variable(initial)


def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)


def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')


def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                          strides=[1, 2, 2, 1], padding='SAME')


def variable_summaries(var, name):
    """Attach a lot of summaries to a Tensor."""
    with tf.name_scope('summaries'):
        mean = tf.reduce_mean(var)
        tf.summary.scalar('mean/' + name, mean)
    with tf.name_scope('stddev'):
        stddev = tf.sqrt(tf.reduce_mean(tf.square(var - mean)))
        tf.summary.scalar('stddev/' + name, stddev)
        tf.summary.scalar('max/' + name, tf.reduce_max(var))
        tf.summary.scalar('min/' + name, tf.reduce_min(var))
        tf.summary.histogram(name, var)


def main(_):
    cifar10 = cifar.Cifar()
    cifar10.ReadDataSets(one_hot=True)

    # Create the model
    x = tf.placeholder(tf.float32, [None, 3072])

    # Define loss and optimizer
    y_ = tf.placeholder(tf.float32, [None, 10])

    x_image = tf.reshape(x, [-1, 32, 32, 3])

    tf.summary.image("images", x_image, max_outputs=6)

    # (32 - 3 + 2 * 1) / 1 +1 = 32
    with tf.name_scope("conv_layer1"):
        W_conv1 = weight_variable([5, 5, 3, 32])
        variable_summaries(W_conv1, "conv_layer1/weights")
        b_conv1 = bias_variable([32])
        variable_summaries(b_conv1, "conv_layer1/biases")
        h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
        h_pool1 = max_pool_2x2(h_conv1)
        tf.summary.image("conv_layer1/images", h_pool1[:, :, :, 0:1], max_outputs=6)

    with tf.name_scope("conv_layer2"):
        W_conv2 = weight_variable([5, 5, 32, 64])
        variable_summaries(W_conv2, "conv_layer2/weights")
        b_conv2 = bias_variable([64])
        variable_summaries(b_conv2, "conv_layer2/biases")
        h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
        h_pool2 = max_pool_2x2(h_conv2)
        tf.summary.image("conv_layer2/images", h_pool2[:, :, :, 0:1], max_outputs=6)

    with tf.name_scope("conv_layer3"):
        W_conv3 = weight_variable([5, 5, 64, 64])
        variable_summaries(W_conv3, "conv_layer3/weights")
        b_conv3 = bias_variable([64])
        variable_summaries(b_conv3, "conv_layer3/biases")
        h_conv3 = tf.nn.relu(conv2d(h_pool2, W_conv3) + b_conv3)
        tf.summary.image("conv_layer3/images", h_conv3[:, :, :, 0:1], max_outputs=6)

    h_conv3_flat = tf.reshape(h_conv3, [-1, 8 * 8 * 64])

    with tf.name_scope("fc_layer1"):
        W_fc1 = weight_variable([8 * 8 * 64, 384])
        variable_summaries(W_fc1, "fc_layer1/weights")
        b_fc1 = bias_variable([384])
        variable_summaries(b_fc1, "fc_layer1/biases")
        h_fc1 = tf.nn.relu(tf.matmul(h_conv3_flat, W_fc1) + b_fc1)

    with tf.name_scope("fc_layer2"):
        W_fc2 = weight_variable([384, 192])
        variable_summaries(W_fc2, "fc_layer2/weights")
        b_fc2 = bias_variable([192])
        variable_summaries(b_fc2, "fc_layer2/biases")
        h_fc2 = tf.nn.relu(tf.matmul(h_fc1, W_fc2) + b_fc2)

    with tf.name_scope("output"):
        W_fc3 = weight_variable([192, 10])
        variable_summaries(W_fc3, "output/weights")
        b_fc3 = bias_variable([10])
        variable_summaries(b_fc3, "output/biases")
        y_conv = tf.matmul(h_fc2, W_fc3) + b_fc3

    global_step = tf.Variable(0, trainable=False)
    starter_learning_rate = 0.0001
    learning_rate = tf.train.exponential_decay(
        starter_learning_rate, global_step, 200, 0.1, staircase=True)

    cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(y_conv, y_))
    tf.summary.scalar('loss', cross_entropy)
    train_step = tf.train.AdamOptimizer(learning_rate).minimize(cross_entropy, global_step=global_step)
    correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    sess = tf.InteractiveSession()

    merged = tf.summary.merge_all()
    train_writer = tf.summary.FileWriter('train', sess.graph)

    sess.run(tf.global_variables_initializer())

    for i in range(200):
        batch = cifar10.train.next_batch(128)
        if i % 100 == 0:
            train_accuracy = accuracy.eval(feed_dict={
                x: cifar10.test.images, y_: cifar10.test.labels})
            print("step %d, training accuracy %g" % (i, train_accuracy))
        summary, _ = sess.run([merged, train_step], feed_dict={x: batch[0], y_: batch[1]})
        train_writer.add_summary(summary, i)

    print("test accuracy %g" % accuracy.eval(feed_dict={
        x: cifar10.test.images, y_: cifar10.test.labels}))


if __name__ == '__main__':
    tf.app.run(main=main)

"""A convolutional neural network for CIFAR-10 classification.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import cifar
import tensorflow as tf


def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.05)
    return tf.Variable(initial)


def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)


def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')


def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                          strides=[1, 2, 2, 1], padding='SAME')


def variable_summaries(var, name):
    """Attach a lot of summaries to a Tensor."""
    with tf.name_scope('summaries'):
        mean = tf.reduce_mean(var)
        tf.summary.scalar('mean/' + name, mean)
    with tf.name_scope('stddev'):
        stddev = tf.sqrt(tf.reduce_mean(tf.square(var - mean)))
        tf.summary.scalar('stddev/' + name, stddev)
        tf.summary.scalar('max/' + name, tf.reduce_max(var))
        tf.summary.scalar('min/' + name, tf.reduce_min(var))
        tf.summary.histogram(name, var)


def main(_):
    cifar10 = cifar.Cifar()
    cifar10.ReadDataSets(one_hot=True)

    # Create the model
    x = tf.placeholder(tf.float32, [None, 3072])

    # Define loss and optimizer
    y_ = tf.placeholder(tf.float32, [None, 10])

    x_image = tf.reshape(x, [-1, 32, 32, 3])

    tf.summary.image("images", x_image, max_outputs=6)

    # (32 - 3 + 2 * 1) / 1 +1 = 32
    with tf.name_scope("conv_layer1"):
        W_conv1 = weight_variable([5, 5, 3, 32])
        variable_summaries(W_conv1, "conv_layer1/weights")
        b_conv1 = bias_variable([32])
        variable_summaries(b_conv1, "conv_layer1/biases")
        h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
        h_pool1 = max_pool_2x2(h_conv1)
        tf.summary.image("conv_layer1/images", h_pool1[:, :, :, 0:1], max_outputs=6)

    with tf.name_scope("conv_layer2"):
        W_conv2 = weight_variable([5, 5, 32, 64])
        variable_summaries(W_conv2, "conv_layer2/weights")
        b_conv2 = bias_variable([64])
        variable_summaries(b_conv2, "conv_layer2/biases")
        h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
        h_pool2 = max_pool_2x2(h_conv2)
        tf.summary.image("conv_layer2/images", h_pool2[:, :, :, 0:1], max_outputs=6)

    with tf.name_scope("conv_layer3"):
        W_conv3 = weight_variable([5, 5, 64, 64])
        variable_summaries(W_conv3, "conv_layer3/weights")
        b_conv3 = bias_variable([64])
        variable_summaries(b_conv3, "conv_layer3/biases")
        h_conv3 = tf.nn.relu(conv2d(h_pool2, W_conv3) + b_conv3)
        tf.summary.image("conv_layer3/images", h_conv3[:, :, :, 0:1], max_outputs=6)

    h_conv3_flat = tf.reshape(h_conv3, [-1, 8 * 8 * 64])

    with tf.name_scope("fc_layer1"):
        W_fc1 = weight_variable([8 * 8 * 64, 384])
        variable_summaries(W_fc1, "fc_layer1/weights")
        b_fc1 = bias_variable([384])
        variable_summaries(b_fc1, "fc_layer1/biases")
        h_fc1 = tf.nn.relu(tf.matmul(h_conv3_flat, W_fc1) + b_fc1)

    with tf.name_scope("fc_layer2"):
        W_fc2 = weight_variable([384, 192])
        variable_summaries(W_fc2, "fc_layer2/weights")
        b_fc2 = bias_variable([192])
        variable_summaries(b_fc2, "fc_layer2/biases")
        h_fc2 = tf.nn.relu(tf.matmul(h_fc1, W_fc2) + b_fc2)

    with tf.name_scope("output"):
        W_fc3 = weight_variable([192, 10])
        variable_summaries(W_fc3, "output/weights")
        b_fc3 = bias_variable([10])
        variable_summaries(b_fc3, "output/biases")
        y_conv = tf.matmul(h_fc2, W_fc3) + b_fc3

    global_step = tf.Variable(0, trainable=False)
    starter_learning_rate = 0.0001
    learning_rate = tf.train.exponential_decay(
        starter_learning_rate, global_step, 200, 0.1, staircase=True)

    cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(y_conv, y_))
    tf.summary.scalar('loss', cross_entropy)
    train_step = tf.train.AdamOptimizer(learning_rate).minimize(cross_entropy, global_step=global_step)
    correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    sess = tf.InteractiveSession()

    merged = tf.summary.merge_all()
    train_writer = tf.summary.FileWriter('train', sess.graph)

    sess.run(tf.global_variables_initializer())

    for i in range(200):
        batch = cifar10.train.next_batch(128)
        if i % 100 == 0:
            train_accuracy = accuracy.eval(feed_dict={
                x: cifar10.test.images, y_: cifar10.test.labels})
            print("step %d, training accuracy %g" % (i, train_accuracy))
        summary, _ = sess.run([merged, train_step], feed_dict={x: batch[0], y_: batch[1]})
        train_writer.add_summary(summary, i)

    print("test accuracy %g" % accuracy.eval(feed_dict={
        x: cifar10.test.images, y_: cifar10.test.labels}))


if __name__ == '__main__':
    tf.app.run(main=main)
