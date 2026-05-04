import sys
import qdarktheme
from PyQt6.QtWidgets import QApplication

from Interfata import SmartExifWatermarkApp

from Logica import (
    actualizeaza_previzualizare,
    actualizeaza_previzualizare_text,
    afiseaza_logo_cu_zoom,
    alege_culoare,
    aplica_template,
    memoreaza_setari_watermark,
    aliniaza_watermark,
)

from ManagerFisiere import (
    incarca_imagine,
    incarca_video,
    schimba_cadru_slider,
    incarca_logo,
    salveaza_fisier,
    proceseaza_mai_multe_poze,
)


def schimba_view(fer, p):
    idx = fer.preview_stack.currentIndex()
    nxt = idx + p

    if nxt > 2:
        nxt = 0
    elif nxt < 0:
        nxt = 2

    fer.preview_stack.setCurrentIndex(nxt)
    fer.controls_stack.setCurrentIndex(nxt)

    if nxt == 0:
        fer.label_view_title.setText("MOD VIZUALIZARE: IMAGINE")
        fer.apply_btn.setText("SALVEAZĂ IMAGINEA PE PC")
    elif nxt == 1:
        fer.label_view_title.setText("MOD VIZUALIZARE: VIDEO")
        fer.apply_btn.setText("SALVEAZĂ VIDEO PE PC")
    elif nxt == 2:
        fer.label_view_title.setText("MOD VIZUALIZARE: LOGO")
        fer.apply_btn.setText("MEMOREAZĂ WATERMARK-UL")
    else:
        fer.label_view_title.setText("")

    actualizeaza_previzualizare(fer)


def main():
    app = QApplication(sys.argv)

    try:
        app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    except Exception as d_err:
        print("Crapa qdarktheme, probabil nu e instalat:", d_err)

    app_win = SmartExifWatermarkApp()

    app_win.btn_logo.clicked.connect(lambda: incarca_logo(app_win))
    app_win.btn_img.clicked.connect(lambda: incarca_imagine(app_win))
    app_win.btn_vid.clicked.connect(lambda: incarca_video(app_win))

    app_win.btn_batch.clicked.connect(lambda: proceseaza_mai_multe_poze(app_win))

    app_win.btn_prev_preview.clicked.connect(lambda: schimba_view(app_win, -1))
    app_win.btn_next_preview.clicked.connect(lambda: schimba_view(app_win, 1))

    app_win.chk_model.stateChanged.connect(lambda: actualizeaza_previzualizare(app_win))
    app_win.chk_data.stateChanged.connect(lambda: actualizeaza_previzualizare(app_win))
    app_win.chk_setari_pro.stateChanged.connect(
        lambda: actualizeaza_previzualizare(app_win)
    )

    app_win.btn_italic.clicked.connect(
        lambda: actualizeaza_previzualizare_text(app_win)
    )
    app_win.custom_text_input.textChanged.connect(
        lambda: actualizeaza_previzualizare_text(app_win)
    )
    app_win.btn_bold.clicked.connect(lambda: actualizeaza_previzualizare_text(app_win))
    app_win.font_size_spin.valueChanged.connect(
        lambda: actualizeaza_previzualizare_text(app_win)
    )

    app_win.btn_memoreaza.clicked.connect(lambda: memoreaza_setari_watermark(app_win))
    app_win.pos_combo.currentTextChanged.connect(lambda: aliniaza_watermark(app_win))

    app_win.slider_opacitate.valueChanged.connect(
        lambda: actualizeaza_previzualizare_text(app_win)
    )
    app_win.font_combo.currentTextChanged.connect(
        lambda: actualizeaza_previzualizare(app_win)
    )

    app_win.timeline_slider.valueChanged.connect(
        lambda val: schimba_cadru_slider(app_win, val)
    )
    app_win.zoom_slider.valueChanged.connect(lambda: afiseaza_logo_cu_zoom(app_win))

    app_win.apply_btn.clicked.connect(lambda: salveaza_fisier(app_win))

    app_win.btn_culoare.clicked.connect(lambda: alege_culoare(app_win))
    app_win.chk_auto_culoare.stateChanged.connect(
        lambda: app_win.btn_culoare.setDisabled(app_win.chk_auto_culoare.isChecked())
    )

    app_win.combo_template.currentTextChanged.connect(lambda: aplica_template(app_win))

    app_win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
