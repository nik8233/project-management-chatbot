# import streamlit as st
# import pandas as pd
# import sqlite3, re, random, os
# from datetime import date, datetime, timedelta

# st.set_page_config(page_title="Project Copilot — Tracker v3", layout="wide")
# st.title("📈 Project Copilot — Tracker (v3)")

# DB_PATH = "projects.db"
# CSV_PATH = "projects_seed.csv"
# TODAY = date.today()

# # ---------- Utils ----------
# def parse_money(x):
#     if x is None or (isinstance(x,float) and pd.isna(x)): return 0.0
#     s = str(x).strip().replace(",", "")
#     try: return float(s)
#     except: return 0.0

# def parse_pct(x):
#     if x is None or (isinstance(x,float) and pd.isna(x)): return 0.0
#     s = str(x).strip().replace("%","")
#     try: return float(s)
#     except: return 0.0

# def parse_date(x):
#     if not x or (isinstance(x,float) and pd.isna(x)): return None
#     s = str(x).strip()
#     for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%d-%b-%Y", "%b %d, %Y"):
#         try: return datetime.strptime(s, fmt).date().isoformat()
#         except: pass
#     try:
#         return pd.to_datetime(s, errors="coerce").date().isoformat()
#     except:
#         return None

# def bucket_for_date(end_date: str):
#     if not end_date: return "—"
#     try: d = datetime.fromisoformat(str(end_date)).date()
#     except: return "—"
#     delta = (d - TODAY).days
#     if delta < 0: return "Overdue"
#     if delta == 0: return "Today"
#     if delta == 1: return "Tomorrow"
#     if delta <= 7: return "Next 7 days"
#     if delta <= 30: return "Next 30 days"
#     return "Later"

# def money(n):
#     try: return f"₹{int(float(n)):,}"
#     except: return "—"

# # ---------- DB ----------
# def get_conn():
#     conn = sqlite3.connect(DB_PATH)
#     conn.execute("PRAGMA foreign_keys = ON;")
#     return conn

# def init_db(modernize=False):
#     conn = get_conn()
#     cur = conn.cursor()
#     cur.execute("""CREATE TABLE IF NOT EXISTS projects (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         name TEXT UNIQUE,
#         status TEXT,
#         phase TEXT,
#         completion REAL,
#         manager TEXT,
#         department TEXT,
#         region TEXT,
#         type TEXT,
#         cost REAL,
#         benefit REAL,
#         start_date TEXT,
#         end_date TEXT,
#         complexity TEXT,
#         description TEXT,
#         archived INTEGER DEFAULT 0
#     )""")
#     cur.execute("""CREATE TABLE IF NOT EXISTS announcements(
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         created_at TEXT,
#         title TEXT,
#         body TEXT
#     )""")
#     conn.commit()

#     # Seed if empty
#     cur.execute("SELECT COUNT(*) FROM projects")
#     if cur.fetchone()[0]==0:
#         df = pd.read_csv(CSV_PATH)
#         df.columns = [c.strip() for c in df.columns]

#         # Column mapping guess (supports your CSV headers)
#         name_col = "Project Name"
#         status_col = "Status"
#         phase_col = "Phase"
#         completion_col = "Completion%"
#         manager_col = "Project Manager"
#         dept_col = "Department"
#         region_col = "Region"
#         type_col = "Project Type"
#         cost_col = "Project Cost" if "Project Cost" in df.columns else " Project Cost "
#         benefit_col = "Project Benefit" if "Project Benefit" in df.columns else " Project Benefit "
#         start_col = "Start Date" if "Start Date" in df.columns else ("OriginalStartDate" if "OriginalStartDate" in df.columns else None)
#         end_col = "End Date" if "End Date" in df.columns else ("OriginalEndDate" if "OriginalEndDate" in df.columns else None)
#         comp_col = "Complexity" if "Complexity" in df.columns else None
#         desc_col = "Project Description" if "Project Description" in df.columns else None

#         recs = []
#         base = TODAY
#         for _, r in df.iterrows():
#             start = parse_date(r.get(start_col)) if start_col else None
#             end = parse_date(r.get(end_col)) if end_col else None

#             if modernize:
#                 # Shift around today: random offsets
#                 dur = ( (datetime.fromisoformat(end).date() - datetime.fromisoformat(start).date()).days if start and end else random.randint(30, 180) )
#                 start = (base - timedelta(days=random.randint(0,60))).isoformat()
#                 end = (datetime.fromisoformat(start) + timedelta(days=dur)).date().isoformat()

#             recs.append((
#                 r.get(name_col),
#                 r.get(status_col),
#                 r.get(phase_col),
#                 parse_pct(r.get(completion_col)),
#                 r.get(manager_col),
#                 r.get(dept_col),
#                 r.get(region_col),
#                 r.get(type_col),
#                 parse_money(r.get(cost_col)),
#                 parse_money(r.get(benefit_col)),
#                 start,
#                 end,
#                 r.get(comp_col) if comp_col else None,
#                 r.get(desc_col) if desc_col else None,
#             ))
#         cur.executemany("""INSERT OR IGNORE INTO projects
#             (name,status,phase,completion,manager,department,region,type,cost,benefit,start_date,end_date,complexity,description)
#             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", recs)
#         conn.commit()
#     conn.close()

# def df_projects(include_archived=False):
#     conn = get_conn()
#     q = "SELECT * FROM projects" + ("" if include_archived else " WHERE archived=0")
#     df = pd.read_sql_query(q, conn)
#     conn.close()
#     return df

# def upsert_project(row):
#     conn = get_conn()
#     cur = conn.cursor()
#     if row.get("id"):
#         cur.execute("""UPDATE projects SET
#             name=?, status=?, phase=?, completion=?, manager=?, department=?, region=?, type=?,
#             cost=?, benefit=?, start_date=?, end_date=?, complexity=?, description=? WHERE id=?""",
#             (row["name"], row["status"], row["phase"], float(row["completion"] or 0),
#              row["manager"], row["department"], row["region"], row["type"],
#              float(row["cost"] or 0), float(row["benefit"] or 0), row["start_date"], row["end_date"],
#              row["complexity"], row["description"], int(row["id"])))
#     else:
#         cur.execute("""INSERT INTO projects
#             (name,status,phase,completion,manager,department,region,type,cost,benefit,start_date,end_date,complexity,description)
#             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
#             (row["name"], row["status"], row["phase"], float(row["completion"] or 0),
#              row["manager"], row["department"], row["region"], row["type"],
#              float(row["cost"] or 0), float(row["benefit"] or 0), row["start_date"], row["end_date"],
#              row["complexity"], row["description"]))
#     conn.commit()
#     conn.close()

# def post_announcement(title, body):
#     conn = get_conn()
#     cur = conn.cursor()
#     cur.execute("INSERT INTO announcements (created_at,title,body) VALUES (?,?,?)",
#                 (datetime.now().strftime("%Y-%m-%d %H:%M"), title, body))
#     conn.commit()
#     conn.close()

# def df_announcements():
#     conn = get_conn()
#     df = pd.read_sql_query("SELECT * FROM announcements ORDER BY id DESC", conn)
#     conn.close()
#     return df

# # ---------- First run controls ----------
# with st.sidebar:
#     st.subheader("First‑run options")
#     modernize = st.checkbox("Modernize dates (shift around today) on first seed", value=True)
#     if st.button("Initialize database"):
#         if os.path.exists(DB_PATH):
#             os.remove(DB_PATH)
#         init_db(modernize=modernize)
#         st.success("Database initialized ✅. Reload the page.")

# # Always ensure DB exists
# if not os.path.exists(DB_PATH):
#     init_db(modernize=True)

# # ---------- Tabs ----------
# tab_proj, tab_alerts, tab_visuals, tab_chat, tab_ann = st.tabs(["🗂 Projects","⏰ Alerts","📊 Visuals","💬 Chat","📣 Announcements"])

# # ---------- Projects (CRUD) ----------
# with tab_proj:
#     st.subheader("Add / Edit Project")
#     with st.form("new_project"):
#         c1, c2, c3 = st.columns(3)
#         with c1:
#             name = st.text_input("Project Name*")
#             status = st.selectbox("Status", ["In - Progress","On - Hold","Completed","Cancelled"])
#             phase = st.selectbox("Phase", ["Phase 1 - Explore","Phase 2 - Plan","Phase 3 - Design","Phase 4 - Implement","Phase 5 - Close"])
#             completion = st.slider("Completion %", 0, 100, 0)
#         with c2:
#             manager = st.text_input("Project Manager")
#             department = st.text_input("Department")
#             region = st.text_input("Region")
#             ptype = st.text_input("Project Type")
#         with c3:
#             cost = st.number_input("Project Cost", min_value=0, value=0, step=1000)
#             benefit = st.number_input("Project Benefit", min_value=0, value=0, step=1000)
#             start_date = st.date_input("Start Date", value=TODAY)
#             end_date = st.date_input("End Date", value=TODAY + timedelta(days=30))
#         desc = st.text_area("Project Description")
#         complexity = st.selectbox("Complexity", ["Low","Medium","High"])
#         submitted = st.form_submit_button("Create Project")
#         if submitted:
#             if not name.strip():
#                 st.error("Name is required.")
#             else:
#                 row = dict(name=name.strip(), status=status, phase=phase, completion=completion,
#                            manager=manager, department=department, region=region, type=ptype,
#                            cost=cost, benefit=benefit, start_date=str(start_date), end_date=str(end_date),
#                            complexity=complexity, description=desc)
#                 upsert_project(row)
#                 st.success("Project created 🎉")

#     st.markdown("---")
#     st.subheader("Inline Edit")
#     df = df_projects()
#     if len(df)==0:
#         st.info("No projects yet. Use the form above to add one.")
#     else:
#         show = df.copy()
#         show["deadline_bucket"] = show["end_date"].apply(bucket_for_date)
#         show = show[["id","name","status","phase","completion","manager","department","region","type","cost","benefit","start_date","end_date","complexity","deadline_bucket","description"]]
#         edited = st.data_editor(show, num_rows="dynamic", use_container_width=True, key="editor")
#         if st.button("Save changes"):
#             for _, r in edited.iterrows():
#                 upsert_project({
#                     "id": int(r["id"]),
#                     "name": r["name"],
#                     "status": r["status"],
#                     "phase": r["phase"],
#                     "completion": r["completion"],
#                     "manager": r["manager"],
#                     "department": r["department"],
#                     "region": r["region"],
#                     "type": r["type"],
#                     "cost": r["cost"],
#                     "benefit": r["benefit"],
#                     "start_date": r["start_date"],
#                     "end_date": r["end_date"],
#                     "complexity": r["complexity"],
#                     "description": r["description"],
#                 })
#             st.success("Saved ✅")

# # ---------- Alerts ----------
# with tab_alerts:
#     st.subheader("Due‑date Alerts")
#     df = df_projects()
#     if len(df)==0:
#         st.info("No projects to analyze yet.")
#     else:
#         df["deadline_bucket"] = df["end_date"].apply(bucket_for_date)
#         buckets = ["Overdue","Today","Tomorrow","Next 7 days","Next 30 days"]
#         cols = st.columns(len(buckets))
#         for i,b in enumerate(buckets):
#             with cols[i]:
#                 st.metric(b, int((df["deadline_bucket"]==b).sum()))

#         st.markdown("#### Details")
#         choice = st.selectbox("Which bucket?", buckets, index=0)
#         view = df[df["deadline_bucket"]==choice]
#         st.dataframe(view[["name","status","manager","completion","end_date","deadline_bucket","department","region"]], use_container_width=True)

#         digest = "\n".join([
#             f"- {r['name']} — {r['status']} | PM {r['manager']} | {int(r['completion'] or 0)}% | due {r['end_date']} ({r['deadline_bucket']})"
#             for _, r in view.iterrows()
#         ]) or "No items."
#         if st.button("Post digest to Announcements"):
#             post_announcement(f"[ALERT] {choice} — {len(view)} project(s)", digest)
#             st.success("Digest posted 📣")
#         st.text_area("Digest preview", value=digest, height=150)


# # ---------- Visuals ----------
# with tab_visuals:
#     st.subheader("Portfolio Visuals")
#     df = df_projects()
#     if len(df)==0:
#         st.info("No data yet.")
#     else:
#         df["deadline_bucket"] = df["end_date"].apply(bucket_for_date)  # <-- FIX ensures column exists
#         c1,c2,c3 = st.columns(3)
#         with c1: st.metric("Total", len(df))
#         with c2: st.metric("Active", int(df["status"].isin(["In - Progress","On - Hold"]).sum()))
#         with c3: st.metric("Overdue", int(df["deadline_bucket"].eq("Overdue").sum()))

#         st.markdown("### By Status")
#         st.bar_chart(df["status"].value_counts())

#         st.markdown("### Completion % (buckets)")
#         bins = pd.cut(df["completion"], bins=[0,25,50,75,100], include_lowest=True).astype(str)
#         st.bar_chart(bins.value_counts())

#         st.markdown("### Cost vs Benefit (bubble ~ completion)")
#         plot_df = df.copy()
#         plot_df["size"] = plot_df["completion"].fillna(0) + 5
#         st.scatter_chart(plot_df, x="cost", y="benefit", size="size", color="status")

#         st.markdown("### Deadline Buckets")
#         st.bar_chart(df["deadline_bucket"].value_counts())

# # ---------- Announcements ----------
# with tab_ann:
#     st.subheader("Announcements")
#     ann = df_announcements()
#     if len(ann)==0:
#         st.caption("Nothing posted yet. Use Alerts to post a digest.")
#     else:
#         for _, row in ann.iterrows():
#             st.markdown(f"**{row['title']}** — _{row['created_at']}_  \n{row['body']}")
#             st.divider()

# # ---------- Chat (NLU, cheerful tone) ----------
# def say(text): return "✨ " + text

# STATUS_SYNS = {
#     "In - Progress": ["in progress","in-progress","ongoing","active","working","ip","progress"],
#     "On - Hold": ["on hold","paused","stalled","hold","onhold"],
#     "Completed": ["completed","done","finished","complete"],
#     "Cancelled": ["cancelled","canceled","dropped","abandoned"]
# }
# METRIC_SYNS = {
#   "status": ["status","state","how's it going","how is it going"],
#   "cost": ["cost","budget","price","how much"],
#   "benefit": ["benefit","roi","value","gain"],
#   "manager": ["manager","managed by","who manages","who is managing","who is the manager","pm"],
#   "start": ["start","starts","start date","begin","kick off","kick-off"],
#   "end": ["end","deadline","finish","ends","end date","due","finish date"],
#   "duration": ["duration","how long","length"],
#   "completion": ["completion","percent","percentage","completion%","progress","% done","percent done"],
#   "complexity": ["complexity","difficulty"],
#   "department": ["department","dept","team"],
#   "region": ["region","geo","area"],
#   "type": ["project type","type","category"],
#   "description": ["description","details","about","what is","tell me about"],
# }

# def fuzzy_project(text, names):
#     # quoted > contains > token overlap
#     m = re.search(r'"([^"]+)"', text)
#     if m:
#         q = m.group(1).lower()
#         best = max(names, key=lambda n: (n.lower()==q, n.lower().startswith(q), int(q in n.lower()), -abs(len(n)-len(q))), default=None)
#         return best
#     low = text.lower()
#     for n in sorted(names, key=lambda x:-len(x)):
#         if n.lower() in low: return n
#     toks = [t for t in re.split(r"[^a-z0-9]+", low) if len(t)>=3]
#     scores = []
#     for n in names:
#         nl = n.lower()
#         s = sum(1 for t in toks if t in nl)
#         scores.append((s,n))
#     scores.sort(reverse=True)
#     return scores[0][1] if scores and scores[0][0]>0 else None

# def get_metric(text):
#     t=text.lower()
#     for m,syns in METRIC_SYNS.items():
#         if m in t or any(s in t for s in syns):
#             return m
#     return None

# with tab_chat:
#     st.subheader("Chat")
#     if "chat" not in st.session_state: st.session_state.chat = []
#     if "last_project" not in st.session_state: st.session_state.last_project = None

#     # show history
#     for msg in st.session_state.chat:
#         with st.chat_message(msg["role"]):
#             st.markdown(msg["content"])

#     # helpers
#     def _norm(s: str) -> str:
#         return re.sub(r"[^a-z0-9%.\- ]+", " ", s.lower()).replace("  ", " ").strip()

#     def _fuzzy_project(text, names):
#         m = re.search(r'"([^"]+)"', text)
#         if m:
#             q = m.group(1).lower()
#             return max(names, key=lambda n: (n.lower()==q, n.lower().startswith(q), int(q in n.lower()), -abs(len(n)-len(q))), default=None)
#         t = text.lower()
#         for n in sorted(names, key=lambda x: -len(x)):
#             if n.lower() in t:
#                 return n
#         toks = set([w for w in re.split(r"[^a-z0-9]+", t) if len(w) >= 3])
#         best = None; score = -1
#         for n in names:
#             s = sum(1 for w in toks if w in n.lower())
#             if s > score:
#                 best, score = n, s
#         return best if score > 0 else (st.session_state.last_project or None)

#     METRICS = {
#         "status": ["status","state"],
#         "cost": ["cost","budget","price","how much"],
#         "benefit": ["benefit","roi","value","gain"],
#         "manager": ["manager","managed by","pm","who manages","who is managing","who is the manager"],
#         "start": ["start","starts","start date","begin","kick off","kick-off"],
#         "end": ["end","deadline","finish","ends","end date","due","finish date","deadline date"],
#         "duration": ["duration","how long","length"],
#         "completion": ["completion","percent","percentage","completion%","progress","% done","percent done"],
#         "complexity": ["complexity","difficulty"],
#         "department": ["department","dept","team"],
#         "region": ["region","geo","area"],
#         "type": ["project type","type","category"],
#         "description": ["description","details","about","what is","tell me about","project details","show details"],
#     }

#     def _metric_of(text):
#         t = _norm(text)
#         for k, syn in METRICS.items():
#             if k in t or any(s in t for s in syn):
#                 return k
#         return None

#     def _year_in(text):
#         m = re.search(r"\b(20\d{2})\b", text)
#         return int(m.group(1)) if m else None

