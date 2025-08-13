# 🛹 Skate 3 Recipe File Library

This library provides tools to **serialize and deserialize Skate 3 Recipes**, which the game uses to define and construct skater data. These files contain everything needed to recreate a skater, from appearance to gear.

Whether you're analyzing skater data or building your own skater profiles, this library gives you full control over the binary format used by Skate 3.

---

## 📦 Features

- 🔍 **Read** and parse recipe bytes into usable structured data.
- ✍️ **serialize** the recipe back into bytes for easy injection or saving.
- ⚙️ Supports known structure fields (appearance, gear, etc.)
- 🧪 Designed for modding, analysis, and custom content pipelines.

---

## Credits

- S4M (Lead Developer)
- Wispp (Original C# Code and reversing Skates recipe format)

## 🧰 Installation

```bash
pip install S3RecipeHandler
```