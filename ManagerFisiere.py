import cv2
import os
import time
import concurrent.futures
from datetime import datetime
from PIL import Image, ExifTags

from PyQt6.QtWidgets import QFileDialog, QApplication, QMessageBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap

from Logica import (
    afiseaza_imagine_statica,
    afiseaza_cadru_video,
    actualizeaza_previzualizare,
    memoreaza_setari_watermark,
    aplica_watermark,
)


def incarca_imagine(fer):
    f_path, _ = QFileDialog.getOpenFileName(
        fer, "Selecteaza Imagine", "", "Imagini (*.jpg *.png)"
    )
    if f_path:
        fer.p_path = f_path
        fer.fis_cur = f_path
        fer.tip_f = "imagine"
        fer.exif = extrage_metadate(f_path, "imagine")

        fer.preview_stack.setCurrentIndex(0)
        fer.controls_stack.setCurrentIndex(0)
        fer.label_view_title.setText("MOD VIZUALIZARE: IMAGINE")
        fer.apply_btn.setText("SALVEAZĂ IMAGINEA PE PC")

        afiseaza_imagine_statica(fer)


def incarca_video(fer):
    f_path, _ = QFileDialog.getOpenFileName(
        fer, "Selecteaza Video", "", "Video (*.mp4)"
    )
    if f_path:
        fer.v_path = f_path
        fer.fis_cur = f_path
        fer.tip_f = "video"
        fer.exif = extrage_metadate(f_path, "video")

        cc = cv2.VideoCapture(f_path)
        fps = cc.get(cv2.CAP_PROP_FPS)
        tot = int(cc.get(cv2.CAP_PROP_FRAME_COUNT))
        cc.release()

        if fps <= 0 or fps != fps:
            fps = 30.0
        if tot < 1:
            tot = 1

        s = tot / fps
        min_v, sec_v = divmod(int(s), 60)

        fer.v_time_s = f"{min_v:02d}:{sec_v:02d}"
        fer.v_fps = fps

        fer.timeline_slider.setEnabled(True)
        fer.timeline_slider.setRange(0, tot - 1)
        fer.timeline_slider.setValue(0)

        fer.ltime.setText(f"00:00 / {fer.v_time_s}")

        fer.preview_stack.setCurrentIndex(1)
        fer.controls_stack.setCurrentIndex(1)
        fer.label_view_title.setText("MOD VIZUALIZARE: VIDEO")
        fer.apply_btn.setText("SALVEAZĂ VIDEO PE PC")

        afiseaza_cadru_video(fer, 0)


def schimba_cadru_slider(fer, x):
    if getattr(fer, "tip_f", "") == "video":
        fps = getattr(fer, "v_fps", 0)
        if fps > 0:
            ts = x / fps
            m, s = divmod(int(ts), 60)
            fer.ltime.setText(f"{m:02d}:{s:02d} / {fer.v_time_s}")
        afiseaza_cadru_video(fer, x)


def extrage_metadate(p, ty):
    d = {
        "data": "N/A",
        "model": "N/A",
        "gps": "N/A",
        "iso": "",
        "apertura": "",
        "expunere": "",
    }

    if ty == "imagine":
        try:
            im = Image.open(p)
            ex = im._getexif()
            if ex:
                for k, val in ex.items():
                    n_tag = ExifTags.TAGS.get(k, k)
                    if n_tag == "DateTimeOriginal":
                        d["data"] = str(val).split(" ")[0].replace(":", "-")
                    elif n_tag == "Model":
                        d["model"] = str(val).strip()
                    elif n_tag == "GPSInfo":
                        d["gps"] = "Gasite"
                    elif n_tag == "ISOSpeedRatings":
                        d["iso"] = f"ISO {val}"
                    elif n_tag == "FNumber":
                        d["apertura"] = f"f/{float(val):.1f}"
                    elif n_tag == "ExposureTime":
                        try:
                            vf = float(val)
                            if vf < 1.0:
                                d["expunere"] = f"1/{int(round(1/vf))}s"
                            else:
                                d["expunere"] = f"{vf}s"
                        except:
                            d["expunere"] = str(val)
        except:
            print("fara meta in imagine")

    if d["data"] == "N/A":
        try:
            tm = os.path.getmtime(p)
            d["data"] = datetime.fromtimestamp(tm).strftime("%Y-%m-%d")
        except:
            print("picat getmtime")

    return d


