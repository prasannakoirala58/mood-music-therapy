export type Emotion = 'Happy' | 'Sad' | 'Angry' | 'Fear' | 'Disgust' | 'Surprise'

export interface Song {
  track_name: string
  artists: string
  emotion: Emotion
  valence: number
  energy: number
  track_id: string
  spotify_url: string
}

export interface RecommendResult {
  emotion: Emotion
  songs: Song[]
}

export interface EmotionMeta {
  color: string
  glow: string
  bg: string
  label: string
}

export interface StepMeta {
  key: string
  label: string
}
