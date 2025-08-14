from .C_M import CM; C = CM()

# Version
def Version():
    version_mapping = {
        "3.8.1": ["3.32.1", "3.32.2", "3.32.3", "3.32.4", "3.32.5", "3.32.6", "3.32.7", "3.32.8"],
        "3.8.0": "3.32.0",
        "3.7.2": ["3.29.2", "3.29.3"],
        "3.7.0": ["3.29.0", "3.29.1"],
        "3.6.2": "3.27.4", 
        "3.6.1": ["3.27.2", "3.27.3"],
        "3.6.0": ["3.27.0", "3.27.1"],
        "3.5.4": ["3.24.4", "3.24.5"],
        "3.5.3": "3.24.3",
        "3.5.2": "3.24.2",
        "3.5.1": "3.24.1",
        "3.5.0": "3.24.0",
        "3.4.4": "3.22.3", 
        "3.4.3": "3.22.2", 
        "3.4.1": "3.22.1", 
        "3.4.0": "3.22.0",
        "3.3.4": "3.19.6", 
        "3.3.3": "3.19.5", 
        "3.3.2": "3.19.4", 
        "3.3.1": "3.19.3",
        "3.3.0": ["3.19.0", "3.19.1", "3.19.2"],
        "3.2.6": "3.16.9", 
        "3.2.5": "3.16.8", 
        "3.2.4": "3.16.7",
        "3.2.3": ["3.16.3", "3.16.4", "3.16.6", "3.16.6"],
        "3.2.2": "3.16.2", 
        "3.2.1": "3.16.1", 
        "3.2.0": "3.16.0",
        "3.1.5": "3.13.9", 
        "3.1.4": "3.13.8", 
        "3.1.3": ["3.13.6", "3.13.7"],
        "3.1.2": "3.13.5",
        "3.1.1": "3.13.3", 
        "3.1.0": ["3.13.0", "3.13.1", "3.13.2"],
        "3.0.6": "3.10.6", 
        "3.0.5": "3.10.5",
        "3.0.3": ["3.10.3", "3.10.4"],
        "3.0.2": "3.10.2", 
        "3.0.1": "3.10.1", 
        "3.0.0": "3.10.0",
        "2.19.6": ["3.7.9", "3.7.10", "3.7.11", "3.7.12"],
        "2.19.5": "3.7.8", 
        "2.19.4": "3.7.7", 
        "2.19.3": "3.7.6",
        "2.19.2": ["3.7.2", "3.7.3", "3.7.4", "3.7.5"],
        "2.19.1": "3.7.1", 
        "2.19.0": "3.7.0", 
        "2.18.6": "3.3.10",
        "2.18.5": "3.3.9", 
        "2.18.4": ["3.3.7", "3.3.8"],
        "2.18.2": ["3.3.3", "3.3.4", "3.3.5", "3.3.6"],
        "2.18.1": "3.3.2",
        "2.18.0": ["3.3.0", "3.3.1"],
        "2.17.6": "3.0.5", 
        "2.17.5": ["3.0.3", "3.0.4"],
        "2.17.3": "3.0.2",
        "2.17.1": "3.0.1", 
        "2.17.0": "3.0.0", 
        "2.16.2": ["2.10.4", "2.10.5"],
        "2.16.1": ["2.10.0", "2.10.1", "2.10.3"],
        "2.16.0": "2.10.0", 
        "2.15.1": "2.8.1", 
        "2.15.0": "2.8.0", 
        "2.14.4": "2.5.3",
        "2.14.3": "2.5.2", 
        "2.14.2": "2.5.1", 
        "2.14.0": "2.5.0", 
        "2.13.4": "2.2.3",
        "2.13.3": "2.2.2", 
        "2.13.1": "2.2.1", 
        "2.13.0": "2.2.0", 
        "2.12.3": ["2.0.5", "2.0.6"],
        "2.12.2": ["2.0.3", "2.0.4"],
        "2.12.1": "2.0.2", 
        "2.12.0": ["2.0.0", "2.0.1"],
        "2.10.4": "1.22.4",
        "2.10.3": "1.22.3", 
        "2.10.2": "1.22.2", 
        "2.10.1": "1.22.1", 
        "2.10.0": "1.22.0",
        "2.9.2": ["1.20.3", "1.20.4"],
        "2.9.1": "1.20.2", 
        "2.9.0": ["1.20.0", "1.20.1"]}
    return version_mapping

