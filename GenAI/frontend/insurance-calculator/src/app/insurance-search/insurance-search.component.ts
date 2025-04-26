import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { InsuranceService } from '../services/insurance.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-insurance-search',
  templateUrl: './insurance-search.component.html',
  styleUrls: ['./insurance-search.component.css']
})
export class InsuranceSearchComponent implements OnInit {
  searchForm: FormGroup;
  applications: any[] = [];
  loading = false;
  showCreateButton = false;
  searchPerformed = false;
  
  displayedColumns: string[] = [
    'id', 
    'applicant_name', 
    'email',
    'phone',
    'city',
    'state',
    'actions'
  ];

  constructor(
    private fb: FormBuilder,
    private insuranceService: InsuranceService,
    private snackBar: MatSnackBar,
    private router: Router
  ) {
    this.searchForm = this.fb.group({
      firstName: ['', Validators.required],
      lastName: ['', Validators.required],
      phoneNumber: ['', Validators.required],
      email: [''],
      addressLine1: ['', Validators.required],
      addressLine2: [''],
      city: ['', Validators.required],
      state: ['', Validators.required],
      zipCode: ['', Validators.required],
    });
  }

  ngOnInit(): void {
    // We won't load all applications by default
  }

  searchApplications(): void {
    // Check if at least one required field is filled
    if (!this.atLeastOneFieldFilled()) {
      this.snackBar.open('Please fill at least one search field', 'Close', { duration: 3000 });
      return;
    }
    
    this.loading = true;
    this.showCreateButton = false;
    this.searchPerformed = true;
    
    const searchData = this.searchForm.value;
    
    // Use the updated searchAccounts method that searches localStorage
    this.insuranceService.searchAccounts(searchData).subscribe({
      next: (data) => {
        this.applications = data;
        this.loading = false;
        
        // Show create button if no results found
        if (this.applications.length === 0) {
          this.showCreateButton = true;
        }
      },
      error: (error) => {
        console.error('Error searching applications', error);
        this.snackBar.open('Error searching applications', 'Close', { duration: 3000 });
        this.loading = false;
        
        // Even on error, we'll show the create button
        this.showCreateButton = true;
      }
    });
  }

  // Check if at least one search field has been filled
  atLeastOneFieldFilled(): boolean {
    const formValues = this.searchForm.value;
    return Object.keys(formValues).some(key => {
      const value = formValues[key];
      return value !== null && value !== undefined && value.toString().trim() !== '';
    });
  }

  createAccount(): void {
    // Navigate to account creation page with form data pre-populated
    const formData = this.searchForm.value;
    this.router.navigate(['/create-account'], { 
      state: { accountData: formData }
    });
  }

  resetForm(): void {
    this.searchForm.reset();
    this.applications = [];
    this.showCreateButton = false;
    this.searchPerformed = false;
  }

  viewDetails(applicationId: number): void {
    // Log the ID for debugging
    console.log('Viewing details for application with ID:', applicationId);
    
    // Ensure we have a valid ID
    if (!applicationId) {
      this.snackBar.open('Invalid application ID', 'Close', { duration: 3000 });
      return;
    }
    
    // Navigate to application details page
    this.router.navigate(['/application', applicationId]);
  }
} 