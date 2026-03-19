export interface SubtopicInfo {
  id: string;
  name: string;
}

export interface TopicInfo {
  id: string;
  name: string;
  subtopics: SubtopicInfo[];
  difficulties: string[];
  template_count: number;
}

export interface GenerateRequest {
  topics: string[];
  difficulty: string;
  count: number;
  seed?: number;
}

export interface QuestionResponse {
  id: number;
  question_latex: string;
  answer_latex: string;
  topic: string;
  difficulty: string;
  subtopic: string;
  solution_steps: string[];
}

export interface TestResponse {
  test_id: string;
  questions: QuestionResponse[];
  created_at: string;
  config: GenerateRequest;
}

// === Auth Types ===

export interface UserProfile {
  id: string;
  email: string;
  email_verified: boolean;
  created_at: string | null;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
  user: UserProfile;
}

export interface RefreshResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
}

export interface AuthMessage {
  message: string;
}

// === Billing Types ===

export interface SubscriptionStatus {
  status: string; // 'active' | 'past_due' | 'expired' | 'inactive'
  is_active: boolean;
  current_period_end: string | null;
  plan: string | null;
}

export interface CheckoutSessionResponse {
  url: string;
}

export interface CancelSubscriptionResponse {
  message: string;
  cancel_at_period_end: boolean;
}

// === Stats Types ===

export interface UserStats {
  tests_generated: number;
  questions_generated: number;
  topic_counts: Record<string, number>;
  streak_current: number;
  streak_best: number;
  is_active_today: boolean;
  last_test_duration: number | null;
}

// === Saved Tests Types ===

export interface SavedTestSummary {
  id: string;
  test_name: string;
  config: GenerateRequest;
  seed: number;
  question_count: number;
  created_at: string;
}

export interface SavedTest {
  id: string;
  test_name: string;
  config: GenerateRequest;
  seed: number;
  questions: QuestionResponse[];
  created_at: string;
}
