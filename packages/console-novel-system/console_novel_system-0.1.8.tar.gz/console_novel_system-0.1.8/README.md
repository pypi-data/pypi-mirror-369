CNS - Console/Text Novel System

A system to help create "visual novels", but run in the console. So more console/text-based rather than visual. 
Or you could call them "interactive novels".

---

**IMPORTANT NOTE**

Upon first installing **or updating** `console-novel-system`, the first function(s) you run will tell you that your current installed version does not match any of the available listed versions on PyPI! Do not be afraid, this is only because **it takes time for it to scan for new versions on PyPI**! This is why that message will pop-up! (Or it might not happen because chances are it's just because when I tested it, I had *just* released the new version and so it didn't know the version existed yet...)

---

**Requires** `requests`, `packaging`, and `colorama`

`cmd` > `pip install colorama requests packaging`

---

**Package name:** console_novel_system

**Install with:** `pip install console-novel-system`

**Update with:** `pip install --upgrade console-novel-system`

**Use with:** `import cns`

---

To get started, run `cns.intro()`.

To check your current version, use `cns.version()`. This will also tell you if you 1. need to update, 2. are using a yanked version, or 3. using an unknown or fake version.

All functions will secretly check the version, in case you need to change versions.

To view the license, please use `cns.license()`.

---

**Created by:** Error Dev **|** [https://devicals.github.io/](https://devicals.github.io/)