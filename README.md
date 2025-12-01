# 🛍️ Ecommerce with Django

Este es un proyecto desarrollado como parte del **curso de Django Full Stack**, donde se implementan las funcionalidades básicas y esenciales de una aplicación de **comercio electrónico** moderna.

---

## ✨ Key Features

The project is designed to be a robust MVP (Minimum Viable Product) of an e-commerce platform, including the following features:

* **Product Catalog:** A comprehensive listing of all available products.
* **Detailed Product View:** In-depth view of each product with images, descriptions, and available options.
* **Variant Handling:** Support for different product variants (e.g., size, color), impacting price and stock levels.
* **Shopping Cart Management (Anonymous and Authenticated):**
    * Non-authenticated users can add products to the cart.
    * The cart is maintained and migrated to the user's session once they log in or register.
* **User Account Management:** Features for registration, login, and profile management.
* **Integrated Payment Process:** Implementation of the *checkout* process using the **PayPal API** for secure payment processing.

---

## 🛠️ Technologies Used

This project was built using the following technology *stack*:

* **Backend:**
    * **Python** (Recommended version: 3.13.5)
    * **Django** (Main Framework)
* **Base de Datos:**
    * **SQLite** (For initial development)
* **Frontend:**
    * **HTML, CSS** (with Bootstrap)
    * **JavaScript** (For dynamic cart interaction and PayPal checkout)
* **Pagos:**
    * **PayPal API** (Integration for processing payments)
 
## 🚀 Local Installation and Setup

Follow these steps to set up and run the project on your local machine:

1. **Clone the Repository**
```bash
git clone [YOUR_REPOSITORY_URL]
cd [project-directory-name]
```

2. **Create and Activate the Virtual Environment**
```bash
# Create a virtual enviroment
python -m venv venv

# Activate environment (Linux/macOS)
source venv/bin/activate

# Activate environment (Windows)
.\venv\Scripts\activate
```
3. **Install Dependencies**
```bash
pip install -r requirements.txt
```
4. **Configure Environment Variables**

Create a file named .env in the project root and add your credentials.

```bash
SECRET_KEY = 'YOUR DJANGO SECRET KEY'
EMAIL_HOST = 'FOR EXAMPLE smtp.gmail.com'
EMAIL_PORT = 'IN GMAIL CASE 587'
EMAIL_HOST_USER = 'HOST TO SEND EMAILS'
EMAIL_HOST_PASSWORD = 'APLICATION KEY FOR THE EMAIL'
EMAIL_USE_TLS = True

PAYPAL_CLIENT_ID = 'I WILL EXPLAIN HOW TO GET THIS CREDENTIALS'
PAYPAL_CLIENT_SECRET = 'SO THIS ONE'
DEBUG = True # FOR DEVELOPMENT

ADMIN_HONEYPOT_URL = 'WHAT EVER URL YOU WANT FOR THE ADMIN PANEL'
```

5. **Database Migrations**

Apply the initial migrations to create the database structure.

```bash
python manage.py migrate
```

6. **Create superuser**

To access the Django admin panel.

```bash
python manage.py createsuperuser
```

7. **Run server**
```bash
python manage.py runserver
```

## 💳 PayPal API Integration Process
To integrate the PayPal API, you must first create a PayPal account (either personal or business) to gain access to the Developer Dashboard at developer.paypal.com.

**Sandbox Environment:**

* Currently, upon accessing the dashboard, the Sandbox environment is typically created by default.

* This includes a pre-configured test application and test user accounts: one Business account (to receive the fictional funds) and one Personal account (to simulate the purchase).

**API Credentials:**

* The crucial Client ID and Client Secret are found within the details of this default application (under the REST API apps section).

* These two keys are necessary to authenticate and initiate transactions within your Django application.

<img width="1814" height="667" alt="image" src="https://github.com/user-attachments/assets/8ce1a418-7917-4031-84bb-1b416ddffc9b" />

