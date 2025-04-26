import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { Quote } from '../../services/quote.service';
import { InsuranceApplication } from '../application-detail.component';

/**
 * Data interface for the quote overview dialog
 */
interface QuoteOverviewData {
  quote: Quote;
  application: InsuranceApplication;
}

/**
 * Risk factor interface
 */
interface RiskFactor {
  factor: string;
  impact: RiskImpact;
  description: string;
}

/**
 * Underwriting concern interface
 */
interface UnderwritingConcern {
  concern: string;
  level: RiskLevel;
  description: string;
}

/**
 * Risk impact levels
 */
type RiskImpact = 'High' | 'Medium' | 'Low' | 'Low to Medium' | 'Medium to High';

/**
 * Risk concern levels
 */
type RiskLevel = 'High' | 'Medium' | 'Low' | 'Low to Medium' | 'Medium to High';

/**
 * Component that displays detailed overview of a quote
 * including risk factors and underwriting considerations
 */
@Component({
  selector: 'app-quote-overview-dialog',
  templateUrl: './quote-overview-dialog.component.html',
  styleUrls: ['./quote-overview-dialog.component.css']
})
export class QuoteOverviewDialogComponent {
  // Risk analysis data
  riskFactors: RiskFactor[] = [];
  underwritingConcerns: UnderwritingConcern[] = [];
  
  // Base premium amount used for calculations
  private readonly BASE_PREMIUM = 500;
  
  constructor(
    public dialogRef: MatDialogRef<QuoteOverviewDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: QuoteOverviewData
  ) {
    this.analyzeQuote();
  }

  /**
   * Close the dialog
   */
  close(): void {
    this.dialogRef.close();
  }
  
  /**
   * Analyze the quote and extract risk factors and concerns
   */
  private analyzeQuote(): void {
    // Extract relevant information from the quote
    const quoteDetails = this.data.quote.quoteDetails;
    
    if (!quoteDetails) {
      return;
    }
    
    // Analyze risk factors and underwriting concerns
    this.analyzeRiskFactors(quoteDetails);
    this.analyzeUnderwritingConcerns(quoteDetails);
  }
  
  /**
   * Analyze the quote details to identify risk factors that affect premium
   */
  private analyzeRiskFactors(quoteDetails: any): void {
    // Health assessment
    this.checkHealthStatus(quoteDetails);
    
    // Smoking status
    this.checkSmokingStatus(quoteDetails);
    
    // Pre-existing conditions
    this.checkPreExistingConditions(quoteDetails);
    
    // Family medical history
    this.checkFamilyMedicalHistory(quoteDetails);
    
    // Hospitalization history
    this.checkHospitalizationHistory(quoteDetails);
    
    // Travel history
    this.checkTravelHistory(quoteDetails);
  }

  /**
   * Check health status and add to risk factors if needed
   */
  private checkHealthStatus(quoteDetails: any): void {
    if (quoteDetails.generalHealth === 'Poor' || quoteDetails.generalHealth === 'Fair') {
      this.riskFactors.push({
        factor: 'General Health',
        impact: quoteDetails.generalHealth === 'Poor' ? 'High' : 'Medium',
        description: `Applicant's self-reported general health is ${quoteDetails.generalHealth.toLowerCase()}, which increases premium rates.`
      });
    }
  }

  /**
   * Check smoking status and add to risk factors if applicable
   */
  private checkSmokingStatus(quoteDetails: any): void {
    if (quoteDetails.smokingStatus === 'Yes') {
      this.riskFactors.push({
        factor: 'Smoking',
        impact: 'High',
        description: 'Applicant is a smoker, which significantly increases health risks and premium rates.'
      });
    }
  }

  /**
   * Check pre-existing conditions and add to risk factors if needed
   */
  private checkPreExistingConditions(quoteDetails: any): void {
    if (quoteDetails.preExistingConditions && quoteDetails.preExistingConditions !== 'None') {
      this.riskFactors.push({
        factor: 'Pre-existing Condition',
        impact: 'High',
        description: `Applicant has ${quoteDetails.preExistingConditions}, which may require additional medical assessment.`
      });
    }
  }

  /**
   * Check family medical history and add to risk factors if needed
   */
  private checkFamilyMedicalHistory(quoteDetails: any): void {
    const familyRisks: string[] = [];
    if (quoteDetails.familyHeartDisease === 'Yes') familyRisks.push('heart disease');
    if (quoteDetails.familyCancer === 'Yes') familyRisks.push('cancer');
    if (quoteDetails.familyDiabetes === 'Yes') familyRisks.push('diabetes');
    
    if (familyRisks.length > 0) {
      this.riskFactors.push({
        factor: 'Family Medical History',
        impact: familyRisks.length > 1 ? 'High' : 'Medium',
        description: `Family history of ${familyRisks.join(', ')}, which may indicate increased genetic risk.`
      });
    }
  }

  /**
   * Check hospitalization history and add to risk factors if needed
   */
  private checkHospitalizationHistory(quoteDetails: any): void {
    if (quoteDetails.hospitalizedLast5Years === 'Yes') {
      this.riskFactors.push({
        factor: 'Recent Hospitalization',
        impact: 'Medium',
        description: 'Applicant has been hospitalized within the last 5 years, which may indicate ongoing health concerns.'
      });
    }
  }

