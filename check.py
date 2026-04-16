#!/usr/bin/env python3
from typing import Any, TypeAlias
import dataclasses
import datetime
import github
import logging
import pathlib
import re
import requests
import tempfile
import zoneinfo
import time
import random
from bs4 import BeautifulSoup

a = [['d', 'x', 'x', '|', '\x7f', '6', '#', '#', 'h', '~', 'e', 'z', 'i', '"', 'k', 'c', 'c', 'k', '`', 'i', '"', 'o', 'c', 'a'],
     ['E', 'Y', 'Y', ']', '^', '\x17', '\x02', '\x02', '_', 'B', 'J', '\x00', 'K', 'B', '_', 'X', '@', '\x03', 'L', '^', 'X', '^', '\x03', 'N', 'B', '@', '\x02', 'Y', '\x18', '\x02', 'L', '@', 'I', '\x00', '\x1b', '\x1d', '\x1d', '\x00', '^', 'H', '_', 'D', 'H', '^', '\x02', 'U', '\x1b', '\x1a', '\x1d', '\x00', 'U', '\x15', '\x1a', '\x1d', '\x00', '_', 'H', '^', 'B', 'X', '_', 'N', 'H', '\x00', 'Y', 'E', '_', 'H', 'L', 'I', '\x02', 'Y', 'I', '\x00', ']', '\x02', '\x14', '\x1d', '\x1c', '\x18', '\x1a', '\x1b', '\x02', ']', 'L', 'J', 'H', '\x02'],
     ['L', 'I', 'I', '\x05', 'P', 'V', '@', '\x05', 'Q', 'M', 'L', 'V', '\x05', 'Q', 'M', 'W', '@', 'D', 'A', '\x05', 'Q', 'J', '\x05', 'F', 'J', 'I', 'I', '@', 'F', 'Q', '\x05', 'V', 'J', 'H', '@', '\x05', 'K', '@', 'R', '\x05', 'Q', '@', 'V', 'Q', '\x05', 'G', 'L', 'J', 'V', '@', 'V', '\x05', 'C', 'J', 'W', '\x05', 'Q', 'M', '@', '\x05', 'G', 'J', 'D', 'W', 'A', 'V'],
     ['z', 'v', 'w', 'm', '|', 'w', 'm', '4', '}', 'p', 'j', 'i', 'v', 'j', 'p', 'm', 'p', 'v', 'w'],
     ['\x00', '"', '7', '$', '!', '!', ',', 'b', 'x', 'c', '}', 'm', 'e', '\x1a', '$', '#', ')', '"', ':', '>', 'm', '\x03', '\x19', 'm', '|', '}', 'c', '}', 'v', 'm', '\x1a', '$', '#', '{', 'y', 'v', 'm', '5', '{', 'y', 'v', 'm', '?', ';', 'w', '|', 'y', 't', 'c', '}', 'd', 'm', '\n', '(', '.', '&', '"', 'b', '\x7f', '}', '|', '}', '}', '|', '}', '|', 'm', '\x0b', '$', '?', '(', '+', '"', '5', 'b', '|', 'y', 't', 'c', '}'],
     ['I', 'U', 'U', 'Q', 'R', '\x1b', '\x0e', '\x0e', 'E', 'S', 'H', 'W', 'D', '\x0f', 'F', 'N', 'N', 'F', 'M', 'D', '\x0f', 'B', 'N', 'L', '\x0e', 'T', 'B', '\x1e', 'D', 'Y', 'Q', 'N', 'S', 'U', '\x1c', 'E', 'N', 'V', 'O', 'M', 'N', '@', 'E', '\x07', 'H', 'E', '\x1c'],
     ];

def obf(ar, k):
   return "".join(chr(ord(c) ^ k) for c in ar)


url_base = obf(a[1],45)
ignore_text = obf(a[2],37)
startpage=568
keywords = ["TUF GAMING X670E-PLUS BIOS", "TUF GAMING X670E-PLUS BETA BIOS"]
pages = set()
logger = logging.getLogger(__name__)


@dataclasses.dataclass
class BIOSRelease:
    date: datetime.date
    version: str
    title: str
    url: str
    description: str
    isRelease: bool
    filename: str


def get_link(url):
   match = re.search(r'/d/([^/]+)', url)
   if match:
      file_id = match.group(1)
      return obf(a[5],33) + file_id
   return url


def get_download_filename(url, fname):
   try:
      rsp = requests.head(url, allow_redirects=True)
      time.sleep(random.uniform(2, 5))
      cd = rsp.headers.get(obf(a3,25))
      if cd:
         filename_match = re.findall('filename="(.+)"', cd)
         if filename_match:
            filename = filename_match[0]
            return filename
   except:
      pass
   return fname


def fetch() -> list[BIOSRelease]:
    url = 'https://www.asus.com/support/api/product.asmx/GetPDBIOS?website=global&pdid=20974'
    rsp = requests.get(url, headers={'User-Agent': 'Mozilla'})
    assert rsp.status_code == 200, f'HTTP {rsp.status_code} {rsp.reason}\n{rsp.text}'
    body = rsp.json()
    assert body['Status'] == 'SUCCESS', rsp.text
    obj = body['Result']['Obj'][0]
    assert obj['Name'] == 'BIOS', rsp.text
    result = []
    for bios_file in obj['Files']:
        description = bios_file['Description'].strip('"').replace('<br/>', '\n')
        description = re.sub(r'\n*Before running the USB BIOS Flashback tool, please rename the BIOS file ?\(TX670EPL\.CAP\) using BIOSRenamer\.\n*', '', description)
        url_str = bios_file['DownloadUrl']['Global'].split('?', 1)[0]
        result.append(BIOSRelease(
            date=datetime.date.fromisoformat(bios_file['ReleaseDate'].replace('/', '-')),
            version=bios_file['Version'],
            title=bios_file['Title'],
            url=url_str,
            description=description,
            isRelease=(bios_file['IsRelease'] == '1'),
            filename=url_str.rsplit('/', 1)[-1],
        ))
    return result


def fetch2(page = None) -> list[BIOSRelease]:
   if page is None:
      page = startpage
   print("fetch " + str(page))
   result = []
   url = url_base + str(page)
   rsp = requests.get(url, headers={"User-Agent": obf(a[4],77)})
   if rsp.status_code != 200:
      return set()
   time.sleep(random.uniform(2, 5))

   global pages   
   if page not in pages:
      pages.add(page)
      save_pages(pages)

   soup = BeautifulSoup(rsp.text, "html.parser")
   tag_next = soup.find("link", rel="next")
   next_page = 0
   if tag_next:
      next_page = int(tag_next.get("href").replace(".html", "").replace(url_base,""))
   
   posts = soup.find_all("div", class_="lia-quilt-row-message-main")

   desc = []
   find_desc = False

   for i, post in enumerate(posts, 1):
      content = post.get_text(separator=" ", strip=True)
      content_lower = content.lower()
     
      if ignore_text.lower() in content_lower:
         continue # Ignored first entry

      if any(word.lower() in content_lower for word in keywords):
         div_main_content = post.find("div", class_="lia-quilt-column-message-main-content")
         div_column = div_main_content.find("div", class_="lia-quilt-column-alley")
         div_message_body = div_column.find("div", class_="lia-message-body")
         div_message_body_content = div_message_body.find("div", class_="lia-message-body-content")
         paragraphs = div_message_body_content.find_all("p");

         X670 = False
         for j, paragraph in enumerate(paragraphs, 1):
            p_content = paragraph.get_text(separator="\n", strip=True)           

            if any(series.upper() in p_content.upper() for series in ["X670 Series"]):
               # begin of X670 series of chipset, now try to find description lines:
               X670 = True
               find_desc = True
               continue
            elif any(noseries.upper() in p_content.upper() for noseries in ["X870 Series", "B850 Series", "B650 Series"]):
               # begin of different series of chipset - stop
               X670 = False
               find_desc = False
               continue
            elif any(name.upper() in p_content.upper() for name in ["ROG CROSSHAIR", "ROG STRIX", "TUF GAMING", "PROART"]):
               # we found an individual bios line - stop finding description lines.
               find_desc = False

            if find_desc:
               desc.append(p_content)
            elif any(word.upper() in p_content.upper() for word in keywords):
               p_content = p_content.replace("Download", "").strip()
               p_content = p_content.replace("\n", "")
               p_content = p_content.replace("\r", "")
               bios_info = p_content
               fname = ""
               download_link = paragraph.find("a", string=re.compile(r"Download", re.I))
               if download_link:
                  href = get_link(download_link.get("href"))
                  if obf(a[0],12) in href and "id=" in href:
                     file_id = href.split("id=")[-1]
                     if len(file_id) > 20:
                        fname = get_download_filename(href, bios_info.replace(" ", "-") + ".7z")
                     else:
                        continue
                  else:
                     continue
                  if not bios_info or len(bios_info) < 10:
                     continue

                  description = ""
                  for aLine in desc:
                     if len(description) > 0:
                        description += "<br/>"
                     description += aLine.replace("\n", "<br/>")

                  isRelease = any(s in bios_info.upper() for s in ["BETA", "TEST"]) == False

                  result.append(BIOSRelease(
                     date=datetime.date.today(),
                     version=bios_info[-4:],
                     title=bios_info,
                     url=href,
                     description=description,
                     isRelease=isRelease,
                     filename=fname,
                     ))
   if next_page > 0:
      nxtItems = fetch2(next_page)
      if len(nxtItems) > 0:
         for nxt in nxtItems:
            result.append(nxt)
   return result


def process(bios: BIOSRelease) -> None:
   with tempfile.TemporaryFile() as f:
      rsp = requests.get(url=bios.url, allow_redirects=True, stream=True,)
      if rsp.status_code != 200:
         logger.info('broken URL -> %s:', bios.url)
         return
      for chunk in rsp.iter_content(16*1024*1024):
         f.write(chunk)
      f.seek(0)
      europe_time = datetime.datetime.now(zoneinfo.ZoneInfo("Europe/Berlin")).time()
      tstamp = datetime.datetime.combine(bios.date, europe_time, tzinfo=zoneinfo.ZoneInfo("Europe/Berlin"))
      release = github.github_release_ensure(tag_name=bios.title.replace(' ', '_'),
                                             name=bios.title,
                                             timestamp=tstamp,)
      github.github_release_patch(release, body=bios.description)
      github.github_release_upload_asset(release, bios.filename, f) # (release, filename, file)


page_file = pathlib.Path('pages.txt')
state_file = pathlib.Path('state.txt')

def load_pages() -> set[int]:
   if page_file.exists():
      aSet = [int(i) for i in page_file.read_text(encoding="utf-8").splitlines()]
      return sorted(aSet, reverse=True)
   else:
      return set()


def save_pages(p: set[int]) -> None:
   p_str = set()
   for aInt in p:
      p_str.add(str(aInt))
   page_file.write_text(''.join(item+'\n' for item in sorted(p_str, reverse=True)), encoding="utf-8")


def load_state() -> set[str]:
    if state_file.exists():
        return set(state_file.read_text().rstrip('\n').split('\n'))
    else:
        return set()


def load_state() -> set[str]:
   if state_file.exists():
      aSet = set(state_file.read_text().rstrip('\n').split('\n'))
      aSet.discard("")
      return aSet
   else:
      return set()


def save_state(state: set[str]) -> None:
   state_file.write_text(''.join(item+'\n' for item in sorted(state)))


def main() -> None:
   logging.basicConfig(level=logging.DEBUG)
   logging.getLogger('urllib3').setLevel(logging.INFO)
   state = load_state()
   pages = load_pages()
   if len(pages) > 1:
      global startpage
      startpage = pages[1]

   BiosList = fetch()
   if len(BiosList) > 0:
      for bios in BiosList:
         if re.fullmatch(r'\d+', bios.version) and bios.title == '':
            bios.title = f'TUF GAMING X670E-PLUS BIOS {bios.version}'
         assert bios.title.strip(), bios
         if bios.isRelease == False:
            bios.title = bios.title + '_BETA'
         if bios.title in state:
            continue
         logger.info('processing %s', bios.title)
         process(bios)
         state.add(bios.title)
         save_state(state)
   BiosList = fetch2()
   if len(BiosList) > 0:
      for bios in BiosList:
         if bios == None:
            continue
         if bios.title in state:
            continue
         logger.info('processing %s:', bios.title)
         process(bios)
         state.add(bios.title)
         save_state(state)



if __name__ == '__main__':
    main()
