# django-referral

````markdown
# Django Referral App

A reusable Django app for implementing a referral system.  
It allows users to generate unique referral links and track sign-ups using those links.

---

## Features
- Generate unique referral codes for each user
- Track referrals from sign-up
- Optionally reward users for successful referrals

---

## Installation

### 1. Install via pip
First, install the app directly from GitHub (or PyPI if you publish it there):

```bash
pip install git+https://github.com/Andrew-oduola/django-referral.git
````



---

### 2. Add to `INSTALLED_APPS`

In your Django project's `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'referral',  # Add this line
]
```

---

### 3. Run Migrations

Run the migrations to create the necessary database tables:

```bash
python manage.py migrate referral
```

---

### 4. Add Middleware (Optional - if using cookies for referral tracking)

In `settings.py`:

```python
MIDDLEWARE = [
    ...
    'referral.middleware.ReferralMiddleware',
]
```

---

### 5. Usage

#### Generate a referral link

Example:
If a user has `referral_code="ABC123"`, their referral link will look like:

```
https://yourdomain.com/signup?ref=ABC123
```

#### Handle sign-ups with referrals

When a new user signs up using a referral link:

* The app detects the referral code
* Links the new user to the referrer
* Saves the relationship in the database

---

## Development Setup (Optional)

If you want to modify or develop the app locally:

```bash
git clone https://github.com/yourusername/django-referral-app.git
cd django-referral-app
pip install -r requirements.txt
```

---

## License

MIT License


