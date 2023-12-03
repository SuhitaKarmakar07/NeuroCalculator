import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, QTimer
import serial
from sklearn.preprocessing import StandardScaler
from random import randint, choice, random
#import tensorflow as tf
from tensorflow.keras.models import load_model

class CalculatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_serial_communication()

    def init_ui(self):
        # Create the main layout
        main_layout = QVBoxLayout()

        # Create the QLabel to display the equation
        self.display_label = QLabel(self)
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display_label.setStyleSheet("font-size: 20px")  # Adjust font size
        main_layout.addWidget(self.display_label)

        # Create the result QLineEdit
        self.result_line = QLineEdit(self)
        self.result_line.setReadOnly(True)
        self.result_line.setStyleSheet("font-size: 20px")  # Adjust font size
        main_layout.addWidget(self.result_line)

        # Create a QLabel to display correctness
        self.correctness_label = QLabel(self)
        self.correctness_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.correctness_label)

        # Create the "Next" button
        next_button = QPushButton('Next', self)
        next_button.clicked.connect(self.generate_numbers)
        main_layout.addWidget(next_button)

        # Set the main layout for the window
        self.setLayout(main_layout)

        # Set window properties
        self.setWindowTitle('Calculator')
        self.setGeometry(100, 100, 400, 200)

        # Initialize the numbers and timer
        self.generate_numbers()

        self.show()

    def setup_serial_communication(self):
        # Adjust the port and baudrate based on your Arduino setup
        self.serial_port = serial.Serial(port='COM3', baudrate=9600)
        self.serial_data = ''
        self.data_acquired = False  # Flag to track whether data is acquired

    def calculate_result(self):
        try:
            if not hasattr(self, 'result_calculated') or not self.result_calculated:
                if self.data_acquired:
                    # Read and process live EEG data from Arduino
                    self.serial_data = self.serial_port.readline().decode('utf-8').strip()
                    eeg_data = [float(val) for val in self.serial_data.split(',')]
                    
                    # Preprocess EEG data (you may need more sophisticated preprocessing)
                    X = np.array(eeg_data).reshape(1, -1)

                    # Load your trained SVM classifier
                    svm_classifier = self.load_cnn_classifier()

                    # Scale the data using the same scaler used during training
                    scaler = self.load_scaler()
                    X_scaled = scaler.transform(X)

                    # Perform classification
                    classification_result = svm_classifier.predict(X_scaled)

                    # Decide the operation based on the classification result
                    if classification_result == 1:  # Assuming 1 corresponds to addition class
                        result = self.perform_addition()
                        self.correctness_label.setText('Correct (Addition)!')
                    elif classification_result == 0:  # Assuming 0 corresponds to subtraction class
                        result = self.perform_subtraction()
                        self.correctness_label.setText('Correct (Subtraction)!')
                    else:
                        # Handle other classification results
                        result = None
                        self.correctness_label.setText('Incorrect!')

                    if result is not None:
                        self.result_line.setText(str(result))

                    # Mark that the result has been calculated for the current equation
                    self.result_calculated = True

        except Exception as e:
            self.result_line.setText('Error')
            self.correctness_label.setText('Error')

    def perform_addition(self):
        num1, num2 = float(self.display_label.text().split()[0]), float(self.display_label.text().split()[2])
        result = num1 + num2
        return result

    def perform_subtraction(self):
        num1, num2 = float(self.display_label.text().split()[0]), float(self.display_label.text().split()[2])
        result = num1 - num2
        return result  # Replace with the actual result of subtraction

    def generate_numbers(self):
        # Restart communication and acquire data for the next 3 seconds
        self.data_acquired = False
        self.result_line.clear()
        self.correctness_label.clear()

        # Generate new numbers
        num1 = randint(1, 9)
        num2 = randint(1, 9)
        operation = choice(['+', '-'])
        self.display_label.setText(f"{num1} {operation} {num2}")
        
        if hasattr(self, 'timer'):
            self.timer.stop()

        # Use QTimer to acquire data for the next 3 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.start_data_acquisition)
        self.timer.start(3000)  # Set the timeout interval to 3000 milliseconds (3 seconds)

    def start_data_acquisition(self):
        self.data_acquired = True

    
    def load_cnn_classifier():
        # Example: Load a pre-trained SVM classifier
        classifier = load_model('best_model.h5')
        # Load your trained model using joblib or pickle
        return classifier
    
    # Replace this function with your actual logic to load the scaler used during training
    def load_scaler():
        # Example: Load a pre-trained scaler
        scaler = StandardScaler()
        # Load your trained scaler using joblib or pickle
        return scaler

if __name__ == '__main__':
    app = QApplication(sys.argv)
    calculator = CalculatorApp()
    
    sys.exit(app.exec_())
