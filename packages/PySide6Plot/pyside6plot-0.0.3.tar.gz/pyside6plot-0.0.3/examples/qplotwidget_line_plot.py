# @Time    : 2025/7/16 21:43
# @Author  : YQ Tsui
# @File    : qplotwidget_line_plot.py
# @Purpose :
from PySide6Plot import QStockPlotter
from PySide6Plot.libs.data_handler import ChildDataFrame
from PySide6Plot.libs.plot_item import LinePlotItem
import numpy as np
import pandas as pd

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
    import sys

    app = QApplication(sys.argv)

    # Create a main window
    main_window = QWidget()
    main_window.setWindowTitle("Line Plot Example")
    main_window.setGeometry(100, 100, 800, 600)

    # Create a QPlotWidget instance
    plot_widget = QStockPlotter()

    # Add some sample data to the plot
    test_df = pd.DataFrame(
        np.random.rand(100), index=pd.date_range(end="2025-07-15", periods=100).rename("date"), columns=["data"]
    )
    # plot_widget.plot(x=list(range(len(test_df["data"]))), y=test_df["data"], pen="b", name="Sample Data")
    line_data = ChildDataFrame(test_df, "data", x_label_key="date")
    line_data_item = LinePlotItem(line_data, marker="circle")

    plot_widget.add_main_item(line_data_item, x_ticks=line_data_item.get_x_ticks())

    # Set up the layout
    layout = QVBoxLayout(main_window)
    layout.addWidget(plot_widget)

    main_window.setLayout(layout)

    main_window.show()

    sys.exit(app.exec())
