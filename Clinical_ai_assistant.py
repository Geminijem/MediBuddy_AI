# app.py
import streamlit as st
import json, os, io
from datetime import datetime
from fpdf import FPDF

# ----- Config -----
st.set_page_config(page_title="Clinical Study Assistant (Non-AI)", layout="wide")

DATA_DIR = "data"
PLANS_FILE = os.path.join(DATA_DIR, "plans.json")
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")

os.makedirs(DATA_DIR, exist_ok=True)

# ----- Helpers: load/save -----
def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ----- Helpers: PDF export -----
def text_to_pdf_bytes(title, items):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, ln=True)
    pdf.ln(4)
    pdf.set_font("Arial", size=12)
    for i, it in enumerate(items, 1):
        # simple wrap: write multi_cell
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"{i}.", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 7, str(it))
        pdf.ln(2)
    buff = io.BytesIO()
    pdf.output(buff)
    buff.seek(0)
    return buff.read()

# ----- Load data into session -----
if "plans" not in st.session_state:
    st.session_state.plans = load_json(PLANS_FILE)
if "notes" not in st.session_state:
    st.session_state.notes = load_json(NOTES_FILE)

# editing indices
if "plan_edit_index" not in st.session_state:
    st.session_state.plan_edit_index = None
if "note_edit_index" not in st.session_state:
    st.session_state.note_edit_index = None

# ----- Sidebar navigation -----
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["🏠 Dashboard", "📅 Study Planner", "📒 Notes / Vault", "⚙️ Settings"])

