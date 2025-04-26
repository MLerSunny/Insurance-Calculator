import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { AccountService } from '../../services/account.service';
import { AccountData } from '../../models/insurance.model';

@Component({
  selector: 'app-account-creation',
  templateUrl: './account-creation.component.html',
  styleUrls: ['./account-creation.component.scss']
})
export class AccountCreationComponent implements OnInit, OnDestroy {
  accountForm!: FormGroup;
  loading = false;
  error: string | null = null;
  success = false;
  private readonly destroy$ = new Subject<void>();

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private route: ActivatedRoute,
    private accountService: AccountService
  ) {
    this.initForm();
  }

  ngOnInit(): void {
    // Pre-fill the form with query params if provided
    this.route.queryParams
      .pipe(takeUntil(this.destroy$))
      .subscribe(params => {
        if (params['firstName'] || params['lastName'] || params['email'] || params['address']) {
          this.accountForm.patchValue({
            firstName: params['firstName'] || '',
            lastName: params['lastName'] || '',
            email: params['email'] || '',
            address: params['address'] || ''
          });
        }
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private initForm(): void {
    this.accountForm = this.fb.group({
      firstName: ['', [Validators.required, Validators.minLength(2)]],
      lastName: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      address: ['', [Validators.required, Validators.minLength(5)]],
      phone: ['', Validators.pattern('^[0-9]{10}$')],
      dateOfBirth: ['']
    });
  }

  onSubmit(): void {
    if (this.accountForm.valid) {
      this.loading = true;
      this.error = null;
      
      const accountData: AccountData = {
        ...this.accountForm.value,
        isNewAccount: true,
        createdAt: new Date()
      };
      
      this.accountService.createAccount(accountData)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: (account) => {
            this.loading = false;
            this.success = true;
            
            // Navigate to calculator after short delay
            setTimeout(() => {
              this.router.navigate(['/calculator'], { 
                queryParams: { 
                  applicationId: account.id,
                  newAccount: 'true'
                } 
              });
            }, 1500);
          },
          error: (err) => {
            this.loading = false;
            this.error = 'Failed to create account. Please try again.';
            console.error('Error creating account:', err);
          }
        });
    } else {
      // Mark all fields as touched to trigger validation messages
      Object.keys(this.accountForm.controls).forEach(key => {
        const control = this.accountForm.get(key);
        control?.markAsTouched();
      });
    }
  }

  goBack(): void {
    this.router.navigate(['/search']);
  }
} 