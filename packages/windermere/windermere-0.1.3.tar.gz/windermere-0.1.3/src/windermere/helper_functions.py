import numpy as np
import matplotlib.pyplot as plt
from linear_regression import LinearRegression

def min_max_normalize(data: np.ndarray) -> np.ndarray:
    """returns normalized data, with all values between 0 and 1."""
    min_, max_ = np.min(data), np.max(data)
    return (data - min_) / (max_ - min_)

def inverse_min_max_normalize(normalized_predictions: np.ndarray, y_train: np.ndarray) -> np.ndarray:
    """undoes the min max normalization to the predictions"""
    min_, max_ = np.min(y_train), np.max(y_train)
    return (normalized_predictions * (max_ - min_)) + min_

def train_test_split(training_data: np.ndarray, testing_data: np.ndarray, print_shapes=False) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """training_data should be an (m,n) matrix, testing_data should be an (m,n) matrix, returns X_train, y_train, X_test, y_test"""
    n_training_rows = len(training_data)
    n_testing_rows = len(testing_data)

    X_train = training_data[:, :-1] # get all the rows and all columns except the last
    y_train = training_data[:, -1].reshape(n_training_rows, 1)
    X_test = testing_data[:, :-1]
    y_test = testing_data[:, -1].reshape(n_testing_rows, 1)

    if print_shapes:
        print(f"X_train shape = {X_train.shape}")
        print(f"y_train shape = {y_train.shape}")
        print(f"X_test shape = {X_test.shape}")
        print(f"y_test shape = {y_test.shape}") 
    
    return (X_train, y_train, X_test, y_test)

def visualise_linear_regression_model(model: LinearRegression, X_test: np.ndarray, y_test: np.ndarray):
    """model is your linear regression object, X_test should be an (m,n) matrix, y_test should be a (m, 1) column vector of true values.
       returns either a matplotlib figure object, axes object or an string error message"""
    
    n_features = model.n_features
    if n_features > 2 or n_features == 0:
        return "Unable to visualise this data"
    
    elif n_features == 1:
        plot = plt.figure(figsize=(8,3))
        theta_0, theta_1 = model.theta[0][0], model.theta[1][0]
        x_min, x_max = np.min(X_test), np.max(X_test)
        x = np.linspace(x_min, x_max, 10000)
        y = theta_0 + theta_1 * x
        plt.plot(x, y, color="red", label="prediction")
        plt.legend(loc="upper center")
        plt.scatter(X_test, y_test, s=1)
        return plot
    
    elif n_features == 2:
        ax = plt.axes(projection="3d")
        theta_0, theta_1, theta_2 = model.theta[0][0], model.theta[1][0], model.theta[2][0]
        x1_min, x1_max = np.min(X_test[:, 0]), np.max(X_test[:, 0])
        x2_min, x2_max = np.min(X_test[:, 1]), np.max(X_test[:, 1])
        x1 = np.linspace(x1_min, x1_max, 10000)
        x2 = np.linspace(x2_min, x2_max, 10000)
        X1, X2 = np.meshgrid(x1, x2)
        y = theta_0 + theta_1 * X1 + theta_2 * X2
        ax.plot_surface(X1, X2, y, color="red", label="prediction", alpha=0.6)
        ax.legend(loc="upper center")
        ax.scatter(X_test[:, 0], X_test[:, 1], y_test.flatten(), s=1)
        return ax