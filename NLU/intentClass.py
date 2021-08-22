# Training data from https://curiousily.com/posts/intent-recognition-with-bert-using-keras-and-tensorflow-2/
# gdown --id 1OlcvGWReJMuyYQuOZm149vHWwPtlboR6 --output train.csv
# gdown --id 1Oi5cRlTybuIF2Fl5Bfsr-KkqrXrdt77w --output valid.csv
# gdown --id 1ep9H6-HvhB4utJRLVcLzieWNUSG3P_uF --output test.csv
# Other links
# https://medium.com/@nutanbhogendrasharma/step-by-step-intent-recognition-with-bert-1473202b8597
# https://analyticsindiamag.com/how-to-implement-intent-recognition-with-bert/
# https://analyticsindiamag.com/multi-class-text-classification-in-pytorch-using-torchtext/
# https://github.com/practical-nlp/practical-nlp/blob/master/Ch6/02_BERT_ATIS.ipynb
# https://stackoverflow.com/questions/44213549/python-nlp-intent-identification
#   http://docs.deeppavlov.ai/en/master/features/skills/odqa.html
#   https://github.com/explosion/spaCy/blob/v2.3.x/examples/training/train_intent_parser.py
# https://stackoverflow.com/questions/56064650/multi-intent-natural-language-processing-and-classification
# https://towardsdatascience.com/multi-label-intent-classification-1cdd4859b93
# https://medium.com/bhavaniravi/intent-classification-demystifying-rasanlu-part-4-685fc02f5c1d



import os
import datetime

import numpy as np
import pandas as pd
import tqdm
import tensorflow as tf

from matplotlib.ticker import MaxNLocator
from sklearn.metrics import classification_report, confusion_matrix
import seaborn

from tensorflow import keras
import matplotlib.pyplot as plt

from bert import BertModelLayer
from bert.loader import StockBertConfig, map_stock_config_to_params, load_stock_weights
from bert.tokenization.bert_tokenization import FullTokenizer

BERT_MODEL_HUB = "https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/4"
BERT_MODEL_NAME = "uncased_L-12_H-768_A-12"  # BERT Base Uncased from BERT GitHub(Googleapis Storage)

bert_ckpt_dir = os.path.join("model/", BERT_MODEL_NAME)
bert_ckpt_file = os.path.join(bert_ckpt_dir, "bert_model.ckpt")
bert_config_file = os.path.join(bert_ckpt_dir, "bert_config.json")


class IntentData:
    DATA_COLUMN = "text"
    LABEL_COLUMN = "intent"

    def __init__(self, train, test, tokenizer: FullTokenizer, classes, max_seq_len=192):
        self.tokenizer = tokenizer
        self.max_seq_len = 0
        self.classes = classes

        ((self.x_train, self.y_train), (self.x_test, self.y_test)) = map(self._prepare, [train, test])

        print("max seq_len", self.max_seq_len)
        self.max_seq_len = min(self.max_seq_len, max_seq_len)
        self.x_train, self.x_test = map(self._pad, [self.x_train, self.x_test])

    def _prepare(self, df):
        x, y = [], []

        for _, row in tqdm.tqdm(df.iterrows()):
            text, label = row[IntentData.DATA_COLUMN], row[IntentData.LABEL_COLUMN]
            tokens = self.tokenizer.tokenize(text)
            tokens = ["[CLS]"] + tokens + ["[SEP]"]
            token_ids = self.tokenizer.convert_tokens_to_ids(tokens)
            self.max_seq_len = max(self.max_seq_len, len(token_ids))
            x.append(token_ids)
            y.append(self.classes.index(label))

        return np.array(x), np.array(y)

    def _pad(self, ids):
        x = []
        for input_ids in ids:
            input_ids = input_ids[:min(len(input_ids), self.max_seq_len - 2)]
            input_ids = input_ids + [0] * (self.max_seq_len - len(input_ids))
            x.append(np.array(input_ids))
        return np.array(x)


