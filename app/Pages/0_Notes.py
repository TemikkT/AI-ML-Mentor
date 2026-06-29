import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import re
import base64

from app.bootstrap import get_loader
from app.ui.theme import apply_glass_theme, glass_card_open, glass_card_close, glass_divider

st.set_page_config(page_title="Лекции", layout="wide")
apply_glass_theme()
st.title("Лекции")

loader = get_loader()
notes = loader.load_notes()

if "selected_note" not in st.session_state:
    st.session_state.selected_note = None

# Группируем по категориям
categories = {}
for note in notes:
    categories.setdefault(note.category, []).append(note)

sorted_cats = sorted(categories.items(), key=lambda x: x[0])

col_left, col_right = st.columns([1, 2.5])

with col_left:
    st.subheader("Категории")
    for cat, cat_notes in sorted_cats:
        with st.expander(cat, expanded=True):
            for n in cat_notes:
                active = st.session_state.selected_note and st.session_state.selected_note.title == n.title
                if st.button(
                    n.title,
                    key=f"note_{n.title}",
                    type="primary" if active else "secondary",
                    use_container_width=True,
                ):
                    st.session_state.selected_note = n
                    st.rerun()

with col_right:
    note = st.session_state.selected_note
    if note is None:
        st.info("Выбери лекцию из списка слева.")
    else:
        glass_card_open(note.category)
        st.subheader(note.title)
        glass_card_close()

        @st.cache_data
        def resolve_image(img_name: str) -> str:
            path = loader.find_image_path(img_name)
            if not path:
                return ""
            try:
                with open(path, "rb") as f:
                    data = f.read()
                ext = Path(path).suffix.lower()
                mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                        "gif": "image/gif", "svg": "image/svg+xml", "webp": "image/webp"}
                mime_type = mime.get(ext.lstrip("."), "image/png")
                return f"data:{mime_type};base64,{base64.b64encode(data).decode()}"
            except Exception:
                return ""

        def render_obsidian_md(content: str) -> str:
            lines = content.split("\n")
            out = []
            in_code = False

            for line in lines:
                stripped = line.strip()

                if stripped.startswith("```"):
                    in_code = not in_code
                    out.append(line)
                    continue

                if in_code:
                    out.append(line)
                    continue

                def replace_image(m):
                    name = m.group(1).split("|")[0].strip()
                    src = resolve_image(name)
                    if src:
                        return f'<img src="{src}" alt="{name}" style="max-width:100%;border-radius:8px;border:1px solid rgba(98,104,128,0.35);margin:0.5rem 0;" />'
                    return f'*[изображение: {name}]*'

                line = re.sub(r'!\[\[([^\]]+)\]\]', replace_image, line)
                line = re.sub(r'\[\[([^\]]+)\]\]', r'\1', line)
                line = re.sub(r'==([^=]+)==', r'<mark style="background:rgba(140,170,238,0.2);color:#c6d0f5;padding:0 0.2em;border-radius:3px;">\1</mark>', line)

                out.append(line)

            return "\n".join(out)

        rendered = render_obsidian_md(note.raw_content)
        st.markdown(rendered, unsafe_allow_html=True)