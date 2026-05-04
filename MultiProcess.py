import cv2
import os
import numpy as np
from datetime import datetime
from PIL import Image, ExifTags
import time
import math


def gaseste_pozitie_inteligenta(img_cv, w_mark, h_mark, marg=20):
    h_poza, w_poza = img_cv.shape[:2]

    gri = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    margini_c = cv2.Canny(gri, 100, 200)

    puncte_test = [
        (marg, marg),
        ((w_poza - w_mark) // 2, marg),
        (w_poza - w_mark - marg, marg),
        (marg, (h_poza - h_mark) // 2),
        ((w_poza - w_mark) // 2, (h_poza - h_mark) // 2),
        (w_poza - w_mark - marg, (h_poza - h_mark) // 2),
        (marg, h_poza - h_mark - marg),
        ((w_poza - w_mark) // 2, h_poza - h_mark - marg),
        (w_poza - w_mark - marg, h_poza - h_mark - marg),
    ]

    min_scr = float("inf")
    poz_buna = puncte_test[-1]

    for px, py in puncte_test:
        sx = int(max(0, px))
        sy = int(max(0, py))
        ex = int(min(w_poza, px + w_mark))
        ey = int(min(h_poza, py + h_mark))

        zona_roi = margini_c[sy:ey, sx:ex]

        if zona_roi.size > 0:
            scor_curent = np.sum(zona_roi)
            if scor_curent < min_scr:
                min_scr = scor_curent
                poz_buna = (px, py)

    return int(poz_buna[0]), int(poz_buna[1])


def extrage_metadate_batch(path_fisier):
    info = {"data": "N/A", "model": "N/A"}
    try:
        img_p = Image.open(path_fisier)
        brut_exif = img_p._getexif()

        if brut_exif:
            for k, v in brut_exif.items():
                nume = ExifTags.TAGS.get(k, k)
                if nume == "DateTimeOriginal":
                    t_str = str(v)
                    info["data"] = t_str.split(" ")[0].replace(":", "-")
                elif nume == "Model":
                    info["model"] = str(v).strip()
    except (AttributeError, KeyError, IndexError) as err:
        print("eroare la citire exif sau n-are:", err)

    if info["data"] == "N/A":
        try:
            tstamp = os.path.getmtime(path_fisier)
            info["data"] = datetime.fromtimestamp(tstamp).strftime("%Y-%m-%d")
        except OSError as e:
            print("nu pot citi ts:", e)

    return info


def aplica_watermark_pe_imagine(task_date):
    cale_src, f_dest, cache = task_date

    try:
        cadru = cv2.imread(cale_src)
        if cadru is None:
            return False, f"nu vrea sa citeasca: {cale_src}"

        poza = cadru.copy()
        hf, wf, _ = poza.shape

        ratia = cache.get("raport_ui", 800)
        s_calc = max(wf, hf) / ratia

        meta = extrage_metadate_batch(cale_src)
        arr_t = []

        if cache.get("chk_data"):
            arr_t.append(meta.get("data", "N/A"))

        if cache.get("chk_model") and meta.get("model") != "N/A":
            arr_t.append(meta.get("model"))

        if cache.get("chk_setari_pro"):
            str_p = " ".join(
                [
                    meta.get("apertura", ""),
                    meta.get("expunere", ""),
                    meta.get("iso", ""),
                ]
            ).strip()
            if str_p:
                arr_t.append(str_p)

        if cache.get("text"):
            arr_t.append(cache["text"])

        str_final = " | ".join(arr_t)

        f_cv = cv2.FONT_HERSHEY_SIMPLEX
        stil = cache.get("font")
        if stil == "Times New Roman":
            f_cv = cv2.FONT_HERSHEY_COMPLEX
        elif stil == "Courier New":
            f_cv = cv2.FONT_HERSHEY_PLAIN
        elif stil == "Helvetica":
            f_cv = cv2.FONT_HERSHEY_TRIPLEX

        sz_f = (cache.get("font_size", 40) / 40.0) * s_calc
        grs = max(1, int(2 * s_calc))

        latT, inaltT = 0, 0
        if str_final:
            dim_txt = cv2.getTextSize(str_final, f_cv, sz_f, grs)
            latT, inaltT = dim_txt[0][0], dim_txt[0][1]

        imgL_rgb, imgL_a, wL, hL = None, None, 0, 0

        if cache.get("logo"):
            try:
                f_logo = cv2.imread(cache["logo"], cv2.IMREAD_UNCHANGED)
                if f_logo is not None:
                    if len(f_logo.shape) == 2:
                        f_logo = cv2.cvtColor(f_logo, cv2.COLOR_GRAY2BGRA)
                    elif f_logo.shape[2] == 3:
                        f_logo = cv2.cvtColor(f_logo, cv2.COLOR_BGR2BGRA)

                    if f_logo.shape[2] == 4:
                        zf = cache.get("zoom", 100) / 100.0
                        wL = int((200 * zf) * s_calc)
                        rt = wL / f_logo.shape[1]
                        hL = int(f_logo.shape[0] * rt)

                        lg_r = cv2.resize(
                            f_logo, (wL, hL), interpolation=cv2.INTER_AREA
                        )
                        imgL_rgb = lg_r[:, :, :3]
                        imgL_a = lg_r[:, :, 3] / 255.0
            except Exception as e_l:
                print("eroare logo:", e_l)

        wQ, hQ = 0, 0
        mat_qr = None
        if cache.get("qr_link"):
            try:
                import qrcode

                generator = qrcode.QRCode(version=1, box_size=10, border=2)
                generator.add_data(cache["qr_link"])
                generator.make(fit=True)

                p_qr = generator.make_image(
                    fill_color="black", back_color="white"
                ).convert("RGB")
                mat_qr = np.array(p_qr)[:, :, ::-1].copy()

                d_bz = cache.get("qr_size", 80)
                wQ = int((d_bz * 1.5) * s_calc)
                hQ = wQ
                mat_qr = cv2.resize(mat_qr, (wQ, hQ), interpolation=cv2.INTER_AREA)
            except ImportError:
                print("modulul qrcode nu e gasit")
            except Exception as ex_q:
                print("bug generare qr", ex_q)

        w_box = max(wL, latT, wQ)
        dist = int(15 * s_calc)

        h_actv = []
        if hL > 0:
            h_actv.append(hL)
        if hQ > 0:
            h_actv.append(hQ)
        if inaltT > 0:
            h_actv.append(inaltT)

        h_box = sum(h_actv) + dist * max(0, len(h_actv) - 1)
        mg_ofs = int(20 * s_calc)

        if cache.get("pozitie_text") == "✨ Inteligent (Auto-Detectare Spațiu Gol)":
            ps_x, ps_y = gaseste_pozitie_inteligenta(poza, w_box, h_box, mg_ofs)
        else:
            p_cx = cache.get("proc_cx", 0.5)
            p_cy = cache.get("proc_cy", 0.5)
            ps_x = int(p_cx * wf - w_box / 2.0)
            ps_y = int(p_cy * hf - h_box / 2.0)

        ps_x = max(mg_ofs, min(ps_x, wf - w_box - mg_ofs))
        ps_y = max(mg_ofs, min(ps_y, hf - h_box - mg_ofs))

        crs_y = ps_y

        if hL > 0:
            ox = ps_x + (w_box - wL) // 2
            roi_l = poza[crs_y : crs_y + hL, ox : ox + wL]

            if roi_l.shape[0] == hL and roi_l.shape[1] == wL:
                for cnl in range(3):
                    roi_l[:, :, cnl] = (
                        imgL_a * imgL_rgb[:, :, cnl] + (1 - imgL_a) * roi_l[:, :, cnl]
                    )
                poza[crs_y : crs_y + hL, ox : ox + wL] = roi_l
            crs_y += hL + dist

        if hQ > 0 and mat_qr is not None:
            oq = ps_x + (w_box - wQ) // 2
            roi_q = poza[crs_y : crs_y + hQ, oq : oq + wQ]
            if roi_q.shape[0] == hQ and roi_q.shape[1] == wQ:
                poza[crs_y : crs_y + hQ, oq : oq + wQ] = mat_qr
            crs_y += hQ + dist

        if inaltT > 0:
            ptx = int(ps_x + (w_box - latT) // 2)
            pty = int(crs_y + inaltT)

            c_rgb = cache.get("culoare", (255, 255, 255))
            c_bgr = [c_rgb[2], c_rgb[1], c_rgb[0]]
            c_bord = None

            if cache.get("auto_culoare", False):
                padd = int(10 * s_calc)
                roi_t = poza[
                    max(0, pty - inaltT - padd) : min(hf, pty + padd),
                    max(0, ptx - padd) : min(wf, ptx + latT + padd),
                ]
                if roi_t.size > 0:
                    mb, mg, mr = cv2.mean(roi_t)[:3]
                    lumi = 0.299 * mr + 0.587 * mg + 0.114 * mb

                    if lumi > 120:
                        c_bgr = (int(mb * 0.2), int(mg * 0.2), int(mr * 0.2))
                        c_bord = (
                            int(min(255, mb + 40)),
                            int(min(255, mg + 40)),
                            int(min(255, mr + 40)),
                        )
                    else:
                        c_bgr = (
                            int(min(255, 215 + mb * 0.15)),
                            int(min(255, 215 + mg * 0.15)),
                            int(min(255, 215 + mr * 0.15)),
                        )
                        c_bord = (int(mb * 0.2), int(mg * 0.2), int(mr * 0.2))

                umb_off = max(2, int(4 * s_calc))
                kbl = int(5 * s_calc) | 1
                opc_u = 0.85

                sy_u = max(0, pty - inaltT - kbl - umb_off)
                ey_u = min(hf, pty + kbl + umb_off)
                sx_u = max(0, ptx - kbl - umb_off)
                ex_u = min(wf, ptx + latT + kbl + umb_off)

                r_umb = poza[sy_u:ey_u, sx_u:ex_u]

                if r_umb.size > 0:
                    s_u = np.zeros_like(r_umb)
                    cv2.putText(
                        s_u,
                        str_final,
                        (ptx - sx_u + umb_off, pty - sy_u + umb_off),
                        f_cv,
                        sz_f,
                        (255, 255, 255),
                        grs + int(2 * s_calc),
                        cv2.LINE_AA,
                    )
                    s_u = cv2.GaussianBlur(s_u, (kbl, kbl), 0)
                    msq = s_u[:, :, 0] / 255.0
                    for k in range(3):
                        r_umb[:, :, k] = r_umb[:, :, k] * (1 - msq * opc_u)
                    poza[sy_u:ey_u, sx_u:ex_u] = r_umb

            if c_bord:
                cv2.putText(
                    poza,
                    str_final,
                    (ptx, pty),
                    f_cv,
                    sz_f,
                    c_bord,
                    grs + int(2 * s_calc),
                    cv2.LINE_AA,
                )

            cv2.putText(
                poza, str_final, (ptx, pty), f_cv, sz_f, c_bgr, grs, cv2.LINE_AA
            )

        trans = cache.get("opacitate", 80) / 100.0
        final_img = cv2.addWeighted(poza, trans, cadru, 1 - trans, 0)

        nm = os.path.basename(cale_src)
        sv_path = os.path.join(f_dest, nm)
        cv2.imwrite(sv_path, final_img)

        return True, nm

    except Exception as e_mare:
        print("A picat aplicarea watermarkului complet:", e_mare)
        return False, str(e_mare)


def aplica_watermark_frame_video(frm_cv, mem_config):
    copie = frm_cv.copy()
    h_v, w_v, _ = copie.shape

    rta = mem_config.get("raport_ui", 800)
    scra = max(w_v, h_v) / rta

    txts = []
    if mem_config.get("text"):
        txts.append(mem_config["text"])
    t_fin = " | ".join(txts)

    fnt = cv2.FONT_HERSHEY_SIMPLEX
    sz = (mem_config.get("font_size", 40) / 40.0) * scra
    thk = max(1, int(2 * scra))

    if t_fin:
        res_t = cv2.getTextSize(t_fin, fnt, sz, thk)
        lt, ht = res_t[0][0], res_t[0][1]
    else:
        lt, ht = 0, 0

    l_bg, l_al, l_w, l_h = None, None, 0, 0
    if mem_config.get("logo"):
        try:
            r_l = cv2.imread(mem_config["logo"], cv2.IMREAD_UNCHANGED)
            if r_l is not None:
                if len(r_l.shape) == 2:
                    r_l = cv2.cvtColor(r_l, cv2.COLOR_GRAY2BGRA)
                elif r_l.shape[2] == 3:
                    r_l = cv2.cvtColor(r_l, cv2.COLOR_BGR2BGRA)

                if r_l.shape[2] == 4:
                    z = mem_config.get("zoom", 100) / 100.0
                    l_w = int((200 * z) * scra)
                    l_h = int(r_l.shape[0] * (l_w / r_l.shape[1]))
                    r_im = cv2.resize(r_l, (l_w, l_h), interpolation=cv2.INTER_AREA)
                    l_bg, l_al = r_im[:, :, :3], r_im[:, :, 3] / 255.0
        except Exception as e:
            print("Nu merge logoul pe video", e)

    q_w, q_h = 0, 0
    q_mat = None
    if mem_config.get("qr_link"):
        try:
            import qrcode

            qo = qrcode.QRCode(version=1, box_size=10, border=1)
            qo.add_data(mem_config["qr_link"])
            qo.make(fit=True)
            qi = qo.make_image(fill_color="black", back_color="white").convert("RGB")
            q_mat = np.array(qi)[:, :, ::-1].copy()

            bsz = mem_config.get("qr_size", 80)
            q_w = int((bsz * 1.5) * scra)
            q_h = q_w
            q_mat = cv2.resize(q_mat, (q_w, q_h), interpolation=cv2.INTER_AREA)
        except Exception as bg:
            print("qr a crapat pe video:", bg)

    wbx = max(l_w, lt, q_w)
    sps = int(15 * scra)

    h_arr = []
    for valh in [l_h, q_h, ht]:
        if valh > 0:
            h_arr.append(valh)

    thx = sum(h_arr) + sps * max(0, len(h_arr) - 1)

    c_xx, c_yy = mem_config.get("proc_cx", 0.5), mem_config.get("proc_cy", 0.5)
    px = max(10, min(int(c_xx * w_v - wbx / 2), w_v - wbx - 10))
    py = max(10, min(int(c_yy * h_v - thx / 2), h_v - thx - 10))

    cy_cur = py

    if l_h > 0:
        ox_l = px + (wbx - l_w) // 2
        roil = copie[cy_cur : cy_cur + l_h, ox_l : ox_l + l_w]
        if roil.shape[0] == l_h and roil.shape[1] == l_w:
            for ch in range(3):
                roil[:, :, ch] = l_al * l_bg[:, :, ch] + (1 - l_al) * roil[:, :, ch]
            copie[cy_cur : cy_cur + l_h, ox_l : ox_l + l_w] = roil
        cy_cur += l_h + sps

    if q_h > 0 and q_mat is not None:
        ox_q = px + (wbx - q_w) // 2
        roiq = copie[cy_cur : cy_cur + q_h, ox_q : ox_q + q_w]
        if roiq.shape[0] == q_h and roiq.shape[1] == q_w:
            copie[cy_cur : cy_cur + q_h, ox_q : ox_q + q_w] = q_mat
        cy_cur += q_h + sps

    if ht > 0:
        pos_t_x = int(px + (wbx - lt) // 2)
        pos_t_y = int(cy_cur + ht)

        c_base = mem_config.get("culoare", (255, 255, 255))
        c_bg = [c_base[2], c_base[1], c_base[0]]
        c_bo = None

        if mem_config.get("auto_culoare", False):
            vp = int(10 * scra)
            rtx = copie[
                max(0, pos_t_y - ht - vp) : min(h_v, pos_t_y + vp),
                max(0, pos_t_x - vp) : min(w_v, pos_t_x + lt + vp),
            ]
            if rtx.size > 0:
                mb, mg, mr = cv2.mean(rtx)[:3]
                lmn = 0.299 * mr + 0.587 * mg + 0.114 * mb
                if lmn > 120:
                    c_bg = (int(mb * 0.2), int(mg * 0.2), int(mr * 0.2))
                    c_bo = (
                        int(min(255, mb + 40)),
                        int(min(255, mg + 40)),
                        int(min(255, mr + 40)),
                    )
                else:
                    c_bg = (
                        int(min(255, 215 + mb * 0.15)),
                        int(min(255, 215 + mg * 0.15)),
                        int(min(255, 215 + mr * 0.15)),
                    )
                    c_bo = (int(mb * 0.2), int(mg * 0.2), int(mr * 0.2))

        fu = max(2, int(4 * scra))
        blk = int(5 * scra) | 1
        opu = 0.85

        u1 = max(0, pos_t_y - ht - blk - fu)
        u2 = min(h_v, pos_t_y + blk + fu)
        v1 = max(0, pos_t_x - blk - fu)
        v2 = min(w_v, pos_t_x + lt + blk + fu)

        z_umb = copie[u1:u2, v1:v2]
        if z_umb.size > 0:
            su = np.zeros_like(z_umb)
            cv2.putText(
                su,
                t_fin,
                (pos_t_x - v1 + fu, pos_t_y - u1 + fu),
                fnt,
                sz,
                (255, 255, 255),
                thk + int(2 * scra),
                cv2.LINE_AA,
            )
            su = cv2.GaussianBlur(su, (blk, blk), 0)
            ms = su[:, :, 0] / 255.0
            for a in range(3):
                z_umb[:, :, a] = z_umb[:, :, a] * (1 - ms * opu)
            copie[u1:u2, v1:v2] = z_umb

        if c_bo:
            cv2.putText(
                copie,
                t_fin,
                (pos_t_x, pos_t_y),
                fnt,
                sz,
                c_bo,
                thk + int(2 * scra),
                cv2.LINE_AA,
            )

        cv2.putText(copie, t_fin, (pos_t_x, pos_t_y), fnt, sz, c_bg, thk, cv2.LINE_AA)

    opa = mem_config.get("opacitate", 80) / 100.0
    return cv2.addWeighted(copie, opa, frm_cv, 1 - opa, 0)
