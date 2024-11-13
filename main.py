import sys
import serial
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# Set up the serial connection
serial_port = '/dev/tty.usbserial-0001'  # Adjust based on your system
baud_rate = 9600
ser = serial.Serial(serial_port, baud_rate)

class EMGPlotter:
    def __init__(self):
        # Create the PyQtGraph application and plot window
        self.app = QApplication([])
        self.win = pg.GraphicsLayoutWidget(show=True, title="Real-Time EMG Signal")
        self.win.resize(1000, 600)
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

                # Limit raw data to the last 100 samples
                if len(self.raw_data) > 100:
                    self.raw_data.pop(0)

                # Add value to the temporary group
                self.temp_group.append(value)

                # When the group reaches 10 samples
                if len(self.temp_group) == 10:
                    self.filtered_data.extend(self.temp_group)  # Add the group to filtered data
                    self.filtered_data.append(0)  # Add a 0 after the group
                    self.temp_group = []  # Clear the temporary group

                    # Limit filtered data to the last 100 values
                    if len(self.filtered_data) > 100:
                        self.filtered_data = self.filtered_data[-100:]

                # Update the raw data curve
                self.raw_curve.setData(self.raw_data)  # Show the last 100 samples for raw data

                # Update the filtered data curve
                self.filtered_curve.setData(self.filtered_data)  # Show the filtered data
            except ValueError:
                pass  # Ignore invalid data

    def run(self):
        # Start the application
        self.win.show()
        sys.exit(self.app.exec_())

if __name__ == '__main__':
    plotter = EMGPlotter()
    plotter.run()