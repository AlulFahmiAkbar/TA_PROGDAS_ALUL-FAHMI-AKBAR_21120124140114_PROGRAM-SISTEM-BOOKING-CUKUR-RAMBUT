import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from collections import deque, defaultdict
from datetime import datetime
import bcrypt
import pickle
import os

class BarberShop:
    def __init__(self):
        self.queue = deque()
        self.completed = []
        self.daily_bookings = defaultdict(list)
        self.users = {}

    def add_booking(self, name, booking_time):
        date = booking_time.split(" ")[0]
        if len(self.daily_bookings[date]) >= 15:
            return False, f"Pemesanan untuk {date} sudah penuh (maksimal 15 orang)."

        for booked_name, booked_time in self.daily_bookings[date]:
            if booked_time == booking_time:
                return False, f"Waktu {booking_time} sudah dipesan oleh {booked_name}."

        try:
            booking_datetime = datetime.strptime(booking_time, "%Y-%m-%d %H:%M")
            opening_time = datetime.strptime(f"{date} 09:00", "%Y-%m-%d %H:%M")
            closing_time = datetime.strptime(f"{date} 21:00", "%Y-%m-%d %H:%M")

            if not (opening_time <= booking_datetime <= closing_time):
                return False, "Maaf, kami sudah tutup."
        except ValueError:
            return False, "Format waktu salah! Gunakan format: HH:MM"

        self.queue.append((name, booking_time))
        self.daily_bookings[date].append((name, booking_time))
        return True, "Pemesanan berhasil ditambahkan."

    def complete_booking(self):
        if self.queue:
            completed_customer = self.queue.popleft()
            self.completed.append(completed_customer)
            booking_time = completed_customer[1]
            date = booking_time.split(" ")[0]
            self.daily_bookings[date].remove(completed_customer)
            return completed_customer
        return None

    def get_current_queue(self):
        return list(self.queue)

    def get_completed_customers(self):
        return self.completed

    def save_data(self, filename):
        with open(filename, "wb") as file:
            pickle.dump(self.daily_bookings, file)
            pickle.dump(self.completed, file)
            pickle.dump(self.users, file)

    def load_data(self, filename):
        if os.path.exists(filename):
            with open(filename, "rb") as file:
                self.daily_bookings = pickle.load(file)
                self.completed = pickle.load(file)
                self.users = pickle.load(file)

    def register_user(self, username, password):
        if username in self.users:
            return False, "Username sudah terdaftar."
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.users[username] = hashed_password
        return True, "Registrasi berhasil!"

    def authenticate_user(self, username, password):
        if username in self.users:
            hashed_password = self.users[username]
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                return True
        return False


