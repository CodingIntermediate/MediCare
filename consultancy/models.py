from django.db import models


class User(models.Model):

    ROLE_CHOICES = (("patient", "Patient"),("doctor", "Doctor"),)

    name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)

    password = models.CharField(max_length=255)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    def __str__(self):
        return self.name


class Patient(models.Model):

    user = models.OneToOneField(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.user.name


class PatientProfile(models.Model):

    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    )

    BLOOD_GROUP_CHOICES = (
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    )

    patient = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True
    )

    height = models.FloatField(
        null=True,
        blank=True
    )

    weight = models.FloatField(
        null=True,
        blank=True
    )

    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUP_CHOICES,
        blank=True
    )

    allergies = models.TextField(
        blank=True
    )

    existing_conditions = models.TextField(
        blank=True
    )

    current_medications = models.TextField(
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    @property
    def bmi(self):

        if self.height and self.weight:

            height_meter = self.height / 100

            return round(
                self.weight / (height_meter ** 2),
                2
            )

        return None
    
    def is_complete(self):

        required_fields = [
            self.date_of_birth,
            self.gender,
            self.height,
            self.weight,
        ]

        return all(required_fields)

    def __str__(self):

        return self.patient.user.name
    
class DoctorCategory(models.Model):

    name = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Doctor(models.Model):

    user = models.OneToOneField(User,on_delete=models.CASCADE)
    category = models.ForeignKey(DoctorCategory,on_delete=models.CASCADE)
    qualification = models.CharField(max_length=200)
    experience = models.PositiveIntegerField()
    consultation_fee = models.DecimalField(max_digits=10,decimal_places=2)
    about = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.user.name
    
    
class Slot(models.Model):

    SESSION_CHOICES = (
        ("morning", "Morning"),
        ("afternoon", "Afternoon"),
        ("evening", "Evening"),
    )

    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE)
    date = models.DateField()
    session = models.CharField( max_length=20,choices=SESSION_CHOICES)
    slot_number = models.PositiveIntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.doctor.user.name} - {self.date} - Token {self.slot_number}"
    
class Booking(models.Model):

    STATUS_CHOICES = (
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    )

    patient = models.ForeignKey(Patient,on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE)
    slot = models.OneToOneField(Slot,on_delete=models.CASCADE)
    booking_id = models.CharField(max_length=30,unique=True)
    token_id = models.PositiveIntegerField()
    consultation_fee = models.DecimalField(max_digits=10,decimal_places=2)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="confirmed")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.booking_id      
    
class Consultation(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    )

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="consultation"
    )

    symptoms = models.TextField(
        blank=True
    )

    doctor_notes = models.TextField(
        blank=True
    )

    diagnosis = models.TextField(
        blank=True
    )

    ai_analysis = models.JSONField(
        blank=True,
        null=True,
        default=dict
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return f"Consultation - {self.booking.booking_id}"
    
    
class Prescription(models.Model):

    consultation = models.OneToOneField(
        Consultation,
        on_delete=models.CASCADE,
        related_name="prescription"
    )

    medicines = models.TextField(
        blank=True
    )

    instructions = models.TextField(
        blank=True
    )

    follow_up_date = models.DateField(
        null=True,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return f"Prescription - {self.consultation.booking.booking_id}"