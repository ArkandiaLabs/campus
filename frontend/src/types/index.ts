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
  total_contents: number;
  completed_contents: number;
}

export interface ContentItem {
  id: string;
  title: string;
  description: string | null;
  content_type: "video" | "download" | "link";
  content_url: string;
  position: number;
  is_preview: boolean;
  completed: boolean;
}

export interface OfferingDetail {
  id: string;
  title: string;
  description: string | null;
  cohort_title: string | null;
  start_date: string | null;
  end_date: string | null;
  contents: ContentItem[];
  total_contents: number;
  completed_contents: number;
}

export interface ProgressRecord {
  id: string;
  user_id: string;
  content_id: string;
  completed_at: string;
}