  /**
   * Check travel history and add to risk factors if needed
   */
  private checkTravelHistory(quoteDetails: any): void {
    if (quoteDetails.travelOutsideCountry === 'Yes') {
      const regions: string[] = quoteDetails.travelRegions || [];
      const highRiskRegions = regions.filter((r: string) => this.isHighRiskRegion(r));
      
      if (highRiskRegions.length > 0) {
        this.riskFactors.push({
          factor: 'Travel History',
          impact: 'Low to Medium',
          description: `Travel to regions with higher health risks: ${highRiskRegions.join(', ')}.`
        });
      }
    }
  }
  
  /**
   * Check if a region is considered high risk for health
   */
  private isHighRiskRegion(region: string): boolean {
    const highRiskRegions = ['Africa', 'Asia', 'South America'];
    return highRiskRegions.includes(region);
  }
  
  /**
   * Analyze underwriting concerns from quote details
   */
  private analyzeUnderwritingConcerns(quoteDetails: any): void {
    // Occupation risk
    this.checkOccupationRisk(quoteDetails);
    
    // Mental health concerns
    this.checkMentalHealth(quoteDetails);
    
    // High stress levels
    this.checkStressLevels(quoteDetails);
    
    // Recent surgeries
    this.checkSurgeryHistory(quoteDetails);
    
    // Alcohol consumption
    this.checkAlcoholConsumption(quoteDetails);
    
    // Drug use
    this.checkDrugUse(quoteDetails);
  }

  /**
   * Check occupation risk and add to concerns if needed
   */
  private checkOccupationRisk(quoteDetails: any): void {
    if (quoteDetails.occupationRiskLevel === 'High Risk') {
      this.underwritingConcerns.push({
        concern: 'High-Risk Occupation',
        level: 'High',
        description: `The applicant works in a high-risk occupation: ${quoteDetails.occupation}. Consider specific exclusions or premium loading.`
      });
    }
  }

  /**
   * Check mental health and add to concerns if needed
   */
  private checkMentalHealth(quoteDetails: any): void {
    if (quoteDetails.mentalHealthDiagnosis === 'Yes') {
      this.underwritingConcerns.push({
        concern: 'Mental Health',
        level: 'Medium',
        description: 'The applicant has reported mental health diagnoses. Consider requesting additional medical reports.'
      });
    }
  }

  /**
   * Check stress levels and add to concerns if needed
   */
  private checkStressLevels(quoteDetails: any): void {
    if (quoteDetails.stressLevel && parseInt(quoteDetails.stressLevel) >= 8) {
      this.underwritingConcerns.push({
        concern: 'High Stress Level',
        level: 'Medium',
        description: 'The applicant reports very high stress levels which could lead to stress-related health complications.'
      });
    }
  }

  /**
   * Check surgery history and add to concerns if needed
   */
  private checkSurgeryHistory(quoteDetails: any): void {
    if (quoteDetails.surgeryLast10Years === 'Yes') {
      this.underwritingConcerns.push({
        concern: 'Recent Surgery',
        level: 'Medium',
        description: 'The applicant has had surgery in the last 10 years. Consider requesting surgical reports and recovery details.'
      });
    }
  }

  /**
   * Check alcohol consumption and add to concerns if needed
   */
  private checkAlcoholConsumption(quoteDetails: any): void {
    if (quoteDetails.alcoholConsumption === 'Yes' && quoteDetails.alcoholFrequency === 'Frequently') {
      this.underwritingConcerns.push({
        concern: 'Alcohol Consumption',
        level: 'Medium to High',
        description: 'The applicant reports frequent alcohol consumption, which may indicate increased health risks.'
      });
    }
  }

  /**
   * Check drug use and add to concerns if needed
   */
  private checkDrugUse(quoteDetails: any): void {
    if (quoteDetails.drugUse === 'Yes') {
      this.underwritingConcerns.push({
        concern: 'Drug Use',
        level: 'High',
        description: 'The applicant has reported drug use. Consider specific exclusions or premium loading.'
      });
    }
  }

  /**
   * Calculate the width percentage for the chart bars
   */
  calculateImpactWidth(impact: string): number {
    switch (impact.toLowerCase()) {
      case 'high':
        return 30;
      case 'medium':
        return 20;
      case 'low':
        return 10;
      case 'medium to high':
      case 'medium-high':
        return 25;
      case 'low to medium':
      case 'low-medium':
        return 15;
      default:
        return 10;
    }
  }
  
  /**
   * Calculate the value amount for each risk factor
   */
  calculateImpactValue(impact: string, totalPremium: number): number {
    const additionalPremium = totalPremium - this.BASE_PREMIUM;
    
    if (additionalPremium <= 0) {
      return 0;
    }
    
    // Calculate percentage based on impact
    const percentage = this.getImpactPercentage(impact);
    
    // Calculate value
    return additionalPremium * percentage;
  }

  /**
   * Get the percentage impact based on the risk level
   */
  private getImpactPercentage(impact: string): number {
    const percentages: {[key: string]: number} = {
      'high': 0.4,
      'medium': 0.2, 
      'low': 0.1,
      'medium to high': 0.3,
      'medium-high': 0.3,
      'low to medium': 0.15,
      'low-medium': 0.15
    };
    
    return percentages[impact.toLowerCase()] || 0.1;
  }
} 