#     def _threshold(text):
#         m = re.search(r"over\s*([\d,]+)", text, re.I)
#         if m: return float(m.group(1).replace(",",""))
#         m = re.search(r">\s*(\d+)", text)
#         if m: return float(m.group(1))
#         m = re.search(r"(\d+)\s*%", text)
#         if m: return float(m.group(1))
#         return None

#     def _say(txt): return "✨ " + txt

#     prompt = st.chat_input("Ask anything about your projects (free phrasing).")
#     if prompt:
#         st.session_state.chat.append({"role":"user","content":prompt})
#         df_all = df_projects()
#         names = df_all["name"].dropna().tolist()
#         t = _norm(prompt)

#         # fun small talk
#         if t in ["hi","hello","hey","yo","hola","hi there","hello there","good morning","good evening"]:
#             out = _say("Hey! I'm your chatty project buddy 🤖✨. Ask me about any project or try **list in‑progress**.")
#         else:
#             p = _fuzzy_project(prompt, names)
#             m = _metric_of(prompt)

#             # combined (cost + manager)
#             if p and ("cost" in t and "manager" in t):
#                 r = df_all[df_all["name"].str.lower()==p.lower()].head(1).iloc[0]
#                 out = _say(f"**{r['name']}** — PM **{r['manager']}**, Cost {money(r['cost'])}.")

#             # single metric about a project
#             elif p and m:
#                 r = df_all[df_all["name"].str.lower()==p.lower()].head(1).iloc[0]
#                 def _dur(s,e):
#                     return f"{(pd.to_datetime(e)-pd.to_datetime(s)).days} days" if s and e else "—"
#                 values = {
#                     "status": r["status"],
#                     "cost": money(r["cost"]),
#                     "benefit": money(r["benefit"]),
#                     "manager": r["manager"],
#                     "start": r["start_date"],
#                     "end": r["end_date"],
#                     "duration": _dur(r["start_date"], r["end_date"]),
#                     "completion": f"{int(r['completion'] or 0)}%",
#                     "complexity": r["complexity"],
#                     "department": r["department"],
#                     "region": r["region"],
#                     "type": r["type"],
#                     "description": r["description"] or "—",
#                 }
#                 out = _say(f"{m.upper()} of **{r['name']}** → {values.get(m, '—')}")

#             # project details
#             elif p and any(x in t for x in ["details","project details","tell me about","about","summary","summarize","show details","show me the project details"]):
#                 r = df_all[df_all["name"].str.lower()==p.lower()].head(1).iloc[0]
#                 buck = bucket_for_date(r["end_date"])
#                 out = _say(
#                     "**"+r["name"]+"** — quick recap:\n"
#                     f"- Status **{r['status']}**, Phase **{r['phase']}**, {int(r['completion'] or 0)}% complete\n"
#                     f"- PM **{r['manager']}**, {r['department']} / {r['region']}\n"
#                     f"- Type **{r['type']}**, Complexity **{r['complexity']}**\n"
#                     f"- Cost {money(r['cost'])}, Benefit {money(r['benefit'])}\n"
#                     f"- {r['start_date']} → {r['end_date']} — **{buck}**"
#                 )

#             # lists by status
#             elif any(w in t for w in ["in progress","in-progress","ongoing","active"]) and any(x in t for x in ["list","show","projects","details","all"]):
#                 rows = df_all[df_all["status"] == "In - Progress"]
#                 bullets = "\n".join([f"- {r['name']} — PM {r['manager']} — {int(r['completion'] or 0)}% — due {r['end_date']} ({bucket_for_date(r['end_date'])})" for _, r in rows.iterrows()]) or "_No matches._"
#                 out = _say(f"In‑Progress — {len(rows)}:\n" + bullets)

#             elif ("on hold" in t or "paused" in t) and any(x in t for x in ["list","show","projects","details","all"]):
#                 rows = df_all[df_all["status"] == "On - Hold"]
#                 bullets = "\n".join([f"- {r['name']} — PM {r['manager']} — due {r['end_date']} ({bucket_for_date(r['end_date'])})" for _, r in rows.iterrows()]) or "_No matches._"
#                 out = _say(f"On‑Hold — {len(rows)}:\n" + bullets)

#             elif "completed" in t and any(x in t for x in ["list","show","projects","details","all"]):
#                 rows = df_all[df_all["status"] == "Completed"]
#                 bullets = "\n".join([f"- {r['name']} — PM {r['manager']}" for _, r in rows.iterrows()]) or "_No matches._"
#                 out = _say(f"Completed — {len(rows)}:\n" + bullets)

#             elif "cancelled" in t and any(x in t for x in ["list","show","projects","details","all","canceled"]):
#                 rows = df_all[df_all["status"] == "Cancelled"]
#                 bullets = "\n".join([f"- {r['name']} — PM {r['manager']}" for _, r in rows.iterrows()]) or "_No matches._"
#                 out = _say(f"Cancelled — {len(rows)}:\n" + bullets)

#             # deadlines
#             elif "today" in t and "deadline" in t:
#                 rows = df_all[df_all["end_date"].apply(bucket_for_date) == "Today"]
#                 bullets = "\n".join([f"- {r['name']} — PM {r['manager']} — {r['end_date']}" for _, r in rows.iterrows()]) or "_No items today._"
#                 out = _say("Today's deadlines:\n" + bullets)

#             elif "tomorrow" in t and "deadline" in t:
#                 rows = df_all[df_all["end_date"].apply(bucket_for_date) == "Tomorrow"]
#                 bullets = "\n".join([f"- {r['name']} — PM {r['manager']} — {r['end_date']}" for _, r in rows.iterrows()]) or "_Nothing due tomorrow._"
#                 out = _say("Tomorrow's deadlines:\n" + bullets)

#             elif ("upcoming" in t and "deadline" in t) or ("nearest" in t and "deadline" in t) or ("upcoming project deadlines" in t):
#                 rows = df_all[df_all["end_date"].apply(bucket_for_date).isin(["Today","Tomorrow","Next 7 days","Next 30 days"])]
#                 if rows.empty:
#                     out = _say("No near deadlines.")
#                 else:
#                     rows = rows.sort_values("end_date")
#                     out = _say("Upcoming deadlines:\n" + "\n".join([f"- {r['name']} — {bucket_for_date(r['end_date'])} ({r['end_date']})" for _, r in rows.iterrows()]))

#             # analytics (samples from your list)
#             elif "how many" in t and "active" in t:
#                 out = _say(f"Active: {int(df_all['status'].isin(['In - Progress','On - Hold']).sum())} project(s).")

#             elif "total number of projects" in t or "how many projects" in t:
#                 out = _say(f"Total: {len(df_all)} project(s).")

#             elif "statuses" in t or "different project statuses" in t or "what are the statuses" in t:
#                 out = _say("Statuses: " + ", ".join(sorted(df_all["status"].dropna().unique())))

#             elif "phases" in t or "available project phases" in t:
#                 out = _say("Phases: " + ", ".join(sorted(df_all["phase"].dropna().unique())))

#             elif "income generation" in t and ("show" in t or "all" in t):
#                 rows = df_all[df_all["type"].str.lower()=="income generation"]
#                 bullets = "\n".join([f"- {r['name']} — {r['status']} — PM {r['manager']}" for _, r in rows.iterrows()]) or "_None_"
#                 out = _say("INCOME GENERATION:\n" + bullets)

#             elif "phase 4" in t and "implement" in t:
#                 rows = df_all[df_all["phase"].str.lower()=="phase 4 - implement"]
#                 bullets = "\n".join([f"- {r['name']} — {r['status']}" for _, r in rows.iterrows()]) or "_None_"
#                 out = _say("Phase 4 - Implement:\n" + bullets)

#             elif "managed by" in t:
#                 m2 = re.search(r"managed by\s+([a-z ]+)", t)
#                 if m2:
#                     who = m2.group(1).strip()
#                     rows = df_all[df_all["manager"].str.lower()==who]
#                     bullets = "\n".join([f"- {r['name']} — {r['status']}" for _, r in rows.iterrows()]) or "_None_"
#                     out = _say(f"Managed by {who.title()}:\n" + bullets)
#                 else:
#                     out = _say("Tell me the manager name after 'managed by ...'")

#             elif "west" in t and "region" in t:
#                 rows = df_all[df_all["region"].str.lower()=="west"]
#                 bullets = "\n".join([f"- {r['name']} — {r['status']}" for _, r in rows.iterrows()]) or "_None_"
#                 out = _say("West region:\n" + bullets)

#             elif "ecommerce" in t and "department" in t:
#                 rows = df_all[df_all["department"].str.lower()=="ecommerce"]
#                 bullets = "\n".join([f"- {r['name']} — {r['status']}" for _, r in rows.iterrows()]) or "_None_"
#                 out = _say("eCommerce department:\n" + bullets)

#             elif "total cost of all" in t and "completed" in t:
#                 total = df_all.loc[df_all["status"]=="Completed","cost"].sum()
#                 out = _say(f"Total cost (Completed): {money(total)}.")

#             elif "department has the highest total project cost" in t:
#                 g = df_all.groupby("department")["cost"].sum().sort_values(ascending=False)
#                 out = _say(f"Highest spend dept: **{g.index[0]}** — {money(g.iloc[0])}.") if len(g)>0 else _say("No data.")

#             elif "average completion percentage" in t and "north" in t:
#                 a = df_all.loc[df_all["region"].str.lower()=="north","completion"].mean()
#                 out = _say(f"Avg completion (North): {a:.1f}%.") if not pd.isna(a) else _say("No data.")

#             elif "count the number of projects for each project type" in t:
#                 g = df_all.groupby("type").size()
#                 out = _say("\n".join([f"- {k}: {v}" for k,v in g.items()]))

#             elif "project manager has the most projects" in t:
#                 g = df_all.groupby("manager").size().sort_values(ascending=False)
#                 out = _say(f"PM with most projects: **{g.index[0]}** — {int(g.iloc[0])}") if len(g)>0 else _say("No data.")

#             elif "high complexity" in t and ("in progress" in t or "in - progress" in t):
#                 rows = df_all[(df_all["complexity"].str.lower()=="high") & (df_all["status"]=="In - Progress")]
#                 bullets = "\n".join([f"- {r['name']} — {int(r['completion'] or 0)}%" for _, r in rows.iterrows()]) or "_None_"
#                 out = _say("High complexity × In‑Progress:\n" + bullets)

#             elif "highest project benefit" in t or ("best" in t and "benefit" in t):
#                 row = df_all.sort_values("benefit", ascending=False).head(1)
#                 bullets = "\n".join([f"- {r['name']} — Benefit {money(r['benefit'])}" for _, r in row.iterrows()]) or "_None_"
#                 out = _say("Top benefit:\n" + bullets)

#             elif "best cost" in t or ("lowest" in t and "cost" in t):
#                 row = df_all.sort_values("cost", ascending=True).head(1)
#                 bullets = "\n".join([f"- {r['name']} — Cost {money(r['cost'])}" for _, r in row.iterrows()]) or "_None_"
#                 out = _say("Best (lowest) cost:\n" + bullets)

#             elif "highest cost" in t or ("most" in t and "expensive" in t):
#                 row = df_all.sort_values("cost", ascending=False).head(1)
#                 bullets = "\n".join([f"- {r['name']} — Cost {money(r['cost'])}" for _, r in row.iterrows()]) or "_None_"
#                 out = _say("Highest cost:\n" + bullets)

#             elif "best completion" in t or "highest completion" in t:
#                 row = df_all.sort_values("completion", ascending=False).head(1)
#                 bullets = "\n".join([f"- {r['name']} — {int(r['completion'] or 0)}%" for _, r in row.iterrows()]) or "_None_"
#                 out = _say("Best completion%:\n" + bullets)

#             elif "short duration" in t or "shortest duration" in t or "quickest" in t:
#                 dur = (pd.to_datetime(df_all["end_date"]) - pd.to_datetime(df_all["start_date"])).dt.days
#                 row = df_all.iloc[dur.sort_values().index].head(1)
#                 bullets = "\n".join([f"- {r['name']} — {int((pd.to_datetime(r['end_date'])-pd.to_datetime(r['start_date'])).days)} days" for _, r in row.iterrows()]) or "_None_"
#                 out = _say("Shortest duration:\n" + bullets)

#             elif "long duration" in t or "longest duration" in t or "slowest" in t:
#                 dur = (pd.to_datetime(df_all["end_date"]) - pd.to_datetime(df_all["start_date"])).dt.days
#                 row = df_all.iloc[dur.sort_values(ascending=False).index].head(1)
#                 bullets = "\n".join([f"- {r['name']} — {int((pd.to_datetime(r['end_date'])-pd.to_datetime(r['start_date'])).days)} days" for _, r in row.iterrows()]) or "_None_"
#                 out = _say("Longest duration:\n" + bullets)

#             elif "active during the year" in t:
#                 y = _year_in(t) or 2021
#                 rows = df_all[(pd.to_datetime(df_all["start_date"]).dt.year<=y) & (pd.to_datetime(df_all["end_date"]).dt.year>=y)]
#                 bullets = "\n".join([f"- {r['name']} — {r['start_date']} → {r['end_date']}" for _, r in rows.iterrows()]) or "_None_"
#                 out = _say(f"Active during {y}:\n" + bullets)

#             elif ("completion" in t and ">" in t) or ("completion%" in t and ">" in t) or ("greater than" in t and "completion" in t):
#                 th = _threshold(t) or 75
#                 rows = df_all[df_all["completion"]>th]
#                 bullets = "\n".join([f"- {r['name']} — {int(r['completion'] or 0)}%" for _, r in rows.iterrows()]) or "_None_"
#                 out = _say(f"Completion > {int(th)}%:\n" + bullets)

#             elif "compare" in t and "income generation" in t and "cost reduction" in t:
#                 A = df_all[df_all["type"].str.lower()=="income generation"]; B = df_all[df_all["type"].str.lower()=="cost reduction"]
#                 out = _say(f"INCOME GENERATION — Avg Cost {money(A['cost'].mean())}, Avg Benefit {money(A['benefit'].mean())}\nCOST REDUCTION — Avg Cost {money(B['cost'].mean())}, Avg Benefit {money(B['benefit'].mean())}")

#             elif "highest average completion" in t and "project manager" in t:
#                 g = df_all.groupby("manager")["completion"].mean().sort_values(ascending=False)
#                 out = _say(f"Highest avg Completion%: **{g.index[0]}** — {g.iloc[0]:.1f}%") if len(g)>0 else _say("No data.")

#             elif "distribution of complexity" in t and "departments" in t:
#                 g = df_all.pivot_table(index="department", columns="complexity", values="id", aggfunc="count", fill_value=0)
#                 lines__=[f"- {dept} — " + ", ".join([f"{lvl}:{int(g.loc[dept,lvl])}" for lvl in sorted(g.columns)]) for dept in g.index]
#                 out = _say("Complexity × Department:\n" + "\n".join(lines__))

#             elif "completed projects changed over the years" in t or ("years" in t and "completed" in t and "changed" in t):
#                 years=[2021,2022,2023]
#                 vals=[]
#                 for y in years:
#                     m2 = df_all[(pd.to_datetime(df_all["start_date"]).dt.year<=y) & (pd.to_datetime(df_all["end_date"]).dt.year>=y) & (df_all["status"]=="Completed")]
#                     vals.append((y, len(m2)))
#                 out = _say("Completed per year: " + ", ".join([f"{y}:{c}" for y,c in vals]))

#             elif "average project duration" in t and "each project type" in t:
#                 dur = (pd.to_datetime(df_all["end_date"]) - pd.to_datetime(df_all["start_date"])).dt.days
#                 g = pd.concat([df_all["type"], dur], axis=1).groupby("type")[0].mean().round(1)
#                 out = _say("\n".join([f"- {k}: {v} days" for k,v in g.items()]))

#             elif "cancelled" in t and ("completion% over" in t or "completion over" in t or (">" in t and "completion" in t)):
#                 th = _threshold(t) or 85
#                 rows = df_all[(df_all["status"]=="Cancelled") & (df_all["completion"]>th)]
#                 bullets = "\n".join([f"- {r['name']} — {int(r['completion'] or 0)}%" for _, r in rows.iterrows()]) or "_None_"
#                 out = _say(f"Cancelled with Completion > {int(th)}%:\n" + bullets)

#             elif "managed by brenda chandler" in t and ("over" in t or "greater than" in t):
#                 rows = df_all[(df_all["manager"].str.lower()=="brenda chandler") & (df_all["cost"]>50000000)]
#                 bullets = "\n".join([f"- {r['name']} — Cost {money(r['cost'])}" for _, r in rows.iterrows()]) or "_None_"
#                 out = _say("Brenda Chandler — Cost > 50,000,000:\n" + bullets)

#             elif "started in the year 2022" in t and "phase 1 - explore" in t:
#                 rows = df_all[(pd.to_datetime(df_all["start_date"]).dt.year==2022) & (df_all["phase"].str.lower()=="phase 1 - explore")]
#                 bullets = "\n".join([f"- {r['name']}" for _, r in rows.iterrows()]) or "_None_"
#                 out = _say("2022 × Phase 1 - Explore:\n" + bullets)

#             else:
#                 out = _say("Try: **status of Rhinestone**, **list in‑progress**, **today's deadlines**, **details of 'A Triumph Of Softwares'**, or **cost + manager of Rhinestone**.")

#             if p: st.session_state.last_project = p

#         st.session_state.chat.append({"role":"assistant","content":out})
#         with st.chat_message("assistant"):
#             st.markdown(out)


# app_tracker.py
# app_tracker.py







# import streamlit as st
# import pandas as pd
# import sqlite3, re, random, os
# from datetime import date, datetime, timedelta

# st.set_page_config(page_title="Project Copilot — Tracker v3", layout="wide")
# st.title("📈 Project Copilot — Tracker (v3)")

# DB_PATH = "projects.db"
# CSV_PATH = "extra-feature-added.csv"   # <-- your CSV filename
# TODAY = date.today()

# # ---------- Utils ----------
# def parse_money(x):
#     if x is None or (isinstance(x, float) and pd.isna(x)):
#         return 0.0
#     s = str(x).strip().replace(",", "")
#     try:
#         return float(s)
#     except:
#         return 0.0

