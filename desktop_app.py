# desktop_budget.py
import customtkinter as ctk
import json
import os
import matplotlib.pyplot as plt

DATA_FILE = "desktop_budget_data.json"

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class BudgetTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window settings
        self.title("Personal Budget Tracker by Joshua Parba")
        self.geometry("550x720")

        # Load saved data on startup
        self.load_data()

        # --- Title ---
        self.title_label = ctk.CTkLabel(self, text="💰 Personal Budget Tracker", font=("Segoe UI", 20, "bold"))
        self.title_label.pack(pady=15)

        # --- Income Section Frame ---
        self.income_frame = ctk.CTkFrame(self)
        self.income_frame.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(self.income_frame, text="Income (₱):", font=("Segoe UI", 12)).pack(side="left", padx=10)
        self.income_entry = ctk.CTkEntry(self.income_frame, width=120)
        self.income_entry.pack(side="left", padx=5)
        self.income_entry.insert(0, str(self.income))
        
        self.save_income_btn = ctk.CTkButton(self.income_frame, text="Update", width=80, command=self.update_income)
        self.save_income_btn.pack(side="left", padx=5)

        # NEW: Reset Income Button
        self.reset_income_btn = ctk.CTkButton(self.income_frame, text="Reset", width=70, fg_color="#c92a2a", hover_color="#a61e1e", command=self.reset_income)
        self.reset_income_btn.pack(side="left", padx=5)

        # --- Expense Section Frame ---
        self.expense_frame = ctk.CTkFrame(self)
        self.expense_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.expense_frame, text="Add New Expense", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.cat_entry = ctk.CTkEntry(self.expense_frame, placeholder_text="Category (e.g. Food)", width=170)
        self.cat_entry.pack(side="left", padx=10, pady=5)

        self.amt_entry = ctk.CTkEntry(self.expense_frame, placeholder_text="Amount (₱)", width=110)
        self.amt_entry.pack(side="left", padx=5, pady=5)

        self.add_btn = ctk.CTkButton(self.expense_frame, text="Add", width=70, command=self.add_expense)
        self.add_btn.pack(side="left", padx=10, pady=5)

        # --- Action Buttons Frame (Chart) ---
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(pady=5, padx=20, fill="x")

        self.chart_btn = ctk.CTkButton(self.action_frame, text="📊 View Spending Chart", fg_color="#2b8a3e", hover_color="#2b7036", command=self.show_chart)
        self.chart_btn.pack(side="left", expand=True, fill="x", padx=0)

        # --- Summary Header Labels ---
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.pack(pady=5, padx=20, fill="x")
        self.stats_label = ctk.CTkLabel(self.stats_frame, text="", font=("Segoe UI", 12, "bold"))
        self.stats_label.pack(pady=8, padx=10)

        # --- NEW: Scrollable Expense Management List ---
        self.list_frame_container = ctk.CTkFrame(self)
        self.list_frame_container.pack(pady=10, padx=20, fill="both", expand=True)

        ctk.CTkLabel(self.list_frame_container, text="Manage Expenses (Delete individual items)", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=5)

        # Scrollable container for dynamic delete rows
        self.scroll_expenses = ctk.CTkScrollableFrame(self.list_frame_container, width=470, height=180)
        self.scroll_expenses.pack(pady=5, padx=10, fill="both", expand=True)

        # Initial UI refresh
        self.refresh_ui()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    data = json.load(f)
                    self.income = data.get("income", 0.0)
                    self.expenses = data.get("expenses", [])
                    return
            except json.JSONDecodeError:
                pass
        self.income = 0.0
        self.expenses = []

    def save_data(self):
        data = {
            "income": self.income,
            "expenses": self.expenses
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def update_income(self):
        try:
            self.income = float(self.income_entry.get())
            self.save_data()
            self.refresh_ui()
        except ValueError:
            pass

    def reset_income(self):
        """Resets monthly income to 0"""
        self.income = 0.0
        self.income_entry.delete(0, 'end')
        self.income_entry.insert(0, "0.0")
        self.save_data()
        self.refresh_ui()

    def add_expense(self):
        cat = self.cat_entry.get().strip().capitalize()
        try:
            amt = float(self.amt_entry.get())
            if cat and amt > 0:
                self.expenses.append({"category": cat, "amount": amt})
                self.save_data()
                self.cat_entry.delete(0, 'end')
                self.amt_entry.delete(0, 'end')
                self.refresh_ui()
        except ValueError:
            pass

    def delete_expense(self, index):
        """Deletes a specific expense by index and refreshes UI"""
        if 0 <= index < len(self.expenses):
            self.expenses.pop(index)
            self.save_data()
            self.refresh_ui()

    def show_chart(self):
        if not self.expenses:
            return 

        cat_spent = {}
        for item in self.expenses:
            cat = item["category"]
            cat_spent[cat] = cat_spent.get(cat, 0.0) + item["amount"]

        categories = list(cat_spent.keys())
        amounts = list(cat_spent.values())

        plt.figure(figsize=(6, 4))
        plt.bar(categories, amounts, color='#1f77b4', width=0.5)
        plt.xlabel("Categories", fontsize=10, fontweight='bold')
        plt.ylabel("Amount Spent (₱)", fontsize=10, fontweight='bold')
        plt.title("Spending Breakdown by Category", fontsize=12, fontweight='bold')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    def refresh_ui(self):
        """Recalculates numbers and redraws the dynamic expense delete list"""
        total_spent = sum(item["amount"] for item in self.expenses)
        remaining = self.income - total_spent

        # Update summary text
        summary_str = f"Income: ₱{self.income:,.2f}   |   Spent: ₱{total_spent:,.2f}   |   Remaining: ₱{remaining:,.2f}"
        self.stats_label.configure(text=summary_str)

        # Clear existing rows in scrollable frame
        for widget in self.scroll_expenses.winfo_children():
            widget.destroy()

        # Repopulate scrollable frame with current expenses & delete buttons
        if self.expenses:
            for idx, item in enumerate(self.expenses):
                row_frame = ctk.CTkFrame(self.scroll_expenses, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)

                lbl = ctk.CTkLabel(row_frame, text=f"{idx+1}. {item['category']} - ₱{item['amount']:,.2f}", font=("Segoe UI", 12))
                lbl.pack(side="left", padx=5)

                del_btn = ctk.CTkButton(row_frame, text="Delete", width=60, height=24, fg_color="#c92a2a", hover_color="#a61e1e", command=lambda i=idx: self.delete_expense(i))
                del_btn.pack(side="right", padx=5)
        else:
            no_exp_lbl = ctk.CTkLabel(self.scroll_expenses, text="No expenses recorded yet.", font=("Segoe UI", 12), text_color="gray")
            no_exp_lbl.pack(pady=10)

if __name__ == "__main__":
    app = BudgetTrackerApp()
    app.mainloop()