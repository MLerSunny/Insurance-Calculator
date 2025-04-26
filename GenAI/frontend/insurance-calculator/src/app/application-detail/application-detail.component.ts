import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { InsuranceService } from '../services/insurance.service';
import { QuoteService, Quote } from '../services/quote.service';
import { forkJoin, Subject } from 'rxjs';
import { takeUntil, finalize, catchError } from 'rxjs/operators';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { QuoteOverviewDialogComponent } from './quote-overview-dialog/quote-overview-dialog.component';

/**
 * Interface for insurance application data
 */
export interface InsuranceApplication {
  id: string;
  accountNumber: string;
  firstName: string;
  lastName: string;
  email: string;
  phoneNumber: string;
  addressLine1: string;
  addressLine2?: string;
  city: string;
  state: string;
  zipCode: string;
  status: string;
  createdAt: string;
  quotes?: Quote[];
}

/**
 * Component for displaying and editing insurance application details
 */
@Component({
  selector: 'app-application-detail',
  templateUrl: './application-detail.component.html',
  styleUrls: ['./application-detail.component.css']
})
export class ApplicationDetailComponent implements OnInit, OnDestroy {
  // Core data
  applicationId: string = '';
  application: InsuranceApplication | null = null;
  loading: boolean = true;
  displayedColumns: string[] = ['quoteNumber', 'premium', 'coverageAmount', 'status', 'createdAt'];
  
  // Edit functionality
  editMode: boolean = false;
  editForm: FormGroup;
  saving: boolean = false;
  
  // Component lifecycle
  private destroy$ = new Subject<void>();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private insuranceService: InsuranceService,
    private quoteService: QuoteService,
    private snackBar: MatSnackBar,
    private fb: FormBuilder,
    private dialog: MatDialog
  ) {
    // Initialize form with validators
    this.editForm = this.createFormGroup();
  }

  /**
   * Create form group with validators
   */
  private createFormGroup(): FormGroup {
    return this.fb.group({
      email: ['', [Validators.email]],
      phoneNumber: ['', [Validators.required, Validators.pattern(/^\d{10}$/)]],
      addressLine1: ['', Validators.required],
      addressLine2: [''],
      city: ['', Validators.required],
      state: ['', Validators.required],
      zipCode: ['', [Validators.required, Validators.pattern(/^\d{5}(?:-\d{4})?$/)]]
    });
  }

  ngOnInit(): void {
    this.route.params
      .pipe(takeUntil(this.destroy$))
      .subscribe(params => {
        this.applicationId = params['id'];
        this.loadApplication();
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Load application data and quotes
   */
  loadApplication(): void {
    this.loading = true;
    
    // Load application and quotes in parallel
    forkJoin({
      application: this.insuranceService.getApplicationById(this.applicationId),
      quotes: this.quoteService.getQuotesByApplicationId(Number(this.applicationId))
    })
    .pipe(
      finalize(() => this.loading = false),
      catchError(error => {
        this.handleError('Failed to load application details', error);
        throw error;
      }),
      takeUntil(this.destroy$)
    )
    .subscribe({
      next: (data) => {
        this.application = data.application;
        if (this.application) {
          this.application.quotes = data.quotes;
          this.loadFormValues();
        }
      }
    });
  }

  /**
   * Load current values into the form
   */
  loadFormValues(): void {
    if (!this.application) return;
    
    this.editForm.patchValue({
      email: this.application.email,
      phoneNumber: this.application.phoneNumber,
      addressLine1: this.application.addressLine1,
      addressLine2: this.application.addressLine2 || '',
      city: this.application.city,
      state: this.application.state,
      zipCode: this.application.zipCode
    });
  }

  /**
   * Toggle edit mode
   */
  toggleEditMode(): void {
    this.editMode = !this.editMode;
    if (this.editMode) {
      this.loadFormValues();
    }
  }

  /**
   * Cancel edit mode
   */
  cancelEdit(): void {
    this.editMode = false;
    this.loadFormValues();
  }

  /**
   * Save changes to application details
   */
  saveChanges(): void {
    if (this.editForm.invalid) {
      this.markFormGroupTouched(this.editForm);
      return;
    }

    this.saving = true;
    const updatedData = {
      ...this.application,
      ...this.editForm.value
    };

    this.insuranceService.updateApplication(updatedData)
      .pipe(
        finalize(() => this.saving = false),
        catchError(error => {
          this.handleError('Failed to update contact details', error);
          throw error;
        }),
        takeUntil(this.destroy$)
      )
      .subscribe({
        next: (response) => {
          this.application = response;
          this.editMode = false;
          this.snackBar.open('Contact details updated successfully', 'Close', {
            duration: 3000
          });
        }
      });
  }

  /**
   * Navigate back to search page
   */
  goBack(): void {
    this.router.navigate(['/search']);
  }

  /**
   * Create a new quote for this application
   */
  createNewQuote(): void {
    if (!this.application) return;
    
    this.router.navigate(['/quote'], { 
      queryParams: { applicationId: this.applicationId }
    });
  }

  /**
   * Open quote overview dialog
   */
  openQuoteOverview(quote: Quote): void {
    if (!quote || !this.application) {
      this.snackBar.open('Quote data is not available', 'Close', { duration: 3000 });
      return;
    }
    
    this.dialog.open(QuoteOverviewDialogComponent, {
      width: '700px',
      data: {
        quote: quote,
        application: this.application
      }
    });
  }

  /**
   * Mark all form controls as touched to trigger validation
   */
  private markFormGroupTouched(formGroup: FormGroup): void {
    Object.keys(formGroup.controls).forEach(key => {
      const control = formGroup.get(key);
      control?.markAsTouched();
    });
  }

  /**
   * Handle error with console log and snackbar
   */
  private handleError(message: string, error: any): void {
    console.error(message, error);
    this.snackBar.open(message, 'Close', {
      duration: 5000
    });
  }
} 