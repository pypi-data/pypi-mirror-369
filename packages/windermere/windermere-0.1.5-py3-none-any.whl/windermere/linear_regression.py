import numpy as np

# Suppose we have m rows and n features
class LinearRegression:
    def __init__(self, n_features, learning_rate=0.01) -> None:
        """inititalises LinearRegression object. Parameters are modelled as an (n_features + 1, 1) column vector"""
        self.n_features = n_features
        self.learning_rate = learning_rate
        self.theta = np.zeros((self.n_features + 1, 1))
    
    def predict(self, x: np.ndarray) -> np.ndarray:
        """x is an (m,n) matrix, returns an (m,1) column vector of predictions"""
        X = np.c_[np.ones((x.shape[0], 1)), x] # X is now a (m,n+1) matrix
        return X @ self.theta # returns an (m,1) column vector of predictions
    
    def gradient_descent(self, X_train: np.ndarray, y_train: np.ndarray, max_epochs=10000, tolerance=1e-6) -> None:
        """X_train is an (m,n) matrix, y_train is an (m,1) column vector of true values"""
        X = np.c_[np.ones((X_train.shape[0], 1)), X_train] # X is now a (m,n+1) matrix
        m = len(X_train)
        y = y_train # y is an (m,1) column vector of true values
        for _ in range(max_epochs):
            previous_theta = self.theta.copy() # create a copy of current parameters
            gradient = (X.T @ ((X @ self.theta) - y)) / m # gradient is the gradient vector of J(theta), shape = (n_features+1,1), so same dimensions as self.theta, hence why we can subtract them
            self.theta -= self.learning_rate * gradient # update the parameters

            if np.linalg.norm(previous_theta - self.theta) < tolerance: # if the parameters have barely changed, i.e. converged, then end algorithm
                break
    
    def normal_equation(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """X_train is an (m,n) matrix, y_train is an (m,1) column vector of true values"""
        X = np.c_[np.ones((X_train.shape[0], 1)), X_train] # X is now a (m,n+1) matrix
        y = y_train
        self.theta = (np.linalg.inv( (X.T @ X) )) @ (X.T @ y) # shape works out to a (n+1,1) column vector, exactly the shape of self.theta
    
    def reset_parameters(self) -> None:
        """resets all parameter values to zero, useful when you want to try both gradient descent and the normal equation"""
        self.theta = np.zeros((self.n_features + 1, 1))
    
    def test_model(self, X_test: np.ndarray, y_test: np.ndarray) -> tuple[float, float, float]:
        """X_test is an (m,n) matrix, y_test is an (m,1) column vector of true values, returns (MSE, RMSE, R2) values"""
        m = len(X_test)
        total_squared_error: float = 0
        total_sum_squares: float = 0
        predictions = self.predict(X_test) # predictions is an (m,1) column vector of predictions
        y = y_test
        y_mean: float = np.mean(y)
        for i in range(m):
            total_squared_error += (y[i][0] - predictions[i][0])**2 # this gets the squared difference of prediction and true value
            total_sum_squares += (y[i][0] - y_mean)**2 # this gets the squared differnece between true value and the mean of the true values

        
        mean_squared_error = total_squared_error / m
        root_mean_squared_error = np.sqrt(mean_squared_error)
        r_squared = 1 - (total_squared_error / total_sum_squares)
        return (mean_squared_error, root_mean_squared_error, r_squared)
    
    def __str__(self) -> str:
        return f"n_features = {self.n_features}, learning_rate = {self.learning_rate}, theta = {self.theta}"
