from django.urls import path

from .views import *


urlpatterns = [

    path(
        "register/",
        patient_register,
        name="patient_register"
    ),

     path(
        "login/",
        patient_login,
        name="patient_login"
    ),
     path(
    "dashboard/",
    patient_dashboard,
    name="patient_dashboard"
),
     path(
    "categories/",
    doctor_categories,
    name="doctor_categories"
),
     path(
    "doctor/availability/",
    doctor_availability,
    name="doctor_availability"
),
     path(
    "doctor/register/",
    doctor_register,
    name="doctor_register"
),
     
     path(
    "doctor/login/",
    doctor_login,
    name="doctor_login"
),
     path(
    "doctor/dashboard/",
    doctor_dashboard,
    name="doctor_dashboard"
),
     path(
    "doctor/<int:doctor_id>/slots/",
    doctor_slots,
    name="doctor_slots"
),
     
     path(
    "categories/<int:category_id>/doctors/",
    doctors_by_category,
    name="doctors_by_category"
),
path(
    "book/<int:slot_id>/",
    book_slot,
    name="book_slot"
),

path(
    "booking/<int:booking_id>/",
    booking_confirmation,
    name="booking_confirmation"
),
path(
    "my-bookings/",
    my_bookings,
    name="my_bookings"
),
path(
    "booking/<int:booking_id>/cancel/",
    cancel_booking,
    name="cancel_booking"
),
path(
    "logout/",
    patient_logout,
    name="patient_logout"
),
path(
    "doctor/bookings/",
    doctor_bookings,
    name="doctor_bookings"
),

path(
    "doctor/my-slots/",
    doctor_slots_list,
    name="doctor_slots_list"
),
path(
    "doctor/logout/",
    doctor_logout,
    name="doctor_logout"
),
path(
    "doctor/profile/",
    doctor_profile,
    name="doctor_profile"
),
path(
    "",
    home,
    name="home"
)
]