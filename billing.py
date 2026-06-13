import tkinter as tk
from tkinter import messagebox, ttk
import sys, json, os, datetime, io
import qrcode
from PIL import Image, ImageTk

# ── colour tokens ──────────────────────────────────────────────────────────────
BRAND       = "#2196F3"
BRAND_DARK  = "#1565C0"
BRAND_LIGHT = "#E3F2FD"
ACCENT      = "#00BCD4"
SUCCESS     = "#43A047"
DANGER      = "#E53935"
WARNING     = "#FB8C00"
BG          = "#F0F4FF"
SIDEBAR_BG  = "#1A237E"
CARD_BG     = "#FFFFFF"
TEXT_DARK   = "#1A237E"
TEXT_MID    = "#132027"
BORDER      = "#BBDEFB"

STORE_NAME  = "ABC Stores"
STORE_ADDR  = "ABC City, Kerala – 678 356"
STORE_PHONE = "+91 87463 89362"
UPI_ID      = "767676767667@upi"

# ── data helpers ───────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_FILE = os.path.join(BASE_DIR, "products.json")

def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return {}
    with open(PRODUCTS_FILE) as f:
        return json.load(f)

def save_products(data):
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ── QR helper: returns a PIL Image ────────────────────────────────────────────
def make_qr_image(data: str, size: int = 120) -> Image.Image:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1A237E", back_color="white").convert("RGB")
    return img.resize((size, size), Image.LANCZOS)

def make_qr_photo(data: str, size: int = 120) -> ImageTk.PhotoImage:
    return ImageTk.PhotoImage(make_qr_image(data, size))

# ── reusable widget helpers ────────────────────────────────────────────────────
def styled_button(parent, text, command, bg=BRAND, fg="white",
                  font_size=10, padx=16, pady=8, **kw):
    return tk.Button(parent, text=text, command=command,
                     bg=bg, fg=fg, activebackground=BRAND_DARK,
                     activeforeground="white",
                     font=("Segoe UI", font_size, "bold"),
                     relief="flat", cursor="hand2",
                     padx=padx, pady=pady, bd=0, **kw)

def card(parent, **kw):
    return tk.Frame(parent, bg=CARD_BG, relief="flat",
                    highlightthickness=1, highlightbackground=BORDER, **kw)

def field_entry(parent, label, bg=CARD_BG):
    f = tk.Frame(parent, bg=bg)
    f.pack(fill="x", pady=4)
    tk.Label(f, text=label, bg=bg, fg=TEXT_MID,
             font=("Segoe UI", 9)).pack(anchor="w")
    e = tk.Entry(f, font=("Segoe UI", 10), relief="solid", bd=1,
                 highlightthickness=1, highlightbackground=BORDER,
                 highlightcolor=BRAND, fg=TEXT_DARK)
    e.pack(fill="x", ipady=5)
    return e

# ── scrollable canvas frame helper ────────────────────────────────────────────
def scrollable_frame(parent, bg=CARD_BG):
    """Returns (outer_frame, inner_frame). Pack outer_frame."""
    outer = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(outer, bg=bg, highlightthickness=0)
    vsb = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    inner = tk.Frame(canvas, bg=bg)
    win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
    inner.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>",
                lambda e: canvas.itemconfig(win_id, width=e.width))
    canvas.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    # mouse-wheel scroll
    def _scroll(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _scroll)
    return outer, inner

