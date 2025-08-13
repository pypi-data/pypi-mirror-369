# shrt62

`shrt62` is a lightweight Python utility for generating short, unique IDs using hashing and Base62 encoding.
Perfect for use cases like URL shorteners, link tracking, database keys, or anywhere you need compact and unique identifiers.

---

## **Features**

* 🔑 Generates short, unique Base62-encoded IDs
* ⚡ Fast and lightweight, no heavy dependencies
* 🛠 Simple API with minimal setup
* 🌐 IDs are URL-friendly and safe to use in links

---

## **Installation**

```bash
pip install shrt62
```

---

## **Usage**

```python
from shrt62 import Generator

unique_id = Generator.generate()
print(f"Generated unique ID: {unique_id}")

for i in range(5):
    print(Generator.generate(6))
```

**Example Output:**

```
Generated unique ID: z8V2j3Q
Pq9mLk
Xh2T5a
1jZmQe
Lp3nHq
M4n7kL
```

---

## **API**

### `Generator.generate(length: int = 9)`

Generates a unique Base62-encoded ID.
**Parameters:**

* `length` *(optional)* — length of the ID. Default is `9`.

**Returns:**

```python
str  # A short, unique, URL-safe ID
```

---

## **License**

This project is licensed under the MIT License.