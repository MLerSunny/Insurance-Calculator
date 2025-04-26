import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  { path: '', redirectTo: '/calculator', pathMatch: 'full' },
  { 
    path: 'calculator', 
    loadChildren: () => import('./insurance-calculator/insurance-calculator.module').then(m => m.InsuranceCalculatorModule) 
  },
  { 
    path: 'search', 
    loadChildren: () => import('./insurance-search/insurance-search.module').then(m => m.InsuranceSearchModule) 
  },
  { 
    path: 'create-account', 
    loadChildren: () => import('./create-account/create-account.module').then(m => m.CreateAccountModule) 
  },
  { 
    path: 'application/:id', 
    loadChildren: () => import('./application-detail/application-detail.module').then(m => m.ApplicationDetailModule) 
  },
  { 
    path: 'quote', 
    loadChildren: () => import('./quote/quote.module').then(m => m.QuoteModule) 
  },
  { path: '**', redirectTo: '/calculator' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { } 