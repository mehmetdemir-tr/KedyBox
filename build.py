from colorama import Fore, init
import os
import glob
import sys

init(autoreset=True)

unzip_loc = "/usr/bin/unzip"
sysroot_loc = os.path.abspath("rootfs/usr")
gcc_loc = "/usr/bin/aarch64-linux-gnu-gcc"

print(Fore.RED + "KedyBox - PatiOS ENV Builder by mehmetdemir-tr")


def extract():
    print(Fore.GREEN + "Dosya sistemi çıkarılıyor..")

    if not os.path.exists(unzip_loc):
        print(Fore.YELLOW + "[!] unzip bulunamadı, kuruluyor...")
        ret = os.system("sudo apt install unzip -y")
        if ret != 0:
            print(Fore.RED + "[-] unzip kurulamadı, çıkılıyor.")
            sys.exit(1)

    ret1 = os.system(f"{unzip_loc} paticommands.zip -d pati-commands/")
    ret2 = os.system(f"{unzip_loc} filesystem.zip -d rootfs/")

    if ret1 != 0 or ret2 != 0:
        print(Fore.RED + "[-] ZIP çıkartma başarısız, çıkılıyor.")
        sys.exit(1)

    print(Fore.GREEN + "[+] Dosya sistemi hazır.")


def compile():
    if not os.path.exists(gcc_loc):
        print(Fore.YELLOW + "[!] aarch64-gcc bulunamadı, kuruluyor...")
        ret = os.system("sudo apt install gcc-aarch64-linux-gnu binutils-aarch64-linux-gnu -y")
        if ret != 0:
            print(Fore.RED + "[-] GCC kurulamadı, çıkılıyor.")
            sys.exit(1)

    dosyalar = glob.glob("pati-commands/*.c")
    if not dosyalar:
        print(Fore.RED + "[-] pati-commands/ içinde .c dosyası bulunamadı.")
        sys.exit(1)

    sysroot = os.path.abspath("rootfs/usr")
    flags = f"--sysroot={sysroot} -I{sysroot}/include -L{sysroot}/lib -static"

    basari = 0
    hata = 0
    for f in dosyalar:
        out = f.replace(".c", "")
        ret = os.system(f"{gcc_loc} {flags} {f} -o {out}")
        if ret == 0:
            print(Fore.GREEN + f"[+] Derlendi: {f} -> {out}")
            basari += 1
        else:
            print(Fore.RED + f"[-] Hata: {f}")
            hata += 1

    print(Fore.GREEN + f"[+] Derleme tamam: {basari} başarılı, {hata} hatalı.")


def move():
    os.makedirs("rootfs/lib/paticommands", exist_ok=True)

    for f in glob.glob("pati-commands/*"):
        if not f.endswith(".c"):
            ret = os.system(f"mv {f} rootfs/lib/paticommands/")
            if ret == 0:
                print(Fore.GREEN + f"[+] Taşındı: {f}")
            else:
                print(Fore.RED + f"[-] Taşınamadı: {f}")

    print(Fore.GREEN + "[+] initramfs oluşturuluyor...")
    ret = os.system("cd rootfs && find . | cpio -o -H newc | gzip -9 > ../initramfs.cpio.gz")
    if ret == 0:
        print(Fore.GREEN + "[+] initramfs.cpio.gz hazır.")
    else:
        print(Fore.RED + "[-] initramfs oluşturulamadı.")
        sys.exit(1)


extract()
compile()
move()