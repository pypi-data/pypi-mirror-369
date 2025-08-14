from .C_M import CM; C = CM()
G2 = "\n" * 2

class FileCheck:
    # Full path to jar & other
    def Set_Path(self):
        run_dir = C.os.path.dirname(C.os.path.abspath(C.sys.argv[0]))
        script_dir = C.os.path.dirname(C.os.path.abspath(__file__))
        self.APKEditor_Path = C.os.path.join(run_dir, "APKEditor.jar")
        self.APKTool_Path = C.os.path.join(run_dir, "APKTool_OR.jar")
        self.Axml2Xml_Path = C.os.path.join(run_dir, "Axml2Xml.jar")
        self.Objectlogger = C.os.path.join(script_dir, "Objectlogger.smali")
        self.Pairip_CoreX = C.os.path.join(script_dir, "lib_Pairip_CoreX.so")

    # Calculate SHA-256 checksum of a file
    def calculate_checksum(self, file_path):
        sha256_hash = C.hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except FileNotFoundError:
            return None

    # Function to download files
    def download_file(self, Jar_Files):
        import requests
        downloaded_urls = set()
        for file_url, local_path, expected_checksum in Jar_Files:
            lo_path = C.os.path.basename(local_path)

            if C.os.path.exists(local_path):
                if self.calculate_checksum(local_path) == expected_checksum:
                    continue
                else:
                    print(f"{C.rd}[ {C.pr}File {C.rd}] {C.c}{lo_path} {C.rd}is Corrupt (Checksum Mismatch).{G2}{C.lb}[ {C.y}INFO ! {C.lb}]{C.rd} Re-Downloading, Need Internet Connection.{C.r}\n")
                    C.os.remove(local_path)
            try:
                Version = C.re.findall(r'version = "([^"]+)"', requests.get("https://raw.githubusercontent.com/TechnoIndian/RKPairip/main/pyproject.toml").text)[0]
                if Version != "3.8":
                    print(f"\n{C.lb}[ {C.y}Update {C.lb}]{C.c} Updating RKPairip 𒁍 {C.g}{Version}...{G2}")
                    cmd = (["pip", "install", "git+https://github.com/TechnoIndian/RKPairip.git"] if C.os.name == "nt" else "pip install --force-reinstall https://github.com/TechnoIndian/RKPairip/archive/refs/heads/main.zip")
                    C.subprocess.run(cmd, shell=isinstance(cmd, str), check=True)

                print(f"\n{C.lb}[ {C.pr}Downloading {C.lb}] {C.c}{lo_path}", end='', flush=True)
                response = requests.get(file_url, stream=True, timeout=10)

                if response.status_code == 200:
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    with open(local_path, 'wb') as f:
                        for data in response.iter_content(1024):
                            downloaded += len(data)
                            f.write(data)
                            progress_line = f"\r{C.lb}[ {C.pr}Downloading {C.lb}] {C.c}{lo_path} {C.g}➸❥ {downloaded / total_size * 100 if total_size > 0 else 0:.2f}% ({downloaded / (1024 * 1024):.2f}/{total_size / (1024 * 1024) if total_size > 0 else 0:.2f} MB)"
                            print(progress_line, end='\r')

                    print(f"\n{C.g}       |\n       └──── {C.r}Downloaded ~{C.g}$ {lo_path} Successfully. ✔\n")

                else:
                    exit(f'{G2}{C.lb}[ {C.rd}Error ! {C.lb}]{C.rd} Failed to download {C.y}{lo_path} {C.rd}Status Code: {response.status_code}{G2}{C.lb}[ {C.y}INFO ! {C.lb}]{C.rd} Restart Script...{C.r}\n')
            except requests.exceptions.RequestException:
                exit(f'{G2}{C.lb}[ {C.rd}Error ! {C.lb}]{C.rd} Got an error while Fetching {C.y}{local_path}{G2}{C.lb}[ {C.rd}Error ! {C.lb}]{C.rd} No internet Connection{G2}{C.lb}[ {C.y}INFO ! {C.lb}]{C.rd} Internet Connection is Required to Download {C.y}{lo_path}\n')

    def F_D(self):
        Jar_Files = [
            ("https://github.com/TechnoIndian/Tools/releases/download/Tools/APKEditor.jar", self.APKEditor_Path, "c242f5fc4591667a0084668320d0016a20e7c2abae102c1bd4d640e11d9f60ee"),
            ("https://raw.githubusercontent.com/TechnoIndian/Objectlogger/main/Objectlogger.smali", self.Objectlogger, "ff31dd1f55d95c595b77888b9606263256f1ed151a5bf5706265e74fc0b46697"),
            ("https://github.com/TechnoIndian/Tools/releases/download/Tools/lib_Pairip_CoreX.so", self.Pairip_CoreX, "22a7954092001e7c87f0cacb7e2efb1772adbf598ecf73190e88d76edf6a7d2a")
        ]
        self.download_file(Jar_Files)
        C.os.system('cls' if C.os.name == 'nt' else 'clear')

    def F_D_A(self, isAPKTool, Fix_Dex):
        Jar_Files = []
        if isAPKTool or Fix_Dex:
            Jar_Files.append(("https://github.com/TechnoIndian/Tools/releases/download/Tools/APKTool.jar", self.APKTool_Path, "effb69dab2f93806cafc0d232f6be32c2551b8d51c67650f575e46c016908fdd"))
        if isAPKTool or Fix_Dex:
            Jar_Files.append(("https://github.com/TechnoIndian/Tools/releases/download/Tools/Axml2Xml.jar", self.Axml2Xml_Path, "e3a09af1255c703fc050e17add898562e463c87bb90c085b4b4e9e56d1b5fa62"))
        if Jar_Files:
            self.download_file(Jar_Files)