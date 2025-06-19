from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from .forms import *
from .decorators import unauthenticated_user, admin_only
from .models import *

import joblib
import pandas as pd
import os
import json
import requests
import sweetify
from datetime import date, timedelta, datetime

current_year = 2024

def home(request):
    return render(request, "home.html")

def form_view(request):
    return render(request, "form.html")

def car(request):
    cars = Car.objects.filter(status='Available')
    paginator = Paginator(cars, 21)
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
    
    return render(request, 'car.html', context)

def car_detail(request, pk):
    
    is_in_wishlist = False
    car = get_object_or_404(Car, id=pk)
    
    if request.user.is_authenticated:
        is_in_wishlist = Wishlist.objects.filter(user=request.user, car=car).exists()
    
    
    context = {'car': car, 'is_in_wishlist': is_in_wishlist}
    
    return render(request, 'car_detail.html', context)

@login_required(login_url='login')
def dashboard(request):
    
    user = request.user
    
    requests = Request.objects.filter(user=user)
    
    context = {'requests': requests}
    
    return render(request, "dashboard.html", context)

@login_required(login_url='login')
@admin_only
def admin_dashboard(request):
    
    pays = Payment.objects.all()
    
    daily_earnings = "{:,}".format(Payment.objects.filter(payment_date=date.today()).aggregate(Sum('car__price'))['car__price__sum'] or 0)
    
    pending_payments = Payment.objects.filter(status='Waiting For Payment').count()
    
    pending_reservations = Request.objects.filter(status='Validating').count()
    
    context = {'payments': pays, 'daily_earnings': daily_earnings, 'pending_payments': pending_payments, 'pending_reservations':pending_reservations}
    
    return render(request, 'admin_dashboard.html', context)

@csrf_exempt
def predict(request):
    if request.method == 'POST':
        try:
            model_path = os.path.join(os.path.dirname(__file__), '..', 'model', 'best_model_pipeline.pkl')
            model_path = os.path.abspath(model_path)
            model = joblib.load(model_path)

            data = json.loads(request.body.decode('utf-8'))
            df = pd.DataFrame([data])
            df['usage_ratio'] = df['odometer'] / (current_year - df['year'] + 1)
            predicted_price_scaled = model.predict(df)
            min_price = 1000
            max_price = 45000
            predicted_price_usd = predicted_price_scaled * (max_price - min_price) + min_price
            response = {
                "result": f"${predicted_price_usd[0]:,.2f}"
            }
            # Ambil nilai tukar USD -> IDR
            usd_to_idr = get_usd_to_idr_rate()
            predicted_price_idr = predicted_price_usd[0] * usd_to_idr

            html_result = (
             "<div style='color: white;'>"
             f"<p>A car from <strong>{data['year']}</strong> with an odometer reading of "
             f"<strong>{data['odometer']:,} km</strong> is estimated to have the following price:</p>"
             "<ul>"
             f"<li><strong>Estimated Price (USD):</strong> <span style='color: green;'>${predicted_price_usd[0]:,.2f}</span></li>"
             f"<li><strong>Estimated Price (IDR):</strong> <span style='color: blue;'>Rp{predicted_price_idr:,.0f}</span></li>"
             "</ul>"
             "<p>This estimate is influenced by factors such as the car's production year and the total distance it has traveled. "
             "Generally, newer cars with lower odometer readings tend to have higher values.</p>"
             "</div>"
             )


            return JsonResponse({
                "result": html_result
            })
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def get_usd_to_idr_rate():
    try:
        url = "https://v6.exchangerate-api.com/v6/f2e3944a450757659cf4fa03/latest/USD"
        response = requests.get(url, timeout=5)
        data = response.json()
        if response.status_code == 200 and 'conversion_rates' in data:
            return data['conversion_rates'].get('IDR', 16000)
    except Exception as e:
        print("Error fetching exchange rate:", e)
    return 16000

