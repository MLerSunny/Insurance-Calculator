import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError, of } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';
import { SavedApplicationData } from '../models/insurance.model';

@Injectable({
  providedIn: 'root'
})
export class InsuranceService {
  private apiUrl = 'http://localhost:8000/api';
  private readonly ACCOUNTS_STORAGE_KEY = 'insurance_accounts';

  constructor(private http: HttpClient) { }

  // Get all stored accounts
  private getStoredAccounts(): any[] {
    const accounts = localStorage.getItem(this.ACCOUNTS_STORAGE_KEY);
    return accounts ? JSON.parse(accounts) : [];
  }

  // Save accounts to localStorage
  private saveAccountsToStorage(accounts: any[]): void {
    localStorage.setItem(this.ACCOUNTS_STORAGE_KEY, JSON.stringify(accounts));
  }

  // Search for accounts by criteria
  searchAccounts(searchData: any): Observable<any[]> {
    // Get accounts from localStorage
    const accounts = this.getStoredAccounts();
    
    // Filter accounts based on search criteria
    const results = accounts.filter(account => {
      // Match on name (case insensitive)
      const firstNameMatch = account.firstName.toLowerCase().includes(searchData.firstName.toLowerCase());
      const lastNameMatch = account.lastName.toLowerCase().includes(searchData.lastName.toLowerCase());
      
      // Match on phone
      const phoneMatch = account.phoneNumber.includes(searchData.phoneNumber);
      
      // Optional email match
      let emailMatch = true;
      if (searchData.email && searchData.email.trim() !== '') {
        emailMatch = account.email && account.email.toLowerCase().includes(searchData.email.toLowerCase());
      }
      
      // Match on address if provided
      let addressMatch = true;
      if (searchData.addressLine1 && searchData.addressLine1.trim() !== '') {
        addressMatch = account.addressLine1.toLowerCase().includes(searchData.addressLine1.toLowerCase());
      }
      
      // Match on city, state, zip
      const cityMatch = account.city.toLowerCase().includes(searchData.city.toLowerCase());
      const stateMatch = account.state.toLowerCase().includes(searchData.state.toLowerCase());
      const zipMatch = account.zipCode.includes(searchData.zipCode);
      
      return firstNameMatch && lastNameMatch && phoneMatch && emailMatch && 
             addressMatch && cityMatch && stateMatch && zipMatch;
    });
    
    return of(results);
  }

  // Create a new account
  createAccount(accountData: any): Observable<any> {
    const accounts = this.getStoredAccounts();
    
    // Generate a unique account number (alphanumeric format)
    const accountNumber = this.generateUniqueAccountNumber();
    
    // Create a new account with unique ID and timestamp
    const timestamp = Date.now();
    const newAccount = {
      id: timestamp, // Use timestamp as unique ID
      ...accountData,
      accountNumber: accountNumber,
      createdAt: new Date(timestamp).toISOString()
    };
    
    console.log('Creating new account:', newAccount);
    
    // Add to the accounts array
    accounts.push(newAccount);
    
    // Save back to localStorage
    this.saveAccountsToStorage(accounts);
    
    // Return the created account
    return of(newAccount);
  }

  // Update an existing application's details
  updateApplication(applicationData: any): Observable<any> {
    // Get all accounts from localStorage
    const accounts = this.getStoredAccounts();
    
    // Find the account with the matching ID
    const accountIndex = accounts.findIndex(a => a.id === Number(applicationData.id));
    
    if (accountIndex >= 0) {
      // Update the account data
      const updatedAccount = {
        ...accounts[accountIndex],
        email: applicationData.email,
        phoneNumber: applicationData.phoneNumber,
        addressLine1: applicationData.addressLine1,
        addressLine2: applicationData.addressLine2,
        city: applicationData.city,
        state: applicationData.state,
        zipCode: applicationData.zipCode
      };
      
      // Replace the account in the array
      accounts[accountIndex] = updatedAccount;
      
      // Save back to localStorage
      this.saveAccountsToStorage(accounts);
      
      // Return the updated account
      return of(updatedAccount);
    }
    
    // If not found, return an error
    return throwError(() => new Error('Account not found'));
  }
  
