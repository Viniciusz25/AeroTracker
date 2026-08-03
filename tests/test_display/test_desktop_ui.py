"""
Testes — Display Layer (PySide6 / Qt)
======================================
Testa a integridade de instanciação da janela principal e das telas em MVC.
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
        Valida a instanciação da MainWindow e das telas MVC.
        """
        window = MainWindow()
        assert window.windowTitle() == "AeroTracker Core — Estação de Monitoramento Aeroespacial"
        assert window.stack.count() == 3
        window.close()