@csrf_exempt
def get_options(request):
    try:
        # Path CSV
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'car_prices_cleaned.csv')
        csv_path = os.path.abspath(csv_path)
        df = pd.read_csv(csv_path)

        if 'model' not in df.columns or 'year' not in df.columns:
            return JsonResponse({'error': "Kolom 'model' atau 'year' tidak ditemukan"}, status=400)

        models = sorted(df['model'].dropna().unique().tolist())
        years = sorted(df['year'].dropna().unique().tolist(), reverse=True)

        return JsonResponse({'models': models, 'years': years})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Login, Register, Logout
@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            sweetify.success(request, 'Login Success', text="You've successfully logged in", persistent='Ok')
            return redirect('home')
        
        else:
            sweetify.error(request, 'Login Failed', text='Username or Password is inccorect', persistent='OK')
        
    return render(request, 'login.html')

@unauthenticated_user
def register(request):
    form = RegisterForm()
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.groups.add(Group.objects.get(name='user'))
            
            sweetify.success(request, 'Register Success', text="You've successfully register, please login", persistent='OK')
            return redirect('login')
        else:
            error_msgs = ''
            
            for field, errors in form.errors.items():
                error_msgs += f"{', '.join(errors,)}\n"
                
            sweetify.error(request, 'Form is not valid', text=error_msgs, persistent='OK')
        
    context = {'form': form}
    
    return render(request, 'register.html', context)

def logoutUser(request):
    logout(request)
    sweetify.success(request, 'Logout Success', text="You've successfully Logout", persistent='Ok')
    return redirect('home')

#Cars
@login_required(login_url='login')
@admin_only
def cars_view(request):
    
    cars = Car.objects.all()
    
    context = {'data': cars}
    
    return render(request, 'cars/cars_table.html', context)

@login_required(login_url='login')
@admin_only
def create_cars(request):
    
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            sweetify.success(
            request,
            title='Success!',
            text='Successfully Create Car Data.',
            icon='success',
            timer=3000
        )
            return redirect("cars_view")
    else:
        form = CarForm()
        
    context = {'form': form}
    
    return render(request, 'cars/cars_create.html', context)

@login_required(login_url='login')
@admin_only
def edit_cars(request, pk):
    data = get_object_or_404(Car, pk=pk)

    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=data)
        if form.is_valid():
            form.save()
            sweetify.success(
            request,
            title='Success!',
            text='Successfully Update Data.',
            icon='success',
            timer=3000
        )
            return redirect('cars_view')
    else:
        form = CarForm(instance=data)
        print("FORM INVALID:", request.FILES)

    context = {'data': data, 'form': form}
    return render(request, 'cars/cars_edit.html', context)

@login_required(login_url='login')
@admin_only
def delete_cars(request, pk):
    data = get_object_or_404(Car, pk=pk)
    
    if request.method == 'POST':
        data.delete()
    
        sweetify.success(
            request,
            title='Success!',
            text='Successfully Delete Car.',
            icon='success',
            timer=3000
        )
        
        return redirect("cars_view")

# Brands
@login_required(login_url='login')
@admin_only
def brands_view(request):
    
    brands = Brand.objects.all()
    
    context = {'data': brands}
    
    return render(request, 'brands/brands_table.html', context)

@login_required(login_url='login')
@admin_only
def create_brands(request):
    
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            sweetify.success(
            request,
            title='Success!',
            text='Successfully Create Brand Data.',
            icon='success',
            timer=3000
        )
            return redirect("brands_view")
    else:
        form = BrandForm()
        
    context = {'form': form}
    
    return render(request, 'brands/brands_create.html', context)

@login_required(login_url='login')
@admin_only
def edit_brands(request, pk):
    brand = get_object_or_404(Brand, pk=pk)

    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            sweetify.success(
            request,
            title='Success!',
            text='Successfully Update Data.',
            icon='success',
            timer=3000
        )
            return redirect('brands_view')
    else:
        form = BrandForm(instance=brand)

    context = {'brand': brand, 'form': form}
    return render(request, 'brands/brands_edit.html', context)

@login_required(login_url='login')
@admin_only
def delete_brands(request, pk):
    data = get_object_or_404(Brand, pk=pk)
    
    if request.method == 'POST':
        data.delete()
    
        sweetify.success(
            request,
            title='Success!',
            text='Successfully Delete Brand.',
            icon='success',
            timer=3000
        )
        
        return redirect("brands_view")

