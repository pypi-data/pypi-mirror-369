# Bollinger Bands

> Originiallly Developed by [Raj Adhikari
> ](https://github.com/r-adhikari97)


A **Financial indicator** based on ratios calculated via financial engine over a specfic or acorss a range of companies.

Returns sma, lower band, and upper band for a range of provided ratio columns

---

## 📦 Changelog

See full [CHANGELOG.md](https://github.com/r-adhikari97/financial-engine/blob/main/CHANGELOG.md)

---

## 📝 Notes

Financial ratios calculations are perfomed on all dates and then filtered by Bollinger bands on basis of window_size,- Allows Storing all financial ratios (if ratios_to_file parameter is set to True)

- More Analysis and calculations can be performed now that all ratios data is saved to a feather file as well
- Final outcome : feather file for ratios and / or bollinger + returning the same for models
- Further down can implement Caching mechanism to  manage all records in better manner and make them readily available for Bollinger bands or other calculations

---

## ✨ Features

- 📈 Built on top of financial-engine
- 🔁 Perform bollinger bands caluclation for provided ratio columns
- 🚗 Accepts Single company (alpha_code) as well as Multiple Companies (list of alpha_codes)
- ⚡ Caching : Option to save ratios and bollingers for further calculations

---

## 🚀 Installation

```bash
pip install financial-bollinger-bands
```

### Step-by-step

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```
2. Create a `.env` file in the root of your project:

   ```dotenv
   MONGO_URI=
   MONGO_DATABASE=
   MONGO_COLLECTION=
   AWS_ACCESS_KEY_ID=
   AWS_SECRET_ACCESS_KEY=
   BUCKET_NAME=
   ```
3. Install the package:

   ```bash
   pip install financial-bollinger-bands
   ```

---

## 🐍 Requirements

- Python ≥ 3.10
- Compatible with major OS environments (Linux, Windows, Mac)

---

## 🛠 Implemented Methods

| Method                                                                                           | Descrip`tion                                  |
| ------------------------------------------------------------------------------------------------ | --------------------------------------------- |
| `get_bollinger_bands( alpha_code , k , windows_size, bollinger_to_file, ratio_to_file )`       | Get bolllinger band for specific alpha_code   |
| `get_bollinger_bands_multiple( alpha_code, k, window_size, bollinger_to_file, ratio_to_file )` | Get bollinger band for a range of alpha_codes |

---
