"""
Testes — Display Layer (Glass Cockpit Engine)
==============================================
Testa a integridade de instanciação das 11 telas independentes MVC na MainWindow.
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
        Valida a instanciação da MainWindow e das 11 telas independentes MVC.
        """
        window = MainWindow()
        assert window.windowTitle() == "AeroTracker Core — Avionics Glass Cockpit & Control Station"
        assert window.stack.count() == 11
        window.close()