# Colors
@login_required(login_url='login')
@admin_only
def colors_view(request):
    
    colors = Color.objects.all()
    
    context = {'data': colors}
    
    return render(request, 'colors/colors_table.html', context)

@login_required(login_url='login')
@admin_only
def create_colors(request):
    
    if request.method == 'POST':
        form = ColorForm(request.POST)
        if form.is_valid():
            form.save()
            sweetify.success(
            request,
            title='Success!',
            text='Successfully Create Color Data.',
            icon='success',
            timer=3000
        )
            return redirect("colors_view")
    else:
        form = ColorForm()
        
    context = {'form': form}
    
    return render(request, 'colors/colors_create.html', context)

@login_required(login_url='login')
@admin_only
def edit_colors(request, pk):
    color = get_object_or_404(Color, pk=pk)

    if request.method == 'POST':
        form = ColorForm(request.POST, instance=color)
        if form.is_valid():
            form.save()
            sweetify.success(
            request,
            title='Success!',
            text='Successfully Update Data.',
            icon='success',
            timer=3000
        )
            return redirect('colors_view')
    else:
        form = ColorForm(instance=color)

    context = {'color': color, 'form': form}
    return render(request, 'colors/colors_edit.html', context)

@login_required(login_url='login')
@admin_only
def delete_colors(request, pk):
    data = get_object_or_404(Color, pk=pk)
    
    if request.method == 'POST':
        data.delete()
    
        sweetify.success(
            request,
            title='Success!',
            text='Successfully Delete color.',
            icon='success',
            timer=3000
        )
        
        return redirect("colors_view")

# Bodies
@login_required(login_url='login')
@admin_only
def body_view(request):
    
    body = Body.objects.all()
    
    context = {'data': body}
    
    return render(request, 'body/body_table.html', context)

@login_required(login_url='login')
@admin_only
def create_body(request):
    
    if request.method == 'POST':
        form = BodyForm(request.POST)
        if form.is_valid():
            form.save()
            sweetify.success(
            request,
            title='Success!',
            text='Successfully Create Color Body.',
            icon='success',
            timer=3000
        )
            return redirect("body_view")
    else:
        form = BodyForm()
        
    context = {'form': form}
    
    return render(request, 'body/body_create.html', context)

@login_required(login_url='login')
@admin_only
def edit_body(request, pk):
    body = get_object_or_404(Body, pk=pk)

    if request.method == 'POST':
        form = BodyForm(request.POST, instance=body)
        if form.is_valid():
            form.save()
            sweetify.success(
            request,
            title='Success!',
            text='Successfully Update Body.',
            icon='success',
            timer=3000
        )
            return redirect('body_view')
    else:
        form = BodyForm(instance=body)

    context = {'body': body, 'form': form}
    return render(request, 'body/body_edit.html', context)

@login_required(login_url='login')
@admin_only
def delete_body(request, pk):
    data = get_object_or_404(Body, pk=pk)
    
    if request.method == 'POST':
        data.delete()
    
        sweetify.success(
            request,
            title='Success!',
            text='Successfully Delete body.',
            icon='success',
            timer=3000
        )
        
        return redirect("body_view")

# Interior Colors
@login_required(login_url='login')
@admin_only
def interior_colors_view(request):
    
    color = InteriorColor.objects.all()
    
    context = {'colors': color}
    
    return render(request, 'interiorColors/interior_colors_table.html', context)

@login_required(login_url='login')
@admin_only
def create_interior_colors(request):
    
    if request.method == 'POST':
        form = InteriorColorForm(request.POST)
        if form.is_valid():
            form.save()
            sweetify.success(
            request,
            title='Success!',
            text='Successfully Create Interior Color Data.',
            icon='success',
            timer=3000
        )
            return redirect("interior_colors_view")
    else:
        form = InteriorColorForm()
        
    context = {'form': form}
    
    return render(request, 'interiorColors/interior_colors_create.html', context)

