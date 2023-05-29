Web (WASM)
----------

Requirements:
  - python >= 3.11
  - pygbag >= 0.7.1

Install dependencies and build WASM version:
  ```sh
  pip3 install pygbag --user --upgrade
  python3 -m pygbag .
  ```

  Now you may open `./build/web/index.html` in a Chromium or Gecko-based browser (Chrome, Firefox).
  Safari and mobile web support is coming soon.