# ── splash ─────────────────────────────────────────────────────────────────────
def build_splash(root):
    f = tk.Frame(root, bg=BRAND)
    f.place(relwidth=1, relheight=1)
    c = tk.Canvas(f, width=120, height=120, bg=BRAND, highlightthickness=0)
    c.place(relx=0.5, rely=0.35, anchor="center")
    c.create_oval(42, 55, 78, 95, fill="white", outline="white")
    c.create_oval(35, 30, 85, 70, fill="white", outline="white")
    for y in (52, 62, 72):
        c.create_rectangle(42, y, 78, y+6, fill=BRAND, outline="")
    c.create_oval(10, 25, 50, 55, fill="#BBDEFB", outline="white", width=2)
    c.create_oval(70, 25, 110, 55, fill="#BBDEFB", outline="white", width=2)
    c.create_line(50, 30, 38, 12, fill="white", width=2)
    c.create_oval(34, 8, 42, 16, fill="white")
    c.create_line(70, 30, 82, 12, fill="white", width=2)
    c.create_oval(78, 8, 86, 16, fill="white")
    tk.Label(f, text="Paybee", font=("Segoe UI", 36, "bold"),
             bg=BRAND, fg="white").place(relx=0.5, rely=0.58, anchor="center")
    tk.Label(f, text="Smart Billing System",
             font=("Segoe UI", 13), bg=BRAND, fg="#BBDEFB").place(
        relx=0.5, rely=0.68, anchor="center")
    bar_bg   = tk.Frame(f, bg="#1565C0", height=4, width=280)
    bar_bg.place(relx=0.5, rely=0.80, anchor="center")
    bar_fill = tk.Frame(bar_bg, bg="white", height=4, width=0)
    bar_fill.place(x=0, y=0)
    def animate(w=0):
        if w <= 280:
            bar_fill.config(width=w)
            root.after(12, animate, w+4)
        else:
            f.destroy()
            build_main(root)
    root.after(200, animate)

