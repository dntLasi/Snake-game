# Snake 3D — Android-ready Python project

A Kivy snake game with a 3D-inspired look (shaded glossy spheres, highlights, neon board), touch swipe controls, on-screen direction buttons, score, pause and restart.

> The artwork is rendered in 2D with shading to create a 3D look; it is not a full 3D engine.

## Run on a computer

Install Python 3 and Kivy, then run:

```bash
pip install kivy
python main.py
```

## Build APK through GitHub Actions

1. Create a new GitHub repository.
2. Upload all files/folders from this project to the repository root.
3. Commit to the `main` branch. The workflow in `.github/workflows/build-apk.yml` starts automatically.
4. Open the repository's **Actions** tab and select the latest **Build Android APK** run.
5. When it finishes, open the run's **Artifacts** section and download `snake3d-debug-apk`. Unzip it to get the `.apk`.

You can also start a build manually in **Actions → Build Android APK → Run workflow**.

## Build locally (Linux)

Install Buildozer and Android build dependencies, then:

```bash
pip install buildozer cython==0.29.36
buildozer android debug
```

The APK is written into `bin/`.

## Notes

- GitHub Actions builds a debug APK for testing, not a store-ready signed release.
- Android SDK/NDK downloads and first build can take a while.
- If GitHub Actions fails, open the failed step's log; Android toolchain versions can occasionally need updates.
