import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { InsuranceService } from '../services/insurance.service';
import { QuoteService } from '../services/quote.service';

@Component({
  selector: 'app-quote',
  templateUrl: './quote.component.html',
  styleUrls: ['./quote.component.css']
})
export class QuoteComponent implements OnInit {
  quoteForm: FormGroup;
  loading = false;
  submitting = false;
  applicantData: any = null;
  
  // Form options for dropdowns
  healthOptions = ['Excellent', 'Good', 'Fair', 'Poor'];
  yesNoOptions = ['Yes', 'No'];
  frequencyOptions = ['Never', 'Rarely', 'Occasionally', 'Regularly', 'Frequently'];
  travelRegions = ['North America', 'South America', 'Europe', 'Africa', 'Asia', 'Australia', 'Antarctica'];
  occupationRiskLevels = ['Low Risk', 'Medium Risk', 'High Risk'];
  stressLevels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  dependentOptions = ['0', '1', '2', '3', '4', '5+'];
  medicalConditions = [
    'None', 
    'Heart Disease', 
    'Diabetes', 
    'Cancer', 
    'Asthma', 
    'Hypertension', 
    'Stroke', 
    'COPD', 
    'Arthritis', 
    'Depression', 
    'Anxiety', 
    'Other'
  ];

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private route: ActivatedRoute,
    private insuranceService: InsuranceService,
    private snackBar: MatSnackBar,
    private quoteService: QuoteService
  ) {
    // Initialize the form
    this.quoteForm = this.fb.group({
      // Applicant info (pre-filled)
      firstName: ['', Validators.required],
      lastName: ['', Validators.required],
      applicationNumber: ['', Validators.required],
      
      // Health section
      generalHealth: ['', Validators.required],
      height: ['', [Validators.required, Validators.pattern(/^\d{2,3}(\.\d{1,2})?$/)]],
      weight: ['', [Validators.required, Validators.pattern(/^\d{2,3}(\.\d{1,2})?$/)]],
      
      // Pre-existing conditions
      preExistingConditions: ['', Validators.required],
      diagnosisDate: [''],
      currentTreatment: [''],
      
      // Medical History
      hospitalizedLast5Years: ['', Validators.required],
      hospitalizationDetails: [''],
      surgeryLast10Years: ['', Validators.required],
      surgeryDetails: [''],
      
      // Family Medical History
      familyHeartDisease: ['', Validators.required],
      familyCancer: ['', Validators.required],
      familyDiabetes: ['', Validators.required],
      otherFamilyConditions: [''],
      
      // Travel History
      travelOutsideCountry: ['', Validators.required],
      travelRegions: [[]],
      travelPurpose: [''],
      
      // Lifestyle
      smokingStatus: ['', Validators.required],
      smokingFrequency: [''],
      smokingYears: [''],
      alcoholConsumption: ['', Validators.required],
      alcoholFrequency: [''],
      drugUse: ['', Validators.required],
      exerciseFrequency: ['', Validators.required],
      
      // Occupation
      occupation: ['', Validators.required],
      occupationRiskLevel: ['', Validators.required],
      workHoursPerWeek: ['', Validators.required],
      
      // Mental Health
      stressLevel: ['', Validators.required],
      mentalHealthDiagnosis: ['', Validators.required],
      mentalHealthDetails: [''],
      
      // Medications
      currentMedications: ['', Validators.required],
      medicationDetails: [''],
      
      // Dependents
      numberOfDependents: ['', Validators.required],
      
      // Additional Information
      additionalInformation: ['']
    });
  }

  ngOnInit(): void {
    // Get application ID from the URL
    this.route.queryParams.subscribe(params => {
      const applicationId = params['applicationId'];
      if (applicationId) {
        this.loadApplicantData(applicationId);
      } else {
        this.snackBar.open('No application ID provided', 'Close', { duration: 3000 });
        this.router.navigate(['/search']);
      }
    });
  }

  loadApplicantData(applicationId: number): void {
    this.loading = true;
    
    this.insuranceService.getApplication(applicationId).subscribe({
      next: (data) => {
        this.applicantData = data;
        this.populateApplicantInfo();
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading applicant data', error);
        this.snackBar.open('Error loading applicant data: ' + error.message, 'Close', { duration: 3000 });
        this.loading = false;
        this.router.navigate(['/search']);
      }
    });
  }

  populateApplicantInfo(): void {
    if (this.applicantData) {
      // Generate a unique application number for this quote
      const uniqueAppNumber = this.generateApplicationNumber();
      
      this.quoteForm.patchValue({
        firstName: this.applicantData.firstName,
        lastName: this.applicantData.lastName,
        applicationNumber: uniqueAppNumber
      });
    }
  }
  
  // Generate a unique application number different from account number
  private generateApplicationNumber(): string {
    // Format: QAP-XXXXX-XXX where X is alphanumeric
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let result = 'QAP-';
    
    // Generate 5 characters
    for (let i = 0; i < 5; i++) {
      result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    
    result += '-';
    
    // Generate 3 more characters
    for (let i = 0; i < 3; i++) {
      result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    
    return result;
  }

  submitForm(): void {
    if (this.quoteForm.invalid) {
      // Mark all fields as touched to show validation errors
      Object.keys(this.quoteForm.controls).forEach(key => {
        const control = this.quoteForm.get(key);
        control?.markAsTouched();
      });
      
      this.snackBar.open('Please fill all required fields correctly', 'Close', { duration: 3000 });
      return;
    }
    
    this.submitting = true;
    
    // Calculate premium based on form data
    const premium = this.calculatePremium();
    const coverageAmount = this.determineCoverageAmount();
    
    // Prepare quote data for saving
    const quoteData = {
      applicationId: this.applicantData.id,
      premium: premium,
      coverageAmount: coverageAmount,
      quoteDetails: this.quoteForm.value // Store all form data for reference
    };
    
    // Save the quote using the QuoteService
    this.quoteService.createQuote(quoteData).subscribe({
      next: (quote) => {
        this.submitting = false;
        this.snackBar.open(`Quote #${quote.quoteNumber} submitted successfully!`, 'Close', { duration: 3000 });
        
        // Navigate back to application details
        if (this.applicantData) {
          this.router.navigate(['/application', this.applicantData.id]);
        } else {
          this.router.navigate(['/search']);
        }
      },
      error: (error) => {
        this.submitting = false;
        this.snackBar.open('Failed to submit quote: ' + error.message, 'Close', { duration: 3000 });
        console.error('Error creating quote:', error);
      }
    });
  }
  
  // Calculate premium based on health and other factors
  private calculatePremium(): number {
    const baseAmount = 500;
    let premium = baseAmount;
    
    // Add factors based on health
    const health = this.quoteForm.get('generalHealth')?.value;
    if (health === 'Poor') premium += 300;
    else if (health === 'Fair') premium += 150;
    else if (health === 'Good') premium += 50;
    
    // Add for pre-existing conditions
    const conditions = this.quoteForm.get('preExistingConditions')?.value;
    if (conditions && conditions !== 'None') premium += 200;
    
    // Add for smoking
    if (this.quoteForm.get('smokingStatus')?.value === 'Yes') premium += 250;
    
    // Add for family history
    if (this.quoteForm.get('familyHeartDisease')?.value === 'Yes') premium += 100;
    if (this.quoteForm.get('familyCancer')?.value === 'Yes') premium += 100;
    if (this.quoteForm.get('familyDiabetes')?.value === 'Yes') premium += 100;
    
    return premium;
  }
  
  // Determine appropriate coverage amount
  private determineCoverageAmount(): number {
    // Base coverage amount
    return 100000;
  }

  cancel(): void {
    if (this.applicantData) {
      this.router.navigate(['/application', this.applicantData.id]);
    } else {
      this.router.navigate(['/search']);
    }
  }
  
  updateConditionalFields(): void {
    // Smoking details
    const smokingStatus = this.quoteForm.get('smokingStatus')?.value;
    if (smokingStatus === 'No') {
      this.quoteForm.get('smokingFrequency')?.setValue('');
      this.quoteForm.get('smokingYears')?.setValue('');
    }
    
    // Alcohol details
    const alcoholConsumption = this.quoteForm.get('alcoholConsumption')?.value;
    if (alcoholConsumption === 'No') {
      this.quoteForm.get('alcoholFrequency')?.setValue('');
    }
    
    // Travel details
    const travelOutsideCountry = this.quoteForm.get('travelOutsideCountry')?.value;
    if (travelOutsideCountry === 'No') {
      this.quoteForm.get('travelRegions')?.setValue([]);
      this.quoteForm.get('travelPurpose')?.setValue('');
    }
    
    // Pre-existing conditions details
    const preExistingConditions = this.quoteForm.get('preExistingConditions')?.value;
    if (preExistingConditions === 'None') {
      this.quoteForm.get('diagnosisDate')?.setValue('');
      this.quoteForm.get('currentTreatment')?.setValue('');
    }
    
    // Hospitalization details
    const hospitalizedLast5Years = this.quoteForm.get('hospitalizedLast5Years')?.value;
    if (hospitalizedLast5Years === 'No') {
      this.quoteForm.get('hospitalizationDetails')?.setValue('');
    }
    
    // Surgery details
    const surgeryLast10Years = this.quoteForm.get('surgeryLast10Years')?.value;
    if (surgeryLast10Years === 'No') {
      this.quoteForm.get('surgeryDetails')?.setValue('');
    }
    
    // Mental health details
    const mentalHealthDiagnosis = this.quoteForm.get('mentalHealthDiagnosis')?.value;
    if (mentalHealthDiagnosis === 'No') {
      this.quoteForm.get('mentalHealthDetails')?.setValue('');
    }
    
    // Medication details
    const currentMedications = this.quoteForm.get('currentMedications')?.value;
    if (currentMedications === 'No') {
      this.quoteForm.get('medicationDetails')?.setValue('');
    }
  }
} 