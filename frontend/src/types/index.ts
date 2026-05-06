export interface UserOffering {
  id: string;
  title: string;
  description: string | null;
  type: string;
  status: string;
  cohort_title: string | null;
  start_date: string | null;
  end_date: string | null;
  purchased_at: string;
}

export interface ContentItem {
  id: string;
  title: string;
  description: string | null;
  content_type: "video" | "download" | "link";
  content_url: string;
  position: number;
  is_preview: boolean;
}

export interface SessionSummary {
  id: string;
  title: string;
  scheduled_at: string | null;
  duration_minutes: number | null;
}

export interface SessionDetail {
  id: string;
  title: string;
  description: string | null;
  scheduled_at: string | null;
  duration_minutes: number | null;
  contents: ContentItem[];
}

export interface OfferingDetail {
  id: string;
  title: string;
  description: string | null;
  cohort_title: string | null;
  start_date: string | null;
  end_date: string | null;
  sessions: SessionSummary[];
  general_resources: ContentItem[];
}
