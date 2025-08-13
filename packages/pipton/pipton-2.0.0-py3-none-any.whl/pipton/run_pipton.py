import sys
from pipton.runner import run_file

def main():
    if len(sys.argv) != 2:
        print("❗ لطفاً مسیر فایل را بدهید")
        return

    filepath = sys.argv[1]
    
    # اگر بخوای فقط .piton بپذیره:
    if not filepath.endswith((".piton",".pipton")):
        print(" Only files with the .piton extension are supported.")
        return

    run_file(filepath)

if __name__ == '__main__':
    main()
