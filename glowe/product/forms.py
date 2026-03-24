from django import forms
from .models import Product, Variant
import re

class ProductForm(forms.ModelForm):
    
    class Meta:
        fields =[
            'name','category',
            "description","ingredients",
            'how_to_use','skin_type'
        ]
    def clean_name(self):
        
        name=self.cleaned_data.get('name','').strip()
        
        if len(name)< 3 :
            raise forms.ValidationError("Product name too short")  
        return name 
    def clean_description(self):
        description=self.cleaned_data.get('description')
        if len(description) < 12 :
            raise forms.ValidationError('description need more than 12chars')
        return description
    def clean_ingredients(self):
        ingredients = self.cleaned_data.get('ingredients', '').strip()

        if ingredients:
            if len(ingredients) < 5:
                raise forms.ValidationError("Ingredients too short")

        return ingredients

    def clean_how_to_use(self):
        how =self.cleaned_data.get('how_to_use')

        if how:
            if len(how) < 5:
                raise forms.ValidationError("How to use is too short")

        return how
    def clean_skin_type(self):
        skin_type=self.cleaned_data.get('skin_type')
        
        if skin_type:
            pattern=r'^[A-Za-z\s&-]+$'
            
            if not re.match(pattern,skin_type):
                raise forms.ValidationError("Only letters and spaces allowed (no numbers or special characters)")
        return skin_type
    
    
        
        
        