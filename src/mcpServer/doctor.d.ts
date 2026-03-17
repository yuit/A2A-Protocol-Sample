export interface DoctorAddress {
  street: string;
  city: string;
  state: string;
  zip_code: string;
}

export interface DoctorEducation {
  medical_school: string;
  residency: string;
  fellowship: string;
}

export interface Doctor {
  id: string;
  name: string;
  specialty: string;
  address: DoctorAddress;
  phone: string;
  email: string;
  years_experience: number;
  board_certified: boolean;
  hospital_affiliations: string[];
  education: DoctorEducation;
  languages: string[];
  accepts_new_patients: boolean;
  insurance_accepted: string[];
}
