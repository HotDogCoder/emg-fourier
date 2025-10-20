import sys
import serial
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# Set up the serial connection
serial_port = '/dev/tty.usbserial-10'  # Adjust based on your system
baud_rate = 9600
ser = serial.Serial(serial_port, baud_rate)

class EMGPlotter:
    def __init__(self):
        # Create the PyQtGraph application and plot window
        self.app = QApplication([])
        self.win = pg.GraphicsLayoutWidget(show=True, title="Real-Time EMG Signal")
        self.win.resize(1000, 800)
        self.win.setWindowTitle("EMG Signal Plot")

        # Plot 1: Raw EMG Data
        self.raw_plot = self.win.addPlot(title="Raw EMG Data")
        self.raw_plot.setYRange(0, 5000)  # Adjust for the range of your EMG signal
        self.raw_plot.setLabel('left', 'Signal', units='')  # Units if applicable
        self.raw_plot.setLabel('bottom', 'Samples', units='')
        self.raw_curve = self.raw_plot.plot(pen=pg.mkPen('b', width=2))  # Blue line

        # Plot 2: Filtered Data for Fourier
        self.win.nextRow()  # Move to the next row for the second plot
        self.filtered_plot = self.win.addPlot(title="Filtered Data for Fourier")
        self.filtered_plot.setYRange(0, 5000)  # Same range, can be adjusted
        self.filtered_plot.setLabel('left', 'Signal', units='')
        self.filtered_plot.setLabel('bottom', 'Groups', units='')
        self.filtered_curve = self.filtered_plot.plot(pen=pg.mkPen('r', width=2))  # Red line

        # Plot 3: Fourier Transform
        self.win.nextRow()  # Move to the next row for the third plot
        self.fourier_plot = self.win.addPlot(title="Fourier Transform")
        self.fourier_plot.setLabel('left', 'Amplitude', units='')
        self.fourier_plot.setLabel('bottom', 'Frequency', units='Hz')
        self.fourier_curve = self.fourier_plot.plot(pen=pg.mkPen('g', width=2))  # Green line

        # Data storage
        self.raw_data = []
        self.filtered_data = []
        self.temp_group = []  # Temporary group for 10 samples

        # Timer for real-time updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(50)  # Update every 50 ms

    def update_plot(self):
        global ser
        if ser.in_waiting:
            try:
                # Read and parse serial data
                line = ser.readline().decode('utf-8').strip()
                value = int(line)  # Convert to integer as values are between 0 and 5000
                self.raw_data.append(value)

                # Limit raw data to the last 500 samples
                if len(self.raw_data) > 500:
                    self.raw_data.pop(0)

                # Add value to the temporary group
                self.temp_group.append(value)

                # When the group reaches 10 samples
                if len(self.temp_group) == 10:
                    self.filtered_data.extend(self.temp_group)  # Add the group to filtered data
                    self.temp_group = []  # Clear the temporary group

                    # Limit filtered data to the last 100 values
                    if len(self.filtered_data) > 100:
                        self.filtered_data = self.filtered_data[-100:]

                # Update the raw data curve
                self.raw_curve.setData(self.raw_data)  # Show the last 500 samples for raw data

                # Update the filtered data curve
                self.filtered_curve.setData(self.filtered_data)  # Show the filtered data

                # Update the Fourier Transform plot
                if len(self.filtered_data) > 10:  # Ensure enough data for Fourier Transform
                    self.update_fourier_plot()

            except ValueError:
                pass  # Ignore invalid data

    def update_fourier_plot(self):
        # Perform Fourier Transform on the filtered data
        filtered_array = np.array(self.filtered_data)
        fourier = np.fft.fft(filtered_array)  # Compute FFT
        frequencies = np.fft.fftfreq(len(filtered_array), d=0.05)  # Compute frequency bins (adjust d if needed)

        # Take only the positive frequencies
        positive_freqs = frequencies[:len(frequencies) // 2]
        positive_amplitudes = np.abs(fourier[:len(fourier) // 2])

        # Update the Fourier Transform curve
        self.fourier_curve.setData(positive_freqs, positive_amplitudes)

    def run(self):
        # Start the application
        self.win.show()
        sys.exit(self.app.exec_())

if __name__ == '__main__':
    plotter = EMGPlotter()
    plotter.run()