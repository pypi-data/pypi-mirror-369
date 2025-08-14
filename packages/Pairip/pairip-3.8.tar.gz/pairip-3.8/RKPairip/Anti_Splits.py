from .C_M import CM; C = CM()
from .Files_Check import FileCheck; F = FileCheck(); F.Set_Path()

Merge_Ext = ['.apks', '.apkm', '.xapk']
C_Line = f"{C.r}{'_' * 61}"; G = "\n" * 3; G2 = "\n" * 2

# Anti_Split
def Anti_Split(apk_path, isMerge, CoreX_Hook):
    base_name, Ext = C.os.path.splitext(apk_path)

    if apk_path and CoreX_Hook and C.os.path.splitext(apk_path)[-1].lower() not in Merge_Ext: exit(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Only Supported Extensions {C.g}{Merge_Ext} with {C.rkj}CoreX\n")

    if Ext in Merge_Ext:
        print(f"{C_Line}{G}{C.lb}[ {C.pr}* {C.lb}] {C.c} Anti-Split Start...")
        output_path = f"{base_name.replace(' ', '_')}.apk"
        print(f"{C.g}  |\n  └──── {C.r}Decompiling ~{C.g}$ java -jar {C.os.path.basename(F.APKEditor_Path)} m -i {apk_path} -f -o {output_path}" + (" -extractNativeLibs true" if CoreX_Hook else "") + f"{G2}{C_Line}{C.g}\n")
        cmd = ["java", "-jar", F.APKEditor_Path, "m", "-i", apk_path, "-f", "-o", output_path]
        if CoreX_Hook:
            cmd += ["-extractNativeLibs", "true"]
        try:
            result = C.subprocess.run(cmd, check=True)
            print(f"\n{C.lb}[ {C.pr}* {C.lb}] {C.c} Anti-Split Successful  {C.g}✔{C.r}{G2}{C_Line}\n")
            if isMerge: exit()
            return output_path
        except C.subprocess.CalledProcessError as e:
            exit(f"\n{C.lb}[ {C.rd}Error ! {C.lb}] {C.rd} Anti-Split Failed ! ✘{C.r}{G2}{C.lb}[ {C.rd}Error ! {C.lb}] {C.rd} Error Output: {e.stderr}\n")

    if isMerge and Ext not in Merge_Ext:
        exit(f"\n{C.lb}[{C.c} Info {C.lb}] {C.rd}Split ✘{C.r}{G}{C.lb}[ {C.pr}* {C.lb}] {C.c} Only Supported Extensions {C.g}{Merge_Ext}\n")
    return apk_path

def Check_Split(apk_path, isCoreX):
    if isCoreX and C.os.path.splitext(apk_path)[-1].lower() not in Merge_Ext:
        print(f"{G2}{C.lb}[ {C.pr}* {C.lb}] {C.c} Only Supported Extensions {C.g}{Merge_Ext} with {C.rkj}CoreX")
        return True
    return False
