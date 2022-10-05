# AniGamerDownloader

## 使用須知

- 目前僅支援 Unix-like 環境
- 目前未處理非 VIP 用戶
- 目前未登入 Cookies 無法使用

**所以，還是先乖乖克金吧！**

## 安裝

下載源碼：
```
git clone https://github.com/an920107/AniGamerDownloader.git
```
安裝依賴：
```
cd AniGamerDownloader
pip3 install -r requirements.txt
```

## Cookies 與 User-Agent

*好懶，心情好再寫。*

## 使用說明

於 main.py 中導入 Anime 類別
```python
from anime import Anime
```
將動畫瘋 sn 碼傳入 Anime 建構子
```python
anime = Anime(sn碼)
```
使用成員函數 download() 開始下載作業
```python
anime.download()
```
亦可傳入指定畫質
```python
anime.download(resolution= 1080)
```
