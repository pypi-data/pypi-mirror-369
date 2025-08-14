import subprocess
import sys
import os
from shutil import which

REQUIRED_TOOLS = ['gf', 'amass'] # Tambahkan semua tool yang dibutuhkan di sini

def check_dependencies():
    """Memeriksa apakah tool yang dibutuhkan sudah ada di PATH sistem."""
    print("🔎 Checking for required external tools...")
    missing_tools = []
    for tool in REQUIRED_TOOLS:
        if which(tool) is None:
            missing_tools.append(tool)

    if missing_tools:
        print("\n❌ Error: The following required tools are not installed or not in your PATH:")
        for tool in missing_tools:
            print(f"  - {tool}")
        print("\nPlease install them first before running this tool.")
        sys.exit(1) # Keluar dari program jika ada tool yang hilang
    print("✅ All required tools are found.")


def run():
    """Fungsi utama yang akan dipanggil oleh 'entry_point'."""
    # Pertama, periksa semua dependensi eksternal
    check_dependencies()

    try:
        # Menemukan path absolut ke direktori 'scripts' di dalam paket yang terinstal
        # __file__ adalah path ke file main.py ini
        package_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(package_dir, 'scripts', 'hades.sh')

        # Memastikan skrip dapat dieksekusi
        os.chmod(script_path, 0o755)

        # Meneruskan semua argumen dari command line (misal: hades -d example.com)
        # ke skrip hades.sh
        args = [script_path] + sys.argv[1:]
        
        # Menjalankan skrip hades.sh
        subprocess.run(args, check=True)

    except FileNotFoundError:
        print("Error: hades.sh script not found!")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running hades.sh: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run()