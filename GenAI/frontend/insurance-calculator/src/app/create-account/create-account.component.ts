import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { InsuranceService } from '../services/insurance.service';

@Component({
  selector: 'app-create-account',
  templateUrl: './create-account.component.html',
  styleUrls: ['./create-account.component.css']
})
export class CreateAccountComponent implements OnInit {
  accountForm: FormGroup;
  loading = false;
  accountNumber: string = '';

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private insuranceService: InsuranceService,
    private snackBar: MatSnackBar
  ) {
    // Initialize the form with validators
    this.accountForm = this.fb.group({
      firstName: ['', [Validators.required, Validators.minLength(2)]],
      lastName: ['', [Validators.required, Validators.minLength(2)]],
      phoneNumber: ['', [Validators.required, Validators.pattern(/^\d{10,15}$/)]],
      email: ['', [Validators.email]],
      addressLine1: ['', [Validators.required, Validators.minLength(5)]],
      addressLine2: [''],
      city: ['', [Validators.required]],
      state: ['', [Validators.required]],
      zipCode: ['', [Validators.required, Validators.pattern(/^\d{5}(-\d{4})?$/)]]
    });

    // Check if we have data from navigation state
    const navigation = this.router.getCurrentNavigation();
    const state = navigation?.extras.state as { accountData: any };
    
    if (state && state.accountData) {
      this.accountForm.patchValue(state.accountData);
    }
  }

  ngOnInit(): void {
    // Generate a random account number
    this.accountNumber = 'ACC' + Date.now().toString().substring(3);
  }

  submitForm(): void {
    if (this.accountForm.invalid) {
      // Mark all fields as touched to trigger validation messages
      Object.keys(this.accountForm.controls).forEach(key => {
        const control = this.accountForm.get(key);
        control?.markAsTouched();
      });
      
      this.snackBar.open('Please fill all required fields correctly', 'Close', { duration: 3000 });
      return;
    }
    
    this.loading = true;
    
    const accountData = {
      ...this.accountForm.value,
      accountNumber: this.accountNumber,
      createdAt: new Date().toISOString()
    };
    
    this.insuranceService.createAccount(accountData).subscribe({
      next: (data) => {
        this.loading = false;
        this.snackBar.open('Account created successfully!', 'Close', { duration: 3000 });
        
        // Navigate to application details page
        setTimeout(() => {
          this.router.navigate(['/application', data.id]);
        }, 1000);
      },
      error: (error) => {
        this.loading = false;
        console.error('Error creating account', error);
        this.snackBar.open('Error creating account: ' + error.message, 'Close', { duration: 5000 });
      }
    });
  }

  cancel(): void {
    this.router.navigate(['/search']);
  }
} 