from django import forms
from .models import SymptomAssessment
from medical.models import Symptom


class SymptomCheckerForm(forms.ModelForm):
    selected_symptoms = forms.ModelMultipleChoiceField(
        queryset=Symptom.objects.all().order_by('display_name'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'symptom-checkbox'}),
        required=True,
        help_text="Select all symptoms you are currently experiencing"
    )
    raw_symptom_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control glass-input',
            'rows': 3,
            'placeholder': 'Optionally describe how you are feeling in your own words (e.g. "I have had a high fever and shortness of breath since yesterday, but no cough")...'
        }),
        help_text="Optional natural-language description. Our clinical NLP engine will parse and highlight recognized symptoms."
    )
    duration_days = forms.IntegerField(
        min_value=1,
        max_value=365,
        initial=2,
        widget=forms.NumberInput(attrs={'class': 'form-control glass-input', 'min': 1, 'max': 365}),
        help_text="Approximately how many days have you had these symptoms?"
    )
    severity = forms.ChoiceField(
        choices=SymptomAssessment.SEVERITY_LEVELS,
        initial='MODERATE',
        widget=forms.Select(attrs={'class': 'form-select glass-input'})
    )

    class Meta:
        model = SymptomAssessment
        fields = ['selected_symptoms', 'raw_symptom_text', 'duration_days', 'severity']

    def clean(self):
        cleaned_data = super().clean()
        symptoms = cleaned_data.get('selected_symptoms')
        if not symptoms or len(symptoms) == 0:
            raise forms.ValidationError("Please select at least one symptom to proceed with clinical evaluation.")
        return cleaned_data
