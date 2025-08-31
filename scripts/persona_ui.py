# scripts/persona_ui.py
"""
Minimal Tkinter UI for managing MCP personas and credentials.

- No extra dependencies (stdlib only)
- Works on macOS/Windows/Linux (uses system keyring if available)
- Reads/updates the same personas index used by the CLI
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Optional

try:
    import tomllib
except Exception:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]

# Optional: keyring; UI still runs if missing
try:
    import keyring  # type: ignore
except Exception:  # pragma: no cover
    keyring = None  # type: ignore

# Project imports (no 3rd party)
from adif_mcp.personas import Persona, PersonaStore

UI_VERSION = "0.0.1"


# ----------------------------
# Helpers (SSOT-ish resolver)
# ----------------------------
def _personas_index_path() -> Path:
    """
    Resolve personas index path from pyproject (tool.adif.personas_index),
    otherwise: ~/.config/adif-mcp/personas.json
    """
    default = Path.home() / ".config" / "adif-mcp" / "personas.json"

    # Look upward for a pyproject.toml
    here = Path.cwd()
    for p in [*here.parents, here]:
        pj = p / "pyproject.toml"
        if pj.exists():
            try:
                if tomllib is None:
                    break
                data = tomllib.loads(pj.read_text(encoding="utf-8"))
                tool = data.get("tool", {})
                adif = tool.get("adif", {})
                custom = adif.get("personas_index")
                if custom:
                    return (pj.parent / custom).resolve()
            except Exception:
                pass
            break
    return default


def _mask(u: str) -> str:
    if not u:
        return "—"
    if len(u) <= 2:
        return "*" * len(u)
    return f"{u[0]}***{u[-1]}"


def _validate_span(start: str, end: str) -> Optional[str]:
    """Return error message or None if ok."""
    if not start and not end:
        return None
    try:
        from datetime import date

        s = date.fromisoformat(start) if start else None
        e = date.fromisoformat(end) if end else None
        if s and e and e < s:
            return "End date cannot be earlier than start date."
    except Exception:
        return "Dates must be YYYY-MM-DD."
    return None


# -------------
# Main window
# -------------
class PersonaUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"ADIF MCP – Personas {UI_VERSION}")
        self.geometry("720x520")
        self.resizable(True, True)

        self.store = PersonaStore(_personas_index_path())

        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.page_creds = ProvidersPage(self, self.store)
        self.page_personas = PersonasPage(self, self.store, on_select=self._on_select)
        nb.add(self.page_personas, text="Personas")
        nb.add(self.page_creds, text="Providers")

        # Footer
        footer = ttk.Frame(self)
        footer.pack(fill=tk.X, padx=8, pady=(0, 8))
        ttk.Label(
            footer,
            text=self._backend_label(),
            foreground="#666",
        ).pack(side=tk.RIGHT)

    def _backend_label(self) -> str:
        if keyring is None:
            return "Keyring: not available"
        try:
            bk = keyring.get_keyring()
            return f"Keyring: {bk.__class__.__module__}.{bk.__class__.__name__}"
        except Exception:
            return "Keyring: available (backend unknown)"

    def _on_select(self, persona: Optional[Persona]) -> None:
        # Sync selection into providers page
        self.page_creds.set_persona(persona)


# ----------------
# Personas page
# ----------------
class PersonasPage(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        store: PersonaStore,
        on_select: callable[[Optional[Persona]], None],
    ) -> None:
        super().__init__(master)
        self.store = store
        self.on_select = on_select

        # Left: list
        left = ttk.Frame(self)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(left, height=16)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=(0, 8), pady=(0, 8))
        self.listbox.bind("<<ListboxSelect>>", self._handle_select)

        # Buttons under list
        btns = ttk.Frame(left)
        btns.pack(fill=tk.X)
        ttk.Button(btns, text="Refresh", command=self.refresh).pack(side=tk.LEFT)
        ttk.Button(btns, text="Remove", command=self.remove).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Remove All", command=self.remove_all).pack(side=tk.LEFT)

        # Right: editor
        right = ttk.LabelFrame(self, text="Edit / Add")
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(8, 0))

        form = ttk.Frame(right)
        form.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

        self.name_var = tk.StringVar()
        self.call_var = tk.StringVar()
        self.start_var = tk.StringVar()
        self.end_var = tk.StringVar()

        self._row(form, 0, "Name", self.name_var)
        self._row(form, 1, "Callsign", self.call_var)
        self._row(form, 2, "Start (YYYY-MM-DD)", self.start_var)
        self._row(form, 3, "End (YYYY-MM-DD)", self.end_var)

        bbar = ttk.Frame(right)
        bbar.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Button(bbar, text="Save / Upsert", command=self.save).pack(side=tk.LEFT)
        ttk.Button(bbar, text="New (clear)", command=self.clear).pack(
            side=tk.LEFT, padx=6
        )

        self.refresh()

    def _row(self, parent: ttk.Frame, r: int, label: str, var: tk.StringVar) -> None:
        ttk.Label(parent, text=label).grid(row=r, column=0, sticky="w", pady=2)
        ttk.Entry(parent, textvariable=var, width=28).grid(
            row=r, column=1, sticky="w", pady=2
        )

    # Actions
    def refresh(self) -> None:
        self.listbox.delete(0, tk.END)
        for p in self.store.list():
            provs = ", ".join(sorted(p.providers)) or "—"
            self.listbox.insert(tk.END, f"{p.name}  ({p.callsign})  providers: {provs}")
        self.on_select(None)

    def _handle_select(self, _evt: object) -> None:
        idxs = self.listbox.curselection()
        if not idxs:
            self.on_select(None)
            return
        idx = idxs[0]
        name = self.store.list()[idx].name
        p = self.store.get(name)
        if not p:
            self.on_select(None)
            return
        # Fill editor
        self.name_var.set(p.name)
        self.call_var.set(p.callsign)
        self.start_var.set(p.start.isoformat() if p.start else "")
        self.end_var.set(p.end.isoformat() if p.end else "")
        self.on_select(p)

    def clear(self) -> None:
        self.name_var.set("")
        self.call_var.set("")
        self.start_var.set("")
        self.end_var.set("")

    def save(self) -> None:
        name = self.name_var.get().strip()
        call = self.call_var.get().strip().upper()
        start = self.start_var.get().strip()
        end = self.end_var.get().strip()

        if not name or not call:
            messagebox.showerror("Missing fields", "Name and callsign are required.")
            return
        err = _validate_span(start, end)
        if err:
            messagebox.showerror("Invalid dates", err)
            return

        from datetime import date

        s = date.fromisoformat(start) if start else None
        e = date.fromisoformat(end) if end else None
        p = self.store.upsert(name=name, callsign=call, start=s, end=e)
        messagebox.showinfo("Saved", f"Saved persona: {p.name} ({p.callsign})")
        self.refresh()

    def remove(self) -> None:
        idxs = self.listbox.curselection()
        if not idxs:
            return
        idx = idxs[0]
        name = self.store.list()[idx].name
        if messagebox.askyesno("Remove", f"Remove persona '{name}'?"):
            self.store.remove(name)
            self.refresh()

    def remove_all(self) -> None:
        if not self.store.list():
            self.refresh()
            return
        if not messagebox.askyesno("Remove all", "Remove ALL personas (index only)?"):
            return
        # Nuke index file and reload
        self.store.index_path.unlink(missing_ok=True)
        self.store = PersonaStore(self.store.index_path)
        self.refresh()


# ----------------
# Providers page
# ----------------
class ProvidersPage(ttk.Frame):
    def __init__(self, master: tk.Misc, store: PersonaStore) -> None:
        super().__init__(master)
        self.store = store
        self.current: Optional[Persona] = None

        top = ttk.Frame(self)
        top.pack(fill=tk.X, pady=(0, 8))

        self.persona_lbl = ttk.Label(top, text="(no persona selected)")
        self.persona_lbl.pack(side=tk.LEFT)

        # Provider editor
        frm = ttk.LabelFrame(self, text="Provider credential")
        frm.pack(fill=tk.X, padx=2, pady=2)

        self.provider_var = tk.StringVar(value="lotw")
        self.user_var = tk.StringVar()
        self.pass_var = tk.StringVar()

        ttk.Label(frm, text="Provider").grid(
            row=0, column=0, sticky="w", padx=6, pady=4
        )
        ttk.Combobox(
            frm,
            textvariable=self.provider_var,
            values=["lotw", "eqsl", "qrz", "clublog"],
            width=12,
            state="readonly",
        ).grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(frm, text="Username").grid(
            row=1, column=0, sticky="w", padx=6, pady=4
        )
        ttk.Entry(frm, textvariable=self.user_var, width=24).grid(
            row=1, column=1, sticky="w", padx=6, pady=4
        )

        ttk.Label(frm, text="Password / Secret").grid(
            row=2, column=0, sticky="w", padx=6, pady=4
        )
        ttk.Entry(frm, textvariable=self.pass_var, width=24, show="*").grid(
            row=2, column=1, sticky="w", padx=6, pady=4
        )

        bbar = ttk.Frame(frm)
        bbar.grid(row=3, column=0, columnspan=2, sticky="w", padx=6, pady=6)
        ttk.Button(bbar, text="Save to keyring", command=self.save).pack(side=tk.LEFT)

        # Current providers table
        self.tree = ttk.Treeview(
            self,
            columns=("provider", "username"),
            show="headings",
            height=8,
        )
        self.tree.heading("provider", text="Provider")
        self.tree.heading("username", text="Username")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

    def set_persona(self, p: Optional[Persona]) -> None:
        self.current = p
        if p is None:
            self.persona_lbl.config(text="(no persona selected)")
            self._refresh_table([])
            return
        self.persona_lbl.config(text=f"{p.name}  ({p.callsign})")
        rows = []
        for prov, ref in p.providers.items():
            rows.append((prov, _mask(ref["username"])))
        self._refresh_table(rows)

    def _refresh_table(self, rows: list[tuple[str, str]]) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for prov, user in rows:
            self.tree.insert("", tk.END, values=(prov, user))

    def save(self) -> None:
        if self.current is None:
            messagebox.showerror("No persona", "Select a persona first.")
            return
        prov = self.provider_var.get().strip().lower()
        user = self.user_var.get().strip()
        sec = self.pass_var.get()

        if not user or not prov:
            messagebox.showerror("Missing fields", "Provider and username required.")
            return

        # Save non-secret ref
        self.store.set_provider_ref(
            persona=self.current.name,
            provider=prov,
            username=user,
        )

        # Save secret to keyring (optional)
        saved = False
        if keyring is not None:
            try:
                keyring.set_password(
                    "adif-mcp", f"{self.current.name}:{prov}:{user}", sec
                )
                saved = True
            except Exception:
                saved = False

        backend = ""
        if saved:
            try:
                bk = keyring.get_keyring() if keyring is not None else None
                if bk:
                    backend = (
                        f" [{bk.__class__.__module__}." f"{bk.__class__.__name__}]"
                    )
            except Exception:
                pass

        messagebox.showinfo(
            "Credential saved",
            (
                f"Saved ref for {self.current.name}/{prov} "
                f"(username={user}).\n"
                f"{'Secret stored in keyring' +
                   backend if saved else 'Secret NOT stored'}"
            ),
        )
        # Refresh table
        p = self.store.get(self.current.name)
        self.set_persona(p)


if __name__ == "__main__":
    PersonaUI().mainloop()
