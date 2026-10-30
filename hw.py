import csv
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests

url = "https://www.musashino-u.ac.jp/"
parsed_url = urlparse(url)
domain = parsed_url.netloc

visited = set()
url_title_dict = {}
queue = [url]

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

print(f"クロールを開始します: {domain}")

csv_filename = "musashino_university_pages.csv"

try:
  while queue:
    current_url = queue.pop(0)

    if current_url in visited:
      continue

    visited.add(current_url)
    print(f"取得中: {current_url}")

    try:
      res = requests.get(current_url, headers=headers, timeout=10)
      res.encoding = res.apparent_encoding

      if "text/html" not in res.headers.get("Content-Type", ""):
        continue

      html_soup = BeautifulSoup(res.content, "html.parser")

      title_tag = html_soup.find("title")
      if title_tag and title_tag.string:
        title = title_tag.string.strip().replace("\n", " ")
      else:
        title = "No Title"

      url_title_dict[current_url] = title

      a_list = html_soup.find_all("a", href=True)
      for a in a_list:
        href = a["href"]
        absolute_url = urljoin(current_url, href)
        parsed_link = urlparse(absolute_url)

        clean_url = (
            f"{parsed_link.scheme}://{parsed_link.netloc}{parsed_link.path}"
        )

        if (
            parsed_link.netloc == domain
            and clean_url not in visited
            and clean_url not in queue
        ):
          queue.append(clean_url)

    except Exception as e:
      print(f"エラー発生 ({current_url}): {e}")

    time.sleep(1.0)

except KeyboardInterrupt:
  print("\n中断されました。ここまでのデータを保存します...")

# Save dictionary contents to a CSV file (now inside/after the try-except)
print(f"{len(url_title_dict)}件のデータを {csv_filename} に保存します...")

with open(csv_filename, mode="w", encoding="utf-8-sig", newline="") as f:
  writer = csv.writer(f)
  writer.writerow(["URL", "Title"])
  for u, t in url_title_dict.items():
    writer.writerow([u, t])

print("保存が完了しました！")