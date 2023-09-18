# -*- coding: utf-8 -*-
"""dynamic pricing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pMuvzwELNm1DsTdL5dfBdA2HCjB6uwgh
"""

# Commented out IPython magic to ensure Python compatibility.
import datetime

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
# %matplotlib inline

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score

dataset = pd.read_csv("Pop_Data.csv")
dataset.head(5)

X_train, X_test, y_train, y_test = train_test_split(dataset.iloc[:, :-1],
                                                    dataset.iloc[:, -1],
                                                    test_size = 0.3,
                                                    random_state = 42)

X_train.info()

"""# EDA"""

X_train = X_train.iloc[:, 3:]
X_test = X_test.iloc[:, 3:]

X_train.info

plt.figure(figsize = (12, 8))
plot = sns.countplot(x = 'day_of_week', data = X_train)
plt.xticks(rotation = 90)
for p in plot.patches:
    plot.annotate(p.get_height(),
                        (p.get_x() + p.get_width() / 2.0,
                         p.get_height()),
                        ha = 'center',
                        va = 'center',
                        xytext = (0, 5),
                        textcoords = 'offset points')

plt.title("Price changes based on day")
plt.xlabel("Day")
plt.ylabel("Price")

print(sum(X_train["day_of_week"].isnull()))
print(sum(X_test["day_of_week"].isnull()))

print(sum(X_train["hour_of_day"].isnull()))
print(sum(X_test["hour_of_day"].isnull()))

print(sum(X_train["popularity_percent_normal"].isnull()))
print(sum(X_test["popularity_percent_normal"].isnull()))

X_train["popularity_percent_normal"].fillna(X_train["popularity_percent_normal"].astype("float64").mean(), inplace = True)

X_train = pd.get_dummies(X_train,
                         columns = ["day_of_week"],
                         drop_first = True)

X_test = pd.get_dummies(X_test,
                         columns = ["day_of_week"],
                         drop_first = True)

missing_cols = set(X_train.columns) - set(X_test.columns)
for col in missing_cols:
    X_test[col] = 0
X_test = X_test[X_train.columns]

standardScaler = StandardScaler()
standardScaler.fit(X_train)
X_train = standardScaler.transform(X_train)
X_test = standardScaler.transform(X_test)

linearRegression = LinearRegression()
linearRegression.fit(X_train, y_train)
y_pred = linearRegression.predict(X_test)
r2_score(y_test, y_pred)

rf = RandomForestRegressor(n_estimators = 100)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)
r2_score(y_test, y_pred)

"""# RNN"""

data = dataset.iloc[:, 3:]
data.info()

train_data, test_data = train_test_split(data.iloc[:, :-1],
                                                    test_size = 0.3,
                                                    random_state = 42)





train_data = pd.get_dummies(train_data,
                         columns = ["day_of_week"],
                         drop_first = True)
test_data = pd.get_dummies(test_data,
                         columns = ["day_of_week"],
                         drop_first = True)

from sklearn.preprocessing import MinMaxScaler

scaler=MinMaxScaler(feature_range=(0,1))
scaled_train_data=scaler.fit_transform(train_data)



X_train=[]
y_train=[]
for i in range(len(scaled_train_data)):
    print(scaled_train_data[i])
    # X_train.append(scaled_train_data[i-90:i,0])
    # y_train.append(scaled_train_data[i,0])

#Converting the data to the numpy array as it is expected by our RNN model
X_train=np.array(X_train)
y_train=np.array(y_train)

#Reshaping
X_train=np.reshape(X_train,(X_train.shape[0],X_train.shape[1],1))

#builiding the model
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout

#Intialising the model
model=Sequential()

#First layer
model.add(LSTM(units=40,return_sequences=True,input_shape=(X_train.shape[1],1)))
model.add(Dropout(0.2))
#Second layer
model.add(LSTM(units=40,return_sequences=True))
model.add(Dropout(0.2))
#Third layer
model.add(LSTM(units=40,return_sequences=True))
model.add(Dropout(0.2))
#Fourth Layer
model.add(LSTM(units=40,return_sequences=False))
model.add(Dropout(0.2))
#Output Layer
model.add(Dense(1))

#compiling the model
model.compile(optimizer='adam',loss='mean_squared_error')

#fitting the model on our dataset
model.fit(X_train,y_train,epochs=50,batch_size=32)

scaled_test_data=scaler.fit_transform(test_data)

X_test=np.array(X_test)
X_test=X_test.reshape(X_test.shape[0],X_test.shape[1],1)

#Getting the stock price of previous 60 days
X_test=[]
for i in range(90,len(test_data)):
    X_test.append(test_data[i-90:i,0])
X_test=np.array(X_test)
X_test=X_test.reshape(X_test.shape[0],X_test.shape[1],1)

