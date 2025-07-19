from keras.datasets import boston_housing
from keras.models import Sequential
from keras.layers import Dense
from sklearn.preprocessing import StandardScaler
# Loading and preprocessing the data
(x_train, y_train), (x_test, y_test) = boston_housing.load_data()
scaler = StandardScaler()
x_train_scaled = scaler.fit_transform(x_train)
x_test_scaled = scaler.transform(x_test)
# Building the neural network model
model = Sequential()
model.add(Dense(64, activation='relu', input_shape=(x_train.shape[1],)))
model.add(Dense(64, activation='relu'))
model.add(Dense(1))
# Compiling the model
model.compile(optimizer='adam', loss='mse', metrics=['mae'])
model.fit(x_train_scaled, y_train, epochs=100, batch_size=8, validation_split=0.2)
# Evaluating the model
test_loss, test_mae = model.evaluate(x_test_scaled, y_test)
print('Test MAE:', test_mae)