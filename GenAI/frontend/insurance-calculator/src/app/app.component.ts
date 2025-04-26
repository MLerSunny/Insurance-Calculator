import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router, NavigationEnd, Event } from '@angular/router';
import { Subject } from 'rxjs';
import { filter, takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit, OnDestroy {
  title = 'Insurance Calculator';
  showCalculator = false;
  currentYear = new Date().getFullYear();
  private readonly destroy$ = new Subject<void>();
  
  constructor(private router: Router) {}
  
  ngOnInit(): void {
    // Show calculator tab only after an account is selected or created
    this.router.events
      .pipe(
        filter((event: Event): event is NavigationEnd => event instanceof NavigationEnd),
        takeUntil(this.destroy$)
      )
      .subscribe((event: NavigationEnd) => {
        // Show calculator tab if navigating to calculator route or has query params
        if (event.url.includes('/calculator') || event.url.includes('?')) {
          this.showCalculator = true;
        }
      });
  }
  
  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
