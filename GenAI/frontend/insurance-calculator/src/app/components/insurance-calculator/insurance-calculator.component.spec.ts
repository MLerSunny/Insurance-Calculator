import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InsuranceCalculatorComponent } from './insurance-calculator.component';

describe('InsuranceCalculatorComponent', () => {
  let component: InsuranceCalculatorComponent;
  let fixture: ComponentFixture<InsuranceCalculatorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InsuranceCalculatorComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InsuranceCalculatorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
