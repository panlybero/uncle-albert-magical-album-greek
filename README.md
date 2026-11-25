# Το Μαγικό Άλμπουμ του Θείου Αλβέρτου (1999 Greek Edition)
### *Uncle Albert's Magical Album* (`mtropolis:albert1`) — Digital Preservation & WebAssembly Port

[![ScummVM Compatible](https://img.shields.io/badge/Engine-ScummVM%20mTropolis-blue.svg)](https://www.scummvm.org/)
[![License](https://img.shields.io/badge/License-GPL--2.0-green.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html)
[![Platform](https://img.shields.io/badge/Platform-Web%20%7C%20Linux%20%7C%20macOS%20%7C%20Windows-orange.svg)](#)

A digital preservation, reverse-engineering, and browser port of **Το Μαγικό Άλμπουμ του Θείου Αλβέρτου** (*L'Album secret de l'oncle Ernest* / *Uncle Albert's Magical Album*), developed by **Lexis Numérique**, published by **Emme Interactive**, and localized into Greek by **MLS LaserSoftware / Πήγασος Interactive (1999)** on the **mTropolis 2.0** engine.

---

## 🎮 Play in Browser (Desktop & Mobile/Touchscreen)

You can play the complete Greek edition directly in any modern browser (Chrome, Firefox, Safari, Edge) with zero installation via GitHub Pages:

> 🌐 **[Play Uncle Albert's Magical Album in Browser](https://plympe.com/uncle-albert-magical-album-greek/)** *(Mirror: [panlybero.github.io/uncle-albert-magical-album-greek](https://panlybero.github.io/uncle-albert-magical-album-greek/))*

### Controls (Desktop & Touchscreen)
- **🖱️ Trackpad Mode (Touchscreens)**: Swipe anywhere on the screen to move the virtual cursor relatively with `Mouse Over` hover preservation (required for the flashlight, Polaroid camera viewfinder, and magnifying glass).
- **👆 Tap / Click**: Single tap or left click to interact.
- **✋ Drag & Drop (`Σύρσιμο` button or Double-Tap-and-Hold)**: Pick up collectibles and photos, store them on the left border (`cardass`), and attach photos into album frames (`zone_photo1` / `zone_photo2`).
- **⌨ Greek & Latin Keyboard (`Πληκτρολόγιο`)**: Enter player names in Greek (`Windows-1253` / Unicode) or Latin on the album selection screen (`choisis`).
- **⏭ Skip Intro (`Παράλειψη` / `Esc` / Tap)**: Skip the intro video cleanly to the first album spread (`00-depart`).

---

## 📸 Visual Verification

| Album Spread (`00-depart`) | Polaroid Viewfinder (`photo_viseur`) |
| :---: | :---: |
| ![Album Spread](docs/screenshots/screen_00_depart.png) | ![Camera Viewfinder](docs/screenshots/step1_viewfinder_on_plat.png) |
| *Opening album spread with tape recorder (`magneto`)* | *Camera viewfinder centered on pebble (`Βότσαλο`)* |

| Developed Photo (`photo1`) | Border Scaling & Frame Attachment (`zone_photo2`) |
| :---: | :---: |
| ![Developed Photo](docs/screenshots/step2_photo_developed.png) | ![Attached Photo](docs/screenshots/step4_photo_attached_to_frame.png) |
| *Developed Polaroid with serrated border and Greek caption* | *Photo scaled from border slot and attached into album frame* |

---

## 🔬 Summary of Reverse-Engineered Engine Fixes

> 📘 Full technical documentation covering the disc layout, all 137 mTropolis scenes, and all 18 subsystems fixed in ScummVM is available in **[`docs/TECHNICAL_FINDINGS.md`](docs/TECHNICAL_FINDINGS.md)**.

1. **Game Detection, Boot Configuration & Greek Encodings**:
   - Added `MTBOOT_ALBERT1_WIN_EL` (`GID_ALBERT1`, `Common::EL_GRC`, `ALBUM.EXE` + `album_gr1.MPL`) and `Windows1253GreekFont` for dynamic `TextLabelElement` rendering (player names and Polaroid photo captions).
2. **Native mTropolis Template Save Loading (`ALBUM/DATA/SAUVE`)**:
   - Implemented `Project::loadModifierFromNativeSaveFile` and `ListVariableModifier` native stream deserialization so starting a new profile loads initial coordinates, pages, and states for every collectible and creature across all 50 playable spreads.
3. **Full `Hoologic` Bitmap Plug-In (`BITMAP.R95`) & `Thereware::RotatorModifier` (`ROTATORK.R95`)**:
   - Implemented `BitmapVariableModifier`, `CaptureBitmapModifier`, `DisplayBitmapModifier`, `ScaleBitmapModifier` (including dynamic `_dimensionsSource` via `1a2d70 'echelle'`), `ImportBitmapModifier`, `SaveBitmapModifier`, and `PrintBitmapModifier` for the 4-slice page-turn transition and Polaroid camera.
4. **Polaroid Camera Viewfinder, Border Storage & Frame Attachment (`photo_placee`)**:
   - Applied `WorldManagerInterface::_cursorHotspot` (`(75, 50)`) to `Runtime::updateCursorElementPosition()`, excluded `objet_vise` from bitmap capture, reset initially-hidden child elements (`cadre`, `texte`, `cardass`) on reparenting (`executeChangeObjectParent`), and implemented `"element"` in `Modifier::writeRefAttribute` so `source(3).parent.element.globalposition := element(1).globalposition` attaches photos into `zone_photo1` / `zone_photo2`.
5. **Low-Latency HTTP Range Streaming & 16 MB CDN Sharding (`ChunkedHTTPReadStream`)**:
   - Implemented a 4-slot C++ LRU chunk reader with synchronous JS cache hits (`0 ms` without `Asyncify` stack unwind), `+3 MB` background prefetching, pause-aware QuickTime video/audio clocks, and transparent 16 MB `.partXX` shard resolution for the 359 MB `album_gr2.MPX` container on GitHub Pages.

---

## 🇫🇷 French Edition (*L'Album secret de l'oncle Ernest*, Windows)

The web player can also run the original French Windows release (`album421.MPL` / `album422.MPX`). Choose the language with the selector in the top bar, or open the page with `?lang=fr`. Each edition keeps its own data folder (`/data/albert` or `/data/albert_fr`) and its own save folder, so albums from one language never appear in the other.

### Game data

The French files are not stored in this repository. Build `albert_game_data_fr.zip` from the French installer:

```bash
sudo apt install innoextract
python3 tools/make_french_game_data.py setup-02763-L_Album_secret_de_l_oncle_Ernest-PCWin.exe
```

The script checks the installer, unpacks it with `innoextract`, verifies that `album421.MPL` and `album422.MPX` match ScummVM's French `albert1` entry, and writes the needed files under `ALBUM/DATA/` (the same layout as the Greek zip). Attach the zip to the `v1.0.0-preservation` release: the deploy workflow then adds the French edition, and skips it when the zip is absent. The language selector only offers editions whose data was deployed.

### Engine changes (`patches/scummvm-french-albert.patch`, applied after the Greek patch)

1. Enables the French `albert1` detection entry and drops the `MTPLAY95.EXE` checksum, because known copies ship a patched player.
2. Implements mTropolis text-label *calculated fields*: a label text such as `<nom_page>` or `<trad_texte>` shows the value of the variable with that name, filled in when the label activates and on the "Update Calculated Fields" command (event 219). Before this, page names, tooltips and the album-selection instructions showed the raw `<...>` placeholders.
3. Lets Escape, the skip button or a click skip the French intro film. In the French release the `film` scene only leaves when the movie reaches its last frame, so the event is sent early.
4. Ignores key auto-repeat when typing a name, so one key press adds one letter.
5. Fixes a crash in `Runtime::checkCollisions` (`Assertion failed: idx < _size ... remove_at`): an expired element was removed from the wrong list.
6. Emscripten: creates folders listed in `Module.scummvmEnsureDirs` after mounting IDBFS, so the page can pass a per-edition `--savepath`.

---

## 📁 Repository Structure

```text
uncle-albert-magical-album-greek/
├── docs/
│   ├── TECHNICAL_FINDINGS.md          # Complete technical reference & engine fix catalog
│   └── screenshots/                   # In-engine verification captures
├── patches/
│   ├── scummvm-greek-albert.patch     # Full ScummVM mTropolis & Emscripten patch
│   └── scummvm-french-albert.patch    # French edition support (apply after the Greek patch)
├── tools/
│   ├── make_french_game_data.py       # Builds albert_game_data_fr.zip from the French installer
│   ├── patch_scummvm_js.py            # Post-build patcher for Emscripten scummvm.js
│   ├── build-make_http_index.py       # HTTP filesystem index.json generator
│   └── serve_range.py                 # Local multi-threaded HTTP 206 Range test server
├── web/                               # WebAssembly player deployed to GitHub Pages
└── run_albert.sh                      # Desktop launcher script
```

---

## ⚖️ Legal & Disclaimer

*Το Μαγικό Άλμπουμ του Θείου Αλβέρτου* (*L'Album secret de l'oncle Ernest*) is © 1998–1999 Lexis Numérique / Emme Interactive / MLS LaserSoftware / Πήγασος Interactive. This project is created strictly for non-commercial historical preservation, accessibility, and educational purposes. All reverse-engineered engine patches, tools, and scripts are licensed under the GNU General Public License v2.0.
