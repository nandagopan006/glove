from django import forms
from .models import Address
import re
import requests
from django.core.exceptions import ValidationError


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ["user"]

    def clean_full_name(self):
        name = self.cleaned_data.get("full_name")
        if len(name) < 4:
            raise ValidationError("Name too short")
        if not re.match(r"^[A-Za-z ]+$", name):
            raise ValidationError("Only letters allowed")
        return name.strip()

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")
        if not re.match(r"^[6-9]\d{9}$", phone):
            raise ValidationError("Invalid phone number")
        return phone

    def clean_pincode(self):
        pin = self.cleaned_data.get("pincode")
        if not re.match(r"^\d{6}$", pin):
            raise ValidationError("Invalid pincode")
        return pin

    def clean_street_address(self):
        address = self.cleaned_data.get("street_address")
        if len(address) < 10:
            raise ValidationError("Address too short")
        return address

    def clean(self):
        cleaned_data = super().clean()
        pincode = cleaned_data.get("pincode")
        city = cleaned_data.get("city")
        state = cleaned_data.get("state")
        district = cleaned_data.get("district")

        if not pincode:
            return cleaned_data

        try:
            data = requests.get(
                f"https://api.postalpincode.in/pincode/{pincode}", timeout=5
            ).json()
        except requests.RequestException:
            return cleaned_data

        if data[0]["Status"] != "Success":
            self.add_error("pincode", "Invalid pincode")
            return cleaned_data

        post_office = data[0]["PostOffice"]
        valid_cities = {p["Name"].lower() for p in post_office}
        valid_states = {p["State"].lower() for p in post_office}
        valid_districts = {
            (p.get("District") or p.get("Division") or "").lower()
            for p in post_office
        } - {""}

        if city and city.lower() not in valid_cities:
            self.add_error("city", "City does not match pincode")
        if state and state.lower() not in valid_states:
            self.add_error("state", "State does not match pincode")
        if district and district.lower() not in valid_districts:
            self.add_error("district", "District does not match pincode")

        return cleaned_data
