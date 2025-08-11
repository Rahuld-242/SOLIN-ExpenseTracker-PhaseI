# SOLIN — AI-Powered Expense Tracker (Phase 1)

SOLIN is a personal AI assistant focused on **expense tracking**, **budgeting**, and **clean CLI UX**.  
Phase 1 showcases SOLIN’s modular architecture and LLM-assisted categorization with a simple, reliable command-line flow.

> Phase 1 goal: a clean, documented, bug-fixed baseline to showcase AI-agent thinking without extra features or UI.

---

## ✨ Features (Phase 1)
- **Natural-language expense entry** (e.g., “Dinner at Domino’s yesterday — ₹450”)
- **AI-assisted categorization** into a fixed set of categories
- **CRUD for expenses**: add, edit, delete
- **Budgets tied to categories**: set, edit, delete; prevents unknown categories
- **Clear CLI prompts** with consistent SOLIN tone
- **Resilient storage** in `memory/` (ignored by Git; tracked using `.gitkeep`)
- **Modular structure** ready for future agents and UI

---

## 📁 Project Structure
```
SOLIN/
├─ core/                 # Task dispatching, session/state mgmt
├─ tools/                # Feature modules (e.g., expense tracker, web tools)
├─ utils/                # Helpers (prompts, formatting, file ops)
├─ memory/               # Runtime data (e.g., expenses.json) — gitignored
│  └─ .gitkeep
├─ main.py               # Entry point
├─ requirements.txt
├─ .gitignore
├─ LICENSE
└─ README.md
```

---

## ⚙️ Setup
1) **Clone & enter folder**
```bash
git clone https://github.com/<your-username>/SOLIN.git
cd SOLIN
```

2) **Create & activate venv**
```bash
python -m venv venv
# Mac/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```

3) **Install dependencies**
```bash
pip install -r requirements.txt
```
> Phase 1 minimal deps: `requests`, `spacy`, `ollama`.  
> If you use spaCy models, install one (example):  
> `python -m spacy download en_core_web_sm`
> SOLIN Phase 1 was tested with Ollama v0.3.11 or newer
> Check your version:
> `ollama --version`
> Install Ollama from: https://ollama.com/download
> After installation, pull the required LLaMA 3 model:
> `ollama pull llama3`

---

## 🚀 Run
```bash
python main.py
```

### Example Commands & Outputs

#### **Add an expense**
```
Add expense: Had breakfast at CCD yesterday for 180
```
Output:
```
✅ Expense added under category: Food & Dining
📊 Total in Food & Dining (this month): ₹ 180
💰 Total monthly spending: ₹ 180
```


#### **Show expenses**
You can pull a numbered list of expenses any time. This is also the first step before editing.

**All expenses (recent first)**
```
Show expenses
```
**By category**
```
Show expenses: Food & Dining
```
Example output:
```
Entries:
1. ₹180 | Breakfast at CCD | Food & Dining | 2025-08-10 08:30
2. ₹450 | Dinner at Domino's | Food & Dining | 2025-08-11 20:00
```
> ℹ️ **Note:** Date-range filtering (e.g., `Show expenses from 2025-08-01 to 2025-08-11`) is planned for **Phase 2**.


#### **Show budgets**
```
Show budgets
```
Output:
```
📊 Budgets:
- Food & Dining: ₹ 5000 (Remaining: ₹ 4820)
- Transport: ₹ 2000 (Remaining: ₹ 2000)
```

#### **Edit a budget**
```
Edit budget: Food & Dining to 4500
```
Output:
```
✏️ Budget for Food & Dining updated from ₹ 5000 to ₹ 4500
Remaining: ₹ 4320
```

#### **Edit an expense entry**
```
Edit expense #3: Change amount to 220
```
Output:
```
✏️ Expense ID 3 updated.
Old: "Breakfast at CCD" — ₹ 180
New: "Breakfast at CCD" — ₹ 220
```

#### **How editing works (important)**
When you choose to edit, SOLIN **first shows a numbered list** of entries (1, 2, 3, …).  
You then **pick an entry by its number**, choose the field to edit, and provide the new value.

**Step-by-step**
1. `Show expenses: Food & Dining` (or `Show expenses` for all)  
2. SOLIN prints the list, e.g.  
   ```
   Entries:
   1. ₹180 | Breakfast at CCD | Food & Dining | 2025-08-10 08:30
   2. ₹450 | Dinner at Domino's | Food & Dining | 2025-08-11 20:00
   ```
3. You enter: `Edit expense #2`  
4. Choose field: `amount` (valid: amount / description / date / time / category)  
5. Enter new value: `420`  
6. SOLIN confirms the update.

---

## 🧠 Data & Persistence
- Runtime files live in `memory/` (gitignored).  
- Keep `.gitkeep` so the folder appears in Git; do **not** commit `expenses.json`.

---

## 🧪 Quick Smoke Test (pre-release)
- Fresh clone → `pip install -r requirements.txt` → `python main.py`
- Add/edit/delete sample expenses
- Set/edit/delete a budget
- Show budgets list
- Show expenses (all / by category / by date range)
- Edit expense entries
- Try empty or missing `expenses.json` and confirm graceful handling

---

## 🗺️ Roadmap (Phase 2, not included here)
- GUI-based chat interface
- LangChain/LangGraph dynamic tool routing
- Invoice → expense parsing (images/PDFs → structured entries)
- Enhanced web search integration
- Analytics & visual summaries

---

## 📜 License
MIT License. See `LICENSE` for details.

---

## 🙌 Acknowledgements
- Thanks to open-source contributors and NLP tooling (spaCy, etc.).
