import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
import serial

# Configure serial port
ser = serial.Serial('/dev/tty.usbserial-0001', 9600)

# Create a PyQtGraph application
app = QtWidgets.QApplication([])
win = pg.GraphicsLayoutWidget(show=True, title="EMG Oscilloscope")
win.resize(800, 600)
plot = win.addPlot(title="EMG Signal")
curve = plot.plot(pen=pg.mkPen(color='b', width=2, style=QtCore.Qt.SolidLine))
plot.setYRange(0, 4095)  # Adjust to your EMG range

# Data buffer
buffer_size = 100
data = [0] * buffer_size

def update():
    global data, curve
    try:
        raw_data = ser.readline().decode('utf-8', errors='ignore').strip()
        if raw_data.isdigit():
            value = int(raw_data)
            data.append(value)  # Add new value to the buffer
            data.pop(0)  # Remove the oldest value
            curve.setData(data)
    except Exception as e:
        print(f"Error: {e}")

# Timer to update the plot
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)  # Update every 50 ms

# Start the PyQtGraph event loop
app.exec_()