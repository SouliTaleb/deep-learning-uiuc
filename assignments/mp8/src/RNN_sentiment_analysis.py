"""
Bag of Words model sentiment analysis.

Part 3 - Language Model
    3c - Learning Sentiment

@author: Zhenye Na
@credit: Logan Courtney
"""


import numpy as np
import torch
import torch.optim as optim

import time
import io

from torch.autograd import Variable
from RNN_model import RNN_model

# imdb_dictionary = np.load('../preprocessed_data/imdb_dictionary.npy')
vocab_size = 8000

x_train = []
with io.open('../preprocessed_data/imdb_train.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for line in lines:
    line = line.strip()
    line = line.split(' ')
    line = np.asarray(line, dtype=np.int)

    line[line > vocab_size] = 0

    x_train.append(line)
x_train = x_train[0:25000]
y_train = np.zeros((25000,))
y_train[0:12500] = 1


x_test = []
with io.open('../preprocessed_data/imdb_test.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for line in lines:
    line = line.strip()
    line = line.split(' ')
    line = np.asarray(line, dtype=np.int)

    line[line > vocab_size] = 0

    x_test.append(line)
y_test = np.zeros((25000,))
y_test[0:12500] = 1


vocab_size += 1

# no_of_hidden_units is 500
model = RNN_model(vocab_size, 500)

language_model = torch.load('language.model')
model.embedding.load_state_dict(language_model.embedding.state_dict())
model.lstm1.lstm.load_state_dict(language_model.lstm1.lstm.state_dict())
model.bn_lstm1.load_state_dict(language_model.bn_lstm1.state_dict())
model.lstm2.lstm.load_state_dict(language_model.lstm2.lstm.state_dict())
model.bn_lstm2.load_state_dict(language_model.bn_lstm2.state_dict())
model.lstm3.lstm.load_state_dict(language_model.lstm3.lstm.state_dict())
model.bn_lstm3.load_state_dict(language_model.bn_lstm3.state_dict())
model.cuda()


params = []
for param in model.embedding.parameters():
    params.append(param)
for param in model.lstm1.parameters():
    params.append(param)
for param in model.bn_lstm1.parameters():
    params.append(param)
for param in model.lstm2.parameters():
    params.append(param)
for param in model.bn_lstm2.parameters():
    params.append(param)
for param in model.lstm3.parameters():
    params.append(param)
for param in model.bn_lstm3.parameters():
    params.append(param)
for param in model.fc_output.parameters():
    params.append(param)


opt = 'adam'
LR = 0.001
if opt == 'adam':
    optimizer = optim.Adam(params, lr=LR)
elif opt == 'sgd':
    optimizer = optim.SGD(params, lr=LR, momentum=0.9)

batch_size = 200
no_of_epochs = 25
L_Y_train = len(y_train)
L_Y_test = len(y_test)

model.train()

train_loss = []
train_accu = []
test_accu = []


# training
for epoch in range(no_of_epochs):

    # training
    model.train()

    epoch_acc = 0.0
    epoch_loss = 0.0

    epoch_counter = 0

    time1 = time.time()

    I_permutation = np.random.permutation(L_Y_train)

    for i in range(0, L_Y_train, batch_size):

        x_input2 = [x_train[j] for j in I_permutation[i:i + batch_size]]
        sequence_length = 250
        x_input = np.zeros((batch_size, sequence_length), dtype=np.int)
        for j in range(batch_size):
            x = np.asarray(x_input2[j])
            sl = x.shape[0]
            if(sl < sequence_length):
                x_input[j, 0:sl] = x
            else:
                start_index = np.random.randint(sl - sequence_length + 1)
                x_input[j, :] = x[start_index:(start_index + sequence_length)]
        y_input = y_train[I_permutation[i:i + batch_size]]

        data = Variable(torch.LongTensor(x_input)).cuda()
        target = Variable(torch.FloatTensor(y_input)).cuda()

        optimizer.zero_grad()
        loss, pred = model(data, target, train=True)
        loss.backward()
        optimizer.step()  # update weights

        prediction = pred >= 0.0
        truth = target >= 0.5
        acc = prediction.eq(truth).sum().cpu().data.numpy()
        epoch_acc += acc
        epoch_loss += loss.data.item()
        epoch_counter += batch_size

    epoch_acc /= epoch_counter
    epoch_loss /= (epoch_counter / batch_size)

    train_loss.append(epoch_loss)
    train_accu.append(epoch_acc)

    print(epoch, "%.2f" % (epoch_acc * 100.0), "%.4f" %
          epoch_loss, "%.4f" % float(time.time() - time1))

    if epoch + 1 % 3 == 0:
        # test
        sequence_length = 200
        model.eval()

        epoch_acc = 0.0
        epoch_loss = 0.0

        epoch_counter = 0

        time1 = time.time()

        I_permutation = np.random.permutation(L_Y_test)

        for i in range(0, L_Y_test, batch_size):

            x_input = [x_test[j] for j in I_permutation[i:i + batch_size]]
            y_input = np.asarray(
                [y_test[j] for j in I_permutation[i:i + batch_size]], dtype=np.int)
            target = Variable(torch.FloatTensor(y_input)).cuda()

            with torch.no_grad():
                loss, pred = model(x_input, target)

            prediction = pred >= 0.0
            truth = target >= 0.5
            acc = prediction.eq(truth).sum().cpu().data.numpy()
            epoch_acc += acc
            epoch_loss += loss.data.item()
            epoch_counter += batch_size

        epoch_acc /= epoch_counter
        epoch_loss /= (epoch_counter / batch_size)

        test_accu.append(epoch_acc)

        time2 = time.time()
        time_elapsed = time2 - time1

        print("  ", "%.2f" % (epoch_acc * 100.0), "%.4f" % epoch_loss)


torch.save(model, 'rnn_language.model')
data = [train_loss, train_accu, test_accu]
data = np.asarray(data)
np.save('data.npy', data)
