import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import LeaveOneOut
from sklearn import svm
import numpy as np
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score

"""df_train = pd.read_csv("train_data.csv")
X_train = df_train.iloc[:, 2:]
Y_train = (df_train['genre_id'] == "action").astype(int)

df_test = pd.read_csv("test_data.csv")
X_test = df_test.iloc[:, 2:]
Y_test = (df_test['genre_id'] == "action").astype(int)"""

df = pd.read_csv("C:\\know_your_genre_magshimim\\features_MI_table.csv")

dataset_train, dataset_test = train_test_split(df, test_size=0.3, random_state=42)

X_test = dataset_test.iloc[:, 3:]
Y_test = (dataset_test['genre_id'] == "action").astype(int)

X_train = dataset_train.iloc[:, 3:]
Y_train = (dataset_train['genre_id'] == "action").astype(int)

clf = svm.SVC()
clf.fit(X_train, Y_train)

pred = clf.predict(X_test)

print(np.mean((pred == Y_test).astype(int)))
print(f1_score(Y_test, pred, zero_division=1))
ax = sns.heatmap(confusion_matrix(Y_test, pred), annot=True, cmap='Blues')

ax.set_title('Seaborn Confusion Matrix with labels\n\n')
ax.set_xlabel('\nPredicted Values')
ax.set_ylabel('Actual Values ')


ax.xaxis.set_ticklabels(['horror','action'])
ax.yaxis.set_ticklabels(['horror','action'])
plt.title("without loo")
plt.figure()

#-----------------------------------------------------------------------------------------------------------------------
# loo

df = pd.read_csv("C:\\know_your_genre_magshimim\\features_MI_table.csv")
features = df.iloc[:, 3:]

X = df.iloc[:, 3:]
y = (df['genre_id'] == "action").astype(int)
loo = LeaveOneOut()
resultes = []

for train_index, test_index in loo.split(X):
    X_train = X.drop(test_index,axis=0)
    X_test = X.iloc[test_index]
    y_train = y.drop(test_index,axis=0)
    y_test = y.iloc[test_index]
    clf = svm.SVC()
    clf.fit(X_train, y_train)
    resultes.extend(clf.predict(X_test))

print(np.mean((resultes == y).astype(int)))

print(confusion_matrix(y, resultes))

print(f1_score(y, resultes, zero_division=1))

ax = sns.heatmap(confusion_matrix(y, resultes), annot=True, cmap='Blues')

ax.set_title('Seaborn Confusion Matrix with labels\n\n')
ax.set_xlabel('\nPredicted Values')
ax.set_ylabel('Actual Values ')

## Ticket labels - List must be in alphabetical order
ax.xaxis.set_ticklabels(['horror','action'])
ax.yaxis.set_ticklabels(['horror','action'])
plt.title("with loo")
plt.show()
