import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';

export interface Quote {
  id: number;
  quoteNumber: string;
  applicationId: number;
  premium: number;
  coverageAmount: number;
  status: 'Pending' | 'Approved' | 'Rejected';
  createdAt: string;
  quoteDetails?: any; // Store all form data
}

@Injectable({
  providedIn: 'root'
})
export class QuoteService {
  private apiUrl = 'http://localhost:8000/api';
  private readonly QUOTES_STORAGE_KEY = 'insurance_quotes';

  constructor(private http: HttpClient) { }

  // Get all stored quotes
  private getStoredQuotes(): Quote[] {
    const quotes = localStorage.getItem(this.QUOTES_STORAGE_KEY);
    return quotes ? JSON.parse(quotes) : [];
  }

  // Save quotes to localStorage
  private saveQuotesToStorage(quotes: Quote[]): void {
    localStorage.setItem(this.QUOTES_STORAGE_KEY, JSON.stringify(quotes));
  }

  // Get quotes for a specific application
  getQuotesByApplicationId(applicationId: number): Observable<Quote[]> {
    // Get quotes from localStorage
    const quotes = this.getStoredQuotes();
    
    // Filter quotes by application ID
    const applicationQuotes = quotes.filter(quote => 
      quote.applicationId === Number(applicationId)
    );
    
    return of(applicationQuotes);
  }

  // Create a new quote
  createQuote(quoteData: any): Observable<Quote> {
    const quotes = this.getStoredQuotes();
    
    // Generate a unique quote number (format: QT-XXXXXX-YY)
    const quoteNumber = this.generateUniqueQuoteNumber();
    
    // Create a new quote with unique ID and timestamp
    const timestamp = Date.now();
    const newQuote: Quote = {
      id: timestamp, // Use timestamp as unique ID
      quoteNumber,
      applicationId: Number(quoteData.applicationId),
      premium: quoteData.premium,
      coverageAmount: quoteData.coverageAmount,
      status: 'Pending',
      createdAt: new Date(timestamp).toISOString(),
      quoteDetails: quoteData.quoteDetails // Store all form data
    };
    
    console.log('Creating new quote:', newQuote);
    
    // Add to the quotes array
    quotes.push(newQuote);
    
    // Save back to localStorage
    this.saveQuotesToStorage(quotes);
    
    // Return the created quote
    return of(newQuote);
  }

  // Generate a unique alpha-numeric quote number
  private generateUniqueQuoteNumber(): string {
    // Format: QT-XXXXXX-YY where X and Y are alphanumeric
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let result = 'QT-';
    
    // Generate 6 characters
    for (let i = 0; i < 6; i++) {
      result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    
    result += '-';
    
    // Generate 2 more characters
    for (let i = 0; i < 2; i++) {
      result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    
    return result;
  }

  // Get a specific quote by ID
  getQuoteById(id: number): Observable<Quote> {
    // Get all quotes from localStorage
    const quotes = this.getStoredQuotes();
    
    // Find the quote with the matching ID
    const quote = quotes.find(q => q.id === Number(id));
    
    if (quote) {
      return of(quote);
    }
    
    // If not found, return an error
    return throwError(() => new Error('Quote not found'));
  }

  // Update quote status
  updateQuoteStatus(id: number, status: 'Pending' | 'Approved' | 'Rejected'): Observable<Quote> {
    // Get all quotes from localStorage
    const quotes = this.getStoredQuotes();
    
    // Find the quote with the matching ID
    const quoteIndex = quotes.findIndex(q => q.id === Number(id));
    
    if (quoteIndex >= 0) {
      // Update the status
      quotes[quoteIndex].status = status;
      
      // Save back to localStorage
      this.saveQuotesToStorage(quotes);
      
      // Return the updated quote
      return of(quotes[quoteIndex]);
    }
    
    // If not found, return an error
    return throwError(() => new Error('Quote not found'));
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