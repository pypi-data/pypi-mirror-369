import time
import fire

from burntool import BurnToolHost, burntool_scan
from burntool import base16_to_bin, carr_to_bin

def scan():
    ts = time.time()
    ports = burntool_scan()
    print(f"Scan complete: {ports}")
    print(f"Total time: {time.time() - ts:.3f} seconds")


def load(port=None, fw=None, timeout=1):
    ts = time.time()
    print("Loading...")
    burntool = BurnToolHost(port=port, fw=fw, timeout=timeout)
    res = burntool.run()
    if res:
        print("Successful")
    else:
        print("Failed")
    burntool.stop()
    print(f"Total time: {time.time() - ts:.3f} seconds")

def main():
    fire.Fire({
        "scan": scan,
        "load": load,
        "base16_to_bin": base16_to_bin,
        "carr_to_bin": carr_to_bin,
    })

if __name__ == '__main__':
    main()
