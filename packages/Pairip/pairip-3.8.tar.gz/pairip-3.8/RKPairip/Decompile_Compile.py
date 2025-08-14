from .C_M import CM; C = CM()
from .Files_Check import FileCheck; F = FileCheck(); F.Set_Path()

C_Line = f"{C.r}{'_' * 61}"; G = "\n" * 3; G2 = "\n" * 2

# Decompile_Apk
def Decompile_Apk(apk_path, decompile_dir, isAPKTool, Fix_Dex):
    print(f'\n{C_Line}\n')
    if isAPKTool or Fix_Dex:
        cmd = ["java", "-jar", F.APKTool_Path, "d", "-f", "-r", '--only-main-classes', apk_path, "-o", decompile_dir]
        print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Decompile with ApkTool...")
        print(f"{C.g}  |\n  └──── {C.r}Decompiling ~{C.g}$ java -jar {C.os.path.basename(F.APKTool_Path)} d -f -r --only-main-classes {apk_path} -o {C.os.path.basename(decompile_dir)}{G2}{C_Line}{C.g}\n")
    else:
        cmd = ["java", "-jar", F.APKEditor_Path, "d", "-f", "-no-dex-debug", "-i", apk_path, "-o", decompile_dir]
        print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Decompile with APKEditor...")
        print(f"{C.g}  |\n  └──── {C.r}Decompiling ~{C.g}$ java -jar {C.os.path.basename(F.APKEditor_Path)} d -f -no-dex-debug -i {apk_path} -o {C.os.path.basename(decompile_dir)}{G2}{C_Line}{C.g}\n")
    try:
        C.subprocess.run(cmd, check=True)
        print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Decompile Successful  {C.g}✔{G2}{C_Line}\n")
    except C.subprocess.CalledProcessError:
        C.shutil.rmtree(decompile_dir)
        exit(f"\n{C.lb}[ {C.rd}Error ! {C.lb}] {C.rd} Decompile Failed ! ✘\n")
        return None, None

# Recompile_Apk
def Recompile_Apk(decompile_dir, isAPKTool, build_dir):
    print(f'{C_Line}\n')
    if isAPKTool:
        cmd = ["java", "-jar", F.APKTool_Path, "b", "-f", decompile_dir, "-o", build_dir]
        print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Recompile APK...")
        print(f"{C.g}  |\n  └──── {C.r}Recompiling with aapt ~{C.g}$ java -jar {C.os.path.basename(F.APKTool_Path)} b -f {C.os.path.basename(decompile_dir)} -o {C.os.path.basename(build_dir)}{G2}{C_Line}{C.g}\n")
        print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} ApkTool Default...{C.g}\n")
        try:
            C.subprocess.run(cmd, check=True)
            print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Recompile Successful  {C.g}✔{G2}{C_Line}\n")
        except C.subprocess.CalledProcessError:
            print(f"\n{C.lb}[ {C.rd}Error ! {C.lb}]{C.rd} Default Recompile Failed! ✘\n")
            cmd = ["java", "-jar", F.APKTool_Path, "b", "-f", "--use-aapt1", decompile_dir, "-o", build_dir]
            print(f"{C_Line}{G}{C.lb}[ {C.pr}* {C.lb}] {C.c} Recompile APK...")
            print(f"{C.g}  |\n  └──── {C.r}Recompiling with aapt1 ~{C.g}$ java -jar {C.os.path.basename(F.APKTool_Path)} b -f --use-aapt1 {C.os.path.basename(decompile_dir)} -o {C.os.path.basename(build_dir)}{G2}{C_Line}{C.g}\n")
            print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} ApkTool AAPT1...{C.g}\n")
            try:
                C.subprocess.run(cmd, check=True)
                print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Recompile Successful with aapt1 {C.g} ✔{G2}{C_Line}\n")
            except C.subprocess.CalledProcessError:
                C.shutil.rmtree(decompile_dir)
                exit(f"\n{C.lb}[ {C.rd}Error ! {C.lb}]{C.rd} AAPT Recompile Failed! ✘{G2}{C.lb}[ {C.rd}Error ! {C.lb}]{C.rd} Recompile Failed with both Default & aapt1 ! ✘\n")

    else:
        cmd = ["java", "-jar", F.APKEditor_Path, "b", "-i", decompile_dir, "-o", build_dir, "-f"]
        print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Recompile APK...")
        print(f"{C.g}  |\n  └──── {C.r}Recompiling ~{C.g}$ java -jar {C.os.path.basename(F.APKEditor_Path)} b -i {C.os.path.basename(decompile_dir)} -o {C.os.path.basename(build_dir)} -f{G2}{C_Line}{C.g}\n")
        try:
            C.subprocess.run(cmd, check=True)
            print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Recompile Successful  {C.g}✔{G2}{C_Line}\n")
        except C.subprocess.CalledProcessError:
            C.shutil.rmtree(decompile_dir)
            exit(f"\n{C.lb}[ {C.rd}Error ! {C.lb}]{C.rd} Recompile Failed with APKEditor ! ✘\n")

    if C.os.path.exists(build_dir): print(f"\n{C.lb}[ {C.c}APK Created {C.lb}] {C.g}➸❥ {C.y}{build_dir} {C.g}✔{G2}{C_Line}\n")

# FixSigBlock
def FixSigBlock(decompile_dir, apk_path, build_dir, rebuild_dir):
    C.os.rename(build_dir, rebuild_dir)
    sig_dir = decompile_dir.replace('_decompiled', '_SigBlock')
    for operation in ["d", "b"]:
        cmd = ["java", "-jar", F.APKEditor_Path, operation, "-t", "sig", "-i", (apk_path if operation == "d" else rebuild_dir), "-f", "-sig", sig_dir]
        if operation == "b":
            cmd.extend(["-o", build_dir])
        C.subprocess.run(cmd, check=True, text=True, capture_output=True)
    C.shutil.rmtree(sig_dir); C.os.remove(rebuild_dir)

