import os
import tempfile
import requests
import time
requests.packages.urllib3.disable_warnings()

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as dir:
        i = 0
        while True:
            t = time.time()
            file = requests.get("https://gist.githubusercontent.com/hrp/900964/raw/2bbee4c296e6b54877b537144be89f19beff75f4/twitter.json", verify=False).text
            with open(os.path.join(dir, str(i) + '.json'), 'w') as f:
                f.write(file)
            if i % 10 == 0:
                img = requests.get("https://ceres.huma-num.fr/lgbt/0ea53a3e4efe4d1da95263991f94f580cd170879.jpg", verify=False).content
                with open(os.path.join(dir, str(i) + '.jpg'), 'wb') as f:
                    f.write(img)
            total = time.time() - t
            print(total)
            # if total > 0:
            #     print(total)
            i += 1
            time.sleep(0.25)