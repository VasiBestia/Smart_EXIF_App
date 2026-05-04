import sys
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QToolBox,
    QCheckBox,
    QSlider,
    QComboBox,
    QProgressBar,
    QStackedWidget,
    QLineEdit,
    QSpinBox,
    QSizePolicy,
    QFontComboBox,
    QColorDialog,
)


class SmartExifWatermarkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Exif Watermark - Pro Editor")
        self.resize(1200, 800)

        self.sd = None
        self.p_path = None
        self.v_path = None
        self.l_path = None

        wp = QWidget()
        self.setCentralWidget(wp)

        lb = QHBoxLayout(wp)
        lb.setContentsMargins(10, 10, 10, 10)
        lb.setSpacing(15)

        ms = QToolBox()
        ms.setFixedWidth(340)

        t1 = QWidget()
        lf = QVBoxLayout(t1)
        lf.setSpacing(10)

        self.btn_img = QPushButton("Incarca Imagine")
        self.btn_vid = QPushButton("Incarca Video")
        self.btn_logo = QPushButton("Incarca Logo PNG")

        lf.addWidget(QLabel("Sursa Media:"))

        self.btn_img.setMinimumHeight(35)
        self.btn_vid.setMinimumHeight(35)
        self.btn_logo.setMinimumHeight(35)

        lf.addWidget(self.btn_img)
        lf.addWidget(self.btn_vid)
        lf.addWidget(self.btn_logo)

        lf.addWidget(QLabel("\nProcesare in Masa:"))
        self.btn_batch = QPushButton("Procesare Multipla (Batch)")
        self.btn_batch.setMinimumHeight(40)
        self.btn_batch.setStyleSheet(
            "background-color: #0277bd; color: white; font-weight: bold;"
        )
        lf.addWidget(self.btn_batch)

        lf.addStretch()
        ms.addItem(t1, "1. Fisiere & Export")

        t2 = QWidget()
        lc = QVBoxLayout(t2)
        lc.setSpacing(8)

        lc.addWidget(QLabel("Format Rapid (Template):"))
        self.combo_template = QComboBox()
        self.combo_template.addItems(
            [
                "Personalizat",
                "Minimalist (Dreapta-Jos)",
                "Fotograf PRO",
                "Jurnal (Data/Ora)",
            ]
        )
        lc.addWidget(self.combo_template)

        lc.addWidget(QLabel("\nText Personalizat:"))
        self.custom_text_input = QLineEdit()
        self.custom_text_input.setPlaceholderText("Scrie watermark aici...")
        lc.addWidget(self.custom_text_input)

        lc.addWidget(QLabel("\nGenereaza QR Code:"))
        self.i_q = QLineEdit()
        self.i_q.setPlaceholderText("ex: https://instagram.com/nume")
        lc.addWidget(self.i_q)

        self.s_q = QSpinBox()
        self.s_q.setRange(20, 400)
        self.s_q.setValue(80)
        self.s_q.hide()
        lc.addWidget(self.s_q)

        lc.addWidget(QLabel("\nExtragere Date (EXIF):"))
        self.chk_data = QCheckBox("Include Data si Ora")
        self.chk_model = QCheckBox("Include Model Camera")
        self.chk_setari_pro = QCheckBox("Include Setari Pro")
        lc.addWidget(self.chk_data)
        lc.addWidget(self.chk_model)
        lc.addWidget(self.chk_setari_pro)

        lc.addWidget(QLabel("\nSecuritate & Intimitate:"))
        self.c_priv = QCheckBox("Privacy Shield (Curata GPS)")
        self.c_priv.setChecked(True)
        self.c_priv.setEnabled(False)
        self.c_priv.setStyleSheet("color: #4caf50; font-weight: bold;")
        lc.addWidget(self.c_priv)

        lc.addStretch()
        ms.addItem(t2, "2. Continut & EXIF")

        t3 = QWidget()
        la = QVBoxLayout(t3)
        la.setSpacing(8)

        la.addWidget(QLabel("Tipografie:"))
        self.font_combo = QFontComboBox()
        la.addWidget(self.font_combo)

        rf = QHBoxLayout()
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(10, 200)
        self.font_size_spin.setValue(40)

        self.btn_bold = QPushButton("B")
        self.btn_bold.setCheckable(True)
        self.btn_bold.setFixedWidth(35)

        self.btn_italic = QPushButton("I")
        self.btn_italic.setCheckable(True)
        self.btn_italic.setFixedWidth(35)

        rf.addWidget(self.font_size_spin)
        rf.addWidget(self.btn_bold)
        rf.addWidget(self.btn_italic)
        la.addLayout(rf)

        la.addWidget(QLabel("\nCuloare:"))
        self.chk_auto_culoare = QCheckBox("Culoare Auto")
        self.chk_auto_culoare.setStyleSheet("color: #ffb300; font-weight: bold;")
        self.btn_culoare = QPushButton("Alege Culoare")
        self.btn_culoare.setStyleSheet(
            "background-color: white; color: black; font-weight: bold;"
        )
        self.cu = QCheckBox("Efect Umbra")
        self.cu.setChecked(True)
        la.addWidget(self.chk_auto_culoare)
        la.addWidget(self.btn_culoare)
        la.addWidget(self.cu)

        la.addWidget(QLabel("\nPozitie:"))
        self.pos_combo = QComboBox()
        self.pos_combo.addItems(
            [
                "Personalizat",
                "Stânga-Sus",
                "Dreapta-Sus",
                "Centru",
                "Stânga-Jos",
                "Dreapta-Jos",
                "✨ Inteligent (Auto-Detectare Spațiu Gol)",
            ]
        )

        self.slider_opacitate = QSlider(Qt.Orientation.Horizontal)
        self.slider_opacitate.setRange(0, 100)
        self.slider_opacitate.setValue(80)
        la.addWidget(self.pos_combo)
        la.addWidget(self.slider_opacitate)

        la.addStretch()
        ms.addItem(t3, "3. Aspect & Pozitionare")

        lb.addWidget(ms)

        pd = QWidget()
        ld = QVBoxLayout(pd)

        rn = QHBoxLayout()
        self.btn_prev_preview = QPushButton("<")
        self.label_view_title = QLabel("PREVIEW")
        self.label_view_title.setStyleSheet("font-weight: bold;")
        self.btn_next_preview = QPushButton(">")

        rn.addWidget(self.btn_prev_preview)
        rn.addStretch()
        rn.addWidget(self.label_view_title)
        rn.addStretch()
        rn.addWidget(self.btn_next_preview)
        ld.addLayout(rn)

        self.preview_stack = QStackedWidget()
        self.preview_stack.setStyleSheet(
            "background-color: #121212; border: 2px solid #333;"
        )

        self.stx = QWidget(self.preview_stack)
        self.stx.setStyleSheet(
            "background-color: transparent; border: 1px dashed rgba(255, 255, 255, 100);"
        )
        lst = QVBoxLayout(self.stx)

        self.ll = QLabel()
        self.ll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ll.hide()

        self.lq = QLabel()
        self.lq.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lq.hide()

        self.lt = QLabel("WATERMARK PREVIEW")
        self.lt.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lst.addWidget(self.ll)
        lst.addWidget(self.lq)
        lst.addWidget(self.lt)
        self.stx.move(50, 50)
        self.stx.hide()

        ign = QSizePolicy.Policy.Ignored

        self.lpi = QLabel("Nicio Imagine")
        self.lpi.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lpi.setSizePolicy(ign, ign)

        self.lpv = QLabel("Niciun Video")
        self.lpv.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lpv.setSizePolicy(ign, ign)

        self.lpl = QLabel("Niciun Logo")
        self.lpl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lpl.setSizePolicy(ign, ign)

        self.preview_stack.addWidget(self.lpi)
        self.preview_stack.addWidget(self.lpv)
        self.preview_stack.addWidget(self.lpl)

        ld.addWidget(self.preview_stack, stretch=1)

        self.controls_stack = QStackedWidget()
        self.controls_stack.setFixedHeight(60)
        self.controls_stack.addWidget(QWidget())

        wv = QWidget()
        lv = QHBoxLayout(wv)
        self.timeline_slider = QSlider(Qt.Orientation.Horizontal)
        self.ltime = QLabel("00:00 / 00:00")
        lv.addWidget(self.timeline_slider)
        lv.addWidget(self.ltime)
        self.controls_stack.addWidget(wv)

        wl = QWidget()
        ll = QHBoxLayout(wl)
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(50, 300)
        self.zoom_slider.setValue(100)
        self.lz = QLabel("Zoom: 100%")
        ll.addWidget(QLabel("Zoom Logo:"))
        ll.addWidget(self.zoom_slider)
        ll.addWidget(self.lz)
        self.controls_stack.addWidget(wl)

        ld.addWidget(self.controls_stack)

        rj = QHBoxLayout()
        self.bp = QProgressBar()
        self.btn_memoreaza = QPushButton("MEMOREAZA")
        self.btn_memoreaza.setMinimumHeight(40)
        self.btn_memoreaza.setStyleSheet(
            "background-color: #d84315; color: white; font-weight: bold;"
        )

        self.apply_btn = QPushButton("SALVEAZA")
        self.apply_btn.setMinimumHeight(40)
        self.apply_btn.setStyleSheet(
            "background-color: #2e7d32; color: white; font-weight: bold;"
        )

        rj.addWidget(self.bp)
        rj.addWidget(self.btn_memoreaza)
        rj.addWidget(self.apply_btn)
        ld.addLayout(rj)

        lb.addWidget(pd, stretch=2)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            geo = self.stx.geometry()
            pct = self.preview_stack.mapFromGlobal(ev.globalPosition().toPoint())

            if geo.contains(pct):
                self.sd = pct - self.stx.pos()
                self.setCursor(Qt.CursorShape.SizeAllCursor)

    def mouseMoveEvent(self, ev):
        if self.sd:
            pct = self.preview_stack.mapFromGlobal(ev.globalPosition().toPoint())
            nx = pct.x() - self.sd.x()
            ny = pct.y() - self.sd.y()

            mx = self.preview_stack.width() - self.stx.width()
            my = self.preview_stack.height() - self.stx.height()

            if nx < 0:
                nx = 0
            if nx > mx:
                nx = mx

            if ny < 0:
                ny = 0
            if ny > my:
                ny = my

            self.stx.move(nx, ny)

    def mouseReleaseEvent(self, ev):
        self.sd = None
        self.unsetCursor()
        self.pos_combo.setCurrentText("Personalizat")

        try:
            from Logica import actualizeaza_previzualizare_text

            actualizeaza_previzualizare_text(self)
        except Exception:
            pass

    def wheelEvent(self, ev):
        pct = self.preview_stack.mapFromGlobal(ev.globalPosition().toPoint())

        if self.stx.geometry().contains(pct) and not self.stx.isHidden():
            delta = ev.angleDelta().y()

            if delta > 0:
                pf, pl, pq = 2, 5, 4
            else:
                pf, pl, pq = -2, -5, -4

            nf = max(10, min(200, self.font_size_spin.value() + pf))
            nl = max(10, min(300, self.zoom_slider.value() + pl))
            nq = max(20, min(400, self.s_q.value() + pq))

            self.font_size_spin.setValue(nf)
            self.zoom_slider.setValue(nl)
            self.s_q.setValue(nq)

            memo = getattr(self, "setari_memorie", None)
            if memo:
                memo["zoom"] = nl
                memo["font_size"] = nf

            try:
                from Logica import actualizeaza_previzualizare_text

                actualizeaza_previzualizare_text(self)
            except:
                pass

            ev.accept()
        else:
            super().wheelEvent(ev)
