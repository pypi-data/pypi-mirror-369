import numpy as np

# Suppose we have m rows and n features
# TODO implement newton raphsons method
class LogisticRegression:
    def __init__(self, n_features, learning_rate=0.01, threshold=0.5):
        """inititalises LogisticRegression object. Parameters are modelled as an (n_features + 1, 1) column vector"""
        self.n_features = n_features
        self.learning_rate = learning_rate
        self.threshold = threshold
        self.theta = np.zeros((n_features + 1, 1))
    
    def sigmoid(self, z: np.ndarray) -> np.ndarray:
        """z should be an (m, 1) column vector of probabilities, returns sigmoid(z), shape = (m, 1)"""
        return 1 / (1 + np.exp(-z))
    
    def get_probabilities(self, x: np.ndarray) -> np.ndarray:
        """x is an (m,n) matrix, returns an (m,1) column vector of probabilities"""
        X = np.c_[np.ones((x.shape[0], 1)), x] # X is now an (m, n+1) matrix
        linear_prediction = X @ self.theta # (m, 1) vector of linear predictions of each feature vector
        return self.sigmoid(linear_prediction) # (m, 1) vector of probabilities
    
    def predict_class(self, x: np.ndarray) -> np.ndarray:
        """x should be an (m,n) matrix, returns an (m, 1) column vector of 0's or 1's"""
        probabilities = self.get_probabilities(x) # (m, 1) column vector of probabilities
        return (probabilities > self.threshold).astype(float) # (m, 1) column vector of 0's or 1's
    
    def gradient_descent(self, X_train: np.ndarray, y_train: np.ndarray, max_epochs=10000, tolerance=1e-6) -> None:
        """X_train is an (m,n) matrix, y_train is an (m,1) column vector of true values"""
        X = np.c_[np.ones((X_train.shape[0], 1)), X_train] # X is now a (m,n+1) matrix
        m = len(X_train)
        y = y_train # y is an (m,1) column vector of true values
        for _ in range(max_epochs):
            previous_theta = self.theta.copy()
            gradient = (X.T @ (self.sigmoid(X @ self.theta) - y)) / m
            self.theta -= self.learning_rate * gradient

            if np.linalg.norm(previous_theta - self.theta) < tolerance:
                break
        
    def test_model(self, X_test: np.ndarray, y_test: np.ndarray) -> float:
        """X_test is an (m,n) matrix, y_test is an (m,1) column vector of true values, returns the accuracy of the model"""
        correct_count = 0
        predictions = self.predict_class(X_test) # (m, 1) column vector of 0's or 1's
        y = y_test
        for i in range(len(predictions)):
            if predictions[i][0] == y[i][0]:
                correct_count += 1
        
        accuracy = correct_count / len(predictions)
        return accuracy
    
    def __str__(self) -> str:
        return f"n_features = {self.n_features}, learning_rate = {self.learning_rate}, threshold = {self.threshold}, theta = {self.theta}"