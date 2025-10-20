import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
import serial
import numpy as np
import os, time

# Configuración
SERIAL_PORT = '/dev/tty.usbserial-10'
BAUDRATE = 9600
FS = 1000
WINDOW_SEC = 0.2
SAVE_DIR = "./emg_sessions"
os.makedirs(SAVE_DIR, exist_ok=True)

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)

class EMGWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Entrenamiento EMG - Detección de Dedo")
        self.resize(1000, 600)

        # Widget principal
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        # --- Plot ---
        self.plot_widget = pg.PlotWidget(title="Señal EMG")
        self.plot_widget.setYRange(0, 4095)
        layout.addWidget(self.plot_widget)
        self.curve = self.plot_widget.plot(pen=pg.mkPen(color='b', width=2))
        self.data = [0]*500

        # --- Controles ---
        self.current_finger = None
        self.raw_buffer = []
        button_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(button_layout)

        self.label = QtWidgets.QLabel("Dedo activo:")
        button_layout.addWidget(self.label)

        self.fingers = ["Pulgar","Índice","Medio","Anular","Meñique"]
        for i, name in enumerate(self.fingers):
            btn = QtWidgets.QPushButton(name)
            btn.clicked.connect(lambda checked, i=i: self.select_finger(i))
            button_layout.addWidget(btn)

        # Timer de actualización
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(5)

    def select_finger(self, fid):
        self.current_finger = fid
        print(f"🖐️ Entrenando dedo: {self.fingers[fid]} (#{fid})")

    def update_plot(self):
        try:
            raw = ser.readline().decode('utf-8', errors='ignore').strip()
            if raw.isdigit():
                val = int(raw)
                self.data.append(val)
                self.data.pop(0)
                self.curve.setData(self.data)
                self.raw_buffer.append(val)
                window_samples = int(FS * WINDOW_SEC)
                if len(self.raw_buffer) >= window_samples and self.current_finger is not None:
                    sig = np.array(self.raw_buffer[-window_samples:])
                    ts = int(time.time()*1000)
                    filename = os.path.join(SAVE_DIR, f"emg_{ts}_finger{self.current_finger}.npz")
                    np.savez_compressed(filename, signal=sig, finger=self.current_finger, fs=FS)
                    print(f"💾 Guardado {filename}")
                    self.raw_buffer = []
        except Exception as e:
            print("Error:", e)

# === Ejecutar la app ===
app = QtWidgets.QApplication([])
window = EMGWindow()
window.show()
app.exec_()
