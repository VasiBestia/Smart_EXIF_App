import cv2
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QColorDialog, QMessageBox
from PyQt6.QtGui import QPixmap, QImage, QFont, QColor
from PyQt6.QtCore import Qt


def actualizeaza_previzualizare_text(fer):
    from PyQt6.QtWidgets import QGraphicsDropShadowEffect

    sur = "ui"
    mem = getattr(fer, "setari_memorie", {})
    t_text = construieste_text(fer, sur)

    if t_text == "":
        fer.lt.hide()
    else:
        fer.lt.setText(t_text)

        fn = QFont(fer.font_combo.currentText())
        fn.setPointSize(fer.font_size_spin.value())
        fn.setBold(fer.btn_bold.isChecked())
        fn.setItalic(fer.btn_italic.isChecked())
        fer.lt.setFont(fn)

        cl = getattr(fer, "culoare_text", (255, 255, 255))
        if sur == "ui" and fer.chk_auto_culoare.isChecked():
            wid = fer.preview_stack.currentWidget()
            if hasattr(wid, "pixmap") and wid.pixmap() and not wid.pixmap().isNull():
                img = wid.pixmap().toImage()

                mij_x = int(fer.stx.x() + fer.stx.width() / 2)
                mij_y = int(fer.stx.y() + fer.stx.height() / 2)

                if 0 <= mij_x < img.width() and 0 <= mij_y < img.height():
                    clr = img.pixelColor(mij_x, mij_y)
                    r_c, g_c, b_c = clr.red(), clr.green(), clr.blue()
                    lum_c = 0.299 * r_c + 0.587 * g_c + 0.114 * b_c

                    if lum_c > 120:
                        cl = (int(r_c * 0.2), int(g_c * 0.2), int(b_c * 0.2))
                    else:
                        cl = (
                            int(min(255, 215 + r_c * 0.15)),
                            int(min(255, 215 + g_c * 0.15)),
                            int(min(255, 215 + b_c * 0.15)),
                        )
        elif sur == "mem" and mem:
            cl = mem.get("culoare", (255, 255, 255))

        fer.lt.setStyleSheet(
            f"color: rgb({cl[0]}, {cl[1]}, {cl[2]}); border: none; background: transparent;"
        )

        umb = False
        if sur == "ui" and fer.cu.isChecked():
            umb = True
        elif sur == "mem" and mem and mem.get("chk_umbra_text", True):
            umb = True

        if umb:
            ef_u = QGraphicsDropShadowEffect()
            ef_u.setBlurRadius(2)
            ef_u.setOffset(2, 2)
            ef_u.setColor(QColor(0, 0, 0, 255))
            fer.lt.setGraphicsEffect(ef_u)
        else:
            fer.lt.setGraphicsEffect(None)

        fer.lt.show()

    qlnk = fer.i_q.text().strip()
    if qlnk:
        try:
            import qrcode

            qr = qrcode.QRCode(version=1, box_size=1, border=1)
            qr.add_data(qlnk)
            qr.make(fit=True)
            pi = qr.make_image(fill_color="black", back_color="white").convert("RGB")

            dbytes = pi.tobytes("raw", "RGB")
            qi = QImage(dbytes, pi.size[0], pi.size[1], QImage.Format.Format_RGB888)
            px_q = QPixmap.fromImage(qi)
            szq = fer.s_q.value() if sur == "ui" else mem.get("qr_size", 80)

            fer.lq.setPixmap(px_q.scaled(szq, szq, Qt.AspectRatioMode.KeepAspectRatio))
            fer.lq.show()
        except Exception as bug:
            print("qr error:", bug)
            fer.lq.hide()
    else:
        fer.lq.hide()

    logp = getattr(fer, "l_path", None)
    if logp:
        pxl = QPixmap(logp)
        if not pxl.isNull():
            z_fact = fer.zoom_slider.value() / 100.0
            widn = int(200 * z_fact)
            px_s = pxl.scaledToWidth(widn, Qt.TransformationMode.SmoothTransformation)
            fer.ll.setPixmap(px_s)
            fer.ll.show()
        else:
            fer.ll.hide()
    else:
        fer.ll.hide()

    if t_text == "" and not logp and not qlnk:
        fer.stx.hide()
    else:
        fer.stx.show()
        fer.stx.adjustSize()
        fer.stx.raise_()

    efo = QGraphicsOpacityEffect()
    efo.setOpacity(fer.slider_opacitate.value() / 100.0)
    fer.stx.setGraphicsEffect(efo)

    fer.apply_btn.setStyleSheet("""
        QPushButton { background-color: #2e7d32; color: white; font-weight: bold; border-radius: 4px; }
        QPushButton:pressed { background-color: #d32f2f; }
    """)


