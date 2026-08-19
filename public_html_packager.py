import os
import json

def package_public_html():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "lotto_data.json")
    html_path = os.path.join(base_dir, "index.html")
    dist_dir = os.path.join(base_dir, "public_html")
    
    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)

    with open(json_path, "r", encoding="utf-8") as f:
        data_json_str = f.read()

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    embedded_script = f"const embeddedLottoData = {data_json_str};\n        let lottoData = embeddedLottoData;"
    target_pattern = "let lottoData = null;"

    if target_pattern in html_content:
        html_content = html_content.replace(target_pattern, embedded_script)

    dist_html_path = os.path.join(dist_dir, "index.html")
    with open(dist_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    dist_json_path = os.path.join(dist_dir, "lotto_data.json")
    with open(dist_json_path, "w", encoding="utf-8") as f:
        f.write(data_json_str)

    print(f"Successfully packaged Enhance Host public_html directory at {dist_dir}")
    print(f"  - {dist_html_path}")
    print(f"  - {dist_json_path}")

if __name__ == "__main__":
    package_public_html()
