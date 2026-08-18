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