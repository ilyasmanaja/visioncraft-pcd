# PROJECT CONTEXT: VisionCraft PCD — Web-Based Digital Image Processing Studio

> **Dokumen Master / Single Source of Truth.**
> Simpan file ini di root repository (`/PROJECT_CONTEXT.md`) dan tempel seluruh isinya di awal setiap sesi AI chat saat melanjutkan pengembangan backend, modul fungsi PCD, frontend, maupun integrasi API. Jika ada konflik antara jawaban AI dan dokumen ini, **dokumen ini yang benar** sampai direvisi secara eksplisit.

| Atribut | Nilai |
|---|---|
| Nama Aplikasi | **VisionCraft PCD** |
| Mata Kuliah | Pengolahan Citra Digital (PCD) |
| Jenis Tugas | Tugas Mandiri (Solo Developer) |
| Pengembang | Muhammad Raihan Ilyasman |
| Platform | Web Application (Python Flask + Single-Page Editor) |
| Versi Dokumen | 1.0 |
| Referensi Menu | *Menu structure – Aplikasi PCD* (Update 19/09/2025) |
| Copyright Footer | `VisionCraft PCD — Copyright © Muhammad Raihan Ilyasman – 2026` |

---

## DAFTAR ISI

1. [Ringkasan Proyek & Tujuan](#1-ringkasan-proyek--tujuan)
2. [Arsitektur & Tech Stack](#2-arsitektur--tech-stack)
3. [Rancangan Struktur Direktori / Folder Proyek](#3-rancangan-struktur-direktori--folder-proyek)
4. [Katalog Modul Operasi PCD & Parameter Engine](#4-katalog-modul-operasi-pcd--parameter-engine)
5. [Spesifikasi Kontrak Komunikasi API](#5-spesifikasi-kontrak-komunikasi-api-requestresponse-format)
6. [Alur Kerja Interaktivitas UI & Edge Cases](#6-alur-kerja-interaktivitas-ui--edge-cases)
7. [Pengembang & Standar Kualitas Mandiri (Solo Workflow)](#7-pengembang--standar-kualitas-mandiri-solo-workflow)
8. [Roadmap / Tahapan Pengerjaan Mandiri](#8-roadmap--tahapan-pengerjaan-mandiri)
9. [Lampiran](#9-lampiran)

---

## 1. RINGKASAN PROYEK & TUJUAN

### 1.1 Latar Belakang Tugas

Tugas mandiri mata kuliah **Pengolahan Citra Digital (PCD)** meminta mahasiswa membangun aplikasi pengolah citra dengan struktur menu yang sudah ditetapkan dosen (File, Basic Ops, Enhancement, Noise, Edge Detection, About). Perintah awal tugas mengarah ke **desktop GUI (Tkinter + Pillow)**. Proyek ini dikerjakan oleh **satu orang (solo developer)**, sehingga seluruh keputusan arsitektur harus mengutamakan kesederhanaan, modularitas, dan kemudahan debugging.

### 1.2 Motivasi Transisi dari Desktop ke Web Editor

| Aspek | Desktop (Tkinter + Pillow) | Web (Flask + Single-Page Editor) — **dipilih** |
|---|---|---|
| Tampilan | Terbatas, gaya widget bawaan | Bebas: dark mode modern ala Photopea/Photoshop Web |
| Interaksi canvas | Sulit (zoom, pan, crop interaktif, koordinat kursor) | Mudah dengan HTML5 Canvas + JavaScript |
| Panel parameter dinamis | Perlu banyak widget manual | Dirender otomatis dari skema JSON |
| Distribusi & demo | Perlu instalasi Python di komputer penguji | Cukup buka browser / deploy ke server |
| Portofolio | Kurang menarik | Dapat dipamerkan lewat tautan publik / GitHub |
| Pemisahan logika | Rawan tercampur dengan kode GUI | Backend murni fungsi, frontend murni tampilan |

### 1.3 Tujuan Proyek

1. Membangun **studio pengolah citra berbasis web** yang mencakup **seluruh menu** pada dokumen *Menu structure – Aplikasi PCD*.
2. Memisahkan logika pemrosesan citra menjadi **fungsi Python murni (pure modular functions)** di `app/operations/`, bukan di file route Flask, sehingga dapat diuji tanpa server.
3. Menyediakan antarmuka editor **side-by-side** (Original vs Processed) dengan panel parameter dinamis.
4. Menghasilkan **dokumentasi GitHub** dan **video tutorial YouTube** sebagai bagian menu *About*.
5. Menjadi **bahan pembelajaran** konsep PCD: operasi titik, aritmetika/boolean, geometri, konvolusi, domain frekuensi, ruang warna, restorasi/noise, dan deteksi tepi.

### 1.4 Ruang Lingkup

| Termasuk (In Scope) | Tidak Termasuk (Out of Scope) |
|---|---|
| Semua menu: File, Basic Ops, Enhancement, Noise, Edge Detection, About | Autentikasi user, database, akun, penyimpanan cloud |
| Pemrosesan citra statis (JPG/PNG/BMP/WEBP) | Video, animasi, batch processing banyak file |
| Operasi dual-image (Aritmatika & Boolean) | Layer system ala Photoshop penuh |
| Undo/Redo sederhana di sisi klien | Kolaborasi multi-user real-time |
| Penyimpanan hasil (Save / Save As) di sisi klien | Machine learning / deep learning |

> **Catatan Segmentation:** Gambar referensi menu pada header menampilkan item `Segmentation`, tetapi **tidak ada rincian submenu**-nya di struktur menu dan **tidak termasuk** dalam spesifikasi proyek ini. Menu tersebut **tidak diimplementasikan** pada versi 1.0. Jika dosen mewajibkan, tambahkan sebagai ekstensi di Tahap 5 (kandidat: Otsu multi-level, K-Means color segmentation, Region Growing) tanpa mengubah kontrak API (cukup mendaftarkan operasi baru pada registry, lihat §4.1).

---

## 2. ARSITEKTUR & TECH STACK

### 2.1 Gaya Arsitektur

**Client–Server, stateless server.** Backend Flask tidak menyimpan gambar pengguna di disk maupun session. Seluruh state gambar (original, current, history) berada di **browser**. Setiap request membawa gambar yang dibutuhkan, server memproses, lalu mengembalikan hasilnya.

Alasan: sederhana, tidak ada manajemen file sementara, aman untuk deployment tanpa storage, mudah diuji.

### 2.2 Diagram Alur Client–Server

```
┌────────────────────────────── BROWSER (SPA) ──────────────────────────────┐
│  Menu Bar ──► Param Drawer ──► [Apply / Preview]                          │
│       │            │                  │                                    │
│       ▼            ▼                  ▼                                    │
│  state.js     ui/params.js      api.js (fetch)                             │
│  (history,    (render form dari  POST /api/process                         │
│   original,    skema operasi)    JSON {operation, params, image, image_b}  │
│   current)                              │                                  │
└─────────────────────────────────────────┼──────────────────────────────────┘
                                          │  Base64 data URL (PNG)
                                          ▼
┌──────────────────────────── FLASK BACKEND ────────────────────────────────┐
│  routes/api.py                                                             │
│    1. validate request (validators.py)                                     │
│    2. decode Base64 ─► PIL.Image ─► np.ndarray (uint8)   (image_io.py)     │
│    3. registry.get(operation) ─► func(img, **params)                       │
│    4. np.ndarray ─► PIL ─► PNG ─► Base64                                   │
│    5. return JSON {ok, image, meta}                                        │
│                     │                                                      │
│                     ▼                                                      │
│  operations/*  (pure functions — NumPy / Pillow / SciPy, tanpa Flask)      │
└────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Mekanisme Transfer Data Gambar

| Skenario | Mekanisme | Format | Keterangan |
|---|---|---|---|
| Upload awal (dari komputer) | **Dibaca langsung di browser** (`FileReader` / `createImageBitmap`) ke Canvas; server **tidak** terlibat kecuali validasi opsional via `POST /api/upload` | File asli | Validasi cepat di klien + validasi ulang di server |
| Trigger operasi 1 gambar | `fetch` **JSON** | `image`: Base64 data URL PNG | Default untuk seluruh operasi |
| Trigger operasi 2 gambar (Aritmatika/Boolean) | `fetch` **JSON** | `image` (A) + `image_b` (B) | Kedua gambar dikirim sebagai Base64 |
| Respons hasil | JSON | `image`: Base64 data URL PNG (lossless) | Disertai `meta` (dimensi, mode, waktu proses) |
| Save / Save As | **Di klien**: `canvas.toBlob()` + `<a download>` | PNG / JPEG / BMP\* / WEBP | \*BMP via encoder JS sederhana atau via endpoint opsional `/api/export` |
| Nilai piksel di status bar | **Di klien**: `ctx.getImageData(x, y, 1, 1)` | — | Tidak membebani server |

> **Keputusan:** gunakan **JSON + Base64** untuk semua operasi (satu kontrak seragam). `FormData` hanya dipakai bila ukuran payload menjadi masalah (opsional, tidak wajib).

### 2.4 Representasi Citra Internal (Backend)

| Item | Aturan |
|---|---|
| Tipe data utama | `numpy.ndarray`, `dtype=uint8`, rentang 0–255 |
| Bentuk | Grayscale: `(H, W)`; RGB: `(H, W, 3)` |
| Komputasi antara | Konversi ke `float32`/`float64` di dalam fungsi, **wajib** `clip` + `astype(uint8)` sebelum return |
| Mode warna masuk | Selalu dinormalisasi ke **`RGB`** atau **`L`** (alpha, palette, CMYK dikonversi di `image_io.py`) |
| Signature fungsi operasi | `def nama_operasi(img: np.ndarray, **params) -> np.ndarray` (dual-image: `def nama(img_a, img_b, **params)`) |
| Efek samping | **Dilarang** (tidak membaca/menulis file, tidak memakai global state) |

### 2.5 Tech Stack

| Lapisan | Teknologi | Peran |
|---|---|---|
| Bahasa | **Python 3.11+** | Seluruh backend |
| Web Framework | **Flask** (+ `flask-cors` bila frontend dipisah saat dev) | Routing, serving template & static |
| Image I/O | **Pillow (PIL)** | Decode/encode, konversi mode, resize, EXIF transpose |
| Numerik | **NumPy** | Matriks, konvolusi (`sliding_window_view`), FFT (`numpy.fft`), noise |
| Ilmiah | **SciPy** (`scipy.ndimage`) — opsional | Median/Gaussian filter cepat, validasi hasil |
| Visualisasi | **Matplotlib** — opsional | Colormap pseudo-coloring (`matplotlib.cm`), histogram bila dirender server |
| Template | **Jinja2** | Satu halaman `editor.html`, partial untuk modal & drawer |
| Frontend | **HTML5, JavaScript murni (ES Modules)**, Fetch API | Logika UI, canvas, state |
| Styling | **Tailwind CSS (CDN/CLI)** atau **Vanilla CSS** | Tema Modern Clean **Dark Mode** ala Photopea |
| Testing | **pytest**, **pytest-cov** | Uji unit fungsi operasi + uji endpoint |
| Kualitas kode | **ruff** / **black**, **mypy** (opsional) | Lint, format, type check |
| Versi kontrol | **Git + GitHub** | Dokumentasi & tautan di menu About |

**Dependensi minimum (`requirements.txt`):**

```text
Flask>=3.0
Pillow>=10.0
numpy>=1.26
scipy>=1.11
matplotlib>=3.8
pytest>=8.0
```

> **Aturan:** **Tidak memakai OpenCV (`cv2`)** — seluruh algoritma inti PCD (konvolusi, Canny, FFT filter, noise, ruang warna, dsb.) ditulis sendiri dengan NumPy agar proses pembelajaran dan penilaian jelas. SciPy hanya untuk akselerasi/validasi.

---

## 3. RANCANGAN STRUKTUR DIREKTORI / FOLDER PROYEK

```
visioncraft-pcd/
├── PROJECT_CONTEXT.md              # dokumen ini (single source of truth)
├── README.md                       # dokumentasi GitHub (instalasi, demo, screenshot)
├── requirements.txt
├── run.py                          # entry point: from app import create_app
├── config.py                       # MAX_CONTENT_LENGTH, MAX_IMAGE_SIDE, dsb.
│
├── app/
│   ├── __init__.py                 # create_app() — application factory
│   │
│   ├── routes/                     # HANYA routing & orkestrasi, tanpa logika PCD
│   │   ├── __init__.py
│   │   ├── pages.py                # GET /  → render editor.html
│   │   └── api.py                  # /api/operations, /api/process, /api/upload, /api/histogram
│   │
│   ├── operations/                 # ★ FUNGSI PCD MURNI (tanpa import Flask)
│   │   ├── __init__.py             # impor semua modul agar ter-register
│   │   ├── registry.py             # decorator @register_operation, OPERATIONS dict, ParamSpec
│   │   │
│   │   ├── basic/
│   │   │   ├── negative.py
│   │   │   ├── arithmetic.py       # add, subtract, multiply, divide (dual-image)
│   │   │   ├── boolean.py          # not, and, or, xor
│   │   │   ├── geometric.py        # translation, rotation, zooming, flipping, cropping
│   │   │   ├── thresholding.py
│   │   │   ├── convolution.py
│   │   │   ├── fourier.py
│   │   │   └── colouring.py        # binary, grayscale, rgb, hsv, cmy, yuv, yiq, pseudo
│   │   │
│   │   ├── enhancement/
│   │   │   ├── brightness_contrast.py
│   │   │   ├── histogram.py        # equalization + hitung histogram
│   │   │   ├── smoothing.py        # spatial (lowpass, median) + frequency (ILPF, BLPF)
│   │   │   ├── sharpening.py       # spatial (highpass, highboost) + frequency (IHPF, BHPF)
│   │   │   └── geometric_correction.py
│   │   │
│   │   ├── edge/
│   │   │   ├── gradient_first.py   # sobel, prewitt, roberts
│   │   │   ├── gradient_second.py  # laplacian, log, canny
│   │   │   └── compass.py          # kirsch, robinson, prewitt-compass
│   │   │
│   │   └── noise/
│   │       └── generators.py       # gaussian, rayleigh, erlang, exponential, uniform, impulse
│   │
│   ├── utils/
│   │   ├── image_io.py             # base64 ⇄ ndarray, normalisasi mode, exif_transpose
│   │   ├── validators.py           # validasi payload, ukuran, tipe, parameter
│   │   ├── colorspace.py           # konversi RGB⇄HSV/CMY/YUV/YIQ (tanpa colorsys loop lambat)
│   │   ├── kernels.py              # kernel preset (sobel, prewitt, gaussian, laplacian, dsb.)
│   │   ├── frequency.py            # helper FFT: pad, shift, mask jarak D(u,v)
│   │   ├── padding.py              # reflect/zero/edge padding untuk konvolusi
│   │   └── errors.py               # class ProcessingError, ValidationError (+ kode error)
│   │
│   ├── templates/
│   │   ├── base.html               # <head>, tema, script loader
│   │   ├── editor.html             # layout utama (navbar, canvas, drawer, statusbar)
│   │   └── partials/
│   │       ├── navbar.html         # multilevel dropdown
│   │       ├── param_drawer.html   # container panel parameter dinamis
│   │       ├── statusbar.html
│   │       └── modal_about.html    # biodata developer + link GitHub/YouTube
│   │
│   └── static/
│       ├── css/
│       │   └── theme.css           # CSS variable dark mode + komponen kustom
│       ├── js/
│       │   ├── main.js             # bootstrap, wiring event
│       │   ├── api.js              # wrapper fetch + error handling + AbortController
│       │   ├── state.js            # original, current, history (undo/redo)
│       │   ├── canvas.js           # render, zoom/pan, koordinat kursor, crop selector
│       │   ├── menu.js             # build menu dari skema /api/operations
│       │   ├── params.js           # render form parameter dinamis (slider, select, dll.)
│       │   ├── dual_image.js       # slot upload gambar kedua
│       │   ├── statusbar.js
│       │   ├── fileio.js           # open, drag-drop, save, save as
│       │   └── modal.js
│       └── img/                    # logo, ikon, sample images untuk demo
│
├── tests/
│   ├── conftest.py                 # fixture: gambar uji (gradien, checkerboard, noise)
│   ├── test_basic.py
│   ├── test_enhancement.py
│   ├── test_edge.py
│   ├── test_noise.py
│   ├── test_colorspace.py
│   └── test_api.py                 # test_client Flask
│
└── docs/
    ├── screenshots/
    └── laporan/                    # bahan laporan / PPT tugas
```

### 3.1 Aturan Pemisahan Tanggung Jawab

| Lapisan | Boleh | Dilarang |
|---|---|---|
| `routes/` | Parse request, panggil `utils` + `registry`, bentuk response JSON | Menulis algoritma PCD |
| `operations/` | Fungsi murni NumPy/Pillow, mendaftar ke registry | `import flask`, I/O file, global state |
| `utils/` | Helper lintas operasi (I/O, validasi, kernel, ruang warna) | Logika spesifik satu operasi |
| `static/js/` | UI, state, fetch | Mengimplementasi algoritma PCD di JS (kecuali pembacaan piksel & Save) |

---

## 4. KATALOG MODUL OPERASI PCD & PARAMETER ENGINE

### 4.1 Mekanisme Registry & Skema Parameter

Setiap operasi **didaftarkan** dengan decorator sehingga: (a) route `/api/process` tidak perlu `if/else` panjang, (b) frontend dapat membangun **menu dan panel parameter secara otomatis** dari `GET /api/operations`.

```python
# app/operations/registry.py  (kerangka)
from dataclasses import dataclass, field
from typing import Callable, Literal

ParamType = Literal["int", "float", "bool", "select", "kernel", "point_list", "rect"]

@dataclass
class ParamSpec:
    name: str
    type: ParamType
    label: str
    default: object
    min: float | None = None
    max: float | None = None
    step: float | None = None
    options: list[str] | None = None      # untuk type="select"
    help: str = ""

@dataclass
class OperationSpec:
    id: str                               # contoh: "enhance.brightness"
    label: str                            # teks menu
    menu_path: list[str]                  # ["Enhancement", "Brightness"]
    func: Callable
    params: list[ParamSpec] = field(default_factory=list)
    inputs: int = 1                       # 1 = satu gambar, 2 = dual-image
    color_policy: str = "per_channel"     # lihat §4.2
    live_preview: bool = False            # boleh preview otomatis saat slider digeser

OPERATIONS: dict[str, OperationSpec] = {}

def register_operation(**kwargs):
    def deco(func):
        spec = OperationSpec(func=func, **kwargs)
        OPERATIONS[spec.id] = spec
        return func
    return deco
```

### 4.2 Kebijakan Warna (`color_policy`)

| Nilai | Arti | Perilaku |
|---|---|---|
| `per_channel` | Operasi dijalankan **terpisah di tiap kanal** R, G, B | Hasil tetap RGB (atau L jika input L) |
| `luminance` | Operasi hanya pada kanal luminans (Y dari YUV), kroma dipertahankan | Hasil tetap RGB — menghindari pergeseran warna |
| `gray_only` | Algoritma hanya bermakna pada intensitas tunggal | Input RGB dikonversi otomatis ke **L**; hasil **L**; `meta.warnings` berisi pemberitahuan |
| `rgb_only` | Butuh 3 kanal | Input **L** diduplikasi ke 3 kanal atau ditolak dengan kode `E_COLOR_MODE` (ditentukan per operasi) |
| `dual` | Dua gambar disamakan mode & ukuran dulu | Lihat §6.2 |

### 4.3 Menu **File**

Sebagian besar dijalankan **di sisi klien** (tanpa memanggil Python). Backend hanya membantu validasi.

| Menu | Parameter / UI | Penanggung Jawab | Catatan |
|---|---|---|---|
| **Open…** | File picker (`accept=image/*`) + **drag-and-drop** ke canvas | `fileio.js` → opsional `POST /api/upload` | Gambar disimpan sebagai `original` & `current` di `state.js` |
| **Save** | Unduh hasil (`current`) dengan nama `<nama_asli>_vc.png` | `fileio.js` (`canvas.toBlob`) | Format default PNG |
| **Save As** | Modal: nama file, format (PNG/JPEG/BMP/WEBP), kualitas (JPEG/WEBP 1–100) | `fileio.js`; BMP via `/api/export` bila perlu | — |
| **Exit / Reset Canvas** | Konfirmasi → bersihkan canvas, history, slot gambar kedua | `state.reset()` | Tidak menutup tab browser; mengembalikan ke layar kosong |

### 4.4 Menu **Basic Ops**

#### 4.4.1 Negative

| ID | `basic.negative` |
|---|---|
| Fungsi | `negative(img)` — `app/operations/basic/negative.py` |
| Parameter | — (tanpa parameter) |
| Rumus | `s = 255 − r` |
| Color policy | `per_channel` |
| Live preview | Ya |

#### 4.4.2 Arithmetic *(dual-image)*

| ID | Fungsi | Rumus | Catatan |
|---|---|---|---|
| `basic.arithmetic.add` | `arith_add(a, b, **p)` | `a + b` | — |
| `basic.arithmetic.subtract` | `arith_subtract(a, b, **p)` | `a − b` | Opsi `abs_diff` |
| `basic.arithmetic.multiply` | `arith_multiply(a, b, **p)` | `(a × b) / 255` | Normalisasi agar tetap 0–255 |
| `basic.arithmetic.divide` | `arith_divide(a, b, **p)` | `a / (b + ε)` lalu diskalakan | `ε = 1e-6`; hindari pembagian nol |

**Parameter bersama (seluruh operasi aritmatika):**

| Param | Tipe | Rentang / Opsi | Default | Keterangan |
|---|---|---|---|---|
| `image_b` | gambar | — | wajib | Dikirim via slot gambar kedua (§6.2) |
| `resize_mode` | select | `resize_b_to_a`, `center_crop`, `pad` | `resize_b_to_a` | Cara menyamakan ukuran B terhadap A |
| `overflow` | select | `clip`, `normalize` | `clip` | `clip` = potong ke 0–255; `normalize` = skala min–max |
| `abs_diff` *(subtract saja)* | bool | — | `false` | Pakai `|a − b|` |
| `scale` *(divide saja)* | float | 1–255 | `128` | Faktor pengali setelah pembagian (agar hasil terlihat) |

Color policy: `dual` (+ `per_channel`). Live preview: Tidak.

#### 4.4.3 Boolean

| ID | Fungsi | Input | Operasi |
|---|---|---|---|
| `basic.boolean.not` | `bool_not(img, **p)` | 1 gambar | Bitwise NOT (`~img`) atau pada citra biner |
| `basic.boolean.and` | `bool_and(a, b, **p)` | 2 gambar | `a & b` |
| `basic.boolean.or` | `bool_or(a, b, **p)` | 2 gambar | `a \| b` |
| `basic.boolean.xor` | `bool_xor(a, b, **p)` | 2 gambar | `a ^ b` |

| Param | Tipe | Rentang / Opsi | Default | Keterangan |
|---|---|---|---|---|
| `mode` | select | `bitwise`, `binary` | `bitwise` | `bitwise` = operasi bit per piksel 8-bit; `binary` = citra di-threshold dulu lalu operasi logika (hasil 0/255) |
| `threshold` | int | 0–255 | `128` | Aktif hanya jika `mode=binary` |
| `resize_mode` | select | seperti aritmatika | `resize_b_to_a` | Hanya AND/OR/XOR |

#### 4.4.4 Geometrics

| ID | Fungsi | Parameter | Catatan |
|---|---|---|---|
| `basic.geometric.translation` | `translate(img, tx, ty, fill)` | `tx` int (−W..W), `ty` int (−H..H), `fill` select `black/white/edge` | Pergeseran; area kosong diisi `fill` |
| `basic.geometric.rotation` | `rotate(img, angle, expand, interpolation, fill)` | `angle` float (−360..360), `expand` bool, `interpolation` select `nearest/bilinear/bicubic`, `fill` | Rotasi sekitar pusat; `expand=true` memperbesar kanvas agar tidak terpotong |
| `basic.geometric.zooming` | `zoom(img, factor, interpolation)` | `factor` float (0.1–4.0), `interpolation` | Resize proporsional; batas piksel akhir ≤ `MAX_IMAGE_SIDE` |
| `basic.geometric.flipping` | `flip(img, axis)` | `axis` select `horizontal/vertical/both` | — |
| `basic.geometric.cropping` | `crop(img, x, y, w, h)` | `rect` (x, y, w, h) | UI: seleksi persegi di canvas (drag), angka ikut ter-update di drawer |

Color policy seluruhnya `per_channel`. Live preview: translation/rotation/zoom/flip = Ya; crop = Tidak (butuh klik Apply).

#### 4.4.5 Thresholding

| ID | `basic.thresholding` |
|---|---|
| Fungsi | `threshold(img, method, value, block_size, c, invert)` |
| Color policy | `gray_only` |
| Live preview | Ya |

| Param | Tipe | Rentang / Opsi | Default |
|---|---|---|---|
| `method` | select | `global`, `otsu`, `adaptive_mean`, `adaptive_gaussian` | `global` |
| `value` | int | 0–255 *(aktif jika `global`)* | `128` |
| `block_size` | int ganjil | 3–101 *(adaptive)* | `11` |
| `c` | float | −20–20 *(adaptive)* | `2` |
| `invert` | bool | — | `false` |

Hasil: citra biner (0 / 255). Otsu: hitung dari histogram, kembalikan nilai ambang di `meta.info.threshold`.

#### 4.4.6 Convolution

| ID | `basic.convolution` |
|---|---|
| Fungsi | `convolve(img, kernel, normalize, padding, bias)` — `convolution.py`, helper `utils/kernels.py`, `utils/padding.py` |
| Color policy | `per_channel` |
| Live preview | Ya (kernel ≤ 7×7) |

| Param | Tipe | Rentang / Opsi | Default | Keterangan |
|---|---|---|---|---|
| `kernel_preset` | select | `identity`, `box_3x3`, `gaussian_3x3`, `gaussian_5x5`, `sharpen`, `emboss`, `edge_enhance`, `custom` | `box_3x3` | Preset kernel |
| `kernel` | kernel (matriks) | ukuran ganjil 3×3 – 9×9, nilai float | sesuai preset | Wajib jika `custom`; dikirim sebagai array 2D |
| `normalize` | bool | — | `true` | Bagi dengan jumlah elemen kernel bila jumlah ≠ 0 |
| `padding` | select | `zero`, `reflect`, `edge` | `reflect` | Perlakuan batas |
| `bias` | int | −255–255 | `0` | Ditambahkan setelah konvolusi (mis. emboss: 128) |

Implementasi: `numpy.lib.stride_tricks.sliding_window_view` + `einsum`/`tensordot`; **bukan** loop piksel Python. UI: grid input angka kernel (N×N) yang dapat diedit.

#### 4.4.7 Fourier Transform

| ID | `basic.fourier` |
|---|---|
| Fungsi | `fourier_transform(img, output, shift, log_scale)` |
| Color policy | `gray_only` |
| Live preview | Tidak |

| Param | Tipe | Opsi | Default | Keterangan |
|---|---|---|---|---|
| `output` | select | `magnitude`, `phase`, `reconstruction` | `magnitude` | `reconstruction` = IFFT(FFT(img)) untuk membuktikan reversibilitas |
| `shift` | bool | — | `true` | `fftshift` (DC di tengah) |
| `log_scale` | bool | — | `true` | `log(1 + |F|)` lalu normalisasi 0–255 |

Rumus: `F(u,v) = FFT2(f(x,y))`; magnitudo = `|F|`; fase = `angle(F)`. Menggunakan `numpy.fft.fft2`, `fftshift`, `ifft2`.

#### 4.4.8 Colouring

| ID | Fungsi | Parameter | Output |
|---|---|---|---|
| `basic.colouring.binary` | `to_binary(img, threshold, invert)` | `threshold` int 0–255 (default 128), `invert` bool | Citra biner (L) |
| `basic.colouring.grayscale` | `to_grayscale(img, method)` | `method` select `luminosity` (0.299R+0.587G+0.114B), `average`, `lightness`, `red`, `green`, `blue` | Citra L |
| `basic.colouring.rgb` | `view_rgb(img, channel)` | `channel` select `composite`, `R`, `G`, `B`, `R_tint`, `G_tint`, `B_tint` | Citra RGB (kanal ditampilkan abu-abu atau diberi tint) |
| `basic.colouring.hsv` | `to_hsv(img, channel)` | `channel` select `composite`, `H`, `S`, `V` | Citra RGB/L representasi HSV |
| `basic.colouring.cmy` | `to_cmy(img, channel)` | `channel` select `composite`, `C`, `M`, `Y` | `C=255−R`, `M=255−G`, `Y=255−B` |
| `basic.colouring.yuv` | `to_yuv(img, channel)` | `channel` select `composite`, `Y`, `U`, `V` | Matriks BT.601 |
| `basic.colouring.yiq` | `to_yiq(img, channel)` | `channel` select `composite`, `Y`, `I`, `Q` | Matriks NTSC |
| `basic.colouring.pseudo` | `pseudo_color(img, colormap, invert)` | `colormap` select `jet`, `hot`, `cool`, `rainbow`, `viridis`, `bone`; `invert` bool | Gray → RGB via LUT 256 entri |

**Aturan tampilan ruang warna:** `composite` menampilkan tiga kanal ruang warna tersebut **dipetakan langsung sebagai R,G,B layar** (sehingga terlihat "aneh" secara visual — itu wajar dan memang bagian pembelajaran). Kanal tunggal ditampilkan sebagai citra abu-abu (`L`) dengan normalisasi 0–255. `meta.info` memuat rentang nilai asli tiap kanal. Konversi diimplementasikan manual di `utils/colorspace.py` (vektorisasi NumPy).

**Matriks konversi (acuan):**

```text
YUV (BT.601)                      YIQ (NTSC)
Y =  0.299 R + 0.587 G + 0.114 B  Y =  0.299 R + 0.587 G + 0.114 B
U = -0.147 R - 0.289 G + 0.436 B  I =  0.596 R - 0.274 G - 0.322 B
V =  0.615 R - 0.515 G - 0.100 B  Q =  0.211 R - 0.523 G + 0.312 B
```

Karena nilai U, V, I, Q bisa negatif, saat ditampilkan dilakukan **offset/normalisasi min–max** ke 0–255.

### 4.5 Menu **Enhancement**

#### 4.5.1 Brightness & Contrast

| ID | Fungsi | Parameter | Rumus | Policy |
|---|---|---|---|---|
| `enhance.brightness` | `adjust_brightness(img, beta)` | `beta` int −255..255 (default 0, slider) | `s = r + β` lalu clip | `per_channel` |
| `enhance.contrast` | `adjust_contrast(img, alpha, pivot)` | `alpha` float 0.0–3.0 (default 1.0), `pivot` int 0–255 (default 128) | `s = α (r − pivot) + pivot` lalu clip | `per_channel` |

Live preview: Ya (kedua operasi). Debounce 150–250 ms.

#### 4.5.2 Histogram Equalization

| ID | `enhance.hist_equalization` |
|---|---|
| Fungsi | `histogram_equalization(img, mode)` — `histogram.py` + helper `compute_histogram(img)` |
| Policy | `luminance` (default) |

| Param | Tipe | Opsi | Default | Keterangan |
|---|---|---|---|---|
| `mode` | select | `luminance`, `per_channel`, `gray` | `luminance` | `luminance`: equalisasi kanal Y (YUV), kroma tetap; `per_channel` dapat menggeser warna; `gray`: ubah ke L dulu |
| `clip_limit` *(opsional lanjutan)* | float | 1.0–10.0 | `null` | Jika diisi → CLAHE sederhana (ekstensi opsional) |

Algoritma: `pdf → cdf → LUT = round((cdf − cdf_min)/(N − cdf_min) × 255)`. Response menyertakan `meta.info.histogram_before` dan `histogram_after` (array 256 nilai) agar frontend dapat menampilkan **grafik histogram** pada drawer.

#### 4.5.3 Smoothing

| Domain | ID | Fungsi | Parameter | Penjelasan |
|---|---|---|---|---|
| Spatial | `enhance.smoothing.spatial.lowpass` | `lowpass_filter(img, kernel_type, ksize, sigma)` | `kernel_type` select `mean`/`gaussian`; `ksize` int ganjil 3–21 (3); `sigma` float 0.1–10 (aktif jika gaussian) | Konvolusi dengan kernel rata-rata/Gaussian |
| Spatial | `enhance.smoothing.spatial.median` | `median_filter(img, ksize)` | `ksize` int ganjil 3–15 (3) | Median per kanal; efektif untuk salt & pepper |
| Frequency | `enhance.smoothing.frequency.ilpf` | `ilpf(img, d0)` | `d0` float 1–min(H,W)/2 (default 30) | Ideal Lowpass: `H=1` jika `D ≤ D0` |
| Frequency | `enhance.smoothing.frequency.blpf` | `blpf(img, d0, order)` | `d0` float (30), `order` int 1–10 (2) | Butterworth Lowpass: `H = 1/(1+(D/D0)^{2n})` |

Policy: spatial = `per_channel`; frequency = `per_channel` (FFT tiap kanal) dengan opsi `apply_on` (`luminance`/`per_channel`) bila diperlukan. Live preview: lowpass/median kecil = Ya; frequency = Tidak (tombol Apply).

Alur filter frekuensi (`utils/frequency.py`): `pad → fft2 → fftshift → kalikan H(u,v) → ifftshift → ifft2 → real → crop → clip`. Mask jarak: `D(u,v) = sqrt((u − P/2)² + (v − Q/2)²)`.

#### 4.5.4 Sharpening

| Domain | ID | Fungsi | Parameter | Penjelasan |
|---|---|---|---|---|
| Spatial | `enhance.sharpening.spatial.highpass` | `highpass_filter(img, kernel_type, add_to_original)` | `kernel_type` select `laplacian_4`, `laplacian_8`, `custom_hp`; `add_to_original` bool (true) | Hasil = original + highpass bila `add_to_original` |
| Spatial | `enhance.sharpening.spatial.highboost` | `highboost_filter(img, A, ksize, sigma)` | `A` float 1.0–5.0 (default 1.5), `ksize` int ganjil (5), `sigma` float (1.0) | `hb = A·f − lowpass(f)` ≡ `(A−1)·f + highpass(f)` |
| Frequency | `enhance.sharpening.frequency.ihpf` | `ihpf(img, d0)` | `d0` float (30) | `H = 0` jika `D ≤ D0`, selain itu 1 |
| Frequency | `enhance.sharpening.frequency.bhpf` | `bhpf(img, d0, order)` | `d0` float (30), `order` int (2) | `H = 1/(1+(D0/D)^{2n})` |

Parameter tambahan filter frekuensi: `add_to_original` bool (default `true`) agar hasil tidak sekadar edge/gelap.

#### 4.5.5 Geometrics Correction

| ID | `enhance.geometric_correction` |
|---|---|
| Fungsi | `geometric_correction(img, mode, **params)` — `geometric_correction.py` |
| Policy | `per_channel` |
| Live preview | Tidak |

| `mode` | Parameter | Deskripsi |
|---|---|---|
| `perspective` | `points` : 4 titik (x,y) sumber (TL, TR, BR, BL) — dipilih klik di canvas; `output_size` opsional | Meluruskan dokumen/papan miring menggunakan homografi (inverse mapping + bilinear) |
| `radial_distortion` | `k1` float −1.0..1.0 (default 0), `k2` float −1.0..1.0 (0) | Koreksi distorsi barrel/pincushion |
| `shear` | `shear_x` float −1..1, `shear_y` float −1..1 | Koreksi kemiringan (skew) |

Semua mode memakai **inverse mapping** (hitung koordinat sumber untuk tiap piksel tujuan) + interpolasi bilinear NumPy.

### 4.6 Menu **Edge Detection**

#### 4.6.1 1st Differential Gradient

| ID | Fungsi | Kernel / Metode |
|---|---|---|
| `edge.first.sobel` | `sobel(img, direction, threshold)` | `Gx = [[-1,0,1],[-2,0,2],[-1,0,1]]`, `Gy = Gxᵀ` |
| `edge.first.prewitt` | `prewitt(img, direction, threshold)` | `Gx = [[-1,0,1],[-1,0,1],[-1,0,1]]`, `Gy = Gxᵀ` |
| `edge.first.roberts` | `roberts(img, direction, threshold)` | `Gx = [[1,0],[0,-1]]`, `Gy = [[0,1],[-1,0]]` (2×2) |

| Param (bersama) | Tipe | Opsi / Rentang | Default | Keterangan |
|---|---|---|---|---|
| `direction` | select | `magnitude`, `horizontal`, `vertical` | `magnitude` | Magnitudo `√(Gx²+Gy²)` atau komponen tunggal |
| `threshold` | int | 0–255 (0 = tanpa threshold) | `0` | Binarisasi hasil bila > 0 |
| `normalize` | bool | — | `true` | Skala hasil ke 0–255 |

Policy: `gray_only`. Live preview: Ya.

#### 4.6.2 2nd Differential Gradient

| ID | Fungsi | Parameter | Penjelasan |
|---|---|---|---|
| `edge.second.laplacian` | `laplacian(img, connectivity, threshold)` | `connectivity` select `4`/`8`; `threshold` int (0) | Kernel `[[0,1,0],[1,-4,1],[0,1,0]]` atau versi 8-konektivitas |
| `edge.second.log` | `laplacian_of_gaussian(img, sigma, ksize, zero_crossing)` | `sigma` float 0.5–10 (1.4); `ksize` int ganjil (auto = 6σ+1); `zero_crossing` bool (true) | Gaussian smoothing + Laplacian; deteksi zero-crossing |
| `edge.second.canny` | `canny(img, sigma, low_threshold, high_threshold)` | `sigma` float 0.5–5 (1.0); `low_threshold` int 0–255 (50); `high_threshold` int 0–255 (150); `l2_gradient` bool (true) | Implementasi manual 5 langkah: (1) Gaussian blur, (2) gradient Sobel, (3) non-maximum suppression, (4) double threshold, (5) hysteresis |

Validasi: `low_threshold < high_threshold` (jika tidak → `E_PARAM_RANGE`). Policy: `gray_only`. Live preview: Laplacian = Ya; LoG/Canny = Tidak.

#### 4.6.3 Compass

| ID | `edge.compass` |
|---|---|
| Fungsi | `compass_operator(img, operator, output, threshold)` — `compass.py` |
| Policy | `gray_only` |

| Param | Tipe | Opsi | Default | Keterangan |
|---|---|---|---|---|
| `operator` | select | `kirsch`, `robinson`, `prewitt_compass` | `kirsch` | 8 kernel hasil rotasi 45° |
| `output` | select | `max_magnitude`, `direction_map` | `max_magnitude` | `max_magnitude` = nilai maksimum dari 8 respons; `direction_map` = pewarnaan arah tepi (indeks 0–7 → warna) |
| `threshold` | int | 0–255 | `0` | — |

### 4.7 Menu **Noise** *(Noise Generator)*

Seluruh noise **ditambahkan ke citra** (`g = f + n`, lalu clip). Pembangkit acak: `numpy.random.default_rng(seed)`.

| ID | Fungsi | Parameter | Distribusi / Rumus Pembangkit |
|---|---|---|---|
| `noise.gaussian` | `gaussian_noise(img, mean, sigma, seed)` | `mean` float −100..100 (0); `sigma` float 0–100 (20) | `n ~ N(μ, σ²)` via `rng.normal` |
| `noise.rayleigh` | `rayleigh_noise(img, a, b, seed)` | `a` float −50..50 (0); `b` float 1–5000 (≈ 400) | `n = a + √(−b · ln(1−U))`, `U ~ U(0,1)` |
| `noise.erlang` | `erlang_noise(img, a, b, seed)` | `a` float 0.01–100 (1.0, parameter laju); `b` int 1–20 (shape/k, default 2) | Jumlah `b` variabel eksponensial: `n = Σ −(1/a)·ln(1−Uᵢ)` ≡ `rng.gamma(b, 1/a)` |
| `noise.exponential` | `exponential_noise(img, a, seed)` | `a` float 0.01–100 (0.05) | `n = −(1/a)·ln(1−U)` via `rng.exponential(1/a)` |
| `noise.uniform` | `uniform_noise(img, a, b, seed)` | `a` float −255..255 (−30); `b` float −255..255 (30), wajib `a < b` | `n ~ U(a, b)` |
| `noise.impulse` | `impulse_noise(img, p_salt, p_pepper, seed)` | `p_salt` float 0–1 (0.05); `p_pepper` float 0–1 (0.05); jumlah ≤ 1 | Piksel acak dibuat 255 (salt) atau 0 (pepper); mode RGB: `per_pixel` atau `per_channel` |

Parameter umum: `seed` int|null (default `null` = acak; isi angka untuk hasil reprodusibel), `per_channel_independent` bool (default `true`; noise berbeda untuk tiap kanal RGB). `meta.info` mengembalikan `seed` yang dipakai agar hasil bisa diulang. Policy: `per_channel`. Live preview: Ya (dengan seed tetap) — saat seed `null`, preview dinonaktifkan dan hanya Apply.

### 4.8 Menu **About**

| Item | Perilaku |
|---|---|
| **Info Developer** | Modal popup: foto (opsional), nama, program studi, universitas, peran (*Solo Developer*), mata kuliah, tahun, ringkasan teknologi |
| **Tutorial → Link GitHub** | Tautan ke repository (`https://github.com/ilyasmanaja/<nama-repo>`), buka tab baru (`target="_blank" rel="noopener noreferrer"`) |
| **Tutorial → Link YouTube** | Tautan ke video tutorial penggunaan aplikasi (diisi setelah Tahap 5) |

### 4.9 Ringkasan Seluruh ID Operasi (untuk Referensi Cepat AI)

```text
basic.negative
basic.arithmetic.{add|subtract|multiply|divide}              [dual]
basic.boolean.not                                            [single]
basic.boolean.{and|or|xor}                                   [dual]
basic.geometric.{translation|rotation|zooming|flipping|cropping}
basic.thresholding
basic.convolution
basic.fourier
basic.colouring.{binary|grayscale|rgb|hsv|cmy|yuv|yiq|pseudo}
enhance.brightness
enhance.contrast
enhance.hist_equalization
enhance.smoothing.spatial.{lowpass|median}
enhance.smoothing.frequency.{ilpf|blpf}
enhance.sharpening.spatial.{highpass|highboost}
enhance.sharpening.frequency.{ihpf|bhpf}
enhance.geometric_correction
edge.first.{sobel|prewitt|roberts}
edge.second.{laplacian|log|canny}
edge.compass
noise.{gaussian|rayleigh|erlang|exponential|uniform|impulse}
```

Total: **± 50 operasi terdaftar** (File & About ditangani klien).

---

## 5. SPESIFIKASI KONTRAK KOMUNIKASI API (REQUEST/RESPONSE FORMAT)

### 5.1 Daftar Endpoint

| Method | Path | Fungsi | Body |
|---|---|---|---|
| `GET` | `/` | Menyajikan halaman editor (`editor.html`) | — |
| `GET` | `/api/operations` | Mengembalikan seluruh skema operasi (menu, parameter, inputs, policy) untuk membangun UI dinamis | — |
| `POST` | `/api/process` | **Endpoint utama**: menjalankan satu operasi PCD | JSON |
| `POST` | `/api/upload` | *(Opsional)* validasi & normalisasi gambar (EXIF, mode, batas ukuran), kembalikan metadata | `multipart/form-data` |
| `POST` | `/api/histogram` | Hitung histogram gambar (untuk panel histogram) | JSON |
| `POST` | `/api/export` | *(Opsional)* konversi ke format tertentu (mis. BMP) dan kembalikan Base64 | JSON |
| `GET` | `/api/health` | Cek status server | — |

### 5.2 `GET /api/operations` — Contoh Respons (Ringkas)

```json
{
  "ok": true,
  "version": "1.0",
  "operations": [
    {
      "id": "enhance.brightness",
      "label": "Brightness",
      "menu_path": ["Enhancement", "Brightness"],
      "inputs": 1,
      "color_policy": "per_channel",
      "live_preview": true,
      "params": [
        {
          "name": "beta", "type": "int", "label": "Brightness",
          "default": 0, "min": -255, "max": 255, "step": 1
        }
      ]
    }
  ]
}
```

### 5.3 `POST /api/process` — Format Request

| Field | Tipe | Wajib | Deskripsi |
|---|---|---|---|
| `operation` | string | ya | ID operasi dari registry (mis. `enhance.brightness`) |
| `params` | object | tidak | Parameter operasi; field yang tidak dikirim memakai `default` |
| `image` | string | ya | Gambar utama (A), Base64 data URL (`data:image/png;base64,...`) |
| `image_b` | string \| null | wajib jika `inputs=2` | Gambar kedua (B) |
| `options.output_format` | string | tidak | `png` (default) |
| `options.max_side` | int | tidak | Batas sisi terpanjang untuk preview cepat (mis. 1024) |
| `options.request_id` | string | tidak | ID unik dari klien untuk membatalkan/membandingkan respons |

**Contoh 1 — Operasi satu gambar (Brightness):**

```json
{
  "operation": "enhance.brightness",
  "params": { "beta": 40 },
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...",
  "options": { "request_id": "req-1730000000-01" }
}
```

**Contoh 2 — Operasi dual-image (Aritmatika Add):**

```json
{
  "operation": "basic.arithmetic.add",
  "params": { "resize_mode": "resize_b_to_a", "overflow": "clip" },
  "image":   "data:image/png;base64,iVBORw0KGgoAAA...",
  "image_b": "data:image/png;base64,iVBORw0KGgoBBB..."
}
```

**Contoh 3 — Noise dengan seed:**

```json
{
  "operation": "noise.gaussian",
  "params": { "mean": 0, "sigma": 25, "seed": 42, "per_channel_independent": true },
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg..."
}
```

**Contoh 4 — Konvolusi kernel kustom:**

```json
{
  "operation": "basic.convolution",
  "params": {
    "kernel_preset": "custom",
    "kernel": [[0, -1, 0], [-1, 5, -1], [0, -1, 0]],
    "normalize": false,
    "padding": "reflect",
    "bias": 0
  },
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg..."
}
```

**Contoh 5 — Cropping:**

```json
{
  "operation": "basic.geometric.cropping",
  "params": { "x": 120, "y": 80, "w": 400, "h": 300 },
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg..."
}
```

### 5.4 `POST /api/process` — Format Respons Sukses (HTTP 200)

```json
{
  "ok": true,
  "operation": "enhance.brightness",
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...",
  "meta": {
    "width": 800,
    "height": 600,
    "mode": "RGB",
    "channels": 3,
    "dtype": "uint8",
    "elapsed_ms": 18,
    "color_policy_applied": "per_channel",
    "warnings": [],
    "info": {},
    "request_id": "req-1730000000-01"
  }
}
```

| Field `meta` | Arti |
|---|---|
| `mode` | `RGB` atau `L` — dipakai status bar |
| `elapsed_ms` | Waktu proses server (untuk debugging performa) |
| `warnings` | Array string, mis. `"Gambar RGB dikonversi otomatis ke grayscale (operasi gray_only)."` |
| `info` | Data tambahan spesifik operasi: `threshold` (Otsu), `seed` (noise), `histogram_before/after` (equalization), `channel_ranges` (ruang warna) |
| `request_id` | Dikembalikan apa adanya agar klien membuang respons usang |

### 5.5 Format Respons Error

```json
{
  "ok": false,
  "error": {
    "code": "E_PARAM_RANGE",
    "message": "Parameter 'ksize' harus ganjil dan berada pada rentang 3–15.",
    "field": "ksize",
    "details": { "received": 4, "min": 3, "max": 15 }
  },
  "request_id": "req-1730000000-01"
}
```

| Kode Error | HTTP | Penyebab | Pesan Pengguna (UI) |
|---|---|---|---|
| `E_BAD_REQUEST` | 400 | JSON rusak / field wajib hilang | "Permintaan tidak valid." |
| `E_UNKNOWN_OPERATION` | 404 | `operation` tidak ada di registry | "Operasi tidak dikenal." |
| `E_IMAGE_DECODE` | 400 | Base64 tidak valid / bukan gambar | "Gambar tidak dapat dibaca." |
| `E_IMAGE_TOO_LARGE` | 413 | Ukuran file / dimensi melebihi batas | "Gambar terlalu besar (maks. … )." |
| `E_IMAGE_B_REQUIRED` | 422 | Operasi dual tanpa `image_b` | "Pilih gambar kedua terlebih dahulu." |
| `E_PARAM_TYPE` | 422 | Tipe parameter salah | "Nilai parameter tidak sesuai." |
| `E_PARAM_RANGE` | 422 | Parameter di luar rentang / syarat (mis. ganjil) | Pesan spesifik dari server |
| `E_COLOR_MODE` | 422 | Mode warna tidak didukung operasi | "Operasi tidak mendukung mode warna ini." |
| `E_PROCESSING` | 500 | Kesalahan tak terduga di fungsi operasi | "Gagal memproses gambar." |
| `E_TIMEOUT` | 504 | Proses melebihi batas waktu | "Proses terlalu lama, coba perkecil gambar." |

### 5.6 Implementasi Referensi Route (Kerangka)

```python
# app/routes/api.py  (kerangka — orkestrasi saja, tanpa algoritma PCD)
from flask import Blueprint, request, jsonify
from app.operations.registry import OPERATIONS
from app.utils import image_io, validators
from app.utils.errors import ApiError
import time

api = Blueprint("api", __name__, url_prefix="/api")

@api.post("/process")
def process():
    t0 = time.perf_counter()
    payload = request.get_json(silent=True)
    validators.validate_process_payload(payload)            # raise ApiError bila salah

    spec = OPERATIONS.get(payload["operation"])
    if spec is None:
        raise ApiError("E_UNKNOWN_OPERATION", "Operasi tidak dikenal.", status=404)

    params = validators.validate_params(spec, payload.get("params", {}))
    img_a = image_io.decode_data_url(payload["image"])      # → ndarray uint8
    args = [img_a]
    if spec.inputs == 2:
        if not payload.get("image_b"):
            raise ApiError("E_IMAGE_B_REQUIRED", "Pilih gambar kedua terlebih dahulu.", status=422)
        args.append(image_io.decode_data_url(payload["image_b"]))

    result, extra = image_io.run_with_policy(spec, args, params)  # terapkan color_policy
    return jsonify(ok=True, operation=spec.id,
                   image=image_io.encode_data_url(result),
                   meta=image_io.build_meta(result, t0, extra, payload))

@api.errorhandler(ApiError)
def handle_api_error(e):
    return jsonify(ok=False, error=e.to_dict()), e.status
```

### 5.7 Konfigurasi Batas (di `config.py`)

| Konstanta | Nilai Default | Fungsi |
|---|---|---|
| `MAX_CONTENT_LENGTH` | 25 MB | Batas ukuran body request (Base64 ±33% lebih besar dari biner) |
| `MAX_UPLOAD_FILE_MB` | 10 | Batas file yang diizinkan di klien |
| `MAX_IMAGE_SIDE` | 4096 px | Batas dimensi mutlak; di atasnya ditolak |
| `PROCESS_SIDE_SOFT_LIMIT` | 2048 px | Di atas ini, klien menawarkan *downscale* otomatis sebelum operasi berat (FFT, Canny, median besar) |
| `ALLOWED_MIME` | `image/png`, `image/jpeg`, `image/bmp`, `image/webp` | Validasi tipe |
| `PROCESS_TIMEOUT_S` | 20 | Batas waktu per operasi (best effort) |

---

## 6. ALUR KERJA INTERAKTIVITAS UI & EDGE CASES

### 6.1 Layout Workspace

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│ VisionCraft PCD — Copyright © Muhammad Raihan Ilyasman – 2026                      │ ← Judul
├────────────────────────────────────────────────────────────────────────────────────┤
│ File ▾ │ Basic Ops ▾ │ Enhancement ▾ │ Noise ▾ │ Edge Detection ▾ │ About ▾        │ ← Menu
├───────────────────────────────────────────────────────┬────────────────────────────┤
│  ┌──────────── ORIGINAL ─────┐ ┌──────── PROCESSED ───┐│  PARAMETER DRAWER         │
│  │                           │ │                      ││  (berubah sesuai operasi) │
│  │   canvas A (read-only)    │ │   canvas B (hasil)   ││  ─ Judul operasi          │
│  │                           │ │                      ││  ─ Slider / select / kernel│
│  │   [drag & drop di sini]   │ │   [loading overlay]  ││  ─ Slot gambar kedua*     │
│  └───────────────────────────┘ └──────────────────────┘│  ─ [Preview] [Apply] [Reset]│
│  Zoom: [−] 100% [+] [Fit]   [Undo] [Redo] [Compare]    │  ─ Histogram (opsional)   │
├───────────────────────────────────────────────────────┴────────────────────────────┤
│ 800 × 600 px │ Mode: RGB │ X: 312  Y: 148 │ Pixel: R 120 G 98 B 77                  │ ← Status bar
└────────────────────────────────────────────────────────────────────────────────────┘
(*) hanya muncul untuk operasi dual-image
```

| Komponen | Spesifikasi |
|---|---|
| **Top Navigation Bar** | Judul aplikasi, teks copyright (tahun otomatis dari JS), menu bar horizontal dengan **dropdown bertingkat** sesuai PDF: `Basic Ops → Arithmetic/Boolean/Geometrics/Colouring` (submenu), `Enhancement → Smoothing/Sharpening → Spatial/Frequency Domain` (3 level), `Edge Detection → 1st/2nd Differential Gradient` (submenu). Dukungan hover (desktop) dan klik/tap (layar sentuh) |
| **Main Canvas** | Dua panel berdampingan; label *Original* & *Processed*; indikator visual aktif (border aksen pada panel yang sedang diinspeksi); **drag-and-drop** upload; overlay **loading spinner** saat fetch berlangsung; zoom & pan tersinkron |
| **Right Drawer** | Dibangun dinamis oleh `params.js` dari skema `/api/operations`: `int/float` → slider + input angka bersinkron; `select` → dropdown; `bool` → toggle; `kernel` → grid angka N×N; `rect` → 4 input + seleksi di canvas; slot gambar kedua untuk operasi `inputs=2`. Tombol: **Preview**, **Apply**, **Reset Param** |
| **Bottom Status Bar** | Dimensi (W×H), mode warna (RGB/L), koordinat kursor (X,Y) dalam piksel citra (bukan piksel layar), nilai piksel (RGB atau intensitas) di bawah kursor — dibaca langsung dari canvas |
| **Modal** | `modal_about`: biodata developer tunggal + tautan GitHub & YouTube. Modal lain: Save As, konfirmasi Reset, tampilan error detail |
| **Tema** | Dark mode: latar `#1e1f22` / panel `#2b2d31` / aksen biru `#3b82f6` / teks `#e5e7eb`; font sistem/Inter; sudut membulat kecil; semua warna lewat CSS variable `--vc-*` |

### 6.2 Penanganan Operasi Dual-Image (Aritmatika & Boolean AND/OR/XOR)

**Alur:**

1. Pengguna memilih operasi dengan `inputs=2` dari menu.
2. Drawer menampilkan **slot "Gambar Kedua (B)"** (dropzone kecil + tombol *Browse* + thumbnail + tombol hapus).
3. Gambar A = `current` (hasil terakhir) **atau** `original` — pengguna memilih lewat toggle *"Gunakan sebagai A: Current / Original"* (default `Current`).
4. Tombol **Apply/Preview dinonaktifkan** sampai gambar B dimuat dan valid.
5. Saat Apply: klien mengirim `image` (A) dan `image_b` (B) dalam satu request.
6. Server menyamakan ukuran & mode (lihat tabel), menjalankan operasi, mengembalikan hasil.
7. Slot B **dipertahankan** selama operasi dual berikutnya dipilih; **dikosongkan** saat Reset Canvas atau ketika pengguna menghapusnya.

**Aturan penyamaan A dan B:**

| Kondisi | Perlakuan |
|---|---|
| Ukuran sama | Langsung diproses |
| Ukuran berbeda, `resize_mode=resize_b_to_a` | B di-resize ke ukuran A (bilinear) — **default** |
| `resize_mode=center_crop` | B dipotong/diisi dari tengah mengikuti ukuran A tanpa distorsi rasio |
| `resize_mode=pad` | B diberi padding hitam hingga ukuran A (jika B lebih kecil), dipotong bila lebih besar |
| A = RGB, B = L | B diduplikasi ke 3 kanal |
| A = L, B = RGB | B dikonversi ke L (luminosity) |
| Salah satu bermode alpha | Dikomposit ke latar putih lalu dikonversi ke RGB |
| Hasil di luar 0–255 | Ditangani `overflow` (`clip`/`normalize`) |
| Pembagian dengan nol | `b + ε`; piksel dengan `b == 0` menghasilkan 255 (atau 0 — ditentukan dan diuji; standar proyek: **255**) |

### 6.3 Penanganan Grayscale vs RGB

| Kategori | Operasi | Perilaku |
|---|---|---|
| **Native per-channel** | Negative, Brightness, Contrast, Geometrics, Konvolusi, Smoothing, Sharpening, Noise, Arithmetic/Boolean | RGB diproses per kanal; L diproses satu kanal; mode keluaran = mode masukan |
| **Luminance-based** | Histogram Equalization (default) | Hanya kanal Y yang diubah; warna terjaga |
| **Gray-only** | Thresholding, Fourier, Edge Detection (semua), Colouring Binary | RGB → L otomatis (`luminosity`), keluaran **L**; `meta.warnings` diisi; status bar berubah ke `L` |
| **RGB-only / transform warna** | Colouring HSV/CMY/YUV/YIQ/RGB | Input L → diduplikasi ke 3 kanal terlebih dahulu (dengan peringatan bahwa kroma nol) |
| **Pseudo-color** | Colouring Pseudo | Input RGB → L dulu; keluaran RGB |

**Aturan penting:**

- Setelah operasi `gray_only`, citra `current` berubah menjadi **L**. Operasi berikutnya yang membutuhkan warna harus mengingatkan pengguna (atau mengulang dari `original` melalui tombol *Revert to Original*).
- Canvas selalu merender citra L sebagai RGB abu-abu (R=G=B); status bar tetap menampilkan mode **L**.
- Tombol *Revert to Original* di toolbar: mengembalikan `current` ke `original` tanpa menghapus history.

### 6.4 Validasi Ukuran & Format Gambar

| Pemeriksaan | Lokasi | Batas | Tindakan |
|---|---|---|---|
| Tipe MIME / ekstensi | Klien + server | PNG, JPEG, BMP, WEBP | Tolak dengan pesan jelas |
| Ukuran file | Klien | ≤ 10 MB | Tolak sebelum upload |
| Dimensi minimum | Klien + server | ≥ 8 × 8 px (≥ 32 × 32 untuk Canny/LoG/frekuensi) | Tolak/peringatkan |
| Dimensi maksimum | Server | sisi terpanjang ≤ 4096 px | `E_IMAGE_TOO_LARGE` |
| Soft limit proses berat | Klien | > 2048 px untuk FFT/Canny/Median besar | Dialog: *Lanjutkan* atau *Perkecil otomatis* (downscale proporsional) |
| Orientasi EXIF | Server (`ImageOps.exif_transpose`) & klien (`createImageBitmap` mengikuti EXIF) | — | Diputar otomatis |
| Mode `P`, `CMYK`, `RGBA`, `LA`, `I;16` | Server (`image_io.normalize_mode`) | — | Konversi aman ke `RGB`/`L`; alpha dikomposit ke putih |
| Parameter operasi | Server (`validators.validate_params`) | sesuai `ParamSpec` | `E_PARAM_*` |
| Kernel konvolusi | Klien + server | persegi, ganjil, ≤ 9×9, nilai finite | `E_PARAM_RANGE` |
| Crop rect | Klien + server | di dalam batas gambar, `w,h ≥ 1` | Dikoreksi/ditolak |
| Respons usang | Klien | `request_id` tidak sama dengan request terakhir | Respons dibuang |

### 6.5 Alur Interaksi Utama

```
IDLE (belum ada gambar)
  └─ Open / Drag-Drop ─► LOADED  (original = current = gambar; history = [original])
LOADED
  └─ pilih operasi di menu ─► CONFIGURING  (drawer menampilkan parameter)
CONFIGURING
  ├─ ubah parameter (live_preview=true) ─► debounce 200 ms ─► PREVIEWING
  ├─ klik Preview ───────────────────────► PREVIEWING
  ├─ klik Apply ─────────────────────────► APPLYING ─► hasil jadi `current`, push history
  └─ klik Reset Param / pilih operasi lain ─► CONFIGURING (param default)
PREVIEWING / APPLYING
  ├─ sukses ─► tampilkan di panel Processed
  ├─ gagal ──► toast error + panel Processed tidak berubah
  └─ request baru ─► AbortController membatalkan request sebelumnya
```

**Aturan state:**

| Aturan | Rincian |
|---|---|
| History | Maksimum **20** langkah (array Base64/Blob); melewati batas → langkah tertua dibuang |
| Undo / Redo | `Ctrl+Z` / `Ctrl+Y`; tombol toolbar; menonaktifkan tombol bila stack kosong |
| Preview vs Apply | **Preview** hanya menampilkan di panel Processed; **Apply** mengomit ke `current` + history |
| Compare | Tombol tahan (*hold to compare*) atau toggle yang menampilkan original menimpa processed |
| Loading | Overlay spinner di panel Processed + tombol Apply dinonaktifkan; timeout klien 30 s |
| Pembatalan | `AbortController` pada setiap `fetch`; `request_id` mencegah respons lama menimpa respons baru |
| Slider berat | Operasi `live_preview=false` tidak otomatis dipanggil; hanya via tombol |
| Sinkron zoom | Zoom/pan di satu panel diterapkan ke panel lainnya |

### 6.6 Edge Cases & Penanganannya

| # | Kasus | Penanganan |
|---|---|---|
| 1 | Operasi dipilih sebelum gambar dibuka | Menu operasi **dinonaktifkan** (abu-abu); klik memunculkan toast "Buka gambar terlebih dahulu." |
| 2 | File bukan gambar / korup | Toast error, state tidak berubah |
| 3 | Gambar sangat besar | Dialog downscale (lihat §6.4) |
| 4 | Gambar PNG transparan | Dikomposit ke latar putih; peringatan di `meta.warnings` |
| 5 | Gambar GIF animasi | Hanya frame pertama; peringatan |
| 6 | Dual-image tanpa B | Apply dinonaktifkan; pesan bantu di slot B |
| 7 | B berukuran jauh berbeda | Terapkan `resize_mode`; tampilkan info ukuran A/B di slot |
| 8 | Median/filter dengan `ksize` genap | Slider melompat per 2; server tetap memvalidasi |
| 9 | `d0` > setengah sisi terpendek | Dikoreksi (clamp) + peringatan |
| 10 | Canny `low ≥ high` | Validasi klien (slider tertaut) + `E_PARAM_RANGE` |
| 11 | Hasil operasi seluruhnya konstan (mis. threshold ekstrem) | Tetap ditampilkan; tidak dianggap error |
| 12 | Divide: pembagi 0 | `ε` & aturan 255 (lihat §6.2) |
| 13 | Operasi `gray_only` pada gambar RGB | Konversi otomatis + toast informatif |
| 14 | Request lambat / server mati | Timeout → toast "Server tidak merespons"; tombol Retry |
| 15 | Pengguna menggeser slider cepat | Debounce + `AbortController`; hanya request terbaru yang dirender |
| 16 | Save saat belum ada gambar | Menu Save/Save As dinonaktifkan |
| 17 | Save JPEG dari citra dengan transparansi | Latar putih sebelum encode |
| 18 | Reset Canvas | Konfirmasi dialog (karena menghapus history) |
| 19 | Layar kecil / mobile | Drawer berubah menjadi *bottom sheet*; panel Original/Processed menjadi tab |
| 20 | Browser menutup tab | Tidak ada persistensi (stateless) — peringatan `beforeunload` bila ada perubahan belum disimpan |

### 6.7 Aksesibilitas & Pengalaman Pengguna

| Fitur | Detail |
|---|---|
| Keyboard | `Ctrl+O` Open, `Ctrl+S` Save, `Ctrl+Shift+S` Save As, `Ctrl+Z/Y` Undo/Redo, `Esc` tutup modal/dropdown |
| Fokus & ARIA | Menu memakai `role="menubar"`/`menuitem`; modal memakai `aria-modal` |
| Umpan balik | Toast sukses/error, status "Processing…", durasi proses ditampilkan di status bar |
| Konsistensi | Semua label menu persis mengikuti PDF (termasuk penulisan "Substract (-)" → diperbaiki menjadi **Subtract (−)** di UI, ID tetap `subtract`) |

---

## 7. PENGEMBANG & STANDAR KUALITAS MANDIRI (SOLO WORKFLOW)

### 7.1 Profil Developer Tunggal

| Atribut | Isi |
|---|---|
| Nama | **Muhammad Raihan Ilyasman** |
| NIM | `[ISI NIM]` |
| Program Studi | S1 Teknik Informatika |
| Institusi | Universitas Riau |
| Peran | **Solo Developer** — perancang arsitektur, backend, frontend, pengujian, dokumentasi, dan video tutorial |
| Mata Kuliah | Pengolahan Citra Digital (PCD) — Tugas Mandiri |
| GitHub | `https://github.com/ilyasmanaja` |
| Repository | `https://github.com/ilyasmanaja/[nama-repo-visioncraft-pcd]` |
| YouTube | `[ISI LINK VIDEO TUTORIAL]` |
| Teknologi Utama | Python, Flask, NumPy, Pillow, JavaScript, Tailwind CSS |

> Placeholder `[ISI ...]` wajib diganti sebelum pengumpulan. Isi modal About (§4.8) mengambil data dari konstanta di `config.py` (`DEVELOPER_INFO`) agar mudah diubah di satu tempat.

### 7.2 Target Fungsionalitas (Ringkasan)

| Kategori | Target Minimum (Wajib) | Target Tambahan (Nice-to-have) |
|---|---|---|
| File | Open, Save, Save As, Reset | Drag-drop, paste clipboard |
| Basic Ops | Seluruh submenu pada PDF berfungsi | Crop interaktif, histogram live |
| Enhancement | Seluruh submenu pada PDF berfungsi | CLAHE, koreksi perspektif interaktif |
| Edge Detection | 1st, 2nd differential, Compass | Visualisasi arah tepi berwarna |
| Noise | 6 jenis noise | Estimasi PSNR/MSE hasil vs original di drawer |
| About | Modal developer + 2 tautan | Mode terang/gelap toggle |
| UI | Layout §6.1 lengkap | Responsif mobile, shortcut keyboard lengkap |

### 7.3 Standar Kode

| Aspek | Aturan |
|---|---|
| Gaya | PEP 8, format `black`, lint `ruff` (0 error sebelum commit) |
| Type hints | Wajib untuk semua fungsi publik di `operations/` & `utils/` |
| Docstring | Gaya Google/NumPy: tujuan, rumus, parameter, rentang, keluaran |
| Kemurnian fungsi | Tidak memodifikasi input (`img.copy()` bila perlu), tanpa global state |
| Vektorisasi | Dilarang loop piksel `for y… for x…` untuk citra penuh; pakai NumPy. Pengecualian: loop kecil (jumlah kernel/arah/langkah algoritma) |
| Dtype | Hasil selalu `uint8`, rentang 0–255, bentuk `(H,W)` atau `(H,W,3)` |
| Penamaan | `snake_case` fungsi/berkas; ID operasi `kategori.sub.nama` |
| Komit | Conventional commits: `feat(edge): add canny`, `fix(api): handle null image_b`, `test(noise): ...` |
| Branch | `main` (stabil), `dev` (kerja harian), `feat/<nama>` per fitur |
| JavaScript | ES Modules, tanpa library UI berat; satu tanggung jawab per file |

### 7.4 Strategi & Kriteria Pengujian Mandiri

**A. Uji Unit Fungsi (pytest, tanpa server)**

| Pemeriksaan Universal (berlaku untuk semua operasi) | Kriteria Lulus |
|---|---|
| Tipe & bentuk | Output `uint8`; shape sama dengan input (kecuali geometri/crop/zoom/FFT-pad yang terdefinisi) |
| Rentang | `0 ≤ min` dan `max ≤ 255` |
| Tidak memodifikasi input | Array input identik sebelum & sesudah |
| Determinisme | Dua kali panggilan dengan parameter sama (dan seed sama) → hasil identik |
| Mode L & RGB | Berjalan tanpa error untuk keduanya |
| Ukuran kecil | Berjalan di gambar 8×8 (kecuali yang dikecualikan) |

| Uji Nilai Spesifik (contoh) | Ekspektasi |
|---|---|
| `negative` pada array `[0, 100, 255]` | `[255, 155, 0]` |
| `brightness(beta=+50)` pada nilai 220 | 255 (clipping) |
| `flip` dua kali pada sumbu sama | Identik dengan input |
| `rotate(90)` empat kali | Identik dengan input |
| Konvolusi kernel `identity` | Identik dengan input |
| Konvolusi box 3×3 pada citra konstan | Citra konstan sama |
| Median pada citra dengan 1 piksel "salt" | Piksel salt hilang |
| `fft → ifft (reconstruction)` | Selisih maksimum ≤ 1 |
| ILPF `d0` sangat besar | Mendekati identik dengan input |
| Histogram equalization pada citra konstan | Tidak error, hasil konstan |
| Sobel pada gradien horizontal linear | Respons Gx konstan > 0, Gy ≈ 0 |
| Canny pada gambar konstan | Tidak ada tepi (semua 0) |
| Noise Gaussian `σ=0` | Identik dengan input |
| Noise impulse `p=0` | Identik dengan input |
| Statistik noise (citra konstan 128, `n=1e5` piksel) | Mean/σ hasil mendekati parameter (toleransi ±5%) sebelum clip |
| Konversi RGB→YUV→RGB, RGB→HSV→RGB | Selisih maks ≤ 2 |
| Boolean `a XOR a` | Seluruhnya 0 |
| `a AND 255`, `a OR 0` | Identik dengan `a` |

**B. Validasi Silang (opsional, di notebook/skrip dev)**

Bandingkan hasil implementasi sendiri dengan `scipy.ndimage` / `Pillow` (`ImageFilter`) pada citra sampel: selisih rata-rata absolut (MAE) ≤ 1.5 untuk Gaussian/Sobel/Median; perbedaan karena penanganan batas dicatat di docstring.

**C. Uji API (`test_api.py`, Flask test client)**

| Skenario | Ekspektasi |
|---|---|
| `GET /api/operations` | 200, memuat semua ID di §4.9 |
| `POST /api/process` valid | 200, `ok=true`, `image` berawalan `data:image/png;base64,` |
| Operasi tidak ada | 404 `E_UNKNOWN_OPERATION` |
| Parameter di luar rentang | 422 `E_PARAM_RANGE` |
| Dual tanpa `image_b` | 422 `E_IMAGE_B_REQUIRED` |
| Base64 rusak | 400 `E_IMAGE_DECODE` |
| Gambar > batas | 413 `E_IMAGE_TOO_LARGE` |

**D. Uji Manual UI (Checklist)**

- [ ] Seluruh item menu pada PDF muncul di dropdown dengan hierarki yang benar
- [ ] Setiap operasi dapat dipilih → drawer berubah sesuai skema
- [ ] Dual-image: slot B muncul hanya untuk Arithmetic & AND/OR/XOR
- [ ] Open via tombol dan drag-drop; format PNG/JPG/BMP/WEBP
- [ ] Save & Save As menghasilkan file valid yang bisa dibuka ulang
- [ ] Undo/Redo konsisten hingga 20 langkah
- [ ] Status bar: dimensi, mode, koordinat, nilai piksel akurat saat zoom ≠ 100%
- [ ] Loading overlay muncul & hilang; error menampilkan toast
- [ ] Modal About tampil; kedua tautan terbuka di tab baru
- [ ] Tampil benar di Chrome & Firefox (minimal); layar 1366×768 dan 1920×1080

**E. Target Performa (gambar 1024×1024, laptop standar)**

| Jenis Operasi | Target Waktu Server |
|---|---|
| Titik (negatif, brightness, contrast, threshold) | < 100 ms |
| Konvolusi / filter spasial ≤ 7×7 | < 500 ms |
| Median 5×5, noise | < 1.5 s |
| FFT & filter frekuensi | < 2 s |
| Canny / LoG | < 2.5 s |

### 7.5 Definition of Done (DoD)

**Per operasi** dianggap *selesai* jika **semua** terpenuhi:

1. Fungsi murni di `app/operations/...` dengan type hints & docstring (rumus + rentang parameter).
2. Terdaftar di registry dengan `ParamSpec` lengkap, `color_policy`, `inputs`, `live_preview`.
3. Lulus uji universal + minimal 1 uji nilai spesifik di `tests/`.
4. Muncul di menu pada posisi yang sesuai PDF & drawer dirender benar.
5. Diuji manual pada gambar RGB **dan** grayscale, serta ukuran kecil & besar.
6. Error ditangani (parameter tidak valid menghasilkan pesan jelas, bukan crash).
7. Dicatat di `README.md` (nama, kegunaan singkat, contoh sebelum/sesudah).

**Per fase** dianggap *selesai* jika seluruh operasi pada fase lulus DoD per operasi, `pytest` hijau, `ruff` bersih, dan commit/tag fase dibuat (mis. `v0.2-basic-ops`).

**Proyek keseluruhan (siap kumpul)** jika:

- [ ] Seluruh menu pada PDF berfungsi (kecuali yang secara eksplisit ditandai out-of-scope di §1.4)
- [ ] `pytest` lulus; cakupan `operations/` ≥ 80%
- [ ] Tidak ada error di console browser pada alur normal
- [ ] README lengkap (instalasi, cara pakai, screenshot, daftar fitur)
- [ ] Video tutorial YouTube diunggah dan tautannya terpasang di menu About
- [ ] Placeholder `[ISI ...]` (NIM, repo, YouTube) sudah diganti
- [ ] Repository publik GitHub bersih (`.gitignore`, tanpa file besar/tidak perlu)
- [ ] Demo end-to-end berjalan dari **instalasi bersih** (`pip install -r requirements.txt` → `python run.py`)

### 7.6 Aturan Kerja dengan AI Assistant (Solo Workflow)

1. **Tempel dokumen ini** di awal setiap sesi chat baru; sebutkan fase yang sedang dikerjakan (mis. "Tahap 3 — smoothing frequency domain").
2. Minta AI mengerjakan **satu modul/operasi per prompt** agar hasil mudah diuji dan di-review.
3. Selalu minta keluaran: **kode fungsi + ParamSpec registry + uji pytest** sekaligus.
4. AI **tidak boleh** mengubah kontrak API (§5), signature fungsi (§2.4), atau struktur folder (§3) tanpa persetujuan eksplisit; jika perlu perubahan, perbarui dokumen ini terlebih dahulu.
5. Setiap keputusan desain baru yang disepakati dicatat di **Changelog Keputusan** (§9.3).
6. Jangan menerima kode yang memakai `cv2`, loop piksel Python, atau menaruh algoritma di `routes/`.

---

## 8. ROADMAP / TAHAPAN PENGERJAAN MANDIRI

> Estimasi dalam **hari kerja efektif** (1 orang, paruh waktu di sela kuliah). Sesuaikan dengan tenggat dosen; urutan tahap **tidak boleh dilompati** karena tahap berikutnya bergantung pada fondasi sebelumnya.

### Ringkasan

| Tahap | Fokus | Estimasi | Tag Git |
|---|---|---|---|
| 1 | Setup Base Flask & UI Editor | 3–4 hari | `v0.1-base` |
| 2 | Operasi Dasar & Ruang Warna | 4–5 hari | `v0.2-basic-ops` |
| 3 | Enhancement & Filter | 5–6 hari | `v0.3-enhancement` |
| 4 | Edge Detection & Noise | 4–5 hari | `v0.4-edge-noise` |
| 5 | Final Testing & Video Tutorial | 3–4 hari | `v1.0-final` |

### Tahap 1 — Setup Base Flask & UI Editor

| Item | Rincian |
|---|---|
| **Tujuan** | Kerangka aplikasi berjalan end-to-end dengan satu operasi contoh |
| **Tugas** | 1) Inisialisasi repo, venv, `requirements.txt`, `.gitignore` · 2) `create_app()`, `config.py`, `run.py` · 3) `registry.py` + `ParamSpec`/`OperationSpec` · 4) `image_io.py` (decode/encode Base64, normalisasi mode, EXIF) · 5) `validators.py` & `errors.py` · 6) Route `/`, `/api/operations`, `/api/process`, `/api/health` · 7) UI: `base.html`, `editor.html`, navbar multilevel statis sesuai PDF, canvas side-by-side, drawer, status bar, tema dark · 8) JS: `fileio.js` (open + drag-drop), `state.js`, `canvas.js` (render, zoom/pan, koordinat & nilai piksel), `api.js`, `params.js` dinamis · 9) Operasi pertama: **Negative** & **Brightness** sebagai bukti alur · 10) Modal About (placeholder) |
| **Deliverable** | Buka gambar → pilih Negative/Brightness → hasil tampil di panel Processed → Save berfungsi |
| **DoD Tahap** | Alur §6.5 berjalan; status bar akurat; `test_api.py` dasar lulus; tag `v0.1-base` |

### Tahap 2 — Operasi Dasar & Ruang Warna

| Item | Rincian |
|---|---|
| **Tujuan** | Seluruh menu **File** dan **Basic Ops** selesai |
| **Tugas** | 1) Save As (modal format/kualitas), Reset Canvas, Undo/Redo + history · 2) Colouring: Binary, Grayscale, RGB, HSV, CMY, YUV, YIQ, Pseudo (`colorspace.py`) · 3) Arithmetic (4 operasi) + **slot gambar kedua** (`dual_image.js`, `resize_mode`) · 4) Boolean (NOT/AND/OR/XOR) · 5) Geometrics: translation, rotation, zooming, flipping, cropping (seleksi interaktif) · 6) Thresholding (global, Otsu, adaptif) · 7) Convolution (preset + editor kernel kustom, padding) · 8) Fourier Transform (magnitude/phase/reconstruction) · 9) Uji unit untuk semua operasi di atas |
| **Deliverable** | Semua item Basic Ops dapat dipanggil dari menu dan berfungsi pada RGB & grayscale |
| **DoD Tahap** | DoD per operasi terpenuhi; edge case dual-image (§6.2) teruji; tag `v0.2-basic-ops` |

### Tahap 3 — Enhancement & Filter

| Item | Rincian |
|---|---|
| **Tujuan** | Seluruh menu **Enhancement** selesai |
| **Tugas** | 1) Contrast (melengkapi Brightness) · 2) Histogram Equalization (luminance/per-channel/gray) + panel histogram sebelum/sesudah (`/api/histogram`) · 3) Smoothing spasial: Lowpass (mean/gaussian), Median · 4) `utils/frequency.py` (padding, mask jarak, pipeline FFT) → ILPF, BLPF · 5) Sharpening spasial: Highpass, Highboost · 6) Sharpening frekuensi: IHPF, BHPF · 7) Geometrics Correction (perspective, radial distortion, shear) · 8) Uji unit + perbandingan silang dengan SciPy · 9) Optimasi performa (vektorisasi, downscale prompt) |
| **Deliverable** | Seluruh submenu Enhancement (termasuk 3 level Smoothing/Sharpening → Spatial/Frequency) berfungsi |
| **DoD Tahap** | Target performa §7.4-E tercapai untuk gambar 1024²; tag `v0.3-enhancement` |

### Tahap 4 — Edge Detection & Noise

| Item | Rincian |
|---|---|
| **Tujuan** | Seluruh menu **Edge Detection** dan **Noise** selesai |
| **Tugas** | 1) 1st gradient: Sobel, Prewitt, Roberts · 2) 2nd gradient: Laplacian, LoG (+ zero crossing), **Canny manual** · 3) Compass (Kirsch, Robinson, Prewitt-compass; peta arah) · 4) Noise: Gaussian, Rayleigh, Erlang(Gamma), Exponential, Uniform, Impulse (seed + `per_channel_independent`) · 5) Uji statistik noise & uji edge sintetis · 6) (Opsional) panel PSNR/MSE hasil vs original · 7) Polesan UI: toast, loading, responsif |
| **Deliverable** | Semua item Edge Detection & Noise berfungsi; kombinasi "noise → smoothing → edge" dapat didemokan |
| **DoD Tahap** | Seluruh menu pada PDF (kecuali out-of-scope) terimplementasi; tag `v0.4-edge-noise` |

### Tahap 5 — Final Testing & Video Tutorial

| Item | Rincian |
|---|---|
| **Tujuan** | Produk siap kumpul: stabil, terdokumentasi, terdemonstrasi |
| **Tugas** | 1) Regresi penuh: `pytest` + checklist manual §7.4-D · 2) Perbaikan bug & edge case §6.6 · 3) Uji lintas browser & resolusi · 4) Lengkapi modal About (NIM, GitHub, YouTube) · 5) README: instalasi, penggunaan, screenshot per menu, daftar operasi, rumus ringkas · 6) Skenario demo video (±8–12 menit): pengenalan UI → File → tiap menu utama → contoh alur kombinasi (noise → filter → edge) · 7) Rekam, edit, unggah YouTube; pasang tautan · 8) Uji instalasi bersih dari repo · 9) (Opsional) deploy (mis. PythonAnywhere/Render) & (opsional) ekstensi *Segmentation* bila diwajibkan dosen |
| **Deliverable** | Repo publik, README lengkap, video tutorial, aplikasi berjalan |
| **DoD Tahap** | Seluruh daftar "Proyek keseluruhan siap kumpul" (§7.5) tercentang; tag `v1.0-final` |

### Matriks Risiko Mandiri

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Waktu terbatas (tugas + mata kuliah lain) | Fitur tidak selesai | Kerjakan berurutan per tahap; fitur *nice-to-have* hanya jika waktu tersisa |
| Operasi frekuensi/Canny lambat | UX buruk | Vektorisasi, downscale otomatis, tombol Apply (tanpa live preview) |
| Hasil tidak sesuai teori | Nilai turun | Validasi silang dengan SciPy, uji nilai spesifik, catat rumus di docstring |
| AI menghasilkan kode melanggar arsitektur | Refactor mahal | Tempel dokumen ini setiap sesi; review sebelum merge (§7.6) |
| Payload Base64 besar | Request lambat/gagal | Batas ukuran, downscale, PNG lossless hanya untuk hasil akhir; preview boleh diperkecil |
| Kehilangan pekerjaan | Mundur berhari-hari | Commit kecil & sering, push ke GitHub tiap akhir sesi kerja |

---

## 9. LAMPIRAN

### 9.1 Pemetaan Menu PDF → ID Operasi

| Menu (PDF) | Submenu | ID Operasi |
|---|---|---|
| File | Open…, Save, Save As, Exit | *(klien)* `fileio.js`, `state.reset()` |
| Basic Ops | Negative | `basic.negative` |
| | Arithmetic → Add (+), Subtract (−), Multiply (*), Divide (/) | `basic.arithmetic.*` |
| | Boolean → NOT, AND, OR, XOR | `basic.boolean.*` |
| | Geometrics → Translation, Rotation, Zooming, Flipping, Cropping | `basic.geometric.*` |
| | Thresholding | `basic.thresholding` |
| | Convolution | `basic.convolution` |
| | Fourier Transform | `basic.fourier` |
| | Colouring → Binary, Grayscale, RGB, HSV, CMY, YUV, YIQ, Pseudo | `basic.colouring.*` |
| Enhancement | Brightness / Contrast / Hist. Equalization | `enhance.brightness` / `enhance.contrast` / `enhance.hist_equalization` |
| | Smoothing → Spatial (Lowpass, Median), Frequency (ILPF, BLPF) | `enhance.smoothing.*` |
| | Sharpening → Spatial (Highpass, Highboost), Frequency (IHPF, BHPF) | `enhance.sharpening.*` |
| | Geometrics Correction | `enhance.geometric_correction` |
| Noise | Gaussian, Rayleigh, Erlang (Gamma), Exponential, Uniform, Impulse | `noise.*` |
| Edge Detection | 1st Differential Gradient → Sobel, Prewitt, Robert(s) | `edge.first.*` |
| | 2nd Differential Gradient → Laplacian, LoG, Canny | `edge.second.*` |
| | Compass | `edge.compass` |
| Segmentation | *(tidak dirinci pada PDF — out of scope v1.0)* | — |
| About | Info Developer, Tutorial (GitHub, YouTube) | *(klien)* `modal.js` |

> Ejaan menu pada PDF ("Substract", "Prewit", "Robert") disesuaikan di UI menjadi **Subtract**, **Prewitt**, **Roberts** (nama baku literatur). ID operasi mengikuti ejaan baku.

### 9.2 Glosarium Singkat

| Istilah | Arti |
|---|---|
| PCD | Pengolahan Citra Digital |
| Spatial Domain | Pemrosesan langsung pada piksel (konvolusi/point op) |
| Frequency Domain | Pemrosesan pada spektrum hasil Fourier Transform |
| ILPF / BLPF | Ideal / Butterworth Lowpass Filter |
| IHPF / BHPF | Ideal / Butterworth Highpass Filter |
| LoG | Laplacian of Gaussian |
| NMS | Non-Maximum Suppression (langkah Canny) |
| Highboost | `A·f − lowpass(f)`, `A ≥ 1` |
| Pseudo-color | Pemetaan intensitas abu-abu ke warna melalui LUT |
| Compass operator | Kumpulan kernel arah (8 arah) untuk mencari respons tepi maksimum |
| Stateless server | Server tidak menyimpan gambar/sesi antar request |
| Registry | Kamus ID → fungsi + skema parameter |

### 9.3 Changelog Keputusan (Diisi Seiring Pengembangan)

| Tanggal | Keputusan | Alasan |
|---|---|---|
| — | Menggunakan Flask web app, bukan Tkinter | Lihat §1.2 |
| — | Server stateless, gambar dikirim Base64 PNG | Sederhana, tanpa storage |
| — | Tanpa OpenCV; algoritma inti ditulis dengan NumPy | Pembelajaran & penilaian jelas |
| — | Segmentation out of scope v1.0 | Tidak dirinci di PDF menu |
| *(tambahkan baris baru di sini)* | | |

### 9.4 Template Pembuka Prompt untuk Sesi AI Baru

```text
[Tempel seluruh isi PROJECT_CONTEXT.md]

KONTEKS SESI INI:
- Tahap yang sedang dikerjakan: <Tahap X — nama>
- Tugas hari ini: <mis. implementasi enhance.smoothing.frequency.blpf>
- File yang sudah ada / relevan: <tempel kode terkait bila perlu>

PERMINTAAN:
Buatkan <fungsi + ParamSpec registry + test pytest> untuk operasi di atas,
patuhi §2.4 (signature & dtype), §3 (lokasi file), §4 (parameter), §5 (kontrak API),
dan DoD §7.5. Jangan ubah kontrak/struktur yang sudah ditetapkan.
```

---

*Akhir dokumen — VisionCraft PCD · Project Context v1.0 · © Muhammad Raihan Ilyasman – 2026*
