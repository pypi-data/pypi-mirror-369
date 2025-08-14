# HL Gaming Official FF Data API (hl-gaming-official-ff-data)

[![PyPI Version](https://img.shields.io/pypi/v/hl-gaming-official-ff-data.svg)](https://pypi.org/project/hl-gaming-official-ff-data/) 
[![Downloads](https://img.shields.io/pypi/dm/hl-gaming-official-ff-data.svg)](https://pypi.org/project/hl-gaming-official-ff-data/)

Official Python client for [HL Gaming Official's Free Fire API](https://www.hlgamingofficial.com/p/api.html)  
Easily fetch player data from Free Fire using your API key.

---

## 📦 Installation

```bash
pip install hl-gaming-official-ff-data
```

---

## 🚀 Usage Example

```python
from hl_gaming_official_ff_data import HLFFClient

api_key = "your-api-key"
player_uid = "9351564274"
user_uid = "your-user-uid"
region = "pk"

client = HLFFClient(api_key=api_key, region=region)
try:
    data = client.get_player_data(player_uid=player_uid, user_uid=user_uid)
    print("✅ Player Data:", data)
except Exception as e:
    print("❌ Error:", e)
```

---

## ❗ Error Handling & Tips

- ✅ Make sure `api_key`, `player_uid`, and `user_uid` are correct.
- ⚠️ Region must be a valid code like `pk`, `in`, etc.
- ❌ If the API returns a 403 or 400 error, check your parameters or visit [API Docs](https://www.hlgamingofficial.com/p/free-fire-api-data-documentation.html)

---

## 📄 Documentation

- 📘 [API Docs](https://www.hlgamingofficial.com/p/free-fire-api-data-documentation.html)
- 🌐 [Main Website](https://www.hlgamingofficial.com)

---


## 📝 Changelog

### Version 2.3.4
- Updated package name and branding  
- Added better error handling and user guidance  
- Improved documentation and examples  

---

## 👨‍💻 Developed by Haroon Brokha

📧 Contact: [developers@hlgamingofficial.com](mailto:developers@hlgamingofficial.com)  
🌐 Project maintained for the HL Gaming Official Community

---

*This README is automatically generated and maintained.*