# ----- Dashboard -----
if page == "🏠 Dashboard":
    st.title("🩺 Clinical Study Assistant — Dashboard")
    st.markdown("**Quick actions**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("➕ Add Plan"):
            st.session_state.plan_edit_index = None
            st.experimental_set_query_params(page="planner")
            st.experimental_rerun()
    with c2:
        if st.button("📝 Add Note"):
            st.session_state.note_edit_index = None
            st.experimental_set_query_params(page="notes")
            st.experimental_rerun()
    with c3:
        if st.button("📥 Export All Data"):
            all_data = {"plans": st.session_state.plans, "notes": st.session_state.notes}
            st.download_button("Download JSON", json.dumps(all_data, indent=2), file_name="clinical_data_backup.json", mime="application/json")

    st.markdown("---")
    st.subheader("Today / Summary")
    st.write(f"Plans: **{len(st.session_state.plans)}** — Notes: **{len(st.session_state.notes)}**")
    if st.session_state.plans:
        st.markdown("**Next plan (most recent):**")
        st.info(st.session_state.plans[-1])
    else:
        st.info("No plans yet — add a plan from Study Planner.")

# ----- Study Planner -----
elif page == "📅 Study Planner":
    st.title("📅 Study Planner")
    st.markdown("Add daily study plans, edit or remove them. Export as JSON/TXT/PDF.")

    # Add or edit form
    with st.form("plan_form", clear_on_submit=False):
        st.subheader("➕ Add / Edit Plan")
        date_input = st.date_input("Date", value=datetime.today())
        time_input = st.time_input("Time (optional)", value=datetime.now().time())
        topic = st.text_input("Topic / Title")
        details = st.text_area("Details / Plan")
        submit = st.form_submit_button("Save Plan")

    if submit:
        entry = {
            "date": date_input.isoformat(),
            "time": time_input.strftime("%H:%M:%S") if time_input else "",
            "topic": topic.strip(),
            "details": details.strip(),
            "created_at": datetime.utcnow().isoformat()
        }
        if st.session_state.plan_edit_index is None:
            st.session_state.plans.append(entry)
            st.success("Plan added.")
        else:
            st.session_state.plans[st.session_state.plan_edit_index] = entry
            st.session_state.plan_edit_index = None
            st.success("Plan updated.")
        save_json(PLANS_FILE, st.session_state.plans)

    st.markdown("---")
    st.subheader("📂 Saved Plans")
    if st.session_state.plans:
        for idx, p in enumerate(st.session_state.plans):
            cols = st.columns((8, 1, 1))
            with cols[0]:
                st.markdown(f"**{idx+1}. {p.get('topic','(no title)')}** — {p.get('date')} {p.get('time')}")
                st.write(p.get("details"))
            with cols[1]:
                if st.button("✏️ Edit", key=f"edit_plan_{idx}"):
                    st.session_state.plan_edit_index = idx
                    # pre-fill by placing values and re-render: set query param to reload page
                    st.experimental_rerun()
            with cols[2]:
                if st.button("🗑️ Delete", key=f"del_plan_{idx}"):
                    st.session_state.plans.pop(idx)
                    save_json(PLANS_FILE, st.session_state.plans)
                    st.experimental_rerun()
        st.markdown("---")
        # Exports
        json_btn = st.download_button("Download Plans (JSON)", json.dumps(st.session_state.plans, indent=2), file_name="plans.json", mime="application/json")
        txt_content = "\n\n".join([f"{i+1}. {p.get('topic','')} ({p.get('date')})\n{p.get('details','')}" for i,p in enumerate(st.session_state.plans)])
        st.download_button("Download Plans (TXT)", txt_content, file_name="plans.txt", mime="text/plain")
        pdf_bytes = text_to_pdf_bytes("Study Plans", [f"{p.get('topic','')} - {p.get('date')} {p.get('time')}\n{p.get('details','')}" for p in st.session_state.plans])
        st.download_button("Download Plans (PDF)", pdf_bytes, file_name="plans.pdf", mime="application/pdf")
    else:
        st.info("No plans yet — add one above.")

# ----- Notes / Medical Vault -----
elif page == "📒 Notes / Vault":
    st.title("📒 Notes & Medical Vault")
    st.markdown("Store notes, mnemonics, exam tips. Edit/delete and export easily.")

    # Create / Edit note
    with st.form("note_form", clear_on_submit=False):
        st.subheader("➕ Add / Edit Note")
        note_title = st.text_input("Title", value=(st.session_state.notes[st.session_state.note_edit_index].get("title") if st.session_state.note_edit_index is not None and st.session_state.note_edit_index < len(st.session_state.notes) else ""))
        note_body = st.text_area("Note", value=(st.session_state.notes[st.session_state.note_edit_index].get("body") if st.session_state.note_edit_index is not None and st.session_state.note_edit_index < len(st.session_state.notes) else ""), height=200)
        note_tags = st.text_input("Tags (comma separated)", value=(",".join(st.session_state.notes[st.session_state.note_edit_index].get("tags",[])) if st.session_state.note_edit_index is not None and st.session_state.note_edit_index < len(st.session_state.notes) else ""))
        save_note = st.form_submit_button("Save Note")
        cancel = st.form_submit_button("Cancel")

    if save_note:
        note_entry = {
            "title": note_title.strip(),
            "body": note_body.strip(),
            "tags": [t.strip() for t in note_tags.split(",") if t.strip()],
            "updated_at": datetime.utcnow().isoformat()
        }
        if st.session_state.note_edit_index is None:
            st.session_state.notes.append(note_entry)
            st.success("Note saved.")
        else:
            st.session_state.notes[st.session_state.note_edit_index] = note_entry
            st.session_state.note_edit_index = None
            st.success("Note updated.")
        save_json(NOTES_FILE, st.session_state.notes)

    if cancel:
        st.session_state.note_edit_index = None
        st.experimental_rerun()

    st.markdown("---")
    st.subheader("📂 Saved Notes")
    if st.session_state.notes:
        for idx, n in enumerate(st.session_state.notes):
            left, right = st.columns([9,1])
            with left:
                st.markdown(f"**{idx+1}. {n.get('title','(no title)')}**  — _tags: {', '.join(n.get('tags',[]))}_")
                st.write(n.get("body",""))
            with right:
                if st.button("✏️", key=f"edit_note_{idx}"):
                    st.session_state.note_edit_index = idx
                    st.experimental_rerun()
                if st.button("🗑️", key=f"del_note_{idx}"):
                    st.session_state.notes.pop(idx)
                    save_json(NOTES_FILE, st.session_state.notes)
                    st.experimental_rerun()
        st.markdown("---")
        # Exports for notes
        st.download_button("Download Notes (JSON)", json.dumps(st.session_state.notes, indent=2), file_name="notes.json", mime="application/json")
        notes_txt = "\n\n".join([f"{i+1}. {n.get('title','')}\n{n.get('body','')}" for i,n in enumerate(st.session_state.notes)])
        st.download_button("Download Notes (TXT)", notes_txt, file_name="notes.txt", mime="text/plain")
        pdf_notes = text_to_pdf_bytes("Notes & Vault", [f"{n.get('title','')}\n{n.get('body','')}" for n in st.session_state.notes])
        st.download_button("Download Notes (PDF)", pdf_notes, file_name="notes.pdf", mime="application/pdf")
    else:
        st.info("No notes yet. Use the form above to create one.")

# ----- Settings -----
elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    st.markdown("Data files are stored locally in the app's `data/` folder.")
    if st.button("Reset all data (delete plans & notes)"):
        if st.confirm("Are you sure? This will permanently delete saved notes & plans."):
            st.session_state.plans = []
            st.session_state.notes = []
            save_json(PLANS_FILE, st.session_state.plans)
            save_json(NOTES_FILE, st.session_state.notes)
            st.success("All data removed.")
