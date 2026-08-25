import json
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import *
from .forms import *
from .models import *
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.utils import timezone
from django.http import JsonResponse
from google import genai
from django.conf import settings


def home(request):

    doctors = Doctor.objects.filter(
        is_approved=True
    ).select_related(
        "user",
        "category"
    )[:6]

    doctor_count = Doctor.objects.filter(
        is_approved=True
    ).count()

    patient_count = Patient.objects.count()

    category_count = DoctorCategory.objects.count()

    booking_count = Booking.objects.filter(
        status="confirmed"
    ).count()

    return render(
        request,
        "consultancy/index.html",
        {
            "doctors": doctors,
            "doctor_count": doctor_count,
            "patient_count": patient_count,
            "category_count": category_count,
            "booking_count": booking_count,
        }
    )
    
# patient side
def patient_register(request):

    if request.method == "POST":

        form = PatientRegisterForm(request.POST)

        if form.is_valid():

            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            confirm_password = form.cleaned_data["confirm_password"]

            if password != confirm_password:

                form.add_error("confirm_password","Passwords do not match.")

            elif User.objects.filter(email=email).exists():

                form.add_error("email","Email already registered." )

            else:

                user = User.objects.create(name=name,email=email,password=make_password(password),role="patient")

                Patient.objects.create(user=user)

                return redirect("patient_login")

    else:

        form = PatientRegisterForm()

    return render(request,"consultancy/register.html",{"form": form})
    
def patient_login(request):

    if request.method == "POST":

        form = PatientLoginForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            try:

                user = User.objects.get(
                    email=email,
                    role="patient"
                )

                if check_password(password, user.password):

                    request.session["user_id"] = user.id
                    request.session["role"] = user.role

                    return redirect("patient_dashboard")

                else:

                    form.add_error("password","Invalid password.")

            except User.DoesNotExist:

                form.add_error("email","Patient account not found.")
    else:

        form = PatientLoginForm()

    return render(
        request,"consultancy/login.html", {"form": form})

def patient_dashboard(request):

    user_id = request.session.get("user_id")

    if not user_id:

        return redirect("patient_login")

    user = User.objects.get(id=user_id)

    return render(request,"consultancy/dashboard.html",{"user": user})

