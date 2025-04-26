// Basic application data types
export interface MedicalHistory {
  conditions: string[];
  medications: string[];
  surgeries: string[];
  allergies: string[];
}

export interface RiskFactors {
  smoking: boolean;
  alcohol_consumption: boolean;
  dangerous_activities: string[];
  occupation_risk: string;
}

export interface InsuranceApplication {
  id?: number;
  applicant_name: string;
  applicant_age: number;
  email: string;
  phone: string;
  medical_history: MedicalHistory;
  risk_factors: RiskFactors;
  coverage_amount: number;
  premium_amount?: number;
  is_approved?: boolean;
  ai_recommendation?: string;
  created_at?: Date;
  updated_at?: Date;
}

// Premium calculation
export interface PremiumCalculationRequest {
  applicant_age: number;
  coverage_amount: number;
  medical_history: MedicalHistory;
  risk_factors: RiskFactors;
}

export interface PremiumCalculationResponse {
  premium_amount: number;
  risk_assessment: string;
  ai_recommendation: string;
}

export interface RiskFactorsObject {
  ageFactor?: number;
  incomeFactor?: number;
  lifestyleFactor?: number;
  occupationFactor?: number;
  mentalHealthFactor?: number;
  medicalFactor?: number;
  familyFactor?: number;
  travelFactor?: number;
  [key: string]: any;
}

// Additional interfaces that were missing
export interface InsuranceRequest {
  name?: string;
  age?: number;
  email?: string;
  phone?: string;
  medicalHistory?: MedicalHistory;
  riskFactors?: RiskFactors;
  coverageAmount?: number;
  annualIncome?: number;
  insuranceScore?: number;
  lifestyle?: string;
  occupation?: string;
  mentalHealth?: string;
  medications?: string[];
  family?: string;
  travel?: string;
  accountId?: string;
  [key: string]: any;
}

export interface PremiumResult {
  premium: number;
  riskAssessment: string;
  recommendation: string;
  riskLevel?: string;
  applicationId?: string;
  accountInfo?: AccountData;
  factors?: RiskFactorsObject;
  recommendations?: any[];
}

export interface AccountData {
  id?: string;
  username?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  firstName?: string;
  lastName?: string;
  address?: string;
  applicationId?: string;
  isNewAccount?: boolean;
  createdAt?: Date;
}

export interface SavedApplicationData {
  id?: number;
  applicantName?: string;
  applicantAge?: number;
  email?: string;
  phone?: string;
  medicalHistory?: MedicalHistory;
  riskFactors?: RiskFactors;
  coverageAmount?: number;
  userId?: number;
  accountId?: string;
  applicationData?: any;
  calculationResult?: any;
  status?: string;
  createdAt?: Date;
  [key: string]: any;
} 