import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { catchError, delay } from 'rxjs/operators';
import { AccountData } from '../models/insurance.model';

@Injectable({
  providedIn: 'root'
})
export class AccountService {
  // Mock data for account service
  private accounts: AccountData[] = [
    {
      id: 'ACC123456',
      username: 'john.smith',
      firstName: 'John',
      lastName: 'Smith',
      email: 'john.smith@example.com',
      address: '123 Main St, Anytown, USA',
      applicationId: 'APP123456'
    },
    {
      id: 'ACC234567',
      username: 'jane.doe',
      firstName: 'Jane',
      lastName: 'Doe',
      email: 'jane.doe@example.com',
      address: '456 Oak Ave, Somewhere, USA',
      applicationId: 'APP234567'
    }
  ];

  constructor() { }

  // Get account by ID (simulated API call)
  getAccount(id: string): Observable<AccountData | null> {
    return of(this.findAccount(id))
      .pipe(
        delay(500), // Simulate network delay
        catchError(this.handleError<AccountData | null>('getAccount', null))
      );
  }

  // Find account by ID
  private findAccount(id: string): AccountData | null {
    const account = this.accounts.find(acc => acc.id === id);
    return account || null;
  }

  // Search accounts by criteria
  searchAccounts(criteria: Partial<AccountData>): Observable<AccountData[]> {
    let filteredAccounts = [...this.accounts];
    
    // Filter by firstName
    if (criteria.firstName) {
      filteredAccounts = filteredAccounts.filter(acc => 
        acc.firstName?.toLowerCase().includes(criteria.firstName!.toLowerCase())
      );
    }
    
    // Filter by lastName
    if (criteria.lastName) {
      filteredAccounts = filteredAccounts.filter(acc => 
        acc.lastName?.toLowerCase().includes(criteria.lastName!.toLowerCase())
      );
    }
    
    // Filter by email
    if (criteria.email) {
      filteredAccounts = filteredAccounts.filter(acc => 
        acc.email?.toLowerCase().includes(criteria.email!.toLowerCase())
      );
    }
    
    // Filter by address
    if (criteria.address) {
      filteredAccounts = filteredAccounts.filter(acc => 
        acc.address?.toLowerCase().includes(criteria.address!.toLowerCase())
      );
    }
    
    return of(filteredAccounts)
      .pipe(
        delay(500), // Simulate network delay
        catchError(this.handleError<AccountData[]>('searchAccounts', []))
      );
  }

  // Create new account
  createAccount(account: AccountData): Observable<AccountData> {
    const id = `ACC${Math.floor(Math.random() * 1000000).toString().padStart(6, '0')}`;
    const newAccount: AccountData = {
      id,
      applicationId: account.applicationId || undefined,
      username: account.username || `user_${id.toLowerCase()}`,
      email: account.email,
      password: account.password,
      firstName: account.firstName,
      lastName: account.lastName,
      address: account.address
    };
    
    this.accounts.push(newAccount);
    
    return of(newAccount)
      .pipe(
        delay(1000), // Simulate network delay
        catchError(this.handleError<AccountData>('createAccount'))
      );
  }

  // Error handling
  private handleError<T>(operation = 'operation', result?: T) {
    return (error: any): Observable<T> => {
      console.error(`${operation} failed: ${error.message}`);
      return of(result as T);
    };
  }
} 