def doctor_categories(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("patient_login")

    categories = DoctorCategory.objects.all()

    return render(
        request,
        "consultancy/categories.html",
        {"categories": categories}
    )

def doctors_by_category(request, category_id):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("patient_login")

    category = DoctorCategory.objects.get(
        id=category_id
    )

    doctors = Doctor.objects.filter(
        category=category,
        is_approved=True,
        is_available=True
    )

    return render(
        request,
        "consultancy/doctors.html",
        {
            "category": category,
            "doctors": doctors
        }
    ) 
# doctor side

def doctor_register(request):

    if request.method == "POST":

        form = DoctorRegisterForm(request.POST)

        if form.is_valid():

            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            confirm_password = form.cleaned_data["confirm_password"]
            category = form.cleaned_data["category"]
            qualification = form.cleaned_data["qualification"]
            experience = form.cleaned_data["experience"]
            consultation_fee = form.cleaned_data["consultation_fee"]
            about = form.cleaned_data["about"]

            if password != confirm_password:

                form.add_error("confirm_password","Passwords do not match.")

            elif User.objects.filter(email=email).exists():

                form.add_error("email","Email already registered.")

            else:

                user = User.objects.create(

                    name=name,

                    email=email,

                    password=make_password(password),

                    role="doctor"

                )

                Doctor.objects.create(

                    user=user,

                    category=category,

                    qualification=qualification,

                    experience=experience,

                    consultation_fee=consultation_fee,

                    about=about,

                    is_approved=False,

                    is_available=True

                )

                return redirect("doctor_login")

    else:

        form = DoctorRegisterForm()

    return render(
        request,
        "consultancy/doctor_register.html",
        {"form": form}
    )   
    
def doctor_login(request):

    if request.method == "POST":

        form = DoctorLoginForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            try:

                user = User.objects.get(email=email,role="doctor")

                if check_password(password,user.password):

                    request.session["user_id"] = user.id
                    request.session["role"] = user.role

                    return redirect("doctor_dashboard")

                else:

                    form.add_error("password","Invalid password.")

            except User.DoesNotExist:

                form.add_error("email","Doctor account not found.")

    else:

        form = DoctorLoginForm()

    return render(request,"consultancy/doctor_login.html",{"form": form})
    
def doctor_dashboard(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("doctor_login")

    user = User.objects.get(id=user_id)

    if user.role != "doctor":
        return redirect("patient_dashboard")

    doctor = Doctor.objects.get(user=user)

    return render(
        request,
        "consultancy/doctor_dashboard.html",
        {
            "user": user,
            "doctor": doctor
        }
    )
# patient side

def doctor_availability(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("doctor_login")

    user = User.objects.get(
        id=user_id
    )

    if user.role != "doctor":
        return redirect("patient_dashboard")

    doctor = Doctor.objects.get(
        user=user
    )

    if request.method == "POST":

        form = AvailabilityForm(request.POST)

        if form.is_valid():

            date = form.cleaned_data["date"]

            session = form.cleaned_data["session"]

            # -----------------------------
            # Check past date
            # -----------------------------

            today = timezone.localdate()

            if date < today:

                form.add_error(
                    "date",
                    "You cannot create slots for a past date."
                )

            else:

                # -----------------------------
                # Check duplicate slots
                # -----------------------------

                existing_slots = Slot.objects.filter(
                    doctor=doctor,
                    date=date,
                    session=session
                ).exists()

                if existing_slots:

                    form.add_error(
                        "session",
                        "Slots already exist for this date and session."
                    )

                else:

                    # -----------------------------
                    # Session timings
                    # -----------------------------

                    if session == "morning":

                        start_time = datetime.strptime(
                            "09:00",
                            "%H:%M"
                        ).time()

                        end_time = datetime.strptime(
                            "12:20",
                            "%H:%M"
                        ).time()

                    elif session == "afternoon":

                        start_time = datetime.strptime(
                            "13:00",
                            "%H:%M"
                        ).time()

                        end_time = datetime.strptime(
                            "16:20",
                            "%H:%M"
                        ).time()

                    else:

                        start_time = datetime.strptime(
                            "17:00",
                            "%H:%M"
                        ).time()

                        end_time = datetime.strptime(
                            "20:20",
                            "%H:%M"
                        ).time()

                    # -----------------------------
                    # Generate slots
                    # -----------------------------

                    current_time = datetime.combine(
                        date,
                        start_time
                    )

                    final_time = datetime.combine(
                        date,
                        end_time
                    )

                    slot_number = 1

                    while (
                        current_time < final_time
                        and slot_number <= 20
                    ):

                        slot_start = current_time

                        slot_end = current_time + timedelta(
                            minutes=10
                        )

                        Slot.objects.create(

                            doctor=doctor,

                            date=date,

                            session=session,

                            slot_number=slot_number,

                            start_time=slot_start.time(),

                            end_time=slot_end.time()

                        )

                        current_time = slot_end

                        slot_number += 1

                    return redirect(
                        "doctor_slots_list"
                    )

    else:

        form = AvailabilityForm()

    return render(
        request,
        "consultancy/availability.html",
        {
            "form": form
        }
    )

# doctor side
def doctor_slots(request, doctor_id):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("patient_login")

    doctor = Doctor.objects.get(
        id=doctor_id,
        is_approved=True,
        is_available=True
    )

    # from here the idea comes to hide older date and time or expired slots
    today = timezone.localdate()

    now = timezone.localtime()

    slots = Slot.objects.filter(
        doctor=doctor,
        is_booked=False,
        # show only current date onwards from 17 to 20 but not 16
        date__gte=today
    ).order_by(
        "date",
        "session",
        "slot_number"
    )

    future_slots = []

    for slot in slots:

        slot_datetime = datetime.combine(
            slot.date,
            slot.start_time
        )

        slot_datetime = timezone.make_aware(
            slot_datetime
        )

        if slot_datetime > now:

            future_slots.append(slot)

    return render(
        request,
        "consultancy/doctor_slots.html",
        {
            "doctor": doctor,
            "slots": future_slots
        }
    )
# patient side
def book_slot(request, slot_id):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("patient_login")

    user = User.objects.get(
        id=user_id,
        role="patient"
    )

    patient = Patient.objects.get(
        user=user
    )
        # --------------------------------
    # Check patient profile
    # --------------------------------

    if not patient.profile.is_complete():

        return redirect("patient_profile")
    slot = Slot.objects.get(
        id=slot_id
    )

    # --------------------------------
    # 1. Check appointment date
    # --------------------------------

    today = timezone.localdate()

    if slot.date < today:

        return HttpResponse("""
            <script>
                alert("This appointment date has already passed.");
                history.back();
            </script>
        """)

    # --------------------------------
    # 2. Check appointment time
    # --------------------------------

    now = timezone.localtime()

    slot_datetime = datetime.combine(
        slot.date,
        slot.start_time
    )

    slot_datetime = timezone.make_aware(
        slot_datetime
    )

    if slot_datetime <= now:

        return HttpResponse("""
            <script>
                alert("This appointment time has already passed.");
                history.back();
            </script>
        """)

    # --------------------------------
    # 3. Check whether slot is booked
    # --------------------------------

    if slot.is_booked:

        return HttpResponse("""
            <script>
                alert("This slot is already booked.");
                history.back();
            </script>
        """)

    # --------------------------------
    # 4. One booking per doctor per day
    # --------------------------------

    existing_booking = Booking.objects.filter(
        patient=patient,
        doctor=slot.doctor,
        # checks booking date and slot date
        slot__date=slot.date,
        status="confirmed"
    ).exists()

    if existing_booking:

        return HttpResponse("""
            <script>
                alert(
                    "You already have a booking with this doctor on this date."
                );
                history.back();
            </script>
        """)

    # --------------------------------
    # 5. Create booking
    # --------------------------------

    booking = Booking.objects.create(

        patient=patient,

        doctor=slot.doctor,

        slot=slot,

        booking_id=f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}",

        token_id=slot.slot_number,

        consultation_fee=slot.doctor.consultation_fee

    )

    # --------------------------------
    # 6. Mark slot as booked
    # --------------------------------

    slot.is_booked = True

    slot.save()

    # --------------------------------
    # 7. Show booking confirmation
    # --------------------------------

    return redirect(
        "booking_confirmation",
        booking_id=booking.id
    )   
    
def booking_confirmation(request, booking_id):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("patient_login")

    booking = Booking.objects.get(id=booking_id)

    return render(
        request,
        "consultancy/booking_confirmation.html",
        {
            "booking": booking
        }
    )

def my_bookings(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("patient_login")


    user = User.objects.get(
        id=user_id,
        role="patient"
    )


    patient = Patient.objects.get(
        user=user
    )


    bookings = Booking.objects.filter(
        patient=patient
    ).select_related(
        "doctor",
        "doctor__user",
        "doctor__category",
        "slot"
    ).order_by(
        "-created_at"
    )


    upcoming_bookings = bookings.filter(
        status="confirmed"
    )


    past_bookings = bookings.exclude(
        status="confirmed"
    )


    return render(
        request,
        "consultancy/my_bookings.html",
        {
            "upcoming_bookings": upcoming_bookings,
            "past_bookings": past_bookings
        }
    )    
def cancel_booking(request, booking_id):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("patient_login")

    user = User.objects.get(
        id=user_id,
        role="patient"
    )

    patient = Patient.objects.get(
        user=user
    )

    booking = Booking.objects.get(
        id=booking_id,
        patient=patient
    )

    if booking.status == "cancelled":

        return HttpResponse("""
            <script>
                alert("This booking is already cancelled.");
                history.back();
            </script>
        """)

    booking.status = "cancelled"

    booking.save()

    slot = booking.slot

    slot.is_booked = False

    slot.save()

    return redirect("my_bookings")

def patient_logout(request):
    request.session.flush()
    return redirect("patient_login")

# for the doctor side
def doctor_bookings(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("doctor_login")

    user = User.objects.get(
        id=user_id,
        role="doctor"
    )

    doctor = Doctor.objects.get(
        user=user
    )

    today = timezone.localdate()

    today_bookings = Booking.objects.filter(
        doctor=doctor,
        slot__date=today,
        status="confirmed"
    ).select_related(
        "patient",
        "patient__user",
        "slot"
    ).order_by(
        "slot__start_time"
    )

    upcoming_bookings = Booking.objects.filter(
        doctor=doctor,
        slot__date__gt=today,
        status="confirmed"
    ).select_related(
        "patient",
        "patient__user",
        "slot"
    ).order_by(
        "slot__date",
        "slot__start_time"
    )

    return render(
        request,
        "consultancy/doctor_bookings.html",
        {
            "doctor": doctor,
            "today_bookings": today_bookings,
            "upcoming_bookings": upcoming_bookings
        }
    )
    
def doctor_slots_list(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("doctor_login")

    user = User.objects.get(
        id=user_id,
        role="doctor"
    )

    doctor = Doctor.objects.get(
        user=user
    )

    slots = Slot.objects.filter(
        doctor=doctor
    ).order_by(
        "date",
        "session",
        "slot_number"
    )

    return render(
        request,
        "consultancy/doctor_slots_list.html",
        {
            "doctor": doctor,
            "slots": slots
        }
    )

def doctor_logout(request):

    request.session.flush()

    return redirect("doctor_login")

def doctor_profile(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("doctor_login")

    user = User.objects.get(
        id=user_id,
        role="doctor"
    )

    doctor = Doctor.objects.get(
        user=user
    )

    if request.method == "POST":

        form = DoctorProfileForm(
            request.POST
        )

        if form.is_valid():

            user.name = form.cleaned_data["name"]

            user.save()

            doctor.qualification = form.cleaned_data[
                "qualification"
            ]

            doctor.experience = form.cleaned_data[
                "experience"
            ]

            doctor.consultation_fee = form.cleaned_data[
                "consultation_fee"
            ]

            doctor.about = form.cleaned_data[
                "about"
            ]

            doctor.is_available = form.cleaned_data[
                "is_available"
            ]

            doctor.save()

            return redirect(
                "doctor_dashboard"
            )

    else:

        form = DoctorProfileForm(
            initial={
                "name": user.name,
                "qualification": doctor.qualification,
                "experience": doctor.experience,
                "consultation_fee": doctor.consultation_fee,
                "about": doctor.about,
                "is_available": doctor.is_available,
            }
        )

    return render(
        request,
        "consultancy/doctor_profile.html",
        {
            "form": form
        }
    )

def patient_profile(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("patient_login")

    user = User.objects.get(
        id=user_id,
        role="patient"
    )

    patient = Patient.objects.get(
        user=user
    )

    profile = patient.profile

    if request.method == "POST":

        form = PatientProfileForm(
            request.POST,
            instance=profile
        )

        if form.is_valid():

            form.save()

            return redirect(
                "patient_profile"
            )

    else:

        form = PatientProfileForm(
            instance=profile
        )

    return render(
        request,
        "consultancy/patient_profile.html",
        {
            "patient": patient,
            "profile": profile,
            "form": form,
        }
    )
    
    
    
    
def doctor_patient_profile(request, patient_id, booking_id):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("doctor_login")

    user = User.objects.get(
        id=user_id,
        role="doctor"
    )

    doctor = Doctor.objects.get(
        user=user
    )

    booking = Booking.objects.get(
        id=booking_id,
        doctor=doctor,
        patient_id=patient_id,
        status="confirmed"
    )

    patient = booking.patient

    return render(
        request,
        "consultancy/doctor_patient_profile.html",
        {
            "doctor": doctor,
            "patient": patient,
            "booking": booking
        }
    )
    
    
    
def start_consultation(request, booking_id):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("doctor_login")

    user = User.objects.get(
        id=user_id,
        role="doctor"
    )

    doctor = Doctor.objects.get(
        user=user
    )

    booking = Booking.objects.get(
        id=booking_id,
        doctor=doctor,
        status="confirmed"
    )

    consultation, created = Consultation.objects.get_or_create(
        booking=booking
    )

    if request.method == "POST":

        consultation.symptoms = request.POST.get(
            "symptoms",
            ""
        )

        consultation.doctor_notes = request.POST.get(
            "doctor_notes",
            ""
        )

        consultation.diagnosis = request.POST.get(
            "diagnosis",
            ""
        )

        consultation.status = request.POST.get(
            "status",
            "pending"
        )

        consultation.save()

        return redirect(
            "start_consultation",
            booking_id=booking.id
        )

    return render(
        request,
        "consultancy/consultation.html",
        {
            "doctor": doctor,
            "booking": booking,
            "consultation": consultation
        }
    )
    
    
    
def create_prescription(request, consultation_id):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("doctor_login")

    user = User.objects.get(
        id=user_id,
        role="doctor"
    )

    doctor = Doctor.objects.get(
        user=user
    )

    consultation = Consultation.objects.get(
        id=consultation_id,
        booking__doctor=doctor
    )

    if consultation.status != "completed":

        return HttpResponse("""
            <script>
                alert("Complete the consultation before creating a prescription.");
                history.back();
            </script>
        """)

    prescription, created = Prescription.objects.get_or_create(
        consultation=consultation
    )

    if request.method == "POST":

        prescription.medicines = request.POST.get(
            "medicines",
            ""
        )

        prescription.instructions = request.POST.get(
            "instructions",
            ""
        )

        follow_up_date = request.POST.get(
            "follow_up_date"
        )

        if follow_up_date:

            prescription.follow_up_date = follow_up_date

        else:

            prescription.follow_up_date = None

        prescription.notes = request.POST.get(
            "notes",
            ""
        )

        prescription.save()

        return redirect(
            "create_prescription",
            consultation_id=consultation.id
        )

    return render(
        request,
        "consultancy/prescription.html",
        {
            "doctor": doctor,
            "consultation": consultation,
            "prescription": prescription
        }
    )
    
    
def my_prescriptions(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("patient_login")

    user = User.objects.get(
        id=user_id,
        role="patient"
    )

    patient = Patient.objects.get(
        user=user
    )

    prescriptions = Prescription.objects.filter(
        consultation__booking__patient=patient
    ).select_related(
        "consultation",
        "consultation__booking",
        "consultation__booking__doctor",
        "consultation__booking__doctor__user"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "consultancy/my_prescriptions.html",
        {
            "patient": patient,
            "prescriptions": prescriptions
        }
    )
    
def analyze_consultation(request, consultation_id):

    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("doctor_login")

    user = User.objects.get(
        id=user_id,
        role="doctor"
    )

    doctor = Doctor.objects.get(
        user=user
    )

    consultation = Consultation.objects.get(
        id=consultation_id,
        booking__doctor=doctor
    )

    patient = consultation.booking.patient

    profile = patient.profile

    # --------------------------------
    # Temporary AI analysis
    # --------------------------------

    client = genai.Client(
    api_key=settings.GEMINI_API_KEY
    )


    prompt = f"""
    You are an AI clinical decision-support assistant helping a doctor.

    Analyze the patient information and current consultation.

    IMPORTANT:
    - Do not prescribe medicines.
    - Do not replace the doctor's judgment.
    - Do not make a definitive diagnosis.
    - Keep the analysis concise.
    - Only use information provided below.
    - Do not invent missing patient information.
    - Also use emojis for better understanding

    PATIENT INFORMATION

    Name: {patient.user.name}
    Date of Birth: {profile.date_of_birth}
    Gender: {profile.gender}
    Height: {profile.height} cm
    Weight: {profile.weight} kg
    BMI: {profile.bmi}
    Blood Group: {profile.blood_group}
    Allergies: {profile.allergies}
    Existing Conditions: {profile.existing_conditions}
    Current Medications: {profile.current_medications}

    CONSULTATION

    Symptoms:
    {consultation.symptoms}

    Doctor Notes:
    {consultation.doctor_notes}

    Doctor Diagnosis:
    {consultation.diagnosis}

    Return ONLY valid JSON.

    Use exactly this structure:

    {{
        "patient_summary": "1-2 short sentences",
        "key_concerns": [
            "concern 1",
            "concern 2",
            "concern 3"
        ],
        "relevant_history": [
            "relevant point 1",
            "relevant point 2",
            "relevant point 3"
        ],
        "doctor_review": [
            "review point 1",
            "review point 2",
            "review point 3"
        ],
        "safety_note": "AI-generated clinical decision support. Final clinical decisions must be made by the doctor."
    }}

    Rules:
    - Maximum 3 items in each list.
    - Keep each item short.
    - If information is unavailable, use an empty list.
    - Do not use Markdown.
    - Do not add ```json.
    - Return JSON only.
    """


    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    analysis = json.loads(
    response.text
    )

    consultation.ai_analysis = analysis

    consultation.save()

    return redirect(
        "start_consultation",
        booking_id=consultation.booking.id
    )