import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { firstValueFrom, Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

import { InsuranceService } from '../../services/insurance.service';
import { InsuranceRequest, PremiumResult, AccountData, SavedApplicationData } from '../../models/insurance.model';

@Component({
  selector: 'app-insurance-calculator',
  templateUrl: './insurance-calculator.component.html',
  styleUrls: ['./insurance-calculator.component.scss']
})
export class InsuranceCalculatorComponent implements OnInit, OnDestroy {
  insuranceForm: FormGroup;
  loading = false;
  error: string | null = null;
  result: PremiumResult | null = null;
  accountInfo: AccountData | null = null;
  applicationId: string | null = null;
  isNewAccount = false;
  savedApplication: SavedApplicationData | null = null;
  saveSuccess = false;
  private readonly destroy$ = new Subject<void>();

  constructor(
    private fb: FormBuilder,
    private insuranceService: InsuranceService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.insuranceForm = this.createForm();
  }

  ngOnInit(): void {
    this.route.queryParams
      .pipe(takeUntil(this.destroy$))
      .subscribe(params => {
        if (params['applicationId']) {
          this.applicationId = params['applicationId'];
          // Load existing application data
          if (this.applicationId) {
            this.loadApplicationData(this.applicationId);
            this.loadSavedApplicationData(this.applicationId);
          }
        }
        
        if (params['newAccount'] === 'true') {
          this.isNewAccount = true;
          // Create a new account with the search parameters
          this.accountInfo = {
            firstName: params['firstName'] || '',
            lastName: params['lastName'] || '',
            email: params['email'] || '',
            address: params['address'] || '',
            isNewAccount: true,
            createdAt: new Date()
          };
        }
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadApplicationData(applicationId: string): void {
    this.loading = true;
    this.insuranceService.getApplicationById(applicationId)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (data) => {
          // Populate the form with existing data
          if (data) {
            this.accountInfo = {
              firstName: data.firstName || '',
              lastName: data.lastName || '',
              applicationId: data.application_id,
              email: data.email || '',
              address: data.address || ''
            };
          }
          this.loading = false;
        },
        error: (err) => {
          console.error('Error loading application data:', err);
          this.error = 'Failed to load application data. Please try again.';
          this.loading = false;
        }
      });
  }

  private loadSavedApplicationData(applicationId: string): void {
    if (!applicationId) return;
    
    this.insuranceService.getCompleteApplicationById(applicationId)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (data) => {
          if (data) {
            this.savedApplication = data;
            // Populate the form with the saved application data
            if (data.applicationData) {
              this.insuranceForm.patchValue(data.applicationData);
            }
            // Set the calculation result if available
            if (data.calculationResult) {
              this.result = data.calculationResult;
            }
          }
        },
        error: (err) => {
          console.error('Error loading saved application data:', err);
        }
      });
  }

  private createForm(): FormGroup {
    return this.fb.group({
      age: ['', [Validators.required, Validators.min(18), Validators.max(100)]],
      annualIncome: ['', [Validators.required, Validators.min(0)]],
      insuranceScore: ['', [Validators.required, Validators.min(300), Validators.max(850)]],
      lifestyle: this.fb.group({
        exerciseFrequency: ['', Validators.required],
        smokingStatus: ['', Validators.required],
        alcoholConsumption: ['', Validators.required],
        dietQuality: ['', Validators.required]
      }),
      occupation: this.fb.group({
        jobTitle: ['', Validators.required],
        riskLevel: ['', Validators.required],
        workEnvironment: ['', Validators.required]
      }),
      mentalHealth: this.fb.group({
        stressLevel: ['', Validators.required],
        previousConditions: ['', Validators.required],
        currentTreatment: ['', Validators.required]
      }),
      medications: this.fb.group({
        currentMedications: [''],
        chronicConditions: [''],
        allergies: ['']
      }),
      family: this.fb.group({
        numberOfDependents: [0, [Validators.required, Validators.min(0)]],
        familyHistory: [''],
        maritalStatus: ['', Validators.required]
      }),
      travel: this.fb.group({
        frequency: ['', Validators.required],
        destinations: [''],
        purpose: ['', Validators.required]
      })
    });
  }

  async onSubmit(): Promise<void> {
    if (this.insuranceForm.valid) {
      this.loading = true;
      this.error = null;
      this.result = null;

      try {
        const formValue = this.insuranceForm.value;
        const request: InsuranceRequest = {
          age: formValue.age,
          annualIncome: formValue.annualIncome,
          insuranceScore: formValue.insuranceScore,
          lifestyle: formValue.lifestyle,
          occupation: formValue.occupation,
          mentalHealth: formValue.mentalHealth,
          medications: formValue.medications,
          family: formValue.family,
          travel: formValue.travel
        };

        // Add account ID if we have one
        if (this.applicationId) {
          request.accountId = this.applicationId;
        }

        // Use takeUntil with firstValueFrom for better cleanup
        this.result = await firstValueFrom(
          this.insuranceService.calculatePremium(request)
            .pipe(takeUntil(this.destroy$))
        );
        
        // Store account info in result
        if (this.result && this.accountInfo) {
          this.result.accountInfo = this.accountInfo;
          
          // If this is a new account, update the UI with the new application ID
          if (this.isNewAccount && this.result.applicationId) {
            this.accountInfo.applicationId = this.result.applicationId;
            this.applicationId = this.result.applicationId;
            this.isNewAccount = false;
            
            // Update URL without navigating away
            this.router.navigate([], {
              relativeTo: this.route,
              queryParams: { applicationId: this.result.applicationId, newAccount: null },
              queryParamsHandling: 'merge'
            });
          }
        }
      } catch (err) {
        this.error = 'Failed to calculate premium. Please try again later.';
        console.error('Error calculating premium:', err);
      } finally {
        this.loading = false;
      }
    } else {
      // Mark all fields as touched to trigger validation messages
      Object.keys(this.insuranceForm.controls).forEach(key => {
        const control = this.insuranceForm.get(key);
        control?.markAsTouched();
      });
    }
  }

  getFactors(): { name: string; value: number }[] {
    if (!this.result?.factors) return [];
    
    const { factors } = this.result;
    
    return [
      { name: 'Age Factor', value: factors.ageFactor || 0 },
      { name: 'Income Factor', value: factors.incomeFactor || 0 },
      { name: 'Lifestyle Factor', value: factors.lifestyleFactor || 0 },
      { name: 'Occupation Factor', value: factors.occupationFactor || 0 },
      { name: 'Mental Health Factor', value: factors.mentalHealthFactor || 0 },
      { name: 'Medical Factor', value: factors.medicalFactor || 0 },
      { name: 'Family Factor', value: factors.familyFactor || 0 },
      { name: 'Travel Factor', value: factors.travelFactor || 0 }
    ];
  }

  getFactorClass(value: number): string {
    if (value >= 1.5) return 'high-priority';
    if (value >= 1.2) return 'medium-priority';
    return 'low-priority';
  }

  /**
   * Calculates the percentage fill for the factor bar visualization
   * Maps factors from 0.8 (min) to 2.0 (max) to 10% - 100% width
   */
  getFillPercentage(value: number): number {
    // Normalize value between min (0.8) and max (2.0)
    const min = 0.8;
    const max = 2.0;
    // Set min display percentage to 10% so even low values have some visible bar
    const minPercent = 10;
    const maxPercent = 100;
    
    // Calculate percentage with constraints
    const normalizedValue = Math.max(min, Math.min(max, value));
    const percent = minPercent + ((normalizedValue - min) / (max - min)) * (maxPercent - minPercent);
    
    return Math.round(percent);
  }

  getRecommendationIcon(coverageType: string): string {
    const icons: Record<string, string> = {
      'Life': 'person',
      'Health': 'local_hospital',
      'Disability': 'accessible',
      'Critical Illness': 'healing',
      'Long-term Care': 'elderly',
      'Travel': 'flight',
      'Accident': 'warning'
    };
    return icons[coverageType] || 'insurance';
  }

  getImportanceColor(importance: string | undefined): string {
    if (!importance) return 'unknown-priority';
    return `${importance.toLowerCase()}-priority`;
  }

  async saveApplication(): Promise<void> {
    if (!this.insuranceForm.valid) {
      // Mark all fields as touched to trigger validation messages
      Object.keys(this.insuranceForm.controls).forEach(key => {
        const control = this.insuranceForm.get(key);
        control?.markAsTouched();
      });
      return;
    }

    if (!this.accountInfo?.id && !this.applicationId) {
      this.error = 'Cannot save application without an account. Please create an account first.';
      return;
    }

    this.loading = true;
    this.error = null;
    this.saveSuccess = false;

    try {
      const formValue = this.insuranceForm.value;
      const request: InsuranceRequest = {
        age: formValue.age,
        annualIncome: formValue.annualIncome,
        insuranceScore: formValue.insuranceScore,
        lifestyle: formValue.lifestyle,
        occupation: formValue.occupation,
        mentalHealth: formValue.mentalHealth,
        medications: formValue.medications,
        family: formValue.family,
        travel: formValue.travel
      };

      // Create the saved application data
      const savedData: SavedApplicationData = {
        id: this.savedApplication?.id,
        accountId: this.applicationId || '',
        applicationData: request,
        calculationResult: this.result || undefined,
        createdAt: this.savedApplication?.createdAt || new Date(),
        status: 'draft'
      };

      // Save the application
      const saved = await firstValueFrom(
        this.insuranceService.saveApplication(savedData)
          .pipe(takeUntil(this.destroy$))
      );

      this.savedApplication = saved;
      this.saveSuccess = true;
      
      setTimeout(() => {
        this.saveSuccess = false;
      }, 3000);
    } catch (err) {
      this.error = 'Failed to save application. Please try again.';
      console.error('Error saving application:', err);
    } finally {
      this.loading = false;
    }
  }
}