# def parse_pct(x):
#     if x is None or (isinstance(x, float) and pd.isna(x)):
#         return 0.0
#     s = str(x).strip().replace("%", "").replace(",", "")
#     try:
#         return float(s)
#     except:
#         return 0.0

# def parse_date(x):
#     if not x or (isinstance(x, float) and pd.isna(x)):
#         return None
#     s = str(x).strip()
#     for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%d-%b-%Y", "%b %d, %Y", "%d-%m-%y"):
#         try:
#             return datetime.strptime(s, fmt).date().isoformat()
#         except:
#             pass
#     try:
#         dt = pd.to_datetime(s, errors="coerce")
#         if pd.isna(dt):
#             return None
#         return dt.date().isoformat()
#     except:
#         return None

# def bucket_for_date(end_date: str):
#     if not end_date:
#         return "—"
#     try:
#         d = datetime.fromisoformat(str(end_date)).date()
#     except:
#         return "—"
#     delta = (d - TODAY).days
#     if delta < 0:
#         return "Overdue"
#     if delta == 0:
#         return "Today"
#     if delta == 1:
#         return "Tomorrow"
#     if delta <= 7:
#         return "Next 7 days"
#     if delta <= 30:
#         return "Next 30 days"
#     return "Later"

# def money(n):
#     try:
#         return f"₹{int(float(n)):,}"
#     except:
#         return "—"

# def safe_float(x, default=0.0):
#     try:
#         if x is None:
#             return float(default)
#         if isinstance(x, float) or isinstance(x, int):
#             if pd.isna(x): return float(default)
#             return float(x)
#         s = str(x).strip().replace(",", "")
#         if s == "":
#             return float(default)
#         return float(s)
#     except:
#         return float(default)

# def safe_int(x, default=0):
#     try:
#         return int(safe_float(x, default=default))
#     except:
#         return int(default)

# # ------------------------------------------------------------------------------------
# # DB SCHEMA (with decision-support fields)
# # ------------------------------------------------------------------------------------
# def get_conn():
#     conn = sqlite3.connect(DB_PATH)
#     conn.execute("PRAGMA foreign_keys = ON;")
#     return conn

# def init_db(modernize=False):
#     conn = get_conn()
#     cur = conn.cursor()