def create_model(classes, max_seq_len, bert_ckpt_file):
    with tf.io.gfile.GFile(bert_config_file, "r") as r:
        bc = StockBertConfig.from_json_string(r.read())
        bert_parm = map_stock_config_to_params(bc)
        bert_parm.adapter_size = None
        bert = BertModelLayer.from_params(bert_parm, name="bert")

    input_ids = keras.layers.Input(shape=(max_seq_len,), dtype='int32', name="input_ids")
    bert_output = bert(input_ids)

    print("bert shape", bert_output.shape)

    cls_out = keras.layers.Lambda(lambda seq: seq[:, 0, :])(bert_output)
    cls_out = keras.layers.Dropout(0.5)(cls_out)
    logits = keras.layers.Dense(units=768, activation="tanh")(cls_out)
    logits = keras.layers.Dropout(0.5)(logits)
    logits = keras.layers.Dense(units=len(classes), activation="softmax")(logits)

    model = keras.Model(inputs=input_ids, outputs=logits)
    model.build(input_shape=(None, max_seq_len))

    load_stock_weights(bert, bert_ckpt_file)

    return model


# Training

train = pd.read_csv("data/train.csv")
valid = pd.read_csv("data/valid.csv")
test = pd.read_csv("data/test.csv")
train = train.append(valid).reset_index(drop=True)

tokenizer = FullTokenizer(vocab_file=os.path.join(bert_ckpt_dir, "vocab.txt"))
classes = train.intent.unique().tolist()
print(classes)

data = IntentData(train, test, tokenizer, classes, max_seq_len=128)

print(
    f'Shape check:\nX_train: {data.x_train.shape} X_test: {data.x_test.shape}\nY_train: {data.y_train.shape} Y_test: {data.y_test.shape}')
print(f'Data max sequence length: {data.max_seq_len}')

model = create_model(classes, data.max_seq_len, bert_ckpt_file)
model.summary()

model.compile(optimizer=keras.optimizers.Adam(1e-5), loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=[keras.metrics.SparseCategoricalAccuracy(name="acc")])

# log_dir = "log/intent_detection/" +\
# datetime.datetime.now().strftime("%Y%m%d-%H%M%s")
# tensorboard_callback = keras.callbacks.TensorBoard(log_dir=log_dir)
tensor_earlystop = keras.callbacks.EarlyStopping(verbose=1, patience=2)
cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath="checkpoints/training/cp-{epoch:04d}.ckpt",
                                                 save_weights_only=True,
                                                 verbose=1)

history = model.fit(
    x=data.x_train,
    y=data.y_train,
    validation_split=0.1,
    batch_size=16,
    shuffle=True,
    epochs=10,
    callbacks=[tensor_earlystop]
)

ax = plt.figure().gca()
ax.xaxis.set_major_locator(MaxNLocator(integer=True))

ax.plot(history.history['loss'])
ax.plot(history.history['val_loss'])
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['train', 'test'])
plt.title('Loss over training epochs')
plt.show()

ax = plt.figure().gca()
ax.xaxis.set_major_locator(MaxNLocator(integer=True))

ax.plot(history.history['acc'])
ax.plot(history.history['val_acc'])
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['train', 'test'])
plt.title('Accuracy over training epochs')
plt.show()

_, train_acc = model.evaluate(data.x_train, data.y_train)
_, test_acc = model.evaluate(data.x_test, data.y_test)

print("train acc", train_acc)
print("test acc", test_acc)
print(history.history)

model.save_weights('checkpoints/training/final_checkpoint')
model.save('checkpoints/saved_model_' + datetime.datetime.now().strftime("%Y%m%d-%H%M%s"))

y_pred = model.predict(data.x_test).argmax(axis=-1)
print(classification_report(data.y_test, y_pred, target_names=classes))

cm = confusion_matrix(data.y_test, y_pred)
df_cm = pd.DataFrame(cm, index=classes, columns=classes)
hmap = seaborn.heatmap(df_cm, annot=True, fmt="d")
hmap.yaxis.set_ticklabels(hmap.yaxis.get_ticklabels(), rotation=0, ha='right')
hmap.xaxis.set_ticklabels(hmap.xaxis.get_ticklabels(), rotation=30, ha='right')
plt.ylabel('True label')
plt.xlabel('Predicted label')
plt.show()

sentence = ["Play our song now", "When is new years?", "How is the weather in California?"]

pred_tokens = map(tokenizer.tokenize, sentence)
pred_tokens = map(lambda tok: ["[CLS]"] + tok + ["[SEP]"], pred_tokens)
pred_token_ids = list(map(tokenizer.convert_tokens_to_ids, pred_tokens))

pred_token_ids = map(lambda tids: tids + [0] * (data.max_seq_len - len(tids)), pred_token_ids)
pred_token_ids = np.array(list(pred_token_ids))

prediction = model.predict(pred_token_ids)
print(prediction)  # confidence by class

for text, label in zip(sentence, prediction.argmax(axis=-1)):
    print("Text:", text, "\nIntent:", classes[label])
    print()