  // Generate a unique alpha-numeric account number
  private generateUniqueAccountNumber(): string {
    // Format: ACC-XXXXX-XX where X is alphanumeric
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let result = 'ACC-';
    
    // Generate 5 characters
    for (let i = 0; i < 5; i++) {
      result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    
    result += '-';
    
    // Generate 2 more characters
    for (let i = 0; i < 2; i++) {
      result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    
    return result;
  }

  // Get all insurance applications
  getApplications(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/insurance/applications/`)
      .pipe(
        retry(1),
        catchError(this.handleError)
      );
  }

  // Get a specific application by ID
  getApplication(id: number | string): Observable<any> {
    // Get all accounts from localStorage
    const accounts = this.getStoredAccounts();
    console.log('Getting application with ID:', id);
    console.log('Available accounts:', accounts);
    
    // Find the account with the matching ID
    const account = accounts.find(a => a.id === Number(id));
    
    if (account) {
      console.log('Found account:', account);
      return of(account);
    }
    
    // If not found in localStorage, try the API
    // But for now, return an error observable since we don't have a backend
    console.error('Account not found with ID:', id);
    return throwError(() => new Error('Account not found'));
  }

  // Alias for getApplication for component compatibility
  getApplicationById(id: number | string): Observable<any> {
    return this.getApplication(id);
  }

  // Get complete application details by ID
  getCompleteApplicationById(id: number | string): Observable<any> {
    // First check localStorage
    const accounts = this.getStoredAccounts();
    const account = accounts.find(a => a.id === Number(id));
    
    if (account) {
      return of(account);
    }
    
    // If not in localStorage, try the API
    return this.http.get<any>(`${this.apiUrl}/insurance/applications/${id}/complete`)
      .pipe(
        retry(1),
        catchError(this.handleError)
      );
  }

  // Create a new application
  createApplication(application: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/insurance/applications/`, application)
      .pipe(
        catchError(this.handleError)
      );
  }

  // Save application data
  saveApplication(applicationData: SavedApplicationData): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/insurance/applications/save`, applicationData)
      .pipe(
        catchError(this.handleError)
      );
  }

  // Calculate premium without creating an application
  calculatePremium(calculationData: any): Observable<any> {
    // Simulate a premium calculation
    const age = parseInt(calculationData.age);
    const isSmoker = calculationData.smoker;
    const coverage = parseInt(calculationData.coverage);
    const medicalConditions = calculationData.medicalConditions || '';
    
    // Base rate calculation
    let premium = coverage / 1000 * 0.5; // $0.50 per $1,000 of coverage
    
    // Age factor
    if (age < 30) {
      premium *= 0.7;
    } else if (age < 45) {
      premium *= 1.0;
    } else if (age < 60) {
      premium *= 1.5;
    } else {
      premium *= 2.2;
    }
    
    // Smoker surcharge
    if (isSmoker) {
      premium *= 1.5;
    }
    
    // Medical conditions risk factor
    if (medicalConditions) {
      const conditions = medicalConditions.split(',').map((c: string) => c.trim().toLowerCase());
      
      const highRiskConditions = ['cancer', 'heart disease', 'stroke'];
      const mediumRiskConditions = ['diabetes', 'hypertension', 'asthma'];
      
      // Check for high risk conditions
      for (const condition of conditions) {
        if (highRiskConditions.some(c => condition.includes(c))) {
          premium *= 1.7;
          break;
        }
      }
      
      // Check for medium risk conditions
      for (const condition of conditions) {
        if (mediumRiskConditions.some(c => condition.includes(c))) {
          premium *= 1.3;
          break;
        }
      }
    }
    
    // Round to 2 decimal places
    premium = Math.round(premium * 100) / 100;
    
    // Generate risk assessment
    let riskAssessment = '';
    if (premium / (coverage / 1000) < 0.8) {
      riskAssessment = '<strong>Low Risk:</strong> You have qualified for our preferred rate based on your profile.';
    } else if (premium / (coverage / 1000) < 1.5) {
      riskAssessment = '<strong>Standard Risk:</strong> Your profile presents a standard risk level.';
    } else {
      riskAssessment = '<strong>Elevated Risk:</strong> Based on the factors provided, your risk profile is higher than average.';
    }
    
    // Add recommendation if smoker
    let recommendation = '';
    if (isSmoker) {
      recommendation = 'Quitting smoking could significantly reduce your premium by up to 33%.';
    }
    
    // Simulate API response delay
    return of({
      premium: premium,
      riskAssessment: riskAssessment,
      recommendation: recommendation,
      coverageAmount: coverage
    });
  }

  // Process complex application with CrewAI
  processComplexApplication(application: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/complex/complex-application/`, application)
      .pipe(
        catchError(this.handleError)
      );
  }

  // Apply underwriting rules to application data
  applyUnderwritingRules(applicationData: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/complex/apply-underwriting-rules/`, applicationData)
      .pipe(
        catchError(this.handleError)
      );
  }

  // Error handling
  private handleError(error: any) {
    let errorMessage = '';
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Server-side error
      errorMessage = `Error Code: ${error.status}\nMessage: ${error.message}`;
    }
    console.error(errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}
