import time
import fire

from burntool import BurnToolHost, BurnToolDevice, BurnToolParser, base16_to_bin, carr_to_bin

def load(port=None, fw=None, timeout=1):
    ts = time.time()
    print("loading...")
    burntool = BurnToolHost(port=port, fw=fw, timeout=timeout)
    res = burntool.run()
    if res:
        print("successful")
    else:
        print("failed")
    burntool.stop()
    print(f"Total time: {time.time() - ts:.3f} seconds")

def main():
    fire.Fire({
        "load": load,
        "host": BurnToolHost,
        "device": BurnToolDevice,
        "parser": BurnToolParser,
        "base16_to_bin": base16_to_bin,
        "carr_to_bin": carr_to_bin,
    })

if __name__ == '__main__':
    main()
