export type CollectionData = {
  attributes: Attributes;
  type: string;
}

interface Attributes {
  imagePath: string;
  score: number;
}