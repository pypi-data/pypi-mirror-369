from PySide6Plot import PriceVolumePlotter
from PySide6Plot.libs.data_handler import HDF5Handler
from PySide6.QtWidgets import QApplication
import sys


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("PriceVolumePlotter")
    sample_stock_data = HDF5Handler("./sample_stock_data.h5")
    widget = PriceVolumePlotter()
    widget.show()
    widget.plot_price_volume(sample_stock_data.month_data.prices, sample_stock_data.month_data.volume)
    # setTheme(Theme.DARK) #switch to dark theme
    # setThemeColor("#0065d5") #change the theme color
    sys.exit(app.exec())
