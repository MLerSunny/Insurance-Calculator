import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { InsuranceService } from '../services/insurance.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-insurance-calculator',
  templateUrl: './insurance-calculator.component.html',
  styleUrls: ['./insurance-calculator.component.css']
})
export class InsuranceCalculatorComponent implements OnInit {
  calculatorForm: FormGroup;
  loading = false;
  premiumResult: any = null;
  
  constructor(
    private fb: FormBuilder,
    private insuranceService: InsuranceService,
    private snackBar: MatSnackBar,
    private router: Router
  ) {
    this.calculatorForm = this.fb.group({
      age: ['', [Validators.required, Validators.min(18), Validators.max(99)]],
      smoker: [false],
      coverage: ['250000', Validators.required],
      medicalConditions: ['']
    });
  }

  ngOnInit(): void {
    // Initialize component
  }

  calculatePremium(): void {
    if (this.calculatorForm.invalid) {
      // Mark all fields as touched to trigger validation messages
      Object.keys(this.calculatorForm.controls).forEach(key => {
        const control = this.calculatorForm.get(key);
        control?.markAsTouched();
      });
      
      this.snackBar.open('Please fill all required fields', 'Close', { duration: 3000 });
      return;
    }
    
    this.loading = true;
    this.premiumResult = null;
    
    const calculationData = this.calculatorForm.value;
    
    this.insuranceService.calculatePremium(calculationData).subscribe({
      next: (result) => {
        this.premiumResult = result;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error calculating premium', error);
        this.snackBar.open('Error calculating premium', 'Close', { duration: 3000 });
        this.loading = false;
      }
    });
  }

  saveApplication(): void {
    if (!this.premiumResult) {
      this.snackBar.open('Please calculate premium first', 'Close', { duration: 3000 });
      return;
    }
    
    // Navigate to application form with premium data
    this.router.navigate(['/create-account'], { 
      state: { 
        premiumData: {
          ...this.calculatorForm.value,
          premium: this.premiumResult.premium,
          riskAssessment: this.premiumResult.riskAssessment
        }
      }
    });
  }

  resetForm(): void {
    this.calculatorForm.reset({
      age: '',
      smoker: false,
      coverage: '250000',
      medicalConditions: ''
    });
    this.premiumResult = null;
  }
} 