class BarberShopApp:
    def __init__(self, root):
        self.shop = BarberShop()
        self.root = root
        self.root.title("Booking Pangkas Rambut by Mas AL")
        self.root.geometry("600x750")
        self.root.configure(bg="#e3f2fd")

        self.shop.load_data("barbershop_data.pkl")

        self.login_frame = self.create_login_frame()
        self.main_frame = self.create_main_frame()
        self.main_frame.pack_forget()

    def create_login_frame(self):
        login_frame = tk.Frame(self.root, bg="#e3f2fd", padx=20, pady=20)

        tk.Label(login_frame, text="Login", font=("Arial", 20, "bold"), bg="#e3f2fd", fg="#1565c0").pack(pady=10)

        tk.Label(login_frame, text="Username", font=("Arial", 12), bg="#e3f2fd", fg="#0d47a1").pack(pady=5)
        self.username_entry = tk.Entry(login_frame, font=("Arial", 14), width=30)
        self.username_entry.pack(pady=5)

        tk.Label(login_frame, text="Password", font=("Arial", 12), bg="#e3f2fd", fg="#0d47a1").pack(pady=5)
        self.password_entry = tk.Entry(login_frame, font=("Arial", 14), show="*", width=30)
        self.password_entry.pack(pady=5)

        tk.Button(
            login_frame, text="Login", font=("Arial", 14), bg="#1976d2", fg="#fff", command=self.login
        ).pack(pady=10, ipadx=20)

        tk.Button(
            login_frame, text="Register", font=("Arial", 14), bg="#d32f2f", fg="#fff", command=self.register
        ).pack(pady=10, ipadx=20)

        login_frame.pack(fill=tk.BOTH, expand=True)
        return login_frame

    def create_main_frame(self):
        main_frame = tk.Frame(self.root, bg="#e3f2fd", padx=20, pady=20)

        tk.Label(main_frame, text="Booking Pangkas Rambut  Mas AL", font=("Arial", 20, "bold"), bg="#e3f2fd", fg="#1565c0").pack(pady=10)

        booking_frame = tk.Frame(main_frame, bg="#e3f2fd")
        tk.Label(booking_frame, text="Nama Pelanggan:", font=("Arial", 12), bg="#e3f2fd", fg="#0d47a1").grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = tk.Entry(booking_frame, font=("Arial", 12), width=25)
        self.name_entry.grid(row=0, column=1, pady=5, padx=10)

        tk.Label(booking_frame, text="Tanggal:", font=("Arial", 12), bg="#e3f2fd", fg="#0d47a1").grid(row=1, column=0, sticky="w", pady=5)
        self.date_entry = DateEntry(booking_frame, font=("Arial", 12), date_pattern="yyyy-mm-dd", width=22)
        self.date_entry.grid(row=1, column=1, pady=5, padx=10)

        tk.Label(booking_frame, text="Waktu (HH:MM):", font=("Arial", 12), bg="#e3f2fd", fg="#0d47a1").grid(row=2, column=0, sticky="w", pady=5)
        self.time_entry = tk.Entry(booking_frame, font=("Arial", 12), width=25)
        self.time_entry.grid(row=2, column=1, pady=5, padx=10)

        tk.Button(booking_frame, text="Tambah Pemesanan", font=("Arial", 12), bg="#1976d2", fg="#fff", command=self.add_booking).grid(row=3, column=1, pady=10, sticky="e")
        booking_frame.pack(pady=20)

        queue_completed_frame = tk.Frame(main_frame, bg="#e3f2fd")

        queue_frame = tk.Frame(queue_completed_frame, bg="#e3f2fd")
        tk.Label(queue_frame, text="Antrian Saat Ini", font=("Arial", 14, "bold"), bg="#e3f2fd", fg="#0d47a1").pack(pady=10)
        self.queue_listbox = tk.Listbox(queue_frame, font=("Arial", 12), width=40, height=10, bg="#ffffff", fg="#0d47a1")
        self.queue_listbox.pack(pady=10)
        tk.Button(queue_frame, text="Selesaikan Pemesanan", font=("Arial", 12), bg="#43a047", fg="#fff", command=self.complete_booking).pack()
        queue_frame.grid(row=0, column=0, padx=10)

        completed_frame = tk.Frame(queue_completed_frame, bg="#e3f2fd")
        tk.Label(completed_frame, text="Pelanggan Selesai", font=("Arial", 14, "bold"), bg="#e3f2fd", fg="#0d47a1").pack(pady=10)
        self.completed_listbox = tk.Listbox(completed_frame, font=("Arial", 12), width=40, height=10, bg="#ffffff", fg="#880e4f")
        self.completed_listbox.pack(pady=10)
        tk.Button(completed_frame, text="Hapus Pelanggan Selesai", font=("Arial", 12), bg="#d32f2f", fg="#fff", command=self.remove_completed_customer).pack()
        completed_frame.grid(row=0, column=1, padx=10)

        queue_completed_frame.pack(pady=20)

        main_frame.pack(fill=tk.BOTH, expand=True)
        return main_frame

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        success, message = self.shop.register_user(username, password)
        messagebox.showinfo("Registrasi", message if success else "Gagal: " + message)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if self.shop.authenticate_user(username, password):
            self.login_frame.pack_forget()
            self.main_frame.pack(fill=tk.BOTH, expand=True)
        else:
            messagebox.showerror("Login Gagal", "Username atau Password salah!")

    def add_booking(self):
        name = self.name_entry.get().strip()
        booking_time = f"{self.date_entry.get()} {self.time_entry.get()}"
        success, message = self.shop.add_booking(name, booking_time)
        if success:
            self.update_queues()
        messagebox.showinfo("Pemesanan", message)

    def complete_booking(self):
        completed_customer = self.shop.complete_booking()
        if completed_customer:
            self.update_queues()
            messagebox.showinfo("Pelanggan Selesai", f"Selamat! Pemesanan {completed_customer[0]} selesai!")
        else:
            messagebox.showwarning("Tidak Ada Pemesanan", "Antrian kosong!")

    def remove_completed_customer(self):
        if self.completed_listbox.curselection():
            selected = self.completed_listbox.curselection()[0]
            self.shop.completed.pop(selected)
            self.update_queues()
        else:
            messagebox.showwarning("Pilih Pelanggan", "Pilih pelanggan yang ingin dihapus dari daftar selesai!")

    def update_queues(self):
        self.queue_listbox.delete(0, tk.END)
        for customer in self.shop.get_current_queue():
            self.queue_listbox.insert(tk.END, f"{customer[0]} - {customer[1]}")

        self.completed_listbox.delete(0, tk.END)
        for customer in self.shop.get_completed_customers():
            self.completed_listbox.insert(tk.END, f"{customer[0]} - {customer[1]}")

        self.shop.save_data("barbershop_data.pkl")


if __name__ == "__main__":
    root = tk.Tk()
    app = BarberShopApp(root)
    root.mainloop()