def afiseaza_logo_cu_zoom(fer):
    fer.lpl.clear()
    zv = fer.zoom_slider.value()
    fer.lz.setText(f"Zoom: {zv}%")
    actualizeaza_previzualizare_text(fer)


def actualizeaza_previzualizare(f):
    c = f.preview_stack.currentIndex()
    if c == 0:
        afiseaza_imagine_statica(f)
    elif c == 1:
        afiseaza_cadru_video(f, getattr(f.timeline_slider, "value", lambda: 0)())
    elif c == 2:
        afiseaza_logo_cu_zoom(f)
    actualizeaza_previzualizare_text(f)


def afiseaza_imagine_statica(f):
    pth = getattr(f, "p_path", None)
    if not pth:
        return

    i = cv2.imread(pth)
    if i is None:
        return

    i = cv2.cvtColor(i, cv2.COLOR_BGR2RGB)
    i = aplica_watermark(f, i)

    hi, wi, ch = i.shape
    qim = QImage(i.data, wi, hi, ch * wi, QImage.Format.Format_RGB888)

    p_lbl = f.lpi
    pxm = QPixmap.fromImage(qim).scaled(
        p_lbl.width(),
        p_lbl.height(),
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    p_lbl.setPixmap(pxm)

    actualizeaza_previzualizare_text(f)


def afiseaza_cadru_video(f, idx_f):
    pth = getattr(f, "v_path", None)
    if not pth:
        return

    c = cv2.VideoCapture(pth)
    if not c.isOpened():
        return

    c.set(cv2.CAP_PROP_POS_FRAMES, idx_f)
    gata, f_v = c.read()
    c.release()

    if gata:
        r = cv2.cvtColor(f_v, cv2.COLOR_BGR2RGB)
        r = aplica_watermark(f, r)

        hi, wi, ch = r.shape
        qim = QImage(r.data, wi, hi, ch * wi, QImage.Format.Format_RGB888)

        p_lbl = f.lpv
        pxm = QPixmap.fromImage(qim).scaled(
            p_lbl.width(),
            p_lbl.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        p_lbl.setPixmap(pxm)

        actualizeaza_previzualizare_text(f)


def aplica_watermark(f, f_rm, exprt=False):
    if not exprt:
        return f_rm

    mm = getattr(f, "setari_memorie", None)
    if not mm:
        return f_rm

    ot = f_rm.copy()
    hy, wx, _ = ot.shape
    tf = construieste_text(f, "mem")

    cf = cv2.FONT_HERSHEY_SIMPLEX
    if mm["font"] == "Times New Roman":
        cf = cv2.FONT_HERSHEY_COMPLEX
    elif mm["font"] == "Courier New":
        cf = cv2.FONT_HERSHEY_PLAIN
    elif mm["font"] == "Helvetica":
        cf = cv2.FONT_HERSHEY_TRIPLEX

    s_f = mm.get("font_size", 40) / 40.0
    thk = max(1, int(2 * s_f))

    w_tx, h_tx = 0, 0
    if tf:
        txt_sz = cv2.getTextSize(tf, cf, s_f, thk)
        w_tx, h_tx = txt_sz[0][0], txt_sz[0][1]

    lg_b, lg_a, wl, hl = None, None, 0, 0
    if mm["logo"]:
        try:
            raw = cv2.imread(mm["logo"], cv2.IMREAD_UNCHANGED)
            if raw is not None:
                if len(raw.shape) == 2:
                    raw = cv2.cvtColor(raw, cv2.COLOR_GRAY2BGRA)
                elif raw.shape[2] == 3:
                    raw = cv2.cvtColor(raw, cv2.COLOR_BGR2BGRA)

                if raw.shape[2] == 4:
                    z = mm["zoom"] / 100.0
                    wl = int(200 * z)
                    rt = wl / raw.shape[1]
                    hl = int(raw.shape[0] * rt)
                    rx = cv2.resize(raw, (wl, hl), interpolation=cv2.INTER_AREA)
                    lg_b = cv2.cvtColor(rx[:, :, :3], cv2.COLOR_BGR2RGB)
                    lg_a = rx[:, :, 3] / 255.0
        except:
            print("skip logo")

    ws = f.preview_stack.width()
    hs = f.preview_stack.height()

    sx = f.stx.x()
    sy = f.stx.y()
    sw = f.stx.width()

    widg = f.preview_stack.currentWidget()
    p_x = widg.pixmap() if hasattr(widg, "pixmap") else None

    if p_x and not p_x.isNull() and ws > 0 and hs > 0:
        pw, ph = p_x.width(), p_x.height()
        ox = (ws - pw) / 2.0
        oy = (hs - ph) / 2.0

        sc_x = wx / pw
        sc_y = hy / ph

        ax = int((sx - ox) * sc_x)
        ay = int((sy - oy) * sc_y)
        bw = int(sw * sc_x)
    else:
        ax = int(sx * (wx / max(ws, 1)))
        ay = int(sy * (hy / max(hs, 1)))
        bw = max(wl, w_tx) + 16

    c_y = ay + 8

    if hl > 0:
        pos_l = ax + (bw - wl) // 2
        if 0 <= c_y and c_y + hl <= hy and 0 <= pos_l and pos_l + wl <= wx:
            for z in range(3):
                ot[c_y : c_y + hl, pos_l : pos_l + wl, z] = (
                    lg_a * lg_b[:, :, z]
                    + (1 - lg_a) * ot[c_y : c_y + hl, pos_l : pos_l + wl, z]
                )
        c_y += hl + 5

    if h_tx > 0 and exprt:
        tpx = ax + (bw - w_tx) // 2
        tpy = c_y + h_tx

        crg = mm.get("culoare", (255, 255, 255))
        cbg = (crg[2], crg[1], crg[0])

        cv2.putText(ot, tf, (tpx, tpy), cf, s_f, cbg, thk, cv2.LINE_AA)

    o = mm["opacitate"] / 100.0
    cv2.addWeighted(ot, o, f_rm, 1 - o, 0, f_rm)

    return f_rm


def actualizeaza_sticker_text(f):
    val = f.custom_text_input.text()
    if val:
        f.stx.setText(val)
        f.stx.adjustSize()
        f.stx.show()
    else:
        f.stx.hide()


def construieste_text(f, mode="ui"):
    dx = getattr(f, "exif", {"data": "2026-04-05", "model": "CameraX"})

    if mode == "ui":
        d = f.chk_data.isChecked()
        m = f.chk_model.isChecked()
        p = f.chk_setari_pro.isChecked()
        t = f.custom_text_input.text()
    else:
        m_set = getattr(f, "setari_memorie", None)
        if not m_set:
            return ""
        d = m_set["chk_data"]
        m = m_set["chk_model"]
        p = m_set.get("chk_setari_pro", False)
        t = m_set["text"]

    b = []
    if d:
        b.append(dx.get("data", "---"))
    if m:
        xx = dx.get("model", "N/A")
        if xx != "N/A":
            b.append(xx)
    if p:
        s = " ".join(
            [dx.get("apertura", ""), dx.get("expunere", ""), dx.get("iso", "")]
        ).strip()
        if s:
            b.append(s)
    if t:
        b.append(t)

    return " | ".join(b)


def alege_culoare(f):
    col = QColorDialog.getColor()
    if col.isValid():
        red, gr, bl = col.red(), col.green(), col.blue()
        f.culoare_text = (red, gr, bl)

        lumin_calc = (red * 299 + gr * 587 + bl * 114) / 1000
        c_btn = "black" if lumin_calc > 128 else "white"

        f.btn_culoare.setText(f"RGB({red}, {gr}, {bl})")
        f.btn_culoare.setStyleSheet(
            f"background-color: rgb({red},{gr},{bl}); color: {c_btn}; font-weight: bold;"
        )
        actualizeaza_previzualizare_text(f)


def aplica_template(f):
    vl = f.combo_template.currentText()
    if vl == "Personalizat":
        return

    if vl == "Minimalist (Dreapta-Jos)":
        f.chk_data.setChecked(True)
        f.chk_model.setChecked(False)
        f.custom_text_input.setText("")
        f.font_size_spin.setValue(30)
        f.font_combo.setCurrentText("Helvetica")
        f.pos_combo.setCurrentText("Dreapta-Jos")
    elif vl == "Fotograf PRO":
        f.chk_data.setChecked(True)
        f.chk_model.setChecked(True)
        f.custom_text_input.setText("© Copy")
        f.font_size_spin.setValue(45)
        f.font_combo.setCurrentText("Times New Roman")
        f.btn_bold.setChecked(True)
        f.pos_combo.setCurrentText("Centru")
    elif vl == "Jurnal (Data/Ora)":
        f.chk_data.setChecked(True)
        f.chk_model.setChecked(False)
        f.custom_text_input.setText("")
        f.font_size_spin.setValue(50)
        f.font_combo.setCurrentText("Courier New")
        f.pos_combo.setCurrentText("Stânga-Sus")

    actualizeaza_previzualizare(f)


def memoreaza_setari_watermark(f, silent=False):
    ww = f.preview_stack.width()
    hh = f.preview_stack.height()

    xx = f.stx.x()
    yy = f.stx.y()
    sw = f.stx.width()
    sh = f.stx.height()

    pxm = None
    c_t = f.preview_stack.currentIndex()

    if c_t == 0 and hasattr(f.lpi, "pixmap"):
        pxm = f.lpi.pixmap()
    elif c_t == 1 and hasattr(f.lpv, "pixmap"):
        pxm = f.lpv.pixmap()

    if pxm and not pxm.isNull() and ww > 0 and hh > 0:
        xw, yh = pxm.width(), pxm.height()
        mx = (ww - xw) / 2.0
        my = (hh - yh) / 2.0

        p_cx = (xx + sw / 2.0 - mx) / max(xw, 1)
        p_cy = (yy + sh / 2.0 - my) / max(yh, 1)
        r_u = max(xw, yh)
    else:
        p_cx = (xx + sw / 2.0) / max(ww, 1)
        p_cy = (yy + sh / 2.0) / max(hh, 1)
        r_u = max(ww, hh)

    f.setari_memorie = {
        "proc_cx": max(0.0, min(p_cx, 1.0)),
        "proc_cy": max(0.0, min(p_cy, 1.0)),
        "raport_ui": r_u,
        "chk_data": f.chk_data.isChecked(),
        "chk_model": f.chk_model.isChecked(),
        "chk_setari_pro": f.chk_setari_pro.isChecked(),
        "text": f.custom_text_input.text(),
        "font": f.font_combo.currentText(),
        "font_size": f.font_size_spin.value(),
        "culoare": getattr(f, "culoare_text", (255, 255, 255)),
        "pozitie_text": f.pos_combo.currentText(),
        "auto_culoare": f.chk_auto_culoare.isChecked(),
        "logo": getattr(f, "l_path", None),
        "qr_link": f.i_q.text().strip(),
        "qr_size": f.s_q.value(),
        "zoom": f.zoom_slider.value(),
        "opacitate": f.slider_opacitate.value(),
    }

    if not silent:
        QMessageBox.information(f, "Memorat", "Salvat")


def aliniaza_watermark(f):
    p = f.pos_combo.currentText()
    if p.startswith("Personalizat") or not f.stx.isVisible():
        return

    wx, hy = f.preview_stack.width(), f.preview_stack.height()
    c_tab = f.preview_stack.currentIndex()

    px = None
    if c_tab == 0 and hasattr(f.lpi, "pixmap"):
        px = f.lpi.pixmap()
    elif c_tab == 1 and hasattr(f.lpv, "pixmap"):
        px = f.lpv.pixmap()

    if px and not px.isNull() and wx > 0 and hy > 0:
        iw, ih = px.width(), px.height()
        ox = (wx - iw) / 2.0
        oy = (hy - ih) / 2.0
    else:
        iw, ih = wx, hy
        ox, oy = 0, 0

    f.stx.adjustSize()
    sw = f.stx.width()
    sh = f.stx.height()

    mg = 20
    nnx, nny = ox + mg, oy + mg

    if "Sus" in p:
        nny = oy + mg
    elif "Jos" in p:
        nny = oy + ih - sh - mg
    elif "Mijloc" in p or p == "Centru":
        nny = oy + (ih - sh) / 2.0

    if "Stânga" in p:
        nnx = ox + mg
    elif "Dreapta" in p:
        nnx = ox + iw - sw - mg
    elif "Centru" in p:
        nnx = ox + (iw - sw) / 2.0

    f.stx.move(int(nnx), int(nny))
