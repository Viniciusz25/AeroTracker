"""
Testes — Display Layer (Airspace Companion UI)
================================================
Testa a integridade de instanciação das 3 áreas na MainWindow e dos módulos MVC.
"""

import sys
import pytest
from PySide6.QtWidgets import QApplication

from display.desktop.app_window import MainWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestDesktopUI:
    def test_main_window_instantiation(self, qapp) -> None:
        """
        Valida a instanciação da MainWindow e das 3 áreas do layout (Sidebar, Workspace, Device Digital Twin).
        """
        window = MainWindow()
        assert window.windowTitle() == "AeroTracker Core — Airspace Instrument & Control Station"
        assert window.stack.count() == 9
        assert window.device_twin_panel is not None
        window.close()