# ── main UI ────────────────────────────────────────────────────────────────────
def build_main(root):
    root.configure(bg=BG)

    products      = load_products()
    session_orders = []
    session_total  = [0]

    # layout
    sidebar   = tk.Frame(root, bg=SIDEBAR_BG, width=220)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)
    main_area = tk.Frame(root, bg=BG)
    main_area.pack(side="left", fill="both", expand=True)

    # topbar
    topbar = tk.Frame(main_area, bg=CARD_BG, height=56,
                      highlightthickness=1, highlightbackground=BORDER)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)
    tk.Label(topbar, text="Paybee  ·  Billing Dashboard",
             font=("Segoe UI", 14, "bold"), bg=CARD_BG, fg=TEXT_DARK).pack(
        side="left", padx=20, pady=14)
    clock_lbl = tk.Label(topbar, text="", font=("Segoe UI", 10),
                         bg=CARD_BG, fg=TEXT_MID)
    clock_lbl.pack(side="right", padx=20)
    def tick():
        clock_lbl.config(
            text=datetime.datetime.now().strftime("%d %b %Y  %H:%M:%S"))
        root.after(1000, tick)
    tick()

    content = tk.Frame(main_area, bg=BG)
    content.pack(fill="both", expand=True, padx=18, pady=18)

    # sidebar brand + nav
    tk.Label(sidebar, text="🐝  Paybee",
             font=("Segoe UI", 15, "bold"), bg=SIDEBAR_BG, fg="white",
             pady=22).pack(fill="x", padx=12)
    tk.Frame(sidebar, bg="#283593", height=1).pack(fill="x", padx=8)

    nav_buttons = []
    def nav_btn(text, icon, cmd):
        f = tk.Frame(sidebar, bg=SIDEBAR_BG, cursor="hand2")
        f.pack(fill="x", padx=8, pady=2)
        lbl = tk.Label(f, text=f"  {icon}  {text}",
                       font=("Segoe UI", 10), bg=SIDEBAR_BG, fg="#90CAF9",
                       anchor="w", padx=8, pady=10)
        lbl.pack(fill="x")
        def on_click(f=f, lbl=lbl):
            for nb, nl in nav_buttons:
                nb.config(bg=SIDEBAR_BG); nl.config(bg=SIDEBAR_BG, fg="#90CAF9")
            f.config(bg=BRAND); lbl.config(bg=BRAND, fg="white")
            cmd()
        f.bind("<Button-1>",  lambda e, fn=on_click: fn())
        lbl.bind("<Button-1>", lambda e, fn=on_click: fn())
        nav_buttons.append((f, lbl))
        return on_click

    def clear():
        for w in content.winfo_children():
            w.destroy()

    # ──────────────────────────────────────────────────────────────────────────
    # VIEW: New Sale
    # ──────────────────────────────────────────────────────────────────────────
    def show_billing():
        clear()
        nonlocal products
        products = load_products()

        tk.Label(content, text="New Sale",
                 font=("Segoe UI", 18, "bold"), bg=BG, fg=TEXT_DARK).pack(anchor="w")
        tk.Label(content, text="Add products to the current bill",
                 font=("Segoe UI", 10), bg=BG, fg=TEXT_MID).pack(anchor="w", pady=(0,12))

        top = tk.Frame(content, bg=BG)
        top.pack(fill="x", pady=4)

        entry_card = card(top, padx=18, pady=18)
        entry_card.pack(side="left", fill="y", padx=(0,12))

        pid_e  = field_entry(entry_card, "Product ID")
        qty_e  = field_entry(entry_card, "Quantity")
        preview = tk.Label(entry_card, text="", bg=CARD_BG, fg=TEXT_MID,
                           font=("Segoe UI", 9), wraplength=200)
        preview.pack(anchor="w", pady=4)

        def on_pid_change(*_):
            pid = pid_e.get().strip()
            if pid in products:
                p = products[pid]
                preview.config(
                    text=f"✔  {p['name']}  ·  ₹{p['price']}  ·  Stock: {p['quantity']}",
                    fg=SUCCESS)
            else:
                preview.config(text="Product not found" if pid else "", fg=DANGER)
        pid_e.bind("<KeyRelease>", on_pid_change)

        def add_item():
            nonlocal products
            try:
                pid = pid_e.get().strip()
                qty = int(qty_e.get().strip())
                if pid not in products:
                    messagebox.showerror("Error", "Product ID not found.", parent=root); return
                p = products[pid]
                if qty <= 0:
                    messagebox.showerror("Error", "Quantity must be > 0.", parent=root); return
                if qty > p["quantity"]:
                    messagebox.showerror("Error", f"Only {p['quantity']} units in stock.", parent=root); return
                total = p["price"] * qty
                session_orders.append({"name": p["name"], "price": p["price"],
                                       "qty": qty, "total": total, "pid": pid,
                                       "category": p["category"]})
                session_total[0] += total
                products[pid]["quantity"] -= qty
                save_products(products)
                tree.insert("", "end",
                            values=(pid, p["name"], p["category"],
                                    qty, f"₹{p['price']:,}", f"₹{total:,}"))
                total_lbl.config(text=f"₹{session_total[0]:,.2f}")
                pid_e.delete(0, tk.END); qty_e.delete(0, tk.END)
                preview.config(text="")
            except ValueError:
                messagebox.showerror("Invalid input", "Enter a valid quantity.", parent=root)

        styled_button(entry_card, "＋  Add to Bill", add_item,
                      bg=BRAND, font_size=10).pack(fill="x", pady=(8,0))

        tbl_card = card(top, padx=12, pady=12)
        tbl_card.pack(side="left", fill="both", expand=True)

        cols = ("ID", "Product", "Category", "Qty", "Price", "Total")
        tree = ttk.Treeview(tbl_card, columns=cols, show="headings", height=12)
        st = ttk.Style()
        st.configure("Treeview", font=("Segoe UI", 9), rowheight=28,
                     background=CARD_BG, fieldbackground=CARD_BG, foreground=TEXT_DARK)
        st.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"),
                     background=BRAND_LIGHT, foreground=TEXT_DARK)
        st.map("Treeview", background=[("selected", BRAND_LIGHT)],
               foreground=[("selected", TEXT_DARK)])
        for c, w in zip(cols, [70,160,110,60,90,90]):
            tree.heading(c, text=c); tree.column(c, width=w, anchor="center")
        sb = tk.Scrollbar(tbl_card, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        tot_bar = tk.Frame(content, bg=BRAND, pady=12, padx=16)
        tot_bar.pack(fill="x", pady=(12,0))
        tk.Label(tot_bar, text="Session Total:", font=("Segoe UI", 12),
                 bg=BRAND, fg="white").pack(side="left")
        total_lbl = tk.Label(tot_bar, text="₹0.00",
                             font=("Segoe UI", 14, "bold"), bg=BRAND, fg="white")
        total_lbl.pack(side="left", padx=12)

        for o in session_orders:
            tree.insert("", "end",
                        values=(o.get("pid",""), o["name"], o.get("category",""),
                                o["qty"], f"₹{o['price']:,}", f"₹{o['total']:,}"))
        total_lbl.config(text=f"₹{session_total[0]:,.2f}")

    # ──────────────────────────────────────────────────────────────────────────
    # VIEW: Final Bill  (with UPI QR code)
    # ──────────────────────────────────────────────────────────────────────────
    def show_bill():
        clear()
        tk.Label(content, text="Final Bill",
                 font=("Segoe UI", 18, "bold"), bg=BG, fg=TEXT_DARK).pack(anchor="w")
        tk.Label(content, text="Tax summary, receipt & UPI payment QR",
                 font=("Segoe UI", 10), bg=BG, fg=TEXT_MID).pack(anchor="w", pady=(0,12))

        sub   = session_total[0]
        gst   = sub * 0.18
        grand = sub + gst
        date_s = datetime.datetime.now().strftime("%d-%m-%Y  %H:%M")

        outer_row = tk.Frame(content, bg=BG)
        outer_row.pack(fill="both", expand=True)

        # ── left: receipt text ────────────────────────────────────────────────
        receipt = card(outer_row, padx=20, pady=18)
        receipt.pack(side="left", fill="both", expand=True, padx=(0,12))

        sep = "─" * 46
        body  = f"{STORE_NAME}\n{STORE_ADDR}\nPhone: {STORE_PHONE}\n"
        body += sep + "\n"
        body += f"{'Product':<22}{'Qty':>5}{'Price':>10}{'Total':>10}\n"
        body += sep + "\n"
        for item in session_orders:
            body += (f"{item['name'][:22]:<22}{item['qty']:>5}"
                     f"₹{item['price']:>9,}₹{item['total']:>9,}\n")
        body += sep + "\n"
        body += f"\n{'Subtotal:':<30}₹{sub:>10,.2f}\n"
        body += f"{'GST (18%):':<30}₹{gst:>10,.2f}\n"
        body += f"{'Grand Total:':<30}₹{grand:>10,.2f}\n\n"
        body += f"Date: {date_s}\n"
        body += sep + "\n"
        body += "  Thank you for shopping at ABC Stores!\n"

        txt = tk.Text(receipt, font=("Courier New", 9), bg=CARD_BG,
                      fg=TEXT_DARK, bd=0, highlightthickness=0, height=22)
        txt.insert("1.0", body)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True)

        # summary chips
        chip_row = tk.Frame(receipt, bg=CARD_BG)
        chip_row.pack(fill="x", pady=(10,0))
        for label, val, color in [("Subtotal", f"₹{sub:,.2f}", TEXT_MID),
                                   ("GST 18%",  f"₹{gst:,.2f}", WARNING),
                                   ("Grand Total", f"₹{grand:,.2f}", SUCCESS)]:
            chip = tk.Frame(chip_row, bg=BG, padx=14, pady=10,
                            highlightthickness=1, highlightbackground=BORDER)
            chip.pack(side="left", padx=4)
            tk.Label(chip, text=label, font=("Segoe UI", 8),
                     bg=BG, fg=TEXT_MID).pack()
            tk.Label(chip, text=val, font=("Segoe UI", 11, "bold"),
                     bg=BG, fg=color).pack()

        # ── right: UPI QR card ────────────────────────────────────────────────
        qr_card = card(outer_row, padx=20, pady=20)
        qr_card.pack(side="left", fill="y")

        tk.Label(qr_card, text="Scan to Pay", font=("Segoe UI", 11, "bold"),
                 bg=CARD_BG, fg=TEXT_DARK).pack()
        tk.Label(qr_card, text="via any UPI app", font=("Segoe UI", 8),
                 bg=CARD_BG, fg=TEXT_MID).pack(pady=(0,10))

        upi_url = (f"upi://pay?pa={UPI_ID}&pn={STORE_NAME.replace(' ','%20')}"
                   f"&am={grand:.2f}&cu=INR&tn=Payment%20to%20{STORE_NAME.replace(' ','%20')}")
        photo = make_qr_photo(upi_url, size=200)
        qr_lbl = tk.Label(qr_card, image=photo, bg=CARD_BG,
                          highlightthickness=2, highlightbackground=BRAND)
        qr_lbl.image = photo   # keep reference
        qr_lbl.pack(pady=6)

        tk.Label(qr_card, text=f"₹{grand:,.2f}",
                 font=("Segoe UI", 18, "bold"), bg=CARD_BG, fg=SUCCESS).pack()
        tk.Label(qr_card, text=UPI_ID, font=("Segoe UI", 8),
                 bg=CARD_BG, fg=TEXT_MID).pack(pady=(2,10))

        # GPay / PhonePe / Paytm logos as text badges
        badge_row = tk.Frame(qr_card, bg=CARD_BG)
        badge_row.pack()
        for app_name, color in [("GPay","#1A73E8"),("PhonePe","#5F259F"),("Paytm","#002970")]:
            tk.Label(badge_row, text=app_name, font=("Segoe UI", 7, "bold"),
                     bg=color, fg="white", padx=6, pady=3).pack(side="left", padx=3)

    # ──────────────────────────────────────────────────────────────────────────
    # VIEW: Inventory  (with per-product QR)
    # ──────────────────────────────────────────────────────────────────────────
    def show_products():
        clear()
        nonlocal products
        products = load_products()

        tk.Label(content, text="Product Inventory",
                 font=("Segoe UI", 18, "bold"), bg=BG, fg=TEXT_DARK).pack(anchor="w")
        tk.Label(content, text=f"{len(products)} products  ·  click a row to view its QR code",
                 font=("Segoe UI", 10), bg=BG, fg=TEXT_MID).pack(anchor="w", pady=(0,12))

        main_row = tk.Frame(content, bg=BG)
        main_row.pack(fill="both", expand=True)

        # ── left: product table ───────────────────────────────────────────────
        tbl_card = card(main_row, padx=12, pady=12)
        tbl_card.pack(side="left", fill="both", expand=True, padx=(0,12))

        sf = tk.Frame(tbl_card, bg=CARD_BG)
        sf.pack(fill="x", pady=(0,8))
        tk.Label(sf, text="🔍", bg=CARD_BG, font=("Segoe UI", 12)).pack(side="left")
        search_var = tk.StringVar()
        tk.Entry(sf, textvariable=search_var, font=("Segoe UI", 10),
                 relief="solid", bd=1, fg=TEXT_DARK).pack(
            side="left", fill="x", expand=True, ipady=4, padx=4)

        cols = ("ID", "Name", "Category", "Price", "Stock", "Status")
        tree = ttk.Treeview(tbl_card, columns=cols, show="headings", height=18)
        for c, w in zip(cols, [80,200,130,100,80,90]):
            tree.heading(c, text=c); tree.column(c, width=w, anchor="center")
        vsb = tk.Scrollbar(tbl_card, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # ── right: QR panel ───────────────────────────────────────────────────
        qr_panel = card(main_row, padx=18, pady=18, width=200)
        qr_panel.pack(side="left", fill="y")
        qr_panel.pack_propagate(False)

        tk.Label(qr_panel, text="Product QR",
                 font=("Segoe UI", 11, "bold"), bg=CARD_BG, fg=TEXT_DARK).pack(pady=(0,6))
        tk.Label(qr_panel, text="Select a product →",
                 font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_MID).pack()

        qr_img_lbl  = tk.Label(qr_panel, bg=CARD_BG)
        qr_img_lbl.pack(pady=8)
        qr_info_lbl = tk.Label(qr_panel, text="", bg=CARD_BG,
                                fg=TEXT_DARK, font=("Segoe UI", 8),
                                wraplength=170, justify="center")
        qr_info_lbl.pack()

        def on_select(event):
            sel = tree.selection()
            if not sel:
                return
            pid = tree.item(sel[0], "values")[0]
            if pid not in products:
                return
            p = products[pid]
            qr_data = (f"Product: {p['name']}\n"
                       f"ID: {pid}\n"
                       f"Category: {p['category']}\n"
                       f"Price: Rs.{p['price']}\n"
                       f"Stock: {p['quantity']}\n"
                       f"Store: {STORE_NAME}")
            photo = make_qr_photo(qr_data, size=160)
            qr_img_lbl.config(image=photo,
                               highlightthickness=2, highlightbackground=BRAND)
            qr_img_lbl.image = photo
            qr_info_lbl.config(
                text=f"{p['name']}\nID: {pid}\n₹{p['price']:,}  ·  Qty: {p['quantity']}")

        tree.bind("<<TreeviewSelect>>", on_select)

        def populate(filter_text=""):
            tree.delete(*tree.get_children())
            for pid, p in products.items():
                if filter_text.lower() not in (pid+p["name"]+p["category"]).lower():
                    continue
                status = ("✔ OK"   if p["quantity"] > 5 else
                          "⚠ Low"  if p["quantity"] > 0 else "✘ Out")
                tag    = ("ok"     if p["quantity"] > 5 else
                          "low"    if p["quantity"] > 0 else "out")
                tree.insert("", "end",
                            values=(pid, p["name"], p["category"],
                                    f"₹{p['price']:,}", p["quantity"], status),
                            tags=(tag,))
            tree.tag_configure("ok",  foreground=SUCCESS)
            tree.tag_configure("low", foreground=WARNING)
            tree.tag_configure("out", foreground=DANGER)

        search_var.trace_add("write", lambda *_: populate(search_var.get()))
        populate()

    # ──────────────────────────────────────────────────────────────────────────
    # VIEW: QR Gallery  (all products, grid of QR codes)
    # ──────────────────────────────────────────────────────────────────────────
    def show_qr_gallery():
        clear()
        nonlocal products
        products = load_products()

        tk.Label(content, text="Product QR Gallery",
                 font=("Segoe UI", 18, "bold"), bg=BG, fg=TEXT_DARK).pack(anchor="w")
        tk.Label(content, text="QR codes for all products — scan to get product details",
                 font=("Segoe UI", 10), bg=BG, fg=TEXT_MID).pack(anchor="w", pady=(0,12))

        outer, inner = scrollable_frame(content, bg=BG)
        outer.pack(fill="both", expand=True)

        COLS = 4
        # keep photo references here to prevent GC
        photo_refs = []

        for idx, (pid, p) in enumerate(products.items()):
            row_i = idx // COLS
            col_i = idx %  COLS

            item_card = card(inner, padx=12, pady=12)
            item_card.grid(row=row_i, column=col_i, padx=8, pady=8, sticky="nsew")

            qr_data = (f"Product: {p['name']}\n"
                       f"ID: {pid}\n"
                       f"Category: {p['category']}\n"
                       f"Price: Rs.{p['price']}\n"
                       f"Stock: {p['quantity']}\n"
                       f"Store: {STORE_NAME}")
            photo = make_qr_photo(qr_data, size=130)
            photo_refs.append(photo)

            lbl = tk.Label(item_card, image=photo, bg=CARD_BG,
                           highlightthickness=2, highlightbackground=BRAND)
            lbl.image = photo
            lbl.pack()

            tk.Label(item_card, text=p["name"], font=("Segoe UI", 9, "bold"),
                     bg=CARD_BG, fg=TEXT_DARK, wraplength=140).pack(pady=(6,0))
            tk.Label(item_card, text=f"ID: {pid}  ·  ₹{p['price']:,}",
                     font=("Segoe UI", 8), bg=CARD_BG, fg=TEXT_MID).pack()

            status_color = (SUCCESS if p["quantity"] > 5 else
                            WARNING if p["quantity"] > 0 else DANGER)
            tk.Label(item_card, text=f"Stock: {p['quantity']}",
                     font=("Segoe UI", 8, "bold"),
                     bg=CARD_BG, fg=status_color).pack()

        # keep refs alive in the frame
        inner._photo_refs = photo_refs

    # ──────────────────────────────────────────────────────────────────────────
    # VIEW: Add Product
    # ──────────────────────────────────────────────────────────────────────────
    def show_add_product():
        clear()
        nonlocal products
        tk.Label(content, text="Add New Product",
                 font=("Segoe UI", 18, "bold"), bg=BG, fg=TEXT_DARK).pack(anchor="w")
        tk.Label(content, text="Register a new product to the inventory",
                 font=("Segoe UI", 10), bg=BG, fg=TEXT_MID).pack(anchor="w", pady=(0,12))

        form = card(content, padx=28, pady=24)
        form.pack(ipadx=10)
        pid_e   = field_entry(form, "Product ID  (e.g. 1008)")
        name_e  = field_entry(form, "Product Name")
        cat_e   = field_entry(form, "Category")
        price_e = field_entry(form, "Price (₹)")
        qty_e   = field_entry(form, "Quantity")
        msg_lbl = tk.Label(form, text="", bg=CARD_BG, font=("Segoe UI", 9))
        msg_lbl.pack(anchor="w", pady=4)

        def submit():
            nonlocal products
            products = load_products()
            pid  = pid_e.get().strip()
            name = name_e.get().strip()
            cat  = cat_e.get().strip()
            try:
                price = int(price_e.get().strip())
                qty   = int(qty_e.get().strip())
            except ValueError:
                msg_lbl.config(text="⚠  Price and Quantity must be numbers.", fg=DANGER); return
            if not all([pid, name, cat]):
                msg_lbl.config(text="⚠  All fields are required.", fg=DANGER); return
            if pid in products:
                msg_lbl.config(text="⚠  Product ID already exists.", fg=DANGER); return
            products[pid] = {"name": name, "category": cat, "price": price, "quantity": qty}
            save_products(products)
            msg_lbl.config(text=f"✔  '{name}' added successfully.", fg=SUCCESS)
            for e in [pid_e, name_e, cat_e, price_e, qty_e]:
                e.delete(0, tk.END)

        styled_button(form, "Save Product", submit, bg=SUCCESS, font_size=10).pack(
            fill="x", pady=(12,0))

    # ──────────────────────────────────────────────────────────────────────────
    # VIEW: Delete Product
    # ──────────────────────────────────────────────────────────────────────────
    def show_delete():
        clear()
        nonlocal products
        tk.Label(content, text="Delete Product",
                 font=("Segoe UI", 18, "bold"), bg=BG, fg=TEXT_DARK).pack(anchor="w")
        tk.Label(content, text="Remove a product from inventory permanently",
                 font=("Segoe UI", 10), bg=BG, fg=TEXT_MID).pack(anchor="w", pady=(0,12))

        form = card(content, padx=28, pady=24)
        form.pack(ipadx=10)
        pid_e   = field_entry(form, "Product ID to delete")
        preview = tk.Label(form, text="", bg=CARD_BG, fg=TEXT_MID,
                           font=("Segoe UI", 9), wraplength=300)
        preview.pack(anchor="w", pady=4)

        def on_pid(*_):
            p_data = load_products()
            pid = pid_e.get().strip()
            if pid in p_data:
                p = p_data[pid]
                preview.config(
                    text=f"Found: {p['name']}  |  ₹{p['price']}  |  Qty: {p['quantity']}",
                    fg=TEXT_DARK)
            else:
                preview.config(text="Product not found" if pid else "", fg=DANGER)
        pid_e.bind("<KeyRelease>", on_pid)

        msg_lbl = tk.Label(form, text="", bg=CARD_BG, font=("Segoe UI", 9))
        msg_lbl.pack(anchor="w")

        def delete():
            nonlocal products
            products = load_products()
            pid = pid_e.get().strip()
            if pid not in products:
                msg_lbl.config(text="⚠  Product ID not found.", fg=DANGER); return
            name = products[pid]["name"]
            if not messagebox.askyesno("Confirm Delete",
                                       f"Delete '{name}' (ID: {pid}) permanently?",
                                       parent=root):
                return
            del products[pid]
            save_products(products)
            msg_lbl.config(text=f"✔  '{name}' deleted.", fg=SUCCESS)
            pid_e.delete(0, tk.END); preview.config(text="")

        styled_button(form, "Delete Product", delete, bg=DANGER, font_size=10).pack(
            fill="x", pady=(12,0))

    # ──────────────────────────────────────────────────────────────────────────
    # VIEW: Dashboard
    # ──────────────────────────────────────────────────────────────────────────
    def show_dashboard():
        clear()
        nonlocal products
        products = load_products()

        tk.Label(content, text="Dashboard",
                 font=("Segoe UI", 18, "bold"), bg=BG, fg=TEXT_DARK).pack(anchor="w")
        tk.Label(content, text=f"Welcome back  ·  {STORE_NAME}",
                 font=("Segoe UI", 10), bg=BG, fg=TEXT_MID).pack(anchor="w", pady=(0,16))

        stats = tk.Frame(content, bg=BG)
        stats.pack(fill="x")
        total_items = sum(p["quantity"] for p in products.values())
        low_stock   = sum(1 for p in products.values() if 0 < p["quantity"] <= 5)

        for label, value, color in [
            ("Products",      str(len(products)), BRAND),
            ("Total Stock",   str(total_items),   ACCENT),
            ("Low Stock",     str(low_stock),      WARNING),
            ("Session Total", f"₹{session_total[0]:,.2f}", SUCCESS),
        ]:
            chip = tk.Frame(stats, bg=CARD_BG, padx=20, pady=16,
                            highlightthickness=1, highlightbackground=BORDER)
            chip.pack(side="left", padx=(0,12), expand=True, fill="x")
            tk.Label(chip, text=value, font=("Segoe UI", 22, "bold"),
                     bg=CARD_BG, fg=color).pack(anchor="w")
            tk.Label(chip, text=label, font=("Segoe UI", 9),
                     bg=CARD_BG, fg=TEXT_MID).pack(anchor="w")

        # category bar chart
        cat_card = card(content, padx=18, pady=16)
        cat_card.pack(fill="x", pady=(16,0))
        tk.Label(cat_card, text="INVENTORY BY CATEGORY",
                 font=("Segoe UI", 8, "bold"), bg=CARD_BG, fg=TEXT_MID).pack(anchor="w")
        cats = {}
        for p in products.values():
            cats[p["category"]] = cats.get(p["category"], 0) + p["quantity"]
        grid = tk.Frame(cat_card, bg=CARD_BG)
        grid.pack(fill="x", pady=8)
        max_qty = max(cats.values()) if cats else 1
        for cat, qty in cats.items():
            row = tk.Frame(grid, bg=CARD_BG)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=cat, font=("Segoe UI", 9),
                     bg=CARD_BG, fg=TEXT_DARK, width=18, anchor="w").pack(side="left")
            bar_bg = tk.Frame(row, bg=BRAND_LIGHT, height=12, width=240)
            bar_bg.pack(side="left", padx=8)
            bar_bg.pack_propagate(False)
            tk.Frame(bar_bg, bg=BRAND, height=12,
                     width=int(240*qty/max_qty)).place(x=0, y=0)
            tk.Label(row, text=str(qty), font=("Segoe UI", 9, "bold"),
                     bg=CARD_BG, fg=TEXT_DARK).pack(side="left")

        info_card = card(content, padx=18, pady=16)
        info_card.pack(fill="x", pady=(12,0))
        tk.Label(info_card, text="STORE INFORMATION",
                 font=("Segoe UI", 8, "bold"), bg=CARD_BG, fg=TEXT_MID).pack(anchor="w")
        for line in [STORE_NAME, STORE_ADDR, f"Phone: {STORE_PHONE}", f"UPI: {UPI_ID}"]:
            tk.Label(info_card, text=line, font=("Segoe UI", 10),
                     bg=CARD_BG, fg=TEXT_DARK).pack(anchor="w")

    # ── sidebar nav buttons ────────────────────────────────────────────────────
    activate_dashboard = nav_btn("Dashboard",    "📊", show_dashboard)
    nav_btn("New Sale",     "🧾", show_billing)
    nav_btn("Final Bill",   "💰", show_bill)
    nav_btn("Inventory",    "📦", show_products)
    nav_btn("QR Gallery",   "📲", show_qr_gallery)
    nav_btn("Add Product",  "➕", show_add_product)
    nav_btn("Remove Item",  "🗑", show_delete)

    tk.Frame(sidebar, bg="#283593", height=1).pack(fill="x", padx=8, pady=10)

    def refresh():
        nonlocal products
        products = load_products()
        activate_dashboard()

    styled_button(sidebar, "⟳  Refresh", refresh,
                  bg=BRAND_DARK, fg="white", font_size=9,
                  padx=8, pady=6).pack(fill="x", padx=12, pady=4)

    activate_dashboard()

# ── entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Paybee Billing")
    root.geometry("1150x740")
    root.minsize(950, 620)
    try:
        root.tk.call("tk", "scaling", 1.25)
    except Exception:
        pass
    build_splash(root)
    root.mainloop()
