from flask import Flask, render_template, request, redirect, url_for, flash,session
import json
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

def load_data(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("\n⚠️ No existing data found. Starting with default cars. ⚠️\n")
        return [
            {"Model": "Toyota Corolla", "Registration_plate": "A1234BC", "Price_per_day": 50, "statu": "Available", "reservation_end": None},
            {"Model": "Hyundai Elantra", "Registration_plate": "B5678DE", "Price_per_day": 45, "statu": "Available", "reservation_end": None},
            {"Model": "Kia Picanto", "Registration_plate": "C9087FG", "Price_per_day": 30, "statu": "Available", "reservation_end": None},
            {"Model": "Chevrolet Malibu", "Registration_plate": "D4567HI", "Price_per_day": 60, "statu": "Available", "reservation_end": None},
            {"Model": "Mercedes-Benz G-Class", "Registration_plate": "E1122JK", "Price_per_day": 150, "statu": "Available", "reservation_end": None},
            {"Model": "Nissan Patrol", "Registration_plate": "F3344LM", "Price_per_day": 100, "statu": "Available", "reservation_end": None},
            {"Model": "Ford Mustang", "Registration_plate": "G7788NO", "Price_per_day": 120, "statu": "Available", "reservation_end": None},
            {"Model": "Jeep Wrangler", "Registration_plate": "H9900PQ", "Price_per_day": 90, "statu": "Available", "reservation_end": None},
            {"Model": "Tesla Model 3", "Registration_plate": "I2468RS", "Price_per_day": 130, "statu": "Available", "reservation_end": None},
            {"Model": "Honda Civic", "Registration_plate": "J1357TU", "Price_per_day": 40, "statu": "Available", "reservation_end": None}
        ]

def load_users(filename="users.json"):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("\n⚠️ No existing user data found. Default admin created. ⚠️\n")
        return {
            "admin": "admin"
        }

def save_users(users, filename="users.json"):
    with open(filename, "w") as file:
        json.dump(users, file, indent=4)

def save_to_json(cars, filename="Cars.json"):
    with open(filename, "w") as file:
        json.dump(cars, file, indent=4)

@app.route('/')
def index():
    cars = load_data("Cars.json")
    return render_template('index.html', cars=cars)

@app.route('/login', methods=['GET', 'POST'])
def login():
    users = load_users()
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        if username in users and users[username] == password:
            session['username'] = username
            if username == 'admin':
                return redirect(url_for('admin_panel'))
            return redirect(url_for('user_panel'))
        else:
            flash("❌ Invalid username or password. Please try again. ❌", "error")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    users = load_users()
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        if username in users:
            flash("❌ Username already exists. Please choose a different one. ❌", "error")
        else:
            users[username] = password
            save_users(users)
            flash("🎉 Signup successful! You can now log in. 🎉", "success")
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/cars')
def display_cars():
    cars = load_data("Cars.json")
    return render_template('cars.html', cars=cars)

@app.route('/book_car', methods=['GET', 'POST'])
def book_car():
    cars = load_data("Cars.json")
    if request.method == 'POST':
        reg_number = request.form['reg_number'].upper().strip()  # استلام رقم السيارة
        car_found = None
        
        # البحث عن السيارة في قائمة السيارات
        for car in cars:
            if car["Registration_plate"] == reg_number:
                car_found = car
                break

        # إذا كانت السيارة غير موجودة
        if not car_found:
            flash("❌ Car not found. Please enter a valid registration number. ❌", "error")
            return redirect(url_for('display_cars'))

        # التحقق من حالة السيارة إذا كانت متاحة
        if car_found["statu"] != "Available":
            flash(f"❌ The car {car_found['Model']} is not available. Please choose another car. ❌", "error")
            return redirect(url_for('display_cars'))

        # التحقق من عدد الأيام المدخلة
        try:
            days_of_book = int(request.form['days'])
            if days_of_book <= 0:
                flash("❌ The number of days must be greater than 0. Please enter a valid number. ❌", "error")
                return redirect(url_for('display_cars'))
        except ValueError:
            flash("❌ Invalid input for days. Please enter a valid number. ❌", "error")
            return redirect(url_for('display_cars'))

        # حساب التكلفة الإجمالية
        total_cost = days_of_book * car_found["Price_per_day"]
        reservation_end_date = datetime.now() + timedelta(days=days_of_book)
        formatted_end_date = reservation_end_date.strftime("%Y-%m-%d")
        
        # تحديث حالة السيارة بعد الحجز
        car_found["statu"] = "Unavailable"
        car_found["reservation_end"] = formatted_end_date
        
        # حفظ البيانات المحدثة
        save_to_json(cars, "Cars.json")
        
        # عرض رسالة نجاح
        flash(f"🎉 Successfully booked {car_found['Model']} for {days_of_book} days. Total cost: ${total_cost}. 🎉", "success")
        return redirect(url_for('display_cars'))

    return render_template('book_car.html', cars=cars)


@app.route('/user_panel')
def user_panel():
    username = session.get('username', None)
    if not username:
        return redirect(url_for('login'))
    return render_template('user_panel.html', username=username)

@app.route('/admin_panel')
def admin_panel():
    username = session.get('username', None)
    if username != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_panel.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/admin/delete_car', methods=['GET', 'POST'])
def delete_car():
    cars = load_data("Cars.json")
    if request.method == 'POST':
        reg_number = request.form['reg_number'].upper().strip()
        car_found = None
        for car in cars:
            if car["Registration_plate"] == reg_number:
                car_found = car
                cars.remove(car)
                save_to_json(cars, "Cars.json")
                flash(f"✅ Car with registration plate {reg_number} deleted successfully. ✅", "success")
                break

        if not car_found:
            flash("❌ Car not found. ❌", "error")
        return redirect(url_for('admin_panel'))

    return render_template('delete_car.html', cars=cars)

@app.before_request
def restrict_admin_routes():
    if 'admin' in request.path and session.get('username') != 'admin':
        flash("❌ Unauthorized access. Please log in as admin. ❌", "error")
        return redirect(url_for('login'))

@app.route('/admin/edit_car', methods=['GET', 'POST'])
def edit_car():
    cars = load_data("Cars.json")
    if request.method == 'POST':
        reg_number = request.form['reg_number'].upper().strip()
        car_found = None
        for car in cars:
            if car["Registration_plate"] == reg_number:
                car_found = car
                new_model = request.form['new_model'].strip()
                new_price = request.form['new_price'].strip()
                if new_model:
                    car["Model"] = new_model
                if new_price:
                    try:
                        car["Price_per_day"] = int(new_price)
                    except ValueError:
                        flash("❌ Invalid price. Please enter a valid number. ❌", "error")
                        return redirect(url_for('edit_car'))
                save_to_json(cars, "Cars.json")
                flash("✅ Car updated successfully. ✅", "success")
                return redirect(url_for('edit_car'))

        if not car_found:
            flash("❌ Car not found. ❌", "error")
    return render_template('edit_car.html', cars=cars)

@app.route('/admin/users', methods=['GET', 'POST'])
def display_users():
    users = load_users()
    if request.method == 'POST':
        username = request.form['username'].strip()
        if username in users:
            del users[username]
            save_users(users)
            flash(f"✅ User {username} deleted successfully. ✅", "success")
        else:
            flash("❌ User not found. ❌", "error")
    return render_template('del_user.html', users=users)



if __name__ == '__main__':
    app.run(debug=True)
    