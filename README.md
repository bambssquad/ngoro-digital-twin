# NGORO Digital Twin

Model kawasan tiga gudang dari NGORO.send.dwg, dengan viewer Three.js dan file SketchUp 2023.

[Buka viewer](https://bambssquad.github.io/ngoro-digital-twin/) · [File SKP](web/dist/downloads/NGORO_Detailed_SU2023.skp)

## Revisi terkini

- [Tahap konstruksi interaktif](https://bambssquad.github.io/ngoro-digital-twin/?mode=construction): delapan tahap ilustratif, putar/jeda, scrub, dan hitungan elemen model. Bukan jadwal/BOQ terverifikasi. [Catatan](docs/construction-playback.md).

- Mode Diorama malam: alas miniatur, nuansa navy, cahaya hangat, dan hujan ringan. Pilih Gaya visual → Arsitektur untuk material/cahaya asli. Lihat [catatan dan verifikasi](docs/diorama.md).

- Tiga gudang, masing-masing 23 × 60 m; puncak atap 12 m dari lantai dan tepi atap sekitar 9,13 m.
- Pintu tiap gudang terdiri dari dua daun geser plat besi penuh dengan kontrol buka/tutup.
- Pagar depan tembok, gerbang baja geser, pohon palm ramping, dan pos dengan atap turun ke timur.
- Jelajah orang pertama/ketiga, karakter kotak 170 cm, tabrakan, dan joystick untuk HP.
- Material dan tekstur lokal dengan kualitas adaptif.
- Mode CAD 2D dan Gambar Teknik: CAD asli, denah bersih, dua tampak dan dua potongan turunan model; zoom, geser, layer dan unduhan SVG/DWG. Ada 12 tampilan vektor dengan label sumber yang jelas.

## Jalankan web lokal

Python 3, tanpa build atau instalasi npm:

```sh
python -m http.server 5186 --directory web/dist
```

Buka http://localhost:5186/. Web harus disajikan melalui HTTP agar modul dan aset dapat dimuat.

## Isi proyek

- `web/dist/`: web siap dijalankan, vendor Three.js, tekstur, dan unduhan SKP.
- `scripts/`: generator model Python serta integrasi Ruby untuk SketchUp.
- `analysis/geometry.json`: geometri sumber hasil pembacaan DWG.
- `outputs/model-manifest.json`: parameter, sumber, dan asumsi model.
- `verification/revision-04/`: bukti pemeriksaan geometri, SKP, dan viewer.
- `docs/cad-viewer.md`: sumber, generator dan batas gambar 2D; `web/dist/assets/drawings/` berisi lembar vektor dan manifest.

Generator scene: `python scripts/build_scene.py`. Skrip SketchUp berasal dari lingkungan produksi Windows dan memiliki lokasi proyek lokal di dalamnya; sesuaikan lokasi tersebut sebelum dijalankan pada komputer lain. File SKP siap dibuka langsung tanpa menjalankan generator.

## Verifikasi dan batas

Revisi 04: 9.972 elemen, file SKP dibuka ulang dengan nol solid nonmanifold. Viewer mengukur karakter 1,700 m dan puncak atap 12 m dari lantai. Tebal penutup/nok berada di atas datum puncak. Profil struktur dan detail sambungan adalah representasi visual, bukan desain konstruksi.

Tekstur ambientCG memakai CC0; atribusi ada di `web/dist/assets/material-sources.json`. Lisensi Three.js ada di `web/dist/vendor/LICENSE-three.txt`.

Repositori publik. Web diterbitkan ke GitHub Pages dari `web/dist` melalui `.github/workflows/pages.yml`; perubahan web pada branch `main` akan diterbitkan otomatis.