def incarca_logo(f):
    dr, _ = QFileDialog.getOpenFileName(
        f, "Cauta Logo", "", "Imagini (*.png *.jpg *.jpeg)"
    )
    if dr:
        f.l_path = dr
        pp = QPixmap(dr)
        ll = f.lpl
        psr = pp.scaled(
            ll.width() - 5,
            ll.height() - 5,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        ll.setPixmap(psr)

        f.preview_stack.setCurrentIndex(2)
        f.controls_stack.setCurrentIndex(2)
        f.label_view_title.setText("MOD VIZUALIZARE: LOGO")
        f.apply_btn.setText("MEMOREAZĂ WATERMARK-UL")

        actualizeaza_previzualizare(f)


def salveaza_fisier(f):
    c_tab = f.preview_stack.currentIndex()

    if c_tab == 2:
        w_s = f.preview_stack.width()
        h_s = f.preview_stack.height()
        xx = f.stx.x()
        yy = f.stx.y()

        px = f.lpi.pixmap() if hasattr(f.lpi, "pixmap") else None
        if not px or px.isNull():
            px = f.lpv.pixmap() if hasattr(f.lpv, "pixmap") else None

        if px and not px.isNull() and w_s > 0 and h_s > 0:
            pw, ph = px.width(), px.height()
            ox = (w_s - pw) / 2.0
            oy = (h_s - ph) / 2.0

            pxx = (xx - ox) / max(pw, 1)
            pyy = (yy - oy) / max(ph, 1)
            r_ui = pw
        else:
            pxx = xx / max(w_s, 1)
            pyy = yy / max(h_s, 1)
            r_ui = w_s

        pxx = max(0.0, min(pxx, 1.0))
        pyy = max(0.0, min(pyy, 1.0))

        f.setari_memorie = {
            "proc_cx": pxx,
            "proc_cy": pyy,
            "raport_ui": r_ui,
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

        for nr in range(1, 101, 5):
            f.bp.setValue(nr)
            QApplication.processEvents()
            time.sleep(0.01)
        f.bp.setValue(0)

        actualizeaza_previzualizare(f)
        return

    if not getattr(f, "fis_cur", None):
        return

    tp = f.tip_f

    if tp == "imagine":
        ds, _ = QFileDialog.getSaveFileName(
            f, "Unde salvezi", "", "JPG (*.jpg);;PNG (*.png)"
        )
        if ds:
            f.bp.setValue(20)
            QApplication.processEvents()

            memoreaza_setari_watermark(f, silent=True)
            mem_c = f.setari_memorie

            task = (f.fis_cur, os.path.dirname(ds), mem_c)

            from MultiProcess import aplica_watermark_pe_imagine

            rez, msg = aplica_watermark_pe_imagine(task)

            if rez:
                nume_o = os.path.join(os.path.dirname(ds), os.path.basename(f.fis_cur))
                if os.path.exists(nume_o) and nume_o != ds:
                    if os.path.exists(ds):
                        os.remove(ds)
                    os.rename(nume_o, ds)

                f.bp.setValue(100)
                QMessageBox.information(f, "Gata", "Salvat cu brio")
            else:
                QMessageBox.critical(f, "Oops", f"Crapa salvarea: {msg}")

            f.bp.setValue(0)

    elif tp == "video":
        ds, _ = QFileDialog.getSaveFileName(f, "Unde salvezi", "", "MP4 (*.mp4)")
        if ds:
            f.apply_btn.setEnabled(False)
            vc = cv2.VideoCapture(f.fis_cur)

            fps = vc.get(cv2.CAP_PROP_FPS) or 30.0
            vv = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
            vh = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
            to = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))

            wri = cv2.VideoWriter(ds, cv2.VideoWriter_fourcc(*"mp4v"), fps, (vv, vh))

            memoreaza_setari_watermark(f, silent=True)
            mmo = f.setari_memorie

            from MultiProcess import aplica_watermark_frame_video

            ct = 0

            while True:
                gata_citit, f_c = vc.read()
                if not gata_citit:
                    break

                f_modificat = aplica_watermark_frame_video(f_c, mmo)
                wri.write(f_modificat)
                ct += 1

                if ct % 10 == 0:
                    f.bp.setValue(int((ct / to) * 100))
                    QApplication.processEvents()

            vc.release()
            wri.release()
            f.bp.setValue(100)
            f.apply_btn.setEnabled(True)
            QMessageBox.information(f, "Super", "E si videoul gata!")
            f.bp.setValue(0)
            QApplication.processEvents()


class ProcesareBatchWorker(QThread):
    prog_sem = pyqtSignal(int)
    fis_sem = pyqtSignal(str)
    gata_sem = pyqtSignal()

    def __init__(self, imgs, dir_o, setar):
        super().__init__()
        self.imgs = imgs
        self.dir_o = dir_o
        self.setar = setar

    def run(self):
        ttk = [(p, self.dir_o, self.setar) for p in self.imgs]
        tot = len(ttk)
        gata = 0

        with concurrent.futures.ProcessPoolExecutor() as ex:
            rs = {ex.submit(aplica_watermark, tt): tt for tt in ttk}
            for viitor in concurrent.futures.as_completed(rs):
                try:
                    scc, mst = viitor.result()
                    gata += 1
                    self.prog_sem.emit(int((gata / tot) * 100))
                    self.fis_sem.emit(mst)
                except Exception as thread_bug:
                    print("A crapat threadul: ", thread_bug)

        self.gata_sem.emit()


def proceseaza_mai_multe_poze(f):
    fs, _ = QFileDialog.getOpenFileNames(f, "Alege pozele", "", "Imagini (*.jpg *.png)")
    if not fs:
        return

    fold = QFileDialog.getExistingDirectory(f, "Alege folder pt salvare")
    if not fold:
        return

    memoreaza_setari_watermark(f, silent=True)
    m = f.setari_memorie

    f.apply_btn.setEnabled(False)
    f.bp.setValue(0)

    f.wrk = ProcesareBatchWorker(fs, fold, m)
    f.wrk.prog_sem.connect(f.bp.setValue)
    f.wrk.gata_sem.connect(lambda: finalizare_batch(f))
    f.wrk.start()


def finalizare_batch(f):
    f.apply_btn.setEnabled(True)
    f.bp.setValue(100)
    QMessageBox.information(f, "Bun", "Toate gata in folder.")
