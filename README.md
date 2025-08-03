# 🍗 Broasted Bytes

**A Full Snack Implementation of a Restaurant Web Application**  
Craving crispy chicken and clean code? This project serves both.

---

## What is Broasted Bytes?

Broasted Bytes is a full-stack web application for a restaurant that:

- Provides a slick and intuitive UI for customers.
- Enables order placement, tracking, and menu browsing.
- Includes admin tools to manage orders in real-time.
- Offers a minimal interface for couriers to deliver meals efficiently.
- Implements proper session management and password hashing.
- Is built with simplicity, security, and user experience in mind.

---

## ✨ Features

- 🔥 **Menu Page** – View and order delicious broasted meals.
- 🛒 **Cart System** – Manage and submit your order.
- 🧑‍💼 **Admin Dashboard** – Accept, cancel, or approve orders.
- 🚚 **Courier Page** – Minimal UI with "Delivered" functionality.
- 🧾 **Order Tracking** – Real-time status for every placed order.
- 📬 **Contact Form** – Integrated using [FoxyForm](https://www.foxyform.com) for secure communication.
- 🔐 **Hashed Passwords** – All credentials are stored securely using bcrypt.

---

## Technologies Used

- **Flask** – Web backend framework
- **SQLite3** – Lightweight relational DB
- **HTML/CSS/JavaScript** – Frontend
- **Jinja2** – Flask's templating engine
- **bcrypt** – For password hashing
- **FoxyForm** – Embedded contact form handling

---

## Setup Instructions

1. **Clone the repo**  
   ```bash
   git clone https://github.com/your-username/broasted-bytes.git
   cd broasted-bytes
   flask run --host=0.0.0.0 --port=5000