def E_V_C(apk_path, version_mapping):
    flutter_libs = []; isFlutter = False

    with C.zipfile.ZipFile(apk_path, 'r') as zip_ref:
        for item in zip_ref.infolist():
            if item.filename.endswith('libflutter.so'):
                flutter_libs.append(item.filename)
                isFlutter = True
                break
        if flutter_libs:
            print(f"\n\n{C.lb}[ {C.y}FYI ! {C.lb}] {C.rkj}So Generate {C.pr}'{C.g}libflutter.so{C.pr}'{C.rkj} in Github With {C.pr}'{C.g}flutter-build.yml{C.pr}' {C.rkj}Script & Then Replace With Your {C.pr}'{C.g}libflutter.so{C.pr}'{C.r}")
            
            mapped_versions = []

            for lib in flutter_libs:
                with zip_ref.open(lib) as lib_file:
                    read = lib_file.read().decode('ascii', errors='ignore').replace('\x00', '')
                    pattern = C.re.compile(r'\\"(.*?) \(stable\)')
                    matches = pattern.findall(read)
                    if matches:
                        version_code = matches[0]
                    else:
                        if " (stable)" in read:
                            version_code = C.re.findall(r'\d+\.\d+\.\d+', read[:read.find(" (stable)")])[-1]
                        else:
                            version_code = "Unknown"

                    print(f"\n\n{C.lb}[ {C.pr}Found Version {C.lb}]  {C.g}➸❥  {version_code}  ✔\n")
                    if version_code in version_mapping:
                        mapped_versions.extend(version_mapping[version_code] if isinstance(version_mapping[version_code], list) else [version_mapping[version_code]])
                        print(f"\n{C.lb}[ {C.pr}Flutter SDK Version {C.lb}]  {C.g}➸❥  {', '.join(mapped_versions)}  ✔\n")
                    else:
                        print(f"\n{C.lb}[ {C.y}Skip {C.lb}] {C.rd} '{version_code}' Version, not in Version Mapping")
            mapped_versions = list(set(mapped_versions))               
            if mapped_versions:
                create_workflow(mapped_versions, C.os.path.dirname(apk_path))
            return mapped_versions

def create_workflow(F_S_V, output_path):
    file_paths = []
    for version in F_S_V:
        content = f"""
name: Flutter Build

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Set up Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '{version}'

      - name: Print Flutter version
        run: flutter --version

      - name: Create and set up Flutter project
        run: |
          flutter create flutter_so
          cd flutter_so
          flutter pub get

      - name: Build APK for arm64 and armeabi-v7a
        run: |
          cd flutter_so
          flutter build apk --release --target-platform android-arm,android-arm64

      - name: Upload libflutter.so for arm64
        uses: actions/upload-artifact@v4
        with:
          name: libflutter_so_arm64
          path: flutter_so/build/app/intermediates/merged_native_libs/release/out/lib/arm64-v8a/libflutter.so

      - name: Upload libflutter.so for armeabi-v7a
        uses: actions/upload-artifact@v4
        with:
          name: libflutter_so_armeabi_v7a
          path: flutter_so/build/app/intermediates/merged_native_libs/release/out/lib/armeabi-v7a/libflutter.so
"""
        file_path = C.os.path.join(output_path, f'flutter-build-{version}.yml')
        open(file_path, 'w', encoding='utf-8', errors='ignore').write(content)
        file_paths.append(file_path)

    print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Workflow Script Saved {C.g}➸❥ {C.y}{', '.join(file_paths)}\n\n\n{C.lb}[ {C.pr}Tutorial {C.lb}] {C.r}https://t.me/TECHNO_INDIA_TUTORIAL/11")