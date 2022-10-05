from sys import stdout
import requests, re, platform, subprocess
from Crypto.Cipher import AES
from tqdm import tqdm
from cookie import Cookie
from ua import UserAgent

HTTPS = "https://"
HOST = "ani.gamer.com.tw"

COOKIE_FILENAME = "config/cookies.txt"
UA_FILENAME = "config/user_agent.txt"
BASH_FILENAME = "temp/composing.sh"
KEY_FILENAME = "temp/key.m3u8key"

TEMP_DEST = "temp/"
DOWNLOAD_DEST = "download/"


class Anime:

    _sn: int
    _cookies: dict
    _headers: dict
    _device_id: str
    _playlist_url: str
    _playlist: dict
    _ffmpeg_path: str

    def __init__(self, sn: int) -> None:
        self._sn = sn
        self._cookies = Cookie(COOKIE_FILENAME).get_cookie()
        self._headers = {"user-agent": UserAgent(UA_FILENAME).get_user_agent()}
        self._device_id = self._get_device_id()
        self._playlist_url = self._get_playlist_url()
        self._playlist = self._get_playlist()
        self._ffmpeg_path = self._get_ffmpeg_path()

    def __requests(self, url: str, addi_headers: dict = {}, no_origin_header: bool = True, no_cookie: bool = False) -> requests.Response:
        headers = self._headers.copy()
        if not no_origin_header:
            headers["origin"] = HTTPS + HOST
        for k, v in addi_headers.items():
            headers[k] = v
        tyied_time = 0
        while True:
            try:
                return requests.get(url, headers= headers, cookies= {} if no_cookie else self._cookies)
            except:
                tyied_time += 1
                if tyied_time >= 3:
                    raise Exception("未知連線錯誤")

    def _get_device_id(self) -> str:
        res = self.__requests(HTTPS + HOST + "/ajax/getdeviceid.php")
        return res.json()["deviceid"]

    def _get_playlist_url(self) -> str:
        res = self.__requests(HTTPS + HOST + "/ajax/m3u8.php?sn=" + str(self._sn) + "&device=" + self._device_id)
        return res.json()["src"]

    def _get_playlist(self) -> dict:
        res = self.__requests(self._playlist_url, no_origin_header= False)
        url_prefix = re.sub(r"playlist.+", "", self._playlist_url) # 切掉後面很亂的東西
        m3u8_list = re.findall(r"\d*p.+", res.content.decode()) # findall 360p...\n 720p...\n 1080p...\n
        m3u8_dict = {}
        for s in m3u8_list:
            key = re.search(r"\d*p", s).group() # 將解析度當作 key
            key = key[:len(key) - 1]
            value = url_prefix + s
            m3u8_dict[int(key)] = value
        return m3u8_dict

    def _get_ffmpeg_path(self) -> str:
        return "ffmpeg.exe" if "windows" in platform.system().lower() else "ffmpeg"

    def download(self, dest: str = "", resolution: int = 1080) -> None:
        if resolution not in self._playlist.keys():
            raise Exception("無法下載 {resolution}p 的影片")
        
        res = self.__requests(self._playlist[resolution], no_origin_header= False)
        m3u8_content = res.content.decode()
        url_prefix = re.sub(r"chunklist.+", "", self._playlist[resolution])
        
        # 儲存 m3u8key
        m3u8_keyfile = re.search(r"(?<=AES-128,URI=\")(.*)(?=\")", m3u8_content).group()
        open(KEY_FILENAME, "wb").write(self.__requests(url_prefix + m3u8_keyfile, no_origin_header= False, no_cookie= True).content)
        

        # 儲存分段 ts 檔
        chunk_list = re.findall(r".*.ts", m3u8_content)
        for filename in tqdm(chunk_list):
            open(TEMP_DEST + filename, "wb").write(self.__requests(url_prefix + filename, no_origin_header= False, no_cookie= True).content)

        # AES-128 解密
        aes_key = open(KEY_FILENAME, "rb").read()
        for filename in chunk_list:
            with open(TEMP_DEST + filename, "rb") as file:
                data = file.read()
            cipher = AES.new(bytes(aes_key), AES.MODE_CBC)
            with open(TEMP_DEST + filename, "wb") as file:
                file.write(cipher.decrypt(data))

        # 合併 ts 檔
        bash_file = open(BASH_FILENAME, "w")
        bash_file.write("#!/bin/bash\ncat ")
        for filename in chunk_list:
            bash_file.write(TEMP_DEST + filename + " ")
        bash_file.write("> " + TEMP_DEST + "media.ts\nmv " + TEMP_DEST + "media.ts " + DOWNLOAD_DEST + str(self._sn) + ".ts\n")
        bash_file.write("rm " + TEMP_DEST + "*.ts\n")
        bash_file.close()
        subprocess.run(["chmod", "+x", BASH_FILENAME])
        subprocess.run([BASH_FILENAME], shell= True)