@login_required(login_url='login')
@admin_only
def edit_interior_colors(request, pk):
    color = get_object_or_404(InteriorColor, pk=pk)

    if request.method == 'POST':
        form = InteriorColorForm(request.POST, instance=color)
        if form.is_valid():
            form.save()
            sweetify.success(
            request,
            title='Success!',
            text='Successfully Update Data.',
            icon='success',
            timer=3000
        )
            return redirect('interior_colors_view')
    else:
        form = InteriorColorForm(instance=color)

    context = {'color': color, 'form': form}
    return render(request, 'interiorColors/interior_colors_edit.html', context)

@login_required(login_url='login')
@admin_only
def delete_interior_colors(request, pk):
    data = get_object_or_404(InteriorColor, pk=pk)
    
    if request.method == 'POST':
        data.delete()
    
        sweetify.success(
            request,
            title='Success!',
            text='Successfully Delete interior color.',
            icon='success',
            timer=3000
        )
        
        return redirect("interior_colors_view")

# Requests
@login_required(login_url='login')
@admin_only
def requests_view(request):
    
    requests = Request.objects.all()
    
    context = {'requests': requests}
    
    return render(request, 'requests/requests_table.html', context)

@login_required(login_url='login')
def cancel_reservations(request, pk):
    data = get_object_or_404(Request, pk=pk)
    
    if request.method == 'POST':
        
        data_mobil = data.car
        data_mobil.status = 'Available'
        data_mobil.save()
        
        data.delete()
        sweetify.success(
            request,
            title='Success!',
            text='Successfully Cancel.',
            icon='success',
            timer=3000
        )
        
        user = request.user
        group = 'admin'
        
        if user.groups.filter(name=group).exists():
            return redirect('requests_view')
        else:
            return redirect('dashboard')

@login_required(login_url='login')
@admin_only
def validate_reservations(request,pk):
    data  = get_object_or_404(Request, pk=pk)
    
    if request.method == 'POST':
        
        pay = Payment()
        pay.user = data.user
        pay.car = data.car
        pay.status = 'Waiting For Payment'
        pay.save()
        
        data.status = 'Validated'
        data.save()
        
        sweetify.success(request, 'Successfully validate the data')
        
        return redirect('requests_view')

@login_required(login_url='login')
@admin_only
def validate_payment(request, pk):
    data = get_object_or_404(Payment, pk=pk)
    
    if request.method == 'POST':
        
        data.status = 'Paid'
        data.payment_date = date.today()
        data.save()
        
        return redirect('admin_dashboard')

# Reservations
@login_required(login_url='login')
def create_reservations(request, pk):
    
    car = get_object_or_404(Car, pk=pk)
    
    min_date = date.today().isoformat()
    max_date = (date.today() + timedelta(days=14)).isoformat()
    
    min_time = "10:00"
    max_time = "16:00"
    
    context = {'car': car, 'min_date': min_date, 'max_date':max_date, 'min_time':min_time, 'max_time':max_time}
    
    if request.method == 'POST':
        input_date = request.POST.get('input_date')
        input_time = request.POST.get('input_time')
        
        parsed_date = datetime.strptime(input_date, '%Y-%m-%d').date()
        parsed_time = datetime.strptime(input_time, '%H:%M').time()
        
        reserve = Request()
        
        reserve.date = parsed_date
        reserve.time = parsed_time
        reserve.user = request.user
        reserve.car = car
        reserve.status = 'Validating'
        reserve.car.status = 'Reserved'
        reserve.save()
        car.save()
        
        sweetify.success(
            request,
            title='Success!',
            text='Successfully Create Reservation Data.',
            icon='success',
            timer=3000
        )

        user = request.user
        group = 'admin'
        
        if user.groups.filter(name=group).exists():
            return redirect('requests_view')
        else:
            return redirect('dashboard')
    
    return render(request, 'requests/requests_create.html', context)

# Wishlist
@login_required(login_url='login')
def wishlists(request):
    
    wishlist = Wishlist.objects.filter(user=request.user)
    
    paginator = Paginator(wishlist, 21)
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
        
    return render(request, 'wishlist.html', context)

@login_required(login_url='login')
def toggle_wishlist(request, pk):
    car = get_object_or_404(Car, id=pk)
    
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, car=car)
    
    if created:
        pass
    else:
        wishlist_item.delete()
        
    return redirect('car_detail', pk = car.id)