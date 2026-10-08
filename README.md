# Rapfi-YixinBoard (Modern GTK3 build)

This repository is a build-and-patch layer for [dhbloo/Yixin-Board](https://github.com/dhbloo/Yixin-Board), itself based on the original [accreator/Yixin-Board](https://github.com/accreator/Yixin-Board). It intentionally preserves upstream engine commands, balance tools, toolbar controls, database integration and BMP skins.

## Changes
- Looks for **rapfi.exe** on Windows instead of engine.exe; on Unix uses ./rapfi.
- Adds optional `modern.css` for contemporary GTK3 styling while retaining all buttons.
- GitHub Actions compiles a Windows x64 GTK3 GUI and uploads a ZIP artifact containing the EXE, required GUI DLLs and upstream assets.

## Download
Go to **Actions → Build Windows ZIP → latest successful run → Artifacts → Rapfi-YixinBoard-Windows-x64**. GitHub wraps the contained ZIP in its own artifact download ZIP.

## Running
Extract the inner `Rapfi-YixinBoard-Windows-x64.zip` if necessary. Copy a compatible `rapfi.exe` next to `Rapfi-YixinBoard.exe` and run the GUI. The Rapfi engine is not included and may require compatible network weights. Engine-specific extended commands (including balance commands) depend on your engine build.

## BMP compatibility
The upstream GTK code uses `piece.bmp` by default and prefers `piece_dark.bmp` if present in dark mode. The original upstream `skin/skin_1.bmp` and `skin/skin_2.bmp` are kept unchanged. `modern.css` only styles standard GTK widgets and does not replace board sprites.

## License / attribution
YixinBoard is BSD-2-Clause licensed, copyright (c) 2009-2017 Kai Sun. This project downloads and patches the upstream at pinned commit `e947fa65b30a22c177f25c8ee671639d76318487`. The original `LICENSE.md` is packaged unmodified as `LICENSE-YixinBoard.md`. Retain the copyright notice, conditions and disclaimer in source and binaries. Third-party GTK libraries have their own redistribution terms; consult their distributed licenses when publishing binaries.

## Build policy
CI performs a clean build from source. No change is made to the separate RapfiBoard repository.