#     # Create projects table (includes decision-support columns)
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS projects (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT UNIQUE,
#             status TEXT,
#             phase TEXT,
#             completion REAL,
#             manager TEXT,
#             department TEXT,
#             region TEXT,
#             type TEXT,
#             cost REAL,
#             benefit REAL,
#             start_date TEXT,
#             end_date TEXT,
#             complexity TEXT,
#             description TEXT,
#             archived INTEGER DEFAULT 0,
#             duration_days REAL,
#             remaining_days REAL,
#             baseline_velocity REAL,
#             baseline_fte REAL,
#             projected_completion REAL,
#             risk_score REAL
#         )
#     """)

#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS announcements (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             created_at TEXT,
#             title TEXT,
#             body TEXT
#         )
#     """)

#     conn.commit()

#     # Seed if empty
#     cur.execute("SELECT COUNT(*) FROM projects")
#     count = cur.fetchone()[0]
#     if count == 0:
#         # Read CSV safely
#         if not os.path.exists(CSV_PATH):
#             conn.close()
#             st.warning(f"CSV seed file not found: {CSV_PATH}")
#             return

#         df = pd.read_csv(CSV_PATH, dtype=str, keep_default_na=False)
#         # normalize columns
#         df.columns = [c.strip() for c in df.columns]

#         # Guess mapping (use the most common headers you've provided)
#         name_col = next((c for c in df.columns if c.lower().strip() in ["project name","project_name","name"]), None)
#         status_col = next((c for c in df.columns if c.lower().strip() in ["status"]), None)
#         phase_col = next((c for c in df.columns if c.lower().strip() in ["phase"]), None)
#         completion_col = next((c for c in df.columns if "completion" in c.lower()), None)
#         manager_col = next((c for c in df.columns if "manager" in c.lower()), None)
#         dept_col = next((c for c in df.columns if "department" in c.lower()), None)
#         region_col = next((c for c in df.columns if "region" in c.lower()), None)
#         type_col = next((c for c in df.columns if "project type" in c.lower() or "type"==c.lower().strip()), None)
#         cost_col = next((c for c in df.columns if "cost" in c.lower()), None)
#         benefit_col = next((c for c in df.columns if "benefit" in c.lower()), None)
#         start_col = next((c for c in df.columns if "start" in c.lower()), None)
#         end_col = next((c for c in df.columns if "end" in c.lower()), None)
#         comp_col = next((c for c in df.columns if "complexity" in c.lower()), None)
#         desc_col = next((c for c in df.columns if "description" in c.lower()), None)

#         # decision-support columns (may or may not be present in CSV)
#         ds_dur = next((c for c in df.columns if c.lower().strip() == "duration_days"), None)
#         ds_rem = next((c for c in df.columns if c.lower().strip() == "remaining_days"), None)
#         ds_vel = next((c for c in df.columns if c.lower().strip() == "baseline_velocity"), None)
#         ds_fte = next((c for c in df.columns if c.lower().strip() == "baseline_fte"), None)
#         ds_proj = next((c for c in df.columns if c.lower().strip() == "projected_completion"), None)
#         ds_risk = next((c for c in df.columns if c.lower().strip() == "risk_score"), None)

#         recs = []
#         for _, r in df.iterrows():
#             # parse basics
#             name = r.get(name_col) if name_col else r.get(df.columns[0])
#             if name is None or str(name).strip() == "":
#                 # skip rows without a name
#                 continue
#             status = r.get(status_col) or ""
#             phase = r.get(phase_col) or ""
#             completion = parse_pct(r.get(completion_col)) if completion_col else 0.0
#             manager = r.get(manager_col) or ""
#             department = r.get(dept_col) or ""
#             region = r.get(region_col) or ""
#             ptype = r.get(type_col) or ""
#             cost = parse_money(r.get(cost_col)) if cost_col else 0.0
#             benefit = parse_money(r.get(benefit_col)) if benefit_col else 0.0

#             start = parse_date(r.get(start_col)) if start_col else None
#             end = parse_date(r.get(end_col)) if end_col else None

#             complexity = r.get(comp_col) or ""
#             description = r.get(desc_col) or ""

#             # ---------- decision-support defaults ----------
#             # duration_days: use CSV value if present else compute from start/end
#             if ds_dur and r.get(ds_dur) not in [None, ""]:
#                 duration_days = safe_float(r.get(ds_dur), default=0.0)
#             else:
#                 if start and end:
#                     try:
#                         sd = datetime.fromisoformat(start).date()
#                         ed = datetime.fromisoformat(end).date()
#                         duration_days = max(0, (ed - sd).days)
#                     except:
#                         duration_days = 0.0
#                 else:
#                     duration_days = 0.0

#             # remaining_days: CSV -> compute from end_date -> default 0
#             if ds_rem and r.get(ds_rem) not in [None, ""]:
#                 remaining_days = safe_float(r.get(ds_rem), default=0.0)
#             else:
#                 if end:
#                     try:
#                         ed = datetime.fromisoformat(end).date()
#                         remaining_days = max(0, (ed - TODAY).days)
#                     except:
#                         remaining_days = 0.0
#                 else:
#                     remaining_days = 0.0

#             # baseline_velocity: CSV -> infer from completion & remaining_days -> default 1
#             if ds_vel and r.get(ds_vel) not in [None, ""]:
#                 baseline_velocity = safe_float(r.get(ds_vel), default=1.0)
#             else:
#                 try:
#                     if remaining_days > 0:
#                         baseline_velocity = max(0.1, (100.0 - completion) / remaining_days)
#                     else:
#                         baseline_velocity = 1.0
#                 except:
#                     baseline_velocity = 1.0

#             # baseline_fte: CSV or default 1.0
#             if ds_fte and r.get(ds_fte) not in [None, ""]:
#                 baseline_fte = safe_float(r.get(ds_fte), default=1.0)
#             else:
#                 baseline_fte = 1.0

#             # projected_completion: CSV or equal to completion
#             if ds_proj and r.get(ds_proj) not in [None, ""]:
#                 projected_completion = safe_float(r.get(ds_proj), default=completion)
#             else:
#                 projected_completion = completion

#             # risk_score: CSV or heuristics (lower completion -> higher risk)
#             if ds_risk and r.get(ds_risk) not in [None, ""]:
#                 risk_score = safe_float(r.get(ds_risk), default=5.0)
#             else:
#                 try:
#                     risk_score = max(1.0, min(10.0, 10 - completion/12))  # simple mapping
#                 except:
#                     risk_score = 5.0

#             recs.append((
#                 name, status, phase, completion, manager, department, region, ptype,
#                 cost, benefit, start, end, complexity, description,
#                 duration_days, remaining_days, baseline_velocity, baseline_fte,
#                 projected_completion, risk_score
#             ))

#         # insert into DB
#         if recs:
#             cur.executemany("""
#                 INSERT OR IGNORE INTO projects
#                 (name,status,phase,completion,manager,department,region,type,cost,benefit,start_date,end_date,complexity,description,
#                  duration_days, remaining_days, baseline_velocity, baseline_fte, projected_completion, risk_score)
#                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#             """, recs)
#             conn.commit()

#     conn.close()

# # ---------- Fetch Projects ----------
# def df_projects(include_archived=False):
#     conn = get_conn()
#     q = "SELECT * FROM projects" + ("" if include_archived else " WHERE archived=0")
#     df = pd.read_sql_query(q, conn)
#     conn.close()
#     return df

# # ---------- Update Project Row ----------
# def upsert_project(row):
#     conn = get_conn()
#     cur = conn.cursor()

#     # coerce/safe defaults for DS fields when writing
#     duration_days = safe_float(row.get("duration_days", 0.0), default=0.0)
#     remaining_days = safe_float(row.get("remaining_days", 0.0), default=0.0)
#     baseline_velocity = safe_float(row.get("baseline_velocity", 1.0), default=1.0)
#     baseline_fte = safe_float(row.get("baseline_fte", 1.0), default=1.0)
#     projected_completion = safe_float(row.get("projected_completion", row.get("completion", 0.0)), default=0.0)
#     risk_score = safe_float(row.get("risk_score", 5.0), default=5.0)

#     if row.get("id"):
#         cur.execute("""
#             UPDATE projects SET
#                 name=?, status=?, phase=?, completion=?, manager=?, department=?, region=?, type=?,
#                 cost=?, benefit=?, start_date=?, end_date=?, complexity=?, description=?,
#                 duration_days=?, remaining_days=?, baseline_velocity=?, baseline_fte=?,
#                 projected_completion=?, risk_score=? WHERE id=?
#         """, (
#             row.get("name"), row.get("status"), row.get("phase"), float(row.get("completion") or 0),
#             row.get("manager"), row.get("department"), row.get("region"), row.get("type"),
#             float(row.get("cost") or 0), float(row.get("benefit") or 0),
#             row.get("start_date"), row.get("end_date"), row.get("complexity"), row.get("description"),
#             duration_days, remaining_days, baseline_velocity, baseline_fte,
#             projected_completion, risk_score,
#             int(row.get("id"))
#         ))
#     else:
#         cur.execute("""
#             INSERT INTO projects
#             (name,status,phase,completion,manager,department,region,type,cost,benefit,start_date,end_date,complexity,description,
#              duration_days, remaining_days, baseline_velocity, baseline_fte, projected_completion, risk_score)
#             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#         """, (
#             row.get("name"), row.get("status"), row.get("phase"), float(row.get("completion") or 0),
#             row.get("manager"), row.get("department"), row.get("region"), row.get("type"),
#             float(row.get("cost") or 0), float(row.get("benefit") or 0),
#             row.get("start_date"), row.get("end_date"), row.get("complexity"), row.get("description"),
#             duration_days, remaining_days, baseline_velocity, baseline_fte,
#             projected_completion, risk_score
#         ))

#     conn.commit()
#     conn.close()

# # ---------- Announcements ----------
# def post_announcement(title, body):
#     conn = get_conn()
#     cur = conn.cursor()
#     cur.execute("INSERT INTO announcements (created_at,title,body) VALUES (?,?,?)",
#                 (datetime.now().strftime("%Y-%m-%d %H:%M"), title, body))
#     conn.commit()
#     conn.close()

# def df_announcements():
#     conn = get_conn()
#     df = pd.read_sql_query("SELECT * FROM announcements ORDER BY id DESC", conn)
#     conn.close()
#     return df

# # ---------- First Run Sidebar ----------
# with st.sidebar:
#     st.subheader("First-run options")
#     modernize = st.checkbox("Modernize dates (shift around today) on first seed", value=True)
#     if st.button("Initialize database"):
#         if os.path.exists(DB_PATH):
#             os.remove(DB_PATH)
#         init_db(modernize=modernize)
#         st.success("Database initialized ✅. Reload the page.")

# # Ensure DB exists
# if not os.path.exists(DB_PATH):
#     init_db(modernize=True)

# # ---------- Tabs ----------
# tab_proj, tab_alerts, tab_visuals, tab_ds, tab_chat, tab_ann = st.tabs([
#     "🗂 Projects", "⏰ Alerts", "📊 Visuals", "🧠 Decision Support", "💬 Chat", "📣 Announcements"
# ])

# # =====================================================================================
# # 🗂 PROJECTS TAB (CRUD)
# # =====================================================================================
# with tab_proj:
#     st.subheader("Add / Edit Project")

#     with st.form("new_project"):
#         c1, c2, c3 = st.columns(3)

#         # Column 1
#         with c1:
#             name = st.text_input("Project Name*")
#             status = st.selectbox("Status", ["In - Progress", "On - Hold", "Completed", "Cancelled"])
#             phase = st.selectbox("Phase", [
#                 "Phase 1 - Explore", "Phase 2 - Plan", "Phase 3 - Design", "Phase 4 - Implement", "Phase 5 - Close"
#             ])
#             completion = st.slider("Completion %", 0, 100, 0)

#         # Column 2
#         with c2:
#             manager = st.text_input("Project Manager")
#             department = st.text_input("Department")
#             region = st.text_input("Region")
#             ptype = st.text_input("Project Type")

#         # Column 3
#         with c3:
#             cost = st.number_input("Project Cost", min_value=0, value=0, step=1000)
#             benefit = st.number_input("Project Benefit", min_value=0, value=0, step=1000)
#             start_date = st.date_input("Start Date", value=TODAY)
#             end_date = st.date_input("End Date", value=TODAY + timedelta(days=30))

#         # Single line
#         desc = st.text_area("Project Description")
#         complexity = st.selectbox("Complexity", ["Low", "Medium", "High"])

#         # NEW DECISION SUPPORT INPUTS
#         st.markdown("### 🧠 Decision-Support Fields")
#         dc1, dc2, dc3 = st.columns(3)
#         with dc1:
#             duration_days = st.number_input("Duration (days)", min_value=0, value=0)
#             remaining_days = st.number_input("Remaining Days", min_value=0, value=0)

#         with dc2:
#             baseline_velocity = st.number_input("Baseline Velocity (units/day)", min_value=0.0, value=0.0)
#             baseline_fte = st.number_input("Baseline FTE", min_value=0.0, value=1.0)

#         with dc3:
#             projected_completion = st.number_input("Projected Completion %", min_value=0, value=0)
#             risk_score = st.number_input("Risk Score (1–10)", min_value=1, max_value=10, value=5)

#         submitted = st.form_submit_button("Create Project")

#         if submitted:
#             if not name.strip():
#                 st.error("Name is required.")
#             else:
#                 row = dict(
#                     name=name.strip(), status=status, phase=phase, completion=completion,
#                     manager=manager, department=department, region=region, type=ptype,
#                     cost=cost, benefit=benefit, start_date=str(start_date), end_date=str(end_date),
#                     complexity=complexity, description=desc,
#                     duration_days=duration_days,
#                     remaining_days=remaining_days,
#                     baseline_velocity=baseline_velocity,
#                     baseline_fte=baseline_fte,
#                     projected_completion=projected_completion,
#                     risk_score=risk_score
#                 )
#                 upsert_project(row)
#                 st.success("Project created 🎉")

#     st.markdown("---")

#     st.subheader("Inline Edit")
#     df = df_projects()

#     if len(df) == 0:
#         st.info("No projects yet. Add one above.")
#     else:
#         show = df.copy()
#         show["deadline_bucket"] = show["end_date"].apply(bucket_for_date)

#         edited = st.data_editor(show, num_rows="dynamic", use_container_width=True, key="editor")

#         if st.button("Save changes"):
#             for _, r in edited.iterrows():
#                 upsert_project(r.to_dict())
#             st.success("Saved changes! ✅")

# # =====================================================================================
# # ⏰ ALERTS TAB
# # =====================================================================================
# with tab_alerts:
#     st.subheader("Due-date Alerts")

#     df = df_projects()
#     if len(df) == 0:
#         st.info("No projects available.")
#     else:
#         df["deadline_bucket"] = df["end_date"].apply(bucket_for_date)
#         buckets = ["Overdue", "Today", "Tomorrow", "Next 7 days", "Next 30 days"]

#         cols = st.columns(len(buckets))
#         for i, b in enumerate(buckets):
#             with cols[i]:
#                 st.metric(b, int((df["deadline_bucket"] == b).sum()))

#         st.markdown("#### Detailed View")
#         choice = st.selectbox("Select bucket", buckets, index=0)
#         view = df[df["deadline_bucket"] == choice]

#         # show same columns table used earlier, preserve interface
#         st.dataframe(view[["name","status","manager","completion","end_date","deadline_bucket","department","region"]], use_container_width=True)

#         # Digest text (preview)
#         digest = "\n".join([
#             f"- {r['name']} — {r['status']} | PM {r['manager']} | {int(r['completion'] or 0)}% | due {r['end_date']} ({bucket_for_date(r['end_date'])})"
#             for _, r in view.iterrows()
#         ]) or "No items."

#         # Post digest button (existing feature)
#         if st.button("Post digest to Announcements"):
#             title = f"[ALERT] {choice} — {len(view)} project(s)"
#             post_announcement(title, digest)
#             st.success("Digest posted 📣")

#         st.text_area("Digest preview", value=digest, height=150)

#         st.markdown("---")
#         # ---------------- Manager custom announcement ----------------
#         st.markdown("### ✉️ Post a custom announcement")
#         ann_title = st.text_input("Announcement title", value=f"[TEAM] {choice} update")
#         ann_body = st.text_area("Message to post (will appear in Announcements)", value="")

#         if st.button("Send announcement"):
#             if not ann_title.strip():
#                 st.error("Please provide a title for the announcement.")
#             elif not ann_body.strip():
#                 st.error("Please write a message to post.")
#             else:
#                 post_announcement(ann_title.strip(), ann_body.strip())
#                 st.success("Announcement posted and will appear in Announcements tab ✅")

# # =====================================================================================
# # 📊 VISUALS TAB
# # =====================================================================================
# with tab_visuals:
#     st.subheader("Portfolio Visuals")
#     df = df_projects()

#     if len(df) == 0:
#         st.info("No project data available.")
#     else:
#         df["deadline_bucket"] = df["end_date"].apply(bucket_for_date)

#         c1, c2, c3 = st.columns(3)
#         with c1:
#             st.metric("Total Projects", len(df))
#         with c2:
#             st.metric("Active", int(df["status"].isin(["In - Progress", "On - Hold"]).sum()))
#         with c3:
#             st.metric("Overdue", int(df["deadline_bucket"].eq("Overdue").sum()))

#         st.markdown("### Status Distribution")
#         st.bar_chart(df["status"].value_counts())

#         st.markdown("### Completion Buckets")
#         bins = pd.cut(df["completion"], bins=[0, 25, 50, 75, 100], include_lowest=True).astype(str)
#         st.bar_chart(bins.value_counts())

#         st.markdown("### Cost vs Benefit (Bubble → Completion)")
#         plot_df = df.copy()
#         plot_df["size"] = plot_df["completion"].fillna(0) + 5
#         st.scatter_chart(plot_df, x="cost", y="benefit", size="size", color="status")

# # =====================================================================================
# # 🧠 DECISION SUPPORT TAB  (fixed)
# # =====================================================================================
# with tab_ds:
#     st.subheader("🧠 Decision Support — What-If Analysis")

#     df = df_projects()
#     if len(df) == 0:
#         st.info("No projects available.")
#     else:
#         # build safe project list (exclude blanks / None)
#         project_list = df["name"].astype(str).fillna("").str.strip()
#         project_list = [p for p in project_list.tolist() if p != ""]
#         if not project_list:
#             st.error("No project names found in DB. Re-initialize database.")
#         else:
#             selected = st.selectbox("Choose a project", ["None"] + project_list, index=0)
#             if selected == "None":
#                 st.info("Choose a project to run scenarios.")
#             else:
#                 # match row safely (case-insensitive, trimmed)
#                 row_df = df[df["name"].astype(str).str.strip().str.lower() == selected.strip().lower()]
#                 if row_df.empty:
#                     st.error("⚠ Project not found in database. Try re-initializing the database.")
#                     st.stop()

#                 r = row_df.iloc[0]

#                 # safe extractions with defaults
#                 comp_val = safe_int(r.get("completion", 0), default=0)
#                 remaining_days = safe_float(r.get("remaining_days", 0), default=0)
#                 baseline_velocity = safe_float(r.get("baseline_velocity", 1.0), default=1.0)
#                 baseline_fte = safe_float(r.get("baseline_fte", 1.0), default=1.0)
#                 proj_comp = safe_float(r.get("projected_completion", comp_val), default=comp_val)
#                 risk_score = safe_float(r.get("risk_score", 5.0), default=5.0)

#                 # Snapshot
#                 st.markdown(f"### 📌 Current Snapshot of **{selected}**")
#                 colA, colB, colC = st.columns(3)
#                 with colA:
#                     st.metric("Completion", f"{comp_val}%")
#                     st.metric("Remaining Days", int(remaining_days or 0))
#                 with colB:
#                     st.metric("Velocity", f"{baseline_velocity:.2f} units/day")
#                     st.metric("FTE", f"{baseline_fte:.1f}")
#                 with colC:
#                     st.metric("Projected Completion", f"{int(proj_comp)}%")
#                     st.metric("Risk Score", f"{int(risk_score)} / 10")

#                 st.markdown("---")
#                 st.markdown("### 🔍 Run a What-If Scenario")

#                 scenario = st.radio(
#                     "Select Scenario",
#                     [
#                         "Increase budget",
#                         "Add extra FTE",
#                         "Increase velocity",
#                         "Reduce remaining duration",
#                         "Predict risk from completion level"
#                     ]
#                 )

#                 out = ""
#                 if scenario == "Increase budget":
#                     pct = st.slider("Increase Budget (%)", 0, 100, 20)
#                     new_velocity = baseline_velocity * (1 + pct/100 * 0.3)
#                     new_proj = min(100, int(proj_comp + pct * 0.4))
#                     out = f"""
#                     ### 💡 Prediction  
#                     Increasing budget by **{pct}%** yields:
#                     - 🔼 Velocity → **{new_velocity:.2f} units/day**
#                     - ⏳ New projected completion → **{new_proj}%**
#                     """

#                 elif scenario == "Add extra FTE":
#                     fte = st.number_input("Add FTE", min_value=0.0, value=1.0)
#                     base_vel = baseline_velocity
#                     base_fte = baseline_fte if baseline_fte > 0 else 1.0
#                     new_velocity = base_vel * (1 + (fte / (base_fte + 0.001)))
#                     # avoid division by zero
#                     if new_velocity <= 0 or base_vel <= 0:
#                         new_remaining = remaining_days
#                     else:
#                         new_remaining = max(1, remaining_days * (base_vel / new_velocity))
#                     out = f"""
#                     ### 👨‍💼 Workforce Impact  
#                     Adding **{fte} FTE** results in:
#                     - 🔼 Velocity → **{new_velocity:.2f}**
#                     - 🗓 Reduced remaining days → **{int(new_remaining)}**
#                     """

#                 elif scenario == "Increase velocity":
#                     vel = st.slider("Velocity Increase (%)", 0, 200, 50)
#                     base_vel = baseline_velocity if baseline_velocity > 0 else 1.0
#                     new_velocity = base_vel * (1 + vel/100)
#                     if new_velocity <= 0:
#                         new_remaining = remaining_days
#                     else:
#                         new_remaining = max(1, remaining_days * (base_vel / new_velocity))
#                     out = f"""
#                     ### ⚡ Speed Simulation  
#                     Velocity +{vel}%:
#                     - New Velocity → **{new_velocity:.2f}**
#                     - New Remaining Days → **{int(new_remaining)}**
#                     """

#                 elif scenario == "Reduce remaining duration":
#                     cut = st.slider("Reduce Remaining Days (%)", 0, 80, 20)
#                     new_remaining = int(max(0, remaining_days * (1 - cut/100)))
#                     new_completion = min(100, int(comp_val + cut * 0.6))
#                     out = f"""
#                     ### ⏳ Timeline Compression  
#                     Duration -{cut}%:
#                     - New Remaining Days → **{new_remaining}**
#                     - New Completion Forecast → **{new_completion}%**
#                     """

#                 elif scenario == "Predict risk from completion level":
#                     comp = st.slider("Completion (%)", 0, 100, comp_val)
#                     predicted_risk = max(1, min(10, int(10 - comp/12)))
#                     out = f"""
#                     ### ⚠ Risk Forecast  
#                     At **{comp}% completion**:
#                     - Predicted Risk Score → **{predicted_risk}/10**
#                     """

#                 st.markdown(out)

# # =====================================================================================
# # 💬 CHAT TAB  (unchanged logic, safe accesses)
# # =====================================================================================
# def say(text):
#     return "✨ " + text

# STATUS_SYNS = {
#     "In - Progress": ["in progress","in-progress","ongoing","active","working","ip","progress"],
#     "On - Hold": ["on hold","paused","stalled","hold","onhold"],
#     "Completed": ["completed","done","finished","complete"],
#     "Cancelled": ["cancelled","canceled","dropped","abandoned"]
# }

# METRIC_SYNS = {
#   "status": ["status","state"],
#   "cost": ["cost","budget","price","how much"],
#   "benefit": ["benefit","roi","value","gain"],
#   "manager": ["manager","managed by","pm"],
#   "start": ["start","start date","begin"],
#   "end": ["end","deadline","finish","end date","due"],
#   "duration": ["duration","how long","length"],
#   "completion": ["completion","percent","progress"],
#   "complexity": ["complexity","difficulty"],
#   "department": ["department","dept","team"],
#   "region": ["region","geo","area"],
#   "type": ["project type","type","category"],
#   "description": ["description","details","about","what is"],
# }

# def _norm(s):
#     return re.sub(r"[^a-z0-9%.\- ]+", " ", s.lower()).strip()

# def _fuzzy_project(text, names):
#     t = text.lower()
#     for n in sorted(names, key=lambda x: -len(str(x))):
#         if str(n).lower() in t:
#             return n
#     toks = set(re.split(r"[^a-z0-9]+", t))
#     best = None; score = -1
#     for n in names:
#         nl = str(n).lower()
#         s = sum(1 for w in toks if w in nl)
#         if s > score:
#             best, score = n, s
#     return best if score > 0 else None

# def _metric_of(text):
#     t = _norm(text)
#     for k, syn in METRIC_SYNS.items():
#         if k in t or any(s in t for s in syn):
#             return k
#     return None

# with tab_chat:
#     st.subheader("Chat")

#     if "chat" not in st.session_state:
#         st.session_state.chat = []
#     if "last_project" not in st.session_state:
#         st.session_state.last_project = None

#     # Chat history
#     for msg in st.session_state.chat:
#         with st.chat_message(msg["role"]):
#             st.markdown(msg["content"])

#     prompt = st.chat_input("Ask me anything about your projects")

#     if prompt:
#         st.session_state.chat.append({"role": "user", "content": prompt})

#         df_all = df_projects()
#         names = df_all["name"].dropna().tolist()

#         p = _fuzzy_project(prompt, names)
#         m = _metric_of(prompt)

#         out = ""
#         # -------------- Metric responses --------------
#         if p and m:
#             row = df_all[df_all["name"].astype(str).str.lower() == str(p).strip().lower()]
#             if not row.empty:
#                 r = row.iloc[0]
#                 value_map = {
#                     "status": r.get("status"),
#                     "cost": money(r.get("cost")),
#                     "benefit": money(r.get("benefit")),
#                     "manager": r.get("manager"),
#                     "start": r.get("start_date"),
#                     "end": r.get("end_date"),
#                     "duration": r.get("duration_days"),
#                     "completion": f"{int(r.get('completion') or 0)}%",
#                     "complexity": r.get("complexity"),
#                     "department": r.get("department"),
#                     "region": r.get("region"),
#                     "type": r.get("type"),
#                     "description": r.get("description")
#                 }
#                 out = say(f"{m.upper()} of **{p}** → {value_map.get(m, '—')}")
#             else:
#                 out = say("Couldn't find that project.")

#         # -------------- Project Details --------------
#         elif p and "details" in prompt.lower():
#             row = df_all[df_all["name"].astype(str).str.lower() == str(p).strip().lower()]
#             if not row.empty:
#                 r = row.iloc[0]
#                 out = say(
#                     f"**{p}** details:\n"
#                     f"- Status: {r.get('status')}\n"
#                     f"- Completion: {int(r.get('completion') or 0)}%\n"
#                     f"- Manager: {r.get('manager')}\n"
#                     f"- Cost: {money(r.get('cost'))}\n"
#                     f"- Duration: {r.get('duration_days')} days\n"
#                     f"- Remaining: {r.get('remaining_days')} days\n"
#                     f"- Risk Score: {r.get('risk_score')}"
#                 )
#             else:
#                 out = say("Couldn't find that project.")

#         else:
#             out = say("Try asking: **status of Rhinestone**, **cost of project X**, **details of 'Blue Bird'**")

#         st.session_state.chat.append({"role": "assistant", "content": out})

#         with st.chat_message("assistant"):
#             st.markdown(out)

# # =====================================================================================
# # 📣 ANNOUNCEMENTS
# # =====================================================================================
# with tab_ann:
#     st.subheader("Announcements")
#     ann = df_announcements()
#     if len(ann) == 0:
#         st.caption("Nothing posted yet. Use Alerts to post a digest.")
#     else:
#         for _, row in ann.iterrows():
#             st.markdown(f"**{row['title']}**  \n_{row['created_at']}_  \n{row['body']}")
#             st.divider()





# Part 1 of 3
# Part 1 of 3









#currrrrrreeeeennnnnttttt


















# import streamlit as st
# import pandas as pd
# import sqlite3, re, random, os
# from datetime import date, datetime, timedelta

# st.set_page_config(page_title="Project Copilot — Tracker v3", layout="wide")
# st.title("📈 Project Copilot — Tracker (v3)")

# DB_PATH = "projects.db"
# CSV_PATH = "projects_seed.csv"   
# TODAY = date.today()

# # ---------- Utils ----------
# def parse_money(x):
#     if x is None or (isinstance(x, float) and pd.isna(x)):
#         return 0.0
#     s = str(x).strip().replace(",", "")
#     try:
#         return float(s)
#     except:
#         return 0.0

# def parse_pct(x):
#     if x is None or (isinstance(x, float) and pd.isna(x)):
#         return 0.0
#     s = str(x).strip().replace("%", "").replace(",", "")
#     try:
#         return float(s)
#     except:
#         return 0.0

# def parse_date(x):
#     if not x or (isinstance(x, float) and pd.isna(x)):
#         return None
#     s = str(x).strip()
#     # Corrected format list: Removed the ambiguous "%d-%m-%y" to ensure "%d-%m-%Y" is used for '03-01-2021'.
#     for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%b-%Y", "%b %d, %Y"):
#         try:
#             return datetime.strptime(s, fmt).date().isoformat()
#         except:
#             pass
#     try:
#         dt = pd.to_datetime(s, errors="coerce")
#         if pd.isna(dt):
#             return None
#         return dt.date().isoformat()
#     except:
#         return None

# def bucket_for_date(end_date: str):
#     if not end_date: return "—"
#     try: d = datetime.fromisoformat(str(end_date)).date()
#     except: return "—"
#     delta = (d - TODAY).days
#     if delta < 0: return "Overdue"
#     if delta == 0: return "Today"
#     if delta == 1: return "Tomorrow"
#     if delta <= 7: return "Next 7 days"
#     if delta <= 30: return "Next 30 days"
#     return "Later"

# def money(n):
#     try:
#         return f"₹{int(float(n)):,}"
#     except:
#         return "—"

# def safe_float(x, default=0.0):
#     try:
#         if x is None:
#             return float(default)
#         if isinstance(x, float) or isinstance(x, int):
#             if pd.isna(x): return float(default)
#             return float(x)
#         s = str(x).strip().replace(",", "")
#         if s == "":
#             return float(default)
#         return float(s)
#     except:
#         return float(default)

# def safe_int(x, default=0):
#     try:
#         return int(safe_float(x, default=default))
#     except:
#         return int(default)

# # ------------------- AUTO-COMPUTE DS FIELDS HELPER -------------------
# def compute_ds_fields_for_row(row):
#     """
#     Given a project 'row' (dict-like), compute/normalize decision-support
#     fields: duration_days, remaining_days, baseline_velocity, baseline_fte,
#     projected_completion, risk_score. Uses TODAY for remaining_days.
#     """
#     # helper to parse iso / other date strings into date
#     def _to_date(x):
#         if not x:
#             return None
#         try:
#             # already ISO 'YYYY-MM-DD'
#             return datetime.fromisoformat(str(x)).date()
#         except:
#             try:
#                 # fallback to pandas parse
#                 dt = pd.to_datetime(str(x), errors="coerce")
#                 if pd.isna(dt):
#                     return None
#                 return dt.date()
#             except:
#                 return None

#     # safe reads
#     start = _to_date(row.get("start_date"))
#     end = _to_date(row.get("end_date"))
#     completion = safe_float(row.get("completion", 0.0), default=0.0)

#     # duration_days: prefer provided positive numeric; else derive from start/end
#     dur = row.get("duration_days")
#     try:
#         duration_days = float(dur) if dur not in (None, "") else None
#     except:
#         duration_days = None
#     if duration_days is None or duration_days < 0:
#         if start and end:
#             try:
#                 duration_days = max(0, (end - start).days)
#             except:
#                 duration_days = 0.0
#         else:
#             duration_days = 0.0

#     # remaining_days: prefer provided numeric; else derive from end_date relative to TODAY
#     rem = row.get("remaining_days")
#     try:
#         remaining_days = float(rem) if rem not in (None, "") else None
#     except:
#         remaining_days = None
#     if remaining_days is None or remaining_days < 0:
#         if end:
#             try:
#                 remaining_days = max(0, (end - TODAY).days)
#             except:
#                 remaining_days = 0.0
#         else:
#             remaining_days = 0.0

#     # baseline_velocity: prefer provided numeric; else infer (100 - completion) / remaining_days if remaining_days>0
#     vel = row.get("baseline_velocity")
#     try:
#         baseline_velocity = float(vel) if vel not in (None, "") else None
#     except:
#         baseline_velocity = None
#     if baseline_velocity is None or baseline_velocity <= 0:
#         try:
#             if remaining_days > 0:
#                 baseline_velocity = max(0.01, (100.0 - completion) / remaining_days)
#             else:
#                 baseline_velocity = 1.0
#         except:
#             baseline_velocity = 1.0

#     # baseline_fte: prefer provided or default 1.0
#     fte = row.get("baseline_fte")
#     try:
#         baseline_fte = float(fte) if fte not in (None, "") else 1.0
#     except:
#         baseline_fte = 1.0
#     if baseline_fte <= 0:
#         baseline_fte = 1.0

#     # projected_completion: prefer provided; else equal to completion
#     proj = row.get("projected_completion")
#     try:
#         projected_completion = float(proj) if proj not in (None, "") else None
#     except:
#         projected_completion = None
#     if projected_completion is None:
#         projected_completion = completion

#     # risk_score: prefer provided; else heuristic (lower completion -> higher risk)
#     rsk = row.get("risk_score")
#     try:
#         risk_score = float(rsk) if rsk not in (None, "") else None
#     except:
#         risk_score = None
#     if risk_score is None:
#         try:
#             risk_score = max(1.0, min(10.0, 10 - completion / 12))
#         except:
#             risk_score = 5.0

#     # final coercions
#     return {
#         "duration_days": float(duration_days),
#         "remaining_days": float(remaining_days),
#         "baseline_velocity": float(baseline_velocity),
#         "baseline_fte": float(baseline_fte),
#         "projected_completion": float(projected_completion),
#         "risk_score": float(risk_score)
#     }

# # ------------------------------------------------------------------------------------
# # DB SCHEMA (with decision-support fields)
# # ------------------------------------------------------------------------------------
# def get_conn():
#     conn = sqlite3.connect(DB_PATH)
#     conn.execute("PRAGMA foreign_keys = ON;")
#     return conn

# def init_db(modernize=False):
#     conn = get_conn()
#     cur = conn.cursor()

#     # Create projects table (includes decision-support columns)
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS projects (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT UNIQUE,
#             status TEXT,
#             phase TEXT,
#             completion REAL,
#             manager TEXT,
#             department TEXT,
#             region TEXT,
#             type TEXT,
#             cost REAL,
#             benefit REAL,
#             start_date TEXT,
#             end_date TEXT,
#             complexity TEXT,
#             description TEXT,
#             archived INTEGER DEFAULT 0,
#             duration_days REAL,
#             remaining_days REAL,
#             baseline_velocity REAL,
#             baseline_fte REAL,
#             projected_completion REAL,
#             risk_score REAL
#         )
#     """)

#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS announcements (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             created_at TEXT,
#             title TEXT,
#             body TEXT
#         )
#     """)

#     conn.commit()

#     # Seed if empty
#     cur.execute("SELECT COUNT(*) FROM projects")
#     count = cur.fetchone()[0]
#     if count == 0:
#         # Read CSV safely
#         if not os.path.exists(CSV_PATH):
#             conn.close()
#             st.warning(f"CSV seed file not found: {CSV_PATH}")
#             return

#         df = pd.read_csv(CSV_PATH, dtype=str, keep_default_na=False)
        
#         # normalize columns
#         df.columns = [c.strip() for c in df.columns]

#         # Guess mapping (use the most common headers you've provided)
#         name_col = next((c for c in df.columns if c.lower().strip() in ["project name","project_name","name"]), None)
#         status_col = next((c for c in df.columns if c.lower().strip() in ["status"]), None)
#         phase_col = next((c for c in df.columns if c.lower().strip() in ["phase"]), None)
#         completion_col = next((c for c in df.columns if "completion" in c.lower()), None)
#         manager_col = next((c for c in df.columns if "manager" in c.lower()), None)
#         dept_col = next((c for c in df.columns if "department" in c.lower()), None)
#         region_col = next((c for c in df.columns if "region" in c.lower()), None)
#         type_col = next((c for c in df.columns if "project type" in c.lower() or "type"==c.lower().strip()), None)
#         cost_col = next((c for c in df.columns if "cost" in c.lower()), None)
#         benefit_col = next((c for c in df.columns if "benefit" in c.lower()), None)
#         start_col = next((c for c in df.columns if "start" in c.lower()), None)
#         end_col = next((c for c in df.columns if "end" in c.lower()), None)
#         comp_col = next((c for c in df.columns if "complexity" in c.lower()), None)
#         desc_col = next((c for c in df.columns if "description" in c.lower()), None)

#         # decision-support columns (may or may not be present in CSV)
#         ds_dur = next((c for c in df.columns if c.lower().strip() == "duration_days"), None)
#         ds_rem = next((c for c in df.columns if c.lower().strip() == "remaining_days"), None)
#         ds_vel = next((c for c in df.columns if c.lower().strip() == "baseline_velocity"), None)
#         ds_fte = next((c for c in df.columns if c.lower().strip() == "baseline_fte"), None)
#         ds_proj = next((c for c in df.columns if c.lower().strip() == "projected_completion"), None)
#         ds_risk = next((c for c in df.columns if c.lower().strip() == "risk_score"), None)

#         recs = []
#         for _, r in df.iterrows():
#             # parse basics
#             name = r.get(name_col) if name_col else r.get(df.columns[0])
#             if name is None or str(name).strip() == "":
#                 # skip rows without a name
#                 continue
#             status = r.get(status_col) or ""
#             phase = r.get(phase_col) or ""
#             completion = parse_pct(r.get(completion_col)) if completion_col else 0.0
#             manager = r.get(manager_col) or ""
#             department = r.get(dept_col) or ""
#             region = r.get(region_col) or ""
#             ptype = r.get(type_col) or ""
#             cost = parse_money(r.get(cost_col)) if cost_col else 0.0
#             benefit = parse_money(r.get(benefit_col)) if benefit_col else 0.0

#             start = parse_date(r.get(start_col)) if start_col else None
#             end = parse_date(r.get(end_col)) if end_col else None

#             complexity = r.get(comp_col) or ""
#             description = r.get(desc_col) or ""
# # Part 2 of 3 (continued)
#             # ---------- decision-support defaults ----------
#             # duration_days: use CSV value if present else compute from start/end
#             if ds_dur and r.get(ds_dur) not in [None, ""]:
#                 duration_days = safe_float(r.get(ds_dur), default=0.0)
#             else:
#                 if start and end:
#                     try:
#                         sd = datetime.fromisoformat(start).date()
#                         ed = datetime.fromisoformat(end).date()
#                         duration_days = max(0, (ed - sd).days)
#                     except:
#                         duration_days = 0.0
#                 else:
#                     duration_days = 0.0

#             # remaining_days: CSV -> compute from end_date -> default 0
#             if ds_rem and r.get(ds_rem) not in [None, ""]:
#                 remaining_days = safe_float(r.get(ds_rem), default=0.0)
#             else:
#                 if end:
#                     try:
#                         ed = datetime.fromisoformat(end).date()
#                         remaining_days = max(0, (ed - TODAY).days)
#                     except:
#                         remaining_days = 0.0
#                 else:
#                     remaining_days = 0.0

#             # baseline_velocity: CSV -> infer from completion & remaining_days -> default 1
#             if ds_vel and r.get(ds_vel) not in [None, ""]:
#                 baseline_velocity = safe_float(r.get(ds_vel), default=1.0)
#             else:
#                 try:
#                     if remaining_days > 0:
#                         baseline_velocity = max(0.1, (100.0 - completion) / remaining_days)
#                     else:
#                         baseline_velocity = 1.0
#                 except:
#                     baseline_velocity = 1.0

#             # baseline_fte: CSV or default 1.0
#             if ds_fte and r.get(ds_fte) not in [None, ""]:
#                 baseline_fte = safe_float(r.get(ds_fte), default=1.0)
#             else:
#                 baseline_fte = 1.0

#             # projected_completion: CSV or equal to completion
#             if ds_proj and r.get(ds_proj) not in [None, ""]:
#                 projected_completion = safe_float(r.get(ds_proj), default=completion)
#             else:
#                 projected_completion = completion

#             # risk_score: CSV or heuristics (lower completion -> higher risk)
#             if ds_risk and r.get(ds_risk) not in [None, ""]:
#                 risk_score = safe_float(r.get(ds_risk), default=5.0)
#             else:
#                 try:
#                     risk_score = max(1.0, min(10.0, 10 - completion/12))  # simple mapping
#                 except:
#                     risk_score = 5.0

#             recs.append((
#                 name, status, phase, completion, manager, department, region, ptype,
#                 cost, benefit, start, end, complexity, description,
#                 duration_days, remaining_days, baseline_velocity, baseline_fte,
#                 projected_completion, risk_score
#             ))

#         # insert into DB
#         if recs:
#             cur.executemany("""
#                 INSERT OR IGNORE INTO projects
#                 (name,status,phase,completion,manager,department,region,type,cost,benefit,start_date,end_date,complexity,description,
#                  duration_days, remaining_days, baseline_velocity, baseline_fte, projected_completion, risk_score)
#                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#             """, recs)
#             conn.commit()

#     conn.close()
# # Part 2 of 3
# # ---------- Fetch Projects ----------
# def df_projects(include_archived=False):
#     conn = get_conn()
#     q = "SELECT * FROM projects" + ("" if include_archived else " WHERE archived=0")
#     df = pd.read_sql_query(q, conn)
#     conn.close()
#     return df

# # ---------- Update Project Row (REPLACED: now auto-computes DS fields before write) ----------
# def upsert_project(row):
#     """
#     Upsert project into DB. Automatically computes and writes decision-support
#     fields (duration_days, remaining_days, baseline_velocity, baseline_fte,
#     projected_completion, risk_score) so Alerts/Visuals always reflect current values.
#     """
#     # compute DS values (this will use start_date, end_date, completion if present)
#     ds = compute_ds_fields_for_row(row)

#     conn = get_conn()
#     cur = conn.cursor()

#     if row.get("id"):
#         cur.execute("""
#             UPDATE projects SET
#                 name=?, status=?, phase=?, completion=?, manager=?, department=?, region=?, type=?,
#                 cost=?, benefit=?, start_date=?, end_date=?, complexity=?, description=?,
#                 duration_days=?, remaining_days=?, baseline_velocity=?, baseline_fte=?,
#                 projected_completion=?, risk_score=? WHERE id=?
#         """, (
#             row.get("name"), row.get("status"), row.get("phase"), float(row.get("completion") or 0),
#             row.get("manager"), row.get("department"), row.get("region"), row.get("type"),
#             float(row.get("cost") or 0), float(row.get("benefit") or 0),
#             row.get("start_date"), row.get("end_date"), row.get("complexity"), row.get("description"),
#             ds["duration_days"], ds["remaining_days"], ds["baseline_velocity"], ds["baseline_fte"],
#             ds["projected_completion"], ds["risk_score"],
#             int(row.get("id"))
#         ))
#     else:
#         cur.execute("""
#             INSERT INTO projects
#             (name,status,phase,completion,manager,department,region,type,cost,benefit,start_date,end_date,complexity,description,
#              duration_days, remaining_days, baseline_velocity, baseline_fte, projected_completion, risk_score)
#             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
#         """, (
#             row.get("name"), row.get("status"), row.get("phase"), float(row.get("completion") or 0),
#             row.get("manager"), row.get("department"), row.get("region"), row.get("type"),
#             float(row.get("cost") or 0), float(row.get("benefit") or 0),
#             row.get("start_date"), row.get("end_date"), row.get("complexity"), row.get("description"),
#             ds["duration_days"], ds["remaining_days"], ds["baseline_velocity"], ds["baseline_fte"],
#             ds["projected_completion"], ds["risk_score"]
#         ))

#     conn.commit()
#     conn.close()

# # ---------- Announcements ----------
# def post_announcement(title, body):
#     conn = get_conn()
#     cur = conn.cursor()
#     cur.execute("INSERT INTO announcements (created_at,title,body) VALUES (?,?,?)",
#                 (datetime.now().strftime("%Y-%m-%d %H:%M"), title, body))
#     conn.commit()
#     conn.close()

# def df_announcements():
#     conn = get_conn()
#     df = pd.read_sql_query("SELECT * FROM announcements ORDER BY id DESC", conn)
#     conn.close()
#     return df

# # ---------- First Run Sidebar ----------
# with st.sidebar:
#     st.subheader("First-run options")
#     modernize = st.checkbox("Modernize dates (shift around today) on first seed", value=True)
#     if st.button("Initialize database"):
#         if os.path.exists(DB_PATH):
#             os.remove(DB_PATH)
#         init_db(modernize=modernize)
#         st.success("Database initialized ✅. Reload the page.")

# # Ensure DB exists
# if not os.path.exists(DB_PATH):
#     init_db(modernize=True)

# # ---------- Tabs ----------
# tab_proj, tab_alerts, tab_visuals, tab_ds, tab_chat, tab_ann = st.tabs([
#     "🗂 Projects", "⏰ Alerts", "📊 Visuals", "🧠 Decision Support", "💬 Chat", "📣 Announcements"
# ])

# # =====================================================================================
# # 🗂 PROJECTS TAB (CRUD)
# # =====================================================================================
# with tab_proj:
#     st.subheader("Add / Edit Project")

#     with st.form("new_project"):
#         c1, c2, c3 = st.columns(3)

#         # Column 1
#         with c1:
#             name = st.text_input("Project Name*")
#             status = st.selectbox("Status", ["In - Progress", "On - Hold", "Completed", "Cancelled"])
#             phase = st.selectbox("Phase", [
#                 "Phase 1 - Explore", "Phase 2 - Plan", "Phase 3 - Design", "Phase 4 - Implement", "Phase 5 - Close"
#             ])
#             completion = st.slider("Completion %", 0, 100, 0)

#         # Column 2
#         with c2:
#             manager = st.text_input("Project Manager")
#             department = st.text_input("Department")
#             region = st.text_input("Region")
#             ptype = st.text_input("Project Type")

#         # Column 3
#         with c3:
#             cost = st.number_input("Project Cost", min_value=0, value=0, step=1000)
#             benefit = st.number_input("Project Benefit", min_value=0, value=0, step=1000)
#             start_date = st.date_input("Start Date", value=TODAY)
#             end_date = st.date_input("End Date", value=TODAY + timedelta(days=30))

#         # Single line
#         desc = st.text_area("Project Description")
#         complexity = st.selectbox("Complexity", ["Low", "Medium", "High"])

#         # NEW DECISION SUPPORT INPUTS
#         st.markdown("### 🧠 Decision-Support Fields")
#         dc1, dc2, dc3 = st.columns(3)
#         with dc1:
#             duration_days = st.number_input("Duration (days)", min_value=0, value=0)
#             remaining_days = st.number_input("Remaining Days", min_value=0, value=0)

#         with dc2:
#             baseline_velocity = st.number_input("Baseline Velocity (units/day)", min_value=0.0, value=0.0)
#             baseline_fte = st.number_input("Baseline FTE", min_value=0.0, value=1.0)

#         with dc3:
#             projected_completion = st.number_input("Projected Completion %", min_value=0, value=0)
#             risk_score = st.number_input("Risk Score (1–10)", min_value=1, max_value=10, value=5)

#         submitted = st.form_submit_button("Create Project")

#         if submitted:
#             if not name.strip():
#                 st.error("Name is required.")
#             else:
#                 row = dict(
#                     name=name.strip(), status=status, phase=phase, completion=completion,
#                     manager=manager, department=department, region=region, type=ptype,
#                     cost=cost, benefit=benefit, start_date=str(start_date), end_date=str(end_date),
#                     complexity=complexity, description=desc,
#                     duration_days=duration_days,
#                     remaining_days=remaining_days,
#                     baseline_velocity=baseline_velocity,
#                     baseline_fte=baseline_fte,
#                     projected_completion=projected_completion,
#                     risk_score=risk_score
#                 )
#                 upsert_project(row)
#                 st.success("Project created 🎉")

#     st.markdown("---")

#     st.subheader("Inline Edit")
#     df = df_projects()

#     if len(df) == 0:
#         st.info("No projects yet. Add one above.")
#     else:
#         show = df.copy()
#         show["deadline_bucket"] = show["end_date"].apply(bucket_for_date)

#         edited = st.data_editor(show, num_rows="dynamic", use_container_width=True, key="editor")

#         if st.button("Save changes"):
#             for _, r in edited.iterrows():
#                 upsert_project(r.to_dict())
#             st.success("Saved changes! ✅")
# # Part 3 of 3
# # =====================================================================================
# # ⏰ ALERTS TAB
# # =====================================================================================
# with tab_alerts:
#     st.subheader("Due‑date Alerts")
#     df = df_projects()
#     if len(df)==0:
#         st.info("No projects to analyze yet.")
#     else:
#         df["deadline_bucket"] = df["end_date"].apply(bucket_for_date)
#         buckets = ["Overdue","Today","Tomorrow","Next 7 days","Next 30 days"]
#         cols = st.columns(len(buckets))
#         for i,b in enumerate(buckets):
#             with cols[i]:
#                 st.metric(b, int((df["deadline_bucket"]==b).sum()))

#         st.markdown("#### Details")
#         choice = st.selectbox("Which bucket?", buckets, index=0)
#         view = df[df["deadline_bucket"]==choice]
#         st.dataframe(view[["name","status","manager","completion","end_date","deadline_bucket","department","region"]], use_container_width=True)

#         digest = "\n".join([
#             f"- {r['name']} — {r['status']} | PM {r['manager']} | {int(r['completion'] or 0)}% | due {r['end_date']} ({r['deadline_bucket']})"
#             for _, r in view.iterrows()
#         ]) or "No items."
#         if st.button("Post digest to Announcements"):
#             post_announcement(f"[ALERT] {choice} — {len(view)} project(s)", digest)
#             st.success("Digest posted 📣")
#         st.text_area("Digest preview", value=digest, height=150)




#         # ---------------- Manager custom announcement ----------------
#         st.markdown("### ✉️ Post a custom announcement")
#         ann_title = st.text_input("Announcement title", value=f"[TEAM] {choice} update")
#         ann_body = st.text_area("Message to post (will appear in Announcements)", value="")

#         if st.button("Send announcement"):
#             if not ann_title.strip():
#                 st.error("Please provide a title for the announcement.")
#             elif not ann_body.strip():
#                 st.error("Please write a message to post.")
#             else:
#                 post_announcement(ann_title.strip(), ann_body.strip())
#                 st.success("Announcement posted and will appear in Announcements tab ✅")

# # =====================================================================================
# # 📊 VISUALS TAB
# # =====================================================================================
# with tab_visuals:
#     st.subheader("Portfolio Visuals")
#     df = df_projects()

#     if len(df) == 0:
#         st.info("No project data available.")
#     else:
#         df["deadline_bucket"] = df["end_date"].apply(bucket_for_date)

#         c1, c2, c3 = st.columns(3)
#         with c1:
#             st.metric("Total Projects", len(df))
#         with c2:
#             st.metric("Active", int(df["status"].isin(["In - Progress", "On - Hold"]).sum()))
#         with c3:
#             st.metric("Overdue", int(df["deadline_bucket"].eq("Overdue").sum()))

#         st.markdown("### Status Distribution")
#         st.bar_chart(df["status"].value_counts())

#         st.markdown("### Completion Buckets")
#         bins = pd.cut(df["completion"], bins=[0, 25, 50, 75, 100], include_lowest=True).astype(str)
#         st.bar_chart(bins.value_counts())

#         st.markdown("### Cost vs Benefit (Bubble → Completion)")
#         plot_df = df.copy()
#         plot_df["size"] = plot_df["completion"].fillna(0) + 5
#         st.scatter_chart(plot_df, x="cost", y="benefit", size="size", color="status")

# # =====================================================================================
# # 🧠 DECISION SUPPORT TAB  (fixed)
# # =====================================================================================
# with tab_ds:
#     st.subheader("🧠 Decision Support — What-If Analysis")

#     df = df_projects()
#     if len(df) == 0:
#         st.info("No projects available.")
#     else:
#         # build safe project list (exclude blanks / None)
#         project_list = df["name"].astype(str).fillna("").str.strip()
#         project_list = [p for p in project_list.tolist() if p != ""]
#         if not project_list:
#             st.error("No project names found in DB. Re-initialize database.")
#         else:
#             selected = st.selectbox("Choose a project", ["None"] + project_list, index=0)
#             if selected == "None":
#                 st.info("Choose a project to run scenarios.")
#             else:
#                 # match row safely (case-insensitive, trimmed)
#                 row_df = df[df["name"].astype(str).str.strip().str.lower() == selected.strip().lower()]
#                 if row_df.empty:
#                     st.error("⚠ Project not found in database. Try re-initializing the database.")
#                     st.stop()

#                 r = row_df.iloc[0]

#                 # safe extractions with defaults
#                 comp_val = safe_int(r.get("completion", 0), default=0)
#                 remaining_days = safe_float(r.get("remaining_days", 0), default=0)
#                 baseline_velocity = safe_float(r.get("baseline_velocity", 1.0), default=1.0)
#                 baseline_fte = safe_float(r.get("baseline_fte", 1.0), default=1.0)
#                 proj_comp = safe_float(r.get("projected_completion", comp_val), default=comp_val)
#                 risk_score = safe_float(r.get("risk_score", 5.0), default=5.0)

#                 # Snapshot
#                 st.markdown(f"### 📌 Current Snapshot of **{selected}**")
#                 colA, colB, colC = st.columns(3)
#                 with colA:
#                     st.metric("Completion", f"{comp_val}%")
#                     st.metric("Remaining Days", int(remaining_days or 0))
#                 with colB:
#                     st.metric("Velocity", f"{baseline_velocity:.2f} units/day")
#                     st.metric("FTE", f"{baseline_fte:.1f}")
#                 with colC:
#                     st.metric("Projected Completion", f"{int(proj_comp)}%")
#                     st.metric("Risk Score", f"{int(risk_score)} / 10")

#                 st.markdown("---")
#                 st.markdown("### 🔍 Run a What-If Scenario")

#                 scenario = st.radio(
#                     "Select Scenario",
#                     [
#                         "Increase budget",
#                         "Add extra FTE",
#                         "Increase velocity",
#                         "Reduce remaining duration",
#                         "Predict risk from completion level"
#                     ]
#                 )

#                 out = ""
#                 if scenario == "Increase budget":
#                     pct = st.slider("Increase Budget (%)", 0, 100, 20)
#                     new_velocity = baseline_velocity * (1 + pct/100 * 0.3)
#                     new_proj = min(100, int(proj_comp + pct * 0.4))
#                     out = f"""
#                     ### 💡 Prediction  
#                     Increasing budget by **{pct}%** yields:
#                     - 🔼 Velocity → **{new_velocity:.2f} units/day**
#                     - ⏳ New projected completion → **{new_proj}%**
#                     """

#                 elif scenario == "Add extra FTE":
#                     fte = st.number_input("Add FTE", min_value=0.0, value=1.0)
#                     base_vel = baseline_velocity
#                     base_fte = baseline_fte if baseline_fte > 0 else 1.0
#                     new_velocity = base_vel * (1 + (fte / (base_fte + 0.001)))
#                     # avoid division by zero
#                     if new_velocity <= 0 or base_vel <= 0:
#                         new_remaining = remaining_days
#                     else:
#                         new_remaining = max(1, remaining_days * (base_vel / new_velocity))
#                     out = f"""
#                     ### 👨‍💼 Workforce Impact  
#                     Adding **{fte} FTE** results in:
#                     - 🔼 Velocity → **{new_velocity:.2f}**
#                     - 🗓 Reduced remaining days → **{int(new_remaining)}**
#                     """

#                 elif scenario == "Increase velocity":
#                     vel = st.slider("Velocity Increase (%)", 0, 200, 50)
#                     base_vel = baseline_velocity if baseline_velocity > 0 else 1.0
#                     new_velocity = base_vel * (1 + vel/100)
#                     if new_velocity <= 0:
#                         new_remaining = remaining_days
#                     else:
#                         new_remaining = max(1, remaining_days * (base_vel / new_velocity))
#                     out = f"""
#                     ### ⚡ Speed Simulation  
#                     Velocity +{vel}%:
#                     - New Velocity → **{new_velocity:.2f}**
#                     - New Remaining Days → **{int(new_remaining)}**
#                     """

#                 elif scenario == "Reduce remaining duration":
#                     cut = st.slider("Reduce Remaining Days (%)", 0, 80, 20)
#                     new_remaining = int(max(0, remaining_days * (1 - cut/100)))
#                     new_completion = min(100, int(comp_val + cut * 0.6))
#                     out = f"""
#                     ### ⏳ Timeline Compression  
#                     Duration -{cut}%:
#                     - New Remaining Days → **{new_remaining}**
#                     - New Completion Forecast → **{new_completion}%**
#                     """

#                 elif scenario == "Predict risk from completion level":
#                     comp = st.slider("Completion (%)", 0, 100, comp_val)
#                     predicted_risk = max(1, min(10, int(10 - comp/12)))
#                     out = f"""
#                     ### ⚠ Risk Forecast  
#                     At **{comp}% completion**:
#                     - Predicted Risk Score → **{predicted_risk}/10**
#                     """

#                 st.markdown(out)

# # =====================================================================================
# # 💬 CHAT TAB  (unchanged logic, safe accesses)
# # =====================================================================================
# def say(text):
#     return "✨ " + text

# STATUS_SYNS = {
#     "In - Progress": ["in progress","in-progress","ongoing","active","working","ip","progress"],
#     "On - Hold": ["on hold","paused","stalled","hold","onhold"],
#     "Completed": ["completed","done","finished","complete"],
#     "Cancelled": ["cancelled","canceled","dropped","abandoned"]
# }

# METRIC_SYNS = {
#   "status": ["status","state"],
#   "cost": ["cost","budget","price","how much"],
#   "benefit": ["benefit","roi","value","gain"],
#   "manager": ["manager","managed by","pm"],
#   "start": ["start","start date","begin"],
#   "end": ["end","deadline","finish","end date","due"],
#   "duration": ["duration","how long","length"],
#   "completion": ["completion","percent","progress"],
#   "complexity": ["complexity","difficulty"],
#   "department": ["department","dept","team"],
#   "region": ["region","geo","area"],
#   "type": ["project type","type","category"],
#   "description": ["description","details","about","what is"],
# }

# def _norm(s):
#     return re.sub(r"[^a-z0-9%.\- ]+", " ", s.lower()).strip()

# def _fuzzy_project(text, names):
#     t = text.lower()
#     for n in sorted(names, key=lambda x: -len(str(x))):
#         if str(n).lower() in t:
#             return n
#     toks = set(re.split(r"[^a-z0-9]+", t))
#     best = None; score = -1
#     for n in names:
#         nl = str(n).lower()
#         s = sum(1 for w in toks if w in nl)
#         if s > score:
#             best, score = n, s
#     return best if score > 0 else None

# def _metric_of(text):
#     t = _norm(text)
#     for k, syn in METRIC_SYNS.items():
#         if k in t or any(s in t for s in syn):
#             return k
#     return None

# with tab_chat:
#     st.subheader("Chat")

#     if "chat" not in st.session_state:
#         st.session_state.chat = []
#     if "last_project" not in st.session_state:
#         st.session_state.last_project = None

#     # Chat history
#     for msg in st.session_state.chat:
#         with st.chat_message(msg["role"]):
#             st.markdown(msg["content"])

#     prompt = st.chat_input("Ask me anything about your projects")

#     if prompt:
#         st.session_state.chat.append({"role": "user", "content": prompt})

#         df_all = df_projects()
#         names = df_all["name"].dropna().tolist()

#         p = _fuzzy_project(prompt, names)
#         m = _metric_of(prompt)

#         out = ""
#         # -------------- Metric responses --------------
#         if p and m:
#             row = df_all[df_all["name"].astype(str).str.lower() == str(p).strip().lower()]
#             if not row.empty:
#                 r = row.iloc[0]
#                 value_map = {
#                     "status": r.get("status"),
#                     "cost": money(r.get("cost")),
#                     "benefit": money(r.get("benefit")),
#                     "manager": r.get("manager"),
#                     "start": r.get("start_date"),
#                     "end": r.get("end_date"),
#                     "duration": r.get("duration_days"),
#                     "completion": f"{int(r.get('completion') or 0)}%",
#                     "complexity": r.get("complexity"),
#                     "department": r.get("department"),
#                     "region": r.get("region"),
#                     "type": r.get("type"),
#                     "description": r.get("description")
#                 }
#                 out = say(f"{m.upper()} of **{p}** → {value_map.get(m, '—')}")
#             else:
#                 out = say("Couldn't find that project.")

#         # -------------- Project Details --------------
#         elif p and "details" in prompt.lower():
#             row = df_all[df_all["name"].astype(str).str.lower() == str(p).strip().lower()]
#             if not row.empty:
#                 r = row.iloc[0]
#                 out = say(
#                     f"**{p}** details:\n"
#                     f"- Status: {r.get('status')}\n"
#                     f"- Completion: {int(r.get('completion') or 0)}%\n"
#                     f"- Manager: {r.get('manager')}\n"
#                     f"- Cost: {money(r.get('cost'))}\n"
#                     f"- Duration: {r.get('duration_days')} days\n"
#                     f"- Remaining: {r.get('remaining_days')} days\n"
#                     f"- Risk Score: {r.get('risk_score')}"
#                 )
#             else:
#                 out = say("Couldn't find that project.")

#         else:
#             out = say("Try asking: **status of Rhinestone**, **cost of project X**, **details of 'Blue Bird'**")

#         st.session_state.chat.append({"role": "assistant", "content": out})

#         with st.chat_message("assistant"):
#             st.markdown(out)

# # =====================================================================================
# # 📣 ANNOUNCEMENTS
# # =====================================================================================
# with tab_ann:
#     st.subheader("Announcements")
#     ann = df_announcements()
#     if len(ann) == 0:
#         st.caption("Nothing posted yet. Use Alerts to post a digest.")
#     else:
#         for _, row in ann.iterrows():
#             st.markdown(f"**{row['title']}**  \n_{row['created_at']}_  \n{row['body']}")
#             st.divider()








#firrrrrrssssssstttttccoooodeeeeee







































import streamlit as st
import pandas as pd
import sqlite3, re, random, os
from datetime import date, datetime, timedelta

st.set_page_config(page_title="Project Copilot — Tracker v3", layout="wide")
st.title("📈 Project Copilot — Tracker (v3)")

DB_PATH = "projects.db"
CSV_PATH = "projects_seed.csv"
TODAY = date.today()

# ---------- Utils ----------
def parse_money(x):
    if x is None or (isinstance(x,float) and pd.isna(x)): return 0.0
    s = str(x).strip().replace(",", "")
    try: return float(s)
    except: return 0.0

def parse_pct(x):
    if x is None or (isinstance(x,float) and pd.isna(x)): return 0.0
    s = str(x).strip().replace("%","")
    try: return float(s)
    except: return 0.0

def parse_date(x):
    if not x or (isinstance(x,float) and pd.isna(x)): return None
    s = str(x).strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%d-%b-%Y", "%b %d, %Y"):
        try: return datetime.strptime(s, fmt).date().isoformat()
        except: pass
    try:
        return pd.to_datetime(s, errors="coerce").date().isoformat()
    except:
        return None

def bucket_for_date(end_date: str):
    if not end_date: return "—"
    try: d = datetime.fromisoformat(str(end_date)).date()
    except: return "—"
    delta = (d - TODAY).days
    if delta < 0: return "Overdue"
    if delta == 0: return "Today"
    if delta == 1: return "Tomorrow"
    if delta <= 7: return "Next 7 days"
    if delta <= 30: return "Next 30 days"
    return "Later"

def money(n):
    try: return f"₹{int(float(n)):,}"
    except: return "—"

# ---------- DB ----------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(modernize=False):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        status TEXT,
        phase TEXT,
        completion REAL,
        manager TEXT,
        department TEXT,
        region TEXT,
        type TEXT,
        cost REAL,
        benefit REAL,
        start_date TEXT,
        end_date TEXT,
        complexity TEXT,
        description TEXT,
        archived INTEGER DEFAULT 0
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS announcements(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        title TEXT,
        body TEXT
    )""")
    conn.commit()

    # Seed if empty
    cur.execute("SELECT COUNT(*) FROM projects")
    if cur.fetchone()[0]==0:
        df = pd.read_csv(CSV_PATH)
        df.columns = [c.strip() for c in df.columns]

        # ---------------------------
        # Safe column mapping (robust to small header differences)
        # ---------------------------
        def pick(target, df_columns):
            tc = target.replace(" ", "").replace("_", "").lower()
            for c in df_columns:
                if c is None: continue
                cc = str(c).replace(" ", "").replace("_", "").lower()
                if cc == tc:
                    return c
            # fallback: check token containment
            for c in df_columns:
                if c is None: continue
                cc = str(c).replace(" ", "").replace("_", "").lower()
                if tc in cc or cc in tc:
                    return c
            # last resort: try partial match on important words
            tparts = [p for p in re.split(r'[^a-z0-9]+', tc) if p]
            if not tparts:
                return None
            best = None; best_score = 0
            for c in df_columns:
                if c is None: continue
                cc = str(c).replace(" ", "").replace("_", "").lower()
                score = sum(1 for p in tparts if p in cc)
                if score > best_score:
                    best_score = score; best = c
            return best if best_score>0 else None

        cols = list(df.columns)
        name_col       = pick("Project Name", cols) or pick("name", cols)
        status_col     = pick("Status", cols) or pick("status", cols)
        phase_col      = pick("Phase", cols) or pick("phase", cols)
        completion_col = pick("Completion%", cols) or pick("Completion", cols) or pick("completion", cols)
        manager_col    = pick("Project Manager", cols) or pick("Manager", cols) or pick("projectmanager", cols)
        dept_col       = pick("Department", cols) or pick("Dept", cols) or pick("department", cols)
        region_col     = pick("Region", cols) or pick("region", cols)
        type_col       = pick("Project Type", cols) or pick("Type", cols) or pick("projecttype", cols)
        cost_col       = pick("Project Cost", cols) or pick("Cost", cols) or pick("projectcost", cols)
        benefit_col    = pick("Project Benefit", cols) or pick("Benefit", cols) or pick("projectbenefit", cols)
        start_col      = pick("Start Date", cols) or pick("StartDate", cols) or pick("start_date", cols) or pick("startdate", cols)
        end_col        = pick("End Date", cols) or pick("EndDate", cols) or pick("end_date", cols) or pick("enddate", cols)
        comp_col       = pick("Complexity", cols) or pick("complexity", cols)
        desc_col       = pick("Project Description", cols) or pick("Description", cols) or pick("projectdescription", cols)

        # If you want to debug mapping, temporarily uncomment this:
        # st.write("Detected columns:", dict(
        #     name_col=name_col, status_col=status_col, phase_col=phase_col,
        #     completion_col=completion_col, manager_col=manager_col, dept_col=dept_col,
        #     region_col=region_col, type_col=type_col, cost_col=cost_col,
        #     benefit_col=benefit_col, start_col=start_col, end_col=end_col,
        #     comp_col=comp_col, desc_col=desc_col
        # ))

        recs = []
        base = TODAY
        for _, r in df.iterrows():
            # safe getters: only attempt get if column name was found
            start_raw = r.get(start_col) if start_col else None
            end_raw   = r.get(end_col) if end_col else None
            start = parse_date(start_raw) if start_raw else None
            end = parse_date(end_raw) if end_raw else None

            if modernize:
                # Shift around today: random offsets
                try:
                    dur = ( (datetime.fromisoformat(end).date() - datetime.fromisoformat(start).date()).days if start and end else random.randint(30, 180) )
                except:
                    dur = random.randint(30, 180)
                start = (base - timedelta(days=random.randint(0,60))).isoformat()
                end = (datetime.fromisoformat(start) + timedelta(days=dur)).date().isoformat()

            name_val = r.get(name_col) if name_col else None
            status_val = r.get(status_col) if status_col else None
            phase_val = r.get(phase_col) if phase_col else None
            completion_val = parse_pct(r.get(completion_col)) if completion_col else 0.0
            manager_val = r.get(manager_col) if manager_col else None
            dept_val = r.get(dept_col) if dept_col else None
            region_val = r.get(region_col) if region_col else None
            type_val = r.get(type_col) if type_col else None
            cost_val = parse_money(r.get(cost_col)) if cost_col else 0.0
            benefit_val = parse_money(r.get(benefit_col)) if benefit_col else 0.0
            comp_val = r.get(comp_col) if comp_col else None
            desc_val = r.get(desc_col) if desc_col else None

            recs.append((
                name_val,
                status_val,
                phase_val,
                completion_val,
                manager_val,
                dept_val,
                region_val,
                type_val,
                cost_val,
                benefit_val,
                start,
                end,
                comp_val,
                desc_val,
            ))
        cur.executemany("""INSERT OR IGNORE INTO projects
            (name,status,phase,completion,manager,department,region,type,cost,benefit,start_date,end_date,complexity,description)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", recs)
        conn.commit()
    conn.close()

def df_projects(include_archived=False):
    conn = get_conn()
    q = "SELECT * FROM projects" + ("" if include_archived else " WHERE archived=0")
    df = pd.read_sql_query(q, conn)
    conn.close()
    return df

def upsert_project(row):
    conn = get_conn()
    cur = conn.cursor()
    if row.get("id"):
        cur.execute("""UPDATE projects SET
            name=?, status=?, phase=?, completion=?, manager=?, department=?, region=?, type=?,
            cost=?, benefit=?, start_date=?, end_date=?, complexity=?, description=? WHERE id=?""",
            (row["name"], row["status"], row["phase"], float(row["completion"] or 0),
             row["manager"], row["department"], row["region"], row["type"],
             float(row["cost"] or 0), float(row["benefit"] or 0), row["start_date"], row["end_date"],
             row["complexity"], row["description"], int(row["id"])))
    else:
        cur.execute("""INSERT INTO projects
            (name,status,phase,completion,manager,department,region,type,cost,benefit,start_date,end_date,complexity,description)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (row["name"], row["status"], row["phase"], float(row["completion"] or 0),
             row["manager"], row["department"], row["region"], row["type"],
             float(row["cost"] or 0), float(row["benefit"] or 0), row["start_date"], row["end_date"],
             row["complexity"], row["description"]))
    conn.commit()
    conn.close()

def post_announcement(title, body):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO announcements (created_at,title,body) VALUES (?,?,?)",
                (datetime.now().strftime("%Y-%m-%d %H:%M"), title, body))
    conn.commit()
    conn.close()

def df_announcements():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM announcements ORDER BY id DESC", conn)
    conn.close()
    return df

# ---------- First run controls ----------
with st.sidebar:
    st.subheader("First-run options")
    modernize = st.checkbox("Modernize dates (shift around today) on first seed", value=True)
    if st.button("Initialize database"):
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        init_db(modernize=modernize)
        st.success("Database initialized ✅. Reload the page.")

# Always ensure DB exists
if not os.path.exists(DB_PATH):
    init_db(modernize=True)

# ---------- Tabs ----------
tab_proj, tab_alerts,tab_ds, tab_visuals, tab_chat, tab_ann = st.tabs(["🗂 Projects","⏰ Alerts","🧠Decision Support","📊 Visuals","💬 Chat","📣 Announcements"])

# ---------- Projects (CRUD) ----------
with tab_proj:
    st.subheader("Add / Edit Project")
    with st.form("new_project"):
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input("Project Name*")
            status = st.selectbox("Status", ["In - Progress","On - Hold","Completed","Cancelled"])
            phase = st.selectbox("Phase", ["Phase 1 - Explore","Phase 2 - Plan","Phase 3 - Design","Phase 4 - Implement","Phase 5 - Close"])
            completion = st.slider("Completion %", 0, 100, 0)
        with c2:
            manager = st.text_input("Project Manager")
            department = st.text_input("Department")
            region = st.text_input("Region")
            ptype = st.text_input("Project Type")
        with c3:
            cost = st.number_input("Project Cost", min_value=0, value=0, step=1000)
            benefit = st.number_input("Project Benefit", min_value=0, value=0, step=1000)
            start_date = st.date_input("Start Date", value=TODAY)
            end_date = st.date_input("End Date", value=TODAY + timedelta(days=30))
        desc = st.text_area("Project Description")
        complexity = st.selectbox("Complexity", ["Low","Medium","High"])
        submitted = st.form_submit_button("Create Project")
        if submitted:
            if not name.strip():
                st.error("Name is required.")
            else:
                row = dict(name=name.strip(), status=status, phase=phase, completion=completion,
                           manager=manager, department=department, region=region, type=ptype,
                           cost=cost, benefit=benefit, start_date=str(start_date), end_date=str(end_date),
                           complexity=complexity, description=desc)
                upsert_project(row)
                st.success("Project created 🎉")

    st.markdown("---")
    st.subheader("Inline Edit")
    df = df_projects()
    if len(df)==0:
        st.info("No projects yet. Use the form above to add one.")
    else:
        show = df.copy()
        show["deadline_bucket"] = show["end_date"].apply(bucket_for_date)
        show = show[["id","name","status","phase","completion","manager","department","region","type","cost","benefit","start_date","end_date","complexity","deadline_bucket","description"]]
        edited = st.data_editor(show, num_rows="dynamic", use_container_width=True, key="editor")
        if st.button("Save changes"):
            for _, r in edited.iterrows():
                upsert_project({
                    "id": int(r["id"]),
                    "name": r["name"],
                    "status": r["status"],
                    "phase": r["phase"],
                    "completion": r["completion"],
                    "manager": r["manager"],
                    "department": r["department"],
                    "region": r["region"],
                    "type": r["type"],
                    "cost": r["cost"],
                    "benefit": r["benefit"],
                    "start_date": r["start_date"],
                    "end_date": r["end_date"],
                    "complexity": r["complexity"],
                    "description": r["description"],
                })
            st.success("Saved ✅")

# ---------- Alerts ----------
with tab_alerts:
    st.subheader("Due-date Alerts")
    df = df_projects()
    if len(df)==0:
        st.info("No projects to analyze yet.")
    else:
        df["deadline_bucket"] = df["end_date"].apply(bucket_for_date)
        buckets = ["Overdue","Today","Tomorrow","Next 7 days","Next 30 days"]
        cols = st.columns(len(buckets))
        for i,b in enumerate(buckets):
            with cols[i]:
                st.metric(b, int((df["deadline_bucket"]==b).sum()))

        st.markdown("#### Details")
        choice = st.selectbox("Which bucket?", buckets, index=0)
        view = df[df["deadline_bucket"]==choice]
        st.dataframe(view[["name","status","manager","completion","end_date","deadline_bucket","department","region"]], use_container_width=True)

        digest = "\n".join([
            f"- {r['name']} — {r['status']} | PM {r['manager']} | {int(r['completion'] or 0)}% | due {r['end_date']} ({r['deadline_bucket']})"
            for _, r in view.iterrows()
        ]) or "No items."
        if st.button("Post digest to Announcements"):
            post_announcement(f"[ALERT] {choice} — {len(view)} project(s)", digest)
            st.success("Digest posted 📣")
        st.text_area("Digest preview", value=digest, height=150)

 # ---------------- Manager custom announcement ----------------
        st.markdown("### ✉️ Post a custom announcement")
        ann_title = st.text_input("Announcement title", value=f"[TEAM] {choice} update")
        ann_body = st.text_area("Message to post (will appear in Announcements)", value="")

        if st.button("Send announcement"):
            if not ann_title.strip():
                st.error("Please provide a title for the announcement.")
            elif not ann_body.strip():
                st.error("Please write a message to post.")
            else:
                post_announcement(ann_title.strip(), ann_body.strip())
                st.success("Announcement posted and will appear in Announcements tab ✅")

# ---------- Visuals ----------
with tab_visuals:
    st.subheader("Portfolio Visuals")
    df = df_projects()
    if len(df)==0:
        st.info("No data yet.")
    else:
        df["deadline_bucket"] = df["end_date"].apply(bucket_for_date)  # <-- FIX ensures column exists
        c1,c2,c3 = st.columns(3)
        with c1: st.metric("Total", len(df))
        with c2: st.metric("Active", int(df["status"].isin(["In - Progress","On - Hold"]).sum()))
        with c3: st.metric("Overdue", int(df["deadline_bucket"].eq("Overdue").sum()))

        st.markdown("### By Status")
        st.bar_chart(df["status"].value_counts())

        st.markdown("### Completion % (buckets)")
        bins = pd.cut(df["completion"], bins=[0,25,50,75,100], include_lowest=True).astype(str)
        st.bar_chart(bins.value_counts())

        st.markdown("### Cost vs Benefit (bubble ~ completion)")
        plot_df = df.copy()
        plot_df["size"] = plot_df["completion"].fillna(0) + 5
        st.scatter_chart(plot_df, x="cost", y="benefit", size="size", color="status")

        st.markdown("### Deadline Buckets")
        st.bar_chart(df["deadline_bucket"].value_counts())

# =========================
# 🧠 DECISION SUPPORT TAB
# =========================
with tab_ds:
    st.subheader("🧠 Decision Support — What-If Analysis")

    df = df_projects()
    if len(df) == 0:
        st.info("No projects available.")
    else:
        # safe project list (non-empty trimmed names)
        project_list = df["name"].astype(str).fillna("").str.strip()
        project_list = [p for p in project_list.tolist() if p != ""]
        if not project_list:
            st.error("No project names found in DB. Re-initialize database.")
        else:
            selected = st.selectbox("Choose a project", ["-- Select --"] + project_list, index=0)
            if selected == "-- Select --":
                st.info("Choose a project to run scenarios.")
            else:
                # pick the first matching row by trimmed lower-case name
                row_df = df[df["name"].astype(str).str.strip().str.lower() == selected.strip().lower()]
                if row_df.empty:
                    st.error("⚠ Project not found in database. Try re-initializing the database.")
                    st.stop()

                r = row_df.iloc[0]

                # --- helper safe conversions ---
                def _to_date(x):
                    try:
                        if x is None or (isinstance(x, float) and pd.isna(x)):
                            return None
                        return pd.to_datetime(x, errors="coerce").date()
                    except:
                        return None

                def _safe_float(val, default=0.0):
                    try:
                        if val is None: return float(default)
                        if isinstance(val, (int, float)) and not pd.isna(val):
                            return float(val)
                        s = str(val).strip().replace("%","").replace(",","")
                        if s == "": return float(default)
                        return float(s)
                    except:
                        return float(default)

                # parse fields
                start_dt = _to_date(r.get("start_date"))
                end_dt = _to_date(r.get("end_date"))
                completion = _safe_float(r.get("completion", 0.0), default=0.0)

                # compute duration and remaining days
                if start_dt and end_dt:
                    try:
                        duration_days = max(0, (end_dt - start_dt).days)
                    except:
                        duration_days = 0
                else:
                    duration_days = 0

                if end_dt:
                    try:
                        remaining_days = max(0, (end_dt - TODAY).days)
                    except:
                        remaining_days = 0
                else:
                    remaining_days = 0

                # baseline velocity heuristic (units of %-points per day)
                if remaining_days > 0:
                    baseline_velocity = max(0.01, (100.0 - completion) / remaining_days)
                else:
                    baseline_velocity = 1.0

                baseline_fte = 1.0  # dataset doesn't have explicit FTE; assume 1

                projected_completion = completion  # default
                # simple risk heuristic: lower completion => higher risk
                try:
                    risk_score = max(1, min(10, int(10 - completion / 12)))
                except:
                    risk_score = 5

                # Snapshot display
                st.markdown(f"### 📌 Snapshot — **{selected}**")
                ca, cb, cc = st.columns(3)
                with ca:
                    st.metric("Completion", f"{int(completion)}%")
                    st.metric("Duration (days)", int(duration_days))
                with cb:
                    st.metric("Remaining Days", int(remaining_days))
                    st.metric("Baseline Velocity (pp/day)", f"{baseline_velocity:.2f}")
                with cc:
                    st.metric("Projected Completion", f"{int(projected_completion)}%")
                    st.metric("Risk Score", f"{int(risk_score)} / 10")

                st.markdown("---")
                st.markdown("### 🔍 Run a What-If Scenario")

                scenario = st.radio(
                    "Select Scenario",
                    [
                        "Increase budget",
                        "Add extra FTE",
                        "Increase velocity",
                        "Reduce remaining duration",
                        "Predict risk from completion level"
                    ],
                    index=0
                )

                result_md = ""
                # Scenario calculations use only computed values above so nothing is None
                if scenario == "Increase budget":
                    pct = st.slider("Increase Budget (%)", 0, 200, 20)
                    # assume budget mainly improves velocity (30% of budget increase translates to velocity)
                    new_velocity = baseline_velocity * (1 + (pct / 100.0) * 0.3)
                    # simple projection: completion increases proportionally (conservative)
                    new_proj = min(100, completion + (pct * 0.4))
                    new_remaining = int(max(0, remaining_days * (baseline_velocity / new_velocity))) if new_velocity>0 else int(remaining_days)
                    result_md = (
                        f"### 💡 Prediction\n\n"
                        f"- Budget +{pct}% → Velocity **{new_velocity:.2f} pp/day**\n"
                        f"- Projected completion → **{int(new_proj)}%**\n"
                        f"- Estimated remaining days → **{new_remaining}**"
                    )

                elif scenario == "Add extra FTE":
                    add_fte = st.number_input("Add FTE", min_value=0.0, value=1.0, step=0.5)
                    # velocity scales roughly linearly with FTE (simple model)
                    base_fte = baseline_fte if baseline_fte > 0 else 1.0
                    new_velocity = baseline_velocity * (1 + (add_fte / (base_fte + 1e-6)))
                    new_remaining = int(max(0, remaining_days * (baseline_velocity / new_velocity))) if new_velocity>0 else int(remaining_days)
                    est_completion = min(100, completion + ( (baseline_velocity / new_velocity) * 0 ))  # completion change not directly computed here
                    result_md = (
                        f"### 👨‍💼 Workforce Impact\n\n"
                        f"- Adding **{add_fte} FTE** → Velocity **{new_velocity:.2f} pp/day**\n"
                        f"- New estimated remaining days → **{new_remaining}**\n"
                        f"- (Projected completion will move faster as work progresses.)"
                    )

                elif scenario == "Increase velocity":
                    pct = st.slider("Velocity Increase (%)", 0, 300, 50)
                    new_velocity = baseline_velocity * (1 + pct/100.0)
                    new_remaining = int(max(0, remaining_days * (baseline_velocity / new_velocity))) if new_velocity>0 else int(remaining_days)
                    result_md = (
                        f"### ⚡ Speed Simulation\n\n"
                        f"- Velocity +{pct}% → **{new_velocity:.2f} pp/day**\n"
                        f"- New Remaining Days → **{new_remaining}**"
                    )

                elif scenario == "Reduce remaining duration":
                    cut_pct = st.slider("Reduce Remaining Days (%)", 0, 90, 20)
                    new_remaining = int(max(0, remaining_days * (1 - cut_pct/100.0)))
                    # rough completion uplift proportional to time saved
                    new_completion = min(100, int(completion + (cut_pct * 0.6)))
                    result_md = (
                        f"### ⏳ Timeline Compression\n\n"
                        f"- Remaining days reduced by {cut_pct}% → **{new_remaining} days**\n"
                        f"- New completion forecast (approx) → **{new_completion}%**"
                    )

                elif scenario == "Predict risk from completion level":
                    comp_slider = st.slider("Completion (%)", 0, 100, int(completion))
                    predicted_risk = max(1, min(10, int(10 - comp_slider / 12)))
                    result_md = (
                        f"### ⚠ Risk Forecast\n\n"
                        f"- At **{comp_slider}%** completion → Predicted risk **{predicted_risk} / 10**"
                    )

                # render result
                st.markdown(result_md)

# ---------- Announcements ----------
with tab_ann:
    st.subheader("Announcements")
    ann = df_announcements()
    if len(ann)==0:
        st.caption("Nothing posted yet. Use Alerts to post a digest.")
    else:
        for _, row in ann.iterrows():
            st.markdown(f"**{row['title']}** — _{row['created_at']}_  \n{row['body']}")
            st.divider()

#---------- Chat (NLU, cheerful tone) ----------
def say(text): return "✨ " + text

STATUS_SYNS = {
    "In - Progress": ["in progress","in-progress","ongoing","active","working","ip","progress"],
    "On - Hold": ["on hold","paused","stalled","hold","onhold"],
    "Completed": ["completed","done","finished","complete"],
    "Cancelled": ["cancelled","canceled","dropped","abandoned"]
}
METRIC_SYNS = {
  "status": ["status","state","how's it going","how is it going"],
  "cost": ["cost","budget","price","how much"],
  "benefit": ["benefit","roi","value","gain"],
  "manager": ["manager","managed by","who manages","who is managing","who is the manager","pm"],
  "start": ["start","starts","start date","begin","kick off","kick-off"],
  "end": ["end","deadline","finish","ends","end date","due","finish date"],
  "duration": ["duration","how long","length"],
  "completion": ["completion","percent","percentage","completion%","progress","% done","percent done"],
  "complexity": ["complexity","difficulty"],
  "department": ["department","dept","team"],
  "region": ["region","geo","area"],
  "type": ["project type","type","category"],
  "description": ["description","details","about","what is","tell me about"],
}

def fuzzy_project(text, names):
    # quoted > contains > token overlap
    m = re.search(r'"([^"]+)"', text)
    if m:
        q = m.group(1).lower()
        best = max(names, key=lambda n: (n.lower()==q, n.lower().startswith(q), int(q in n.lower()), -abs(len(n)-len(q))), default=None)
        return best
    low = text.lower()
    for n in sorted(names, key=lambda x:-len(x)):
        if n.lower() in low: return n
    toks = [t for t in re.split(r"[^a-z0-9]+", low) if len(t)>=3]
    scores = []
    for n in names:
        nl = n.lower()
        s = sum(1 for t in toks if t in nl)
        scores.append((s,n))
    scores.sort(reverse=True)
    return scores[0][1] if scores and scores[0][0]>0 else None

def get_metric(text):
    t=text.lower()
    for m,syns in METRIC_SYNS.items():
        if m in t or any(s in t for s in syns):
            return m
    return None

with tab_chat:
    st.subheader("Chat")
    if "chat" not in st.session_state: st.session_state.chat = []
    if "last_project" not in st.session_state: st.session_state.last_project = None

    # show history
    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # helpers
    def _norm(s: str) -> str:
        return re.sub(r"[^a-z0-9%.\- ]+", " ", s.lower()).replace("  ", " ").strip()

    def _fuzzy_project(text, names):
        m = re.search(r'"([^"]+)"', text)
        if m:
            q = m.group(1).lower()
            return max(names, key=lambda n: (n.lower()==q, n.lower().startswith(q), int(q in n.lower()), -abs(len(n)-len(q))), default=None)
        t = text.lower()
        for n in sorted(names, key=lambda x: -len(x)):
            if n.lower() in t:
                return n
        toks = set([w for w in re.split(r"[^a-z0-9]+", t) if len(w) >= 3])
        best = None; score = -1
        for n in names:
            s = sum(1 for w in toks if w in n.lower())
            if s > score:
                best, score = n, s
        return best if score > 0 else (st.session_state.last_project or None)

    METRICS = {
        "status": ["status","state"],
        "cost": ["cost","budget","price","how much"],
        "benefit": ["benefit","roi","value","gain"],
        "manager": ["manager","managed by","pm","who manages","who is managing","who is the manager"],
        "start": ["start","starts","start date","begin","kick off","kick-off"],
        "end": ["end","deadline","finish","ends","end date","due","finish date","deadline date"],
        "duration": ["duration","how long","length"],
        "completion": ["completion","percent","percentage","completion%","progress","% done","percent done"],
        "complexity": ["complexity","difficulty"],
        "department": ["department","dept","team"],
        "region": ["region","geo","area"],
        "type": ["project type","type","category"],
        "description": ["description","details","about","what is","tell me about","project details","show details"],
    }

    def _metric_of(text):
        t = _norm(text)
        for k, syn in METRICS.items():
            if k in t or any(s in t for s in syn):
                return k
        return None

    def _year_in(text):
        m = re.search(r"\b(20\d{2})\b", text)
        return int(m.group(1)) if m else None

    def _threshold(text):
        m = re.search(r"over\s*([\d,]+)", text, re.I)
        if m: return float(m.group(1).replace(",",""))
        m = re.search(r">\s*(\d+)", text)
        if m: return float(m.group(1))
        m = re.search(r"(\d+)\s*%", text)
        if m: return float(m.group(1))
        return None

    def _say(txt): return "✨ " + txt

    prompt = st.chat_input("Ask anything about your projects (free phrasing).")
    if prompt:
        st.session_state.chat.append({"role":"user","content":prompt})
        df_all = df_projects()
        names = df_all["name"].dropna().tolist()
        t = _norm(prompt)

        # fun small talk
        if t in ["hi","hello","hey","yo","hola","hi there","hello there","good morning","good evening"]:
            out = _say("Hey! I'm your chatty project buddy 🤖✨. Ask me about any project or try **list in‑progress**.")
        else:
            p = _fuzzy_project(prompt, names)
            m = _metric_of(prompt)

            # combined (cost + manager)
            if p and ("cost" in t and "manager" in t):
                r = df_all[df_all["name"].str.lower()==p.lower()].head(1).iloc[0]
                out = _say(f"**{r['name']}** — PM **{r['manager']}**, Cost {money(r['cost'])}.")

            # single metric about a project
            elif p and m:
                r = df_all[df_all["name"].str.lower()==p.lower()].head(1).iloc[0]
                def _dur(s,e):
                    return f"{(pd.to_datetime(e)-pd.to_datetime(s)).days} days" if s and e else "—"
                values = {
                    "status": r["status"],
                    "cost": money(r["cost"]),
                    "benefit": money(r["benefit"]),
                    "manager": r["manager"],
                    "start": r["start_date"],
                    "end": r["end_date"],
                    "duration": _dur(r["start_date"], r["end_date"]),
                    "completion": f"{int(r['completion'] or 0)}%",
                    "complexity": r["complexity"],
                    "department": r["department"],
                    "region": r["region"],
                    "type": r["type"],
                    "description": r["description"] or "—",
                }
                out = _say(f"{m.upper()} of **{r['name']}** → {values.get(m, '—')}")

            # project details
            elif p and any(x in t for x in ["details","project details","tell me about","about","summary","summarize","show details","show me the project details"]):
                r = df_all[df_all["name"].str.lower()==p.lower()].head(1).iloc[0]
                buck = bucket_for_date(r["end_date"])
                out = _say(
                    "**"+r["name"]+"** — quick recap:\n"
                    f"- Status **{r['status']}**, Phase **{r['phase']}**, {int(r['completion'] or 0)}% complete\n"
                    f"- PM **{r['manager']}**, {r['department']} / {r['region']}\n"
                    f"- Type **{r['type']}**, Complexity **{r['complexity']}**\n"
                    f"- Cost {money(r['cost'])}, Benefit {money(r['benefit'])}\n"
                    f"- {r['start_date']} → {r['end_date']} — **{buck}**"
                )

            # lists by status
            elif any(w in t for w in ["in progress","in-progress","ongoing","active"]) and any(x in t for x in ["list","show","projects","details","all"]):
                rows = df_all[df_all["status"] == "In - Progress"]
                bullets = "\n".join([f"- {r['name']} — PM {r['manager']} — {int(r['completion'] or 0)}% — due {r['end_date']} ({bucket_for_date(r['end_date'])})" for _, r in rows.iterrows()]) or "_No matches._"
                out = _say(f"In‑Progress — {len(rows)}:\n" + bullets)

            elif ("on hold" in t or "paused" in t) and any(x in t for x in ["list","show","projects","details","all"]):
                rows = df_all[df_all["status"] == "On - Hold"]
                bullets = "\n".join([f"- {r['name']} — PM {r['manager']} — due {r['end_date']} ({bucket_for_date(r['end_date'])})" for _, r in rows.iterrows()]) or "_No matches._"
                out = _say(f"On‑Hold — {len(rows)}:\n" + bullets)

            elif "completed" in t and any(x in t for x in ["list","show","projects","details","all"]):
                rows = df_all[df_all["status"] == "Completed"]
                bullets = "\n".join([f"- {r['name']} — PM {r['manager']}" for _, r in rows.iterrows()]) or "_No matches._"
                out = _say(f"Completed — {len(rows)}:\n" + bullets)

            elif "cancelled" in t and any(x in t for x in ["list","show","projects","details","all","canceled"]):
                rows = df_all[df_all["status"] == "Cancelled"]
                bullets = "\n".join([f"- {r['name']} — PM {r['manager']}" for _, r in rows.iterrows()]) or "_No matches._"
                out = _say(f"Cancelled — {len(rows)}:\n" + bullets)

            # deadlines
            elif "today" in t and "deadline" in t:
                rows = df_all[df_all["end_date"].apply(bucket_for_date) == "Today"]
                bullets = "\n".join([f"- {r['name']} — PM {r['manager']} — {r['end_date']}" for _, r in rows.iterrows()]) or "_No items today._"
                out = _say("Today's deadlines:\n" + bullets)

            elif "tomorrow" in t and "deadline" in t:
                rows = df_all[df_all["end_date"].apply(bucket_for_date) == "Tomorrow"]
                bullets = "\n".join([f"- {r['name']} — PM {r['manager']} — {r['end_date']}" for _, r in rows.iterrows()]) or "_Nothing due tomorrow._"
                out = _say("Tomorrow's deadlines:\n" + bullets)

            elif ("upcoming" in t and "deadline" in t) or ("nearest" in t and "deadline" in t) or ("upcoming project deadlines" in t):
                rows = df_all[df_all["end_date"].apply(bucket_for_date).isin(["Today","Tomorrow","Next 7 days","Next 30 days"])]
                if rows.empty:
                    out = _say("No near deadlines.")
                else:
                    rows = rows.sort_values("end_date")
                    out = _say("Upcoming deadlines:\n" + "\n".join([f"- {r['name']} — {bucket_for_date(r['end_date'])} ({r['end_date']})" for _, r in rows.iterrows()]))

            # analytics (samples from your list)
            elif "how many" in t and "active" in t:
                out = _say(f"Active: {int(df_all['status'].isin(['In - Progress','On - Hold']).sum())} project(s).")

            elif "total number of projects" in t or "how many projects" in t:
                out = _say(f"Total: {len(df_all)} project(s).")

            elif "statuses" in t or "different project statuses" in t or "what are the statuses" in t:
                out = _say("Statuses: " + ", ".join(sorted(df_all["status"].dropna().unique())))

            elif "phases" in t or "available project phases" in t:
                out = _say("Phases: " + ", ".join(sorted(df_all["phase"].dropna().unique())))

            elif "income generation" in t and ("show" in t or "all" in t):
                rows = df_all[df_all["type"].str.lower()=="income generation"]
                bullets = "\n".join([f"- {r['name']} — {r['status']} — PM {r['manager']}" for _, r in rows.iterrows()]) or "_None_"
                out = _say("INCOME GENERATION:\n" + bullets)

            elif "phase 4" in t and "implement" in t:
                rows = df_all[df_all["phase"].str.lower()=="phase 4 - implement"]
                bullets = "\n".join([f"- {r['name']} — {r['status']}" for _, r in rows.iterrows()]) or "_None_"
                out = _say("Phase 4 - Implement:\n" + bullets)

            elif "managed by" in t:
                m2 = re.search(r"managed by\s+([a-z ]+)", t)
                if m2:
                    who = m2.group(1).strip()
                    rows = df_all[df_all["manager"].str.lower()==who]
                    bullets = "\n".join([f"- {r['name']} — {r['status']}" for _, r in rows.iterrows()]) or "_None_"
                    out = _say(f"Managed by {who.title()}:\n" + bullets)
                else:
                    out = _say("Tell me the manager name after 'managed by ...'")

            elif "west" in t and "region" in t:
                rows = df_all[df_all["region"].str.lower()=="west"]
                bullets = "\n".join([f"- {r['name']} — {r['status']}" for _, r in rows.iterrows()]) or "_None_"
                out = _say("West region:\n" + bullets)

            elif "ecommerce" in t and "department" in t:
                rows = df_all[df_all["department"].str.lower()=="ecommerce"]
                bullets = "\n".join([f"- {r['name']} — {r['status']}" for _, r in rows.iterrows()]) or "_None_"
                out = _say("eCommerce department:\n" + bullets)

            elif "total cost of all" in t and "completed" in t:
                total = df_all.loc[df_all["status"]=="Completed","cost"].sum()
                out = _say(f"Total cost (Completed): {money(total)}.")

            elif "department has the highest total project cost" in t:
                g = df_all.groupby("department")["cost"].sum().sort_values(ascending=False)
                out = _say(f"Highest spend dept: **{g.index[0]}** — {money(g.iloc[0])}.") if len(g)>0 else _say("No data.")

            elif "average completion percentage" in t and "north" in t:
                a = df_all.loc[df_all["region"].str.lower()=="north","completion"].mean()
                out = _say(f"Avg completion (North): {a:.1f}%.") if not pd.isna(a) else _say("No data.")

            elif "count the number of projects for each project type" in t:
                g = df_all.groupby("type").size()
                out = _say("\n".join([f"- {k}: {v}" for k,v in g.items()]))

            elif "project manager has the most projects" in t:
                g = df_all.groupby("manager").size().sort_values(ascending=False)
                out = _say(f"PM with most projects: **{g.index[0]}** — {int(g.iloc[0])}") if len(g)>0 else _say("No data.")

            elif "high complexity" in t and ("in progress" in t or "in - progress" in t):
                rows = df_all[(df_all["complexity"].str.lower()=="high") & (df_all["status"]=="In - Progress")]
                bullets = "\n".join([f"- {r['name']} — {int(r['completion'] or 0)}%" for _, r in rows.iterrows()]) or "_None_"
                out = _say("High complexity × In‑Progress:\n" + bullets)

            elif "highest project benefit" in t or ("best" in t and "benefit" in t):
                row = df_all.sort_values("benefit", ascending=False).head(1)
                bullets = "\n".join([f"- {r['name']} — Benefit {money(r['benefit'])}" for _, r in row.iterrows()]) or "_None_"
                out = _say("Top benefit:\n" + bullets)

            elif "best cost" in t or ("lowest" in t and "cost" in t):
                row = df_all.sort_values("cost", ascending=True).head(1)
                bullets = "\n".join([f"- {r['name']} — Cost {money(r['cost'])}" for _, r in row.iterrows()]) or "_None_"
                out = _say("Best (lowest) cost:\n" + bullets)

            elif "highest cost" in t or ("most" in t and "expensive" in t):
                row = df_all.sort_values("cost", ascending=False).head(1)
                bullets = "\n".join([f"- {r['name']} — Cost {money(r['cost'])}" for _, r in row.iterrows()]) or "_None_"
                out = _say("Highest cost:\n" + bullets)

            elif "best completion" in t or "highest completion" in t:
                row = df_all.sort_values("completion", ascending=False).head(1)
                bullets = "\n".join([f"- {r['name']} — {int(r['completion'] or 0)}%" for _, r in row.iterrows()]) or "_None_"
                out = _say("Best completion%:\n" + bullets)

            elif "short duration" in t or "shortest duration" in t or "quickest" in t:
                dur = (pd.to_datetime(df_all["end_date"]) - pd.to_datetime(df_all["start_date"])).dt.days
                row = df_all.iloc[dur.sort_values().index].head(1)
                bullets = "\n".join([f"- {r['name']} — {int((pd.to_datetime(r['end_date'])-pd.to_datetime(r['start_date'])).days)} days" for _, r in row.iterrows()]) or "_None_"
                out = _say("Shortest duration:\n" + bullets)

            elif "long duration" in t or "longest duration" in t or "slowest" in t:
                dur = (pd.to_datetime(df_all["end_date"]) - pd.to_datetime(df_all["start_date"])).dt.days
                row = df_all.iloc[dur.sort_values(ascending=False).index].head(1)
                bullets = "\n".join([f"- {r['name']} — {int((pd.to_datetime(r['end_date'])-pd.to_datetime(r['start_date'])).days)} days" for _, r in row.iterrows()]) or "_None_"
                out = _say("Longest duration:\n" + bullets)

            elif "active during the year" in t:
                y = _year_in(t) or 2021
                rows = df_all[(pd.to_datetime(df_all["start_date"]).dt.year<=y) & (pd.to_datetime(df_all["end_date"]).dt.year>=y)]
                bullets = "\n".join([f"- {r['name']} — {r['start_date']} → {r['end_date']}" for _, r in rows.iterrows()]) or "_None_"
                out = _say(f"Active during {y}:\n" + bullets)

            elif ("completion" in t and ">" in t) or ("completion%" in t and ">" in t) or ("greater than" in t and "completion" in t):
                th = _threshold(t) or 75
                rows = df_all[df_all["completion"]>th]
                bullets = "\n".join([f"- {r['name']} — {int(r['completion'] or 0)}%" for _, r in rows.iterrows()]) or "_None_"
                out = _say(f"Completion > {int(th)}%:\n" + bullets)

            elif "compare" in t and "income generation" in t and "cost reduction" in t:
                A = df_all[df_all["type"].str.lower()=="income generation"]; B = df_all[df_all["type"].str.lower()=="cost reduction"]
                out = _say(f"INCOME GENERATION — Avg Cost {money(A['cost'].mean())}, Avg Benefit {money(A['benefit'].mean())}\nCOST REDUCTION — Avg Cost {money(B['cost'].mean())}, Avg Benefit {money(B['benefit'].mean())}")

            elif "highest average completion" in t and "project manager" in t:
                g = df_all.groupby("manager")["completion"].mean().sort_values(ascending=False)
                out = _say(f"Highest avg Completion%: **{g.index[0]}** — {g.iloc[0]:.1f}%") if len(g)>0 else _say("No data.")

            elif "distribution of complexity" in t and "departments" in t:
                g = df_all.pivot_table(index="department", columns="complexity", values="id", aggfunc="count", fill_value=0)
                lines__=[f"- {dept} — " + ", ".join([f"{lvl}:{int(g.loc[dept,lvl])}" for lvl in sorted(g.columns)]) for dept in g.index]
                out = _say("Complexity × Department:\n" + "\n".join(lines__))

            elif "completed projects changed over the years" in t or ("years" in t and "completed" in t and "changed" in t):
                years=[2021,2022,2023]
                vals=[]
                for y in years:
                    m2 = df_all[(pd.to_datetime(df_all["start_date"]).dt.year<=y) & (pd.to_datetime(df_all["end_date"]).dt.year>=y) & (df_all["status"]=="Completed")]
                    vals.append((y, len(m2)))
                out = _say("Completed per year: " + ", ".join([f"{y}:{c}" for y,c in vals]))

            elif "average project duration" in t and "each project type" in t:
                dur = (pd.to_datetime(df_all["end_date"]) - pd.to_datetime(df_all["start_date"])).dt.days
                g = pd.concat([df_all["type"], dur], axis=1).groupby("type")[0].mean().round(1)
                out = _say("\n".join([f"- {k}: {v} days" for k,v in g.items()]))

            elif "cancelled" in t and ("completion% over" in t or "completion over" in t or (">" in t and "completion" in t)):
                th = _threshold(t) or 85
                rows = df_all[(df_all["status"]=="Cancelled") & (df_all["completion"]>th)]
                bullets = "\n".join([f"- {r['name']} — {int(r['completion'] or 0)}%" for _, r in rows.iterrows()]) or "_None_"
                out = _say(f"Cancelled with Completion > {int(th)}%:\n" + bullets)

            elif "managed by brenda chandler" in t and ("over" in t or "greater than" in t):
                rows = df_all[(df_all["manager"].str.lower()=="brenda chandler") & (df_all["cost"]>50000000)]
                bullets = "\n".join([f"- {r['name']} — Cost {money(r['cost'])}" for _, r in rows.iterrows()]) or "_None_"
                out = _say("Brenda Chandler — Cost > 50,000,000:\n" + bullets)

            elif "started in the year 2022" in t and "phase 1 - explore" in t:
                rows = df_all[(pd.to_datetime(df_all["start_date"]).dt.year==2022) & (df_all["phase"].str.lower()=="phase 1 - explore")]
                bullets = "\n".join([f"- {r['name']}" for _, r in rows.iterrows()]) or "_None_"
                out = _say("2022 × Phase 1 - Explore:\n" + bullets)

            else:
                out = _say("Try: **status of Rhinestone**, **list in‑progress**, **today's deadlines**, **details of 'A Triumph Of Softwares'**, or **cost + manager of Rhinestone**.")

            if p: st.session_state.last_project = p

        st.session_state.chat.append({"role":"assistant","content":out})
        with st.chat_message("assistant"):
            st.markdown(out)















































