// Type descriptions
export type Course = {
    courseTitle: string;
    courseDesc: string;
    courseID: string;

    subjectID: string;
    subjectName: string;
    
    creditHrs: number;
    url: string;

    genEds: string;
    pot: string;
    location: string;
}

export type GenEd = "1QR1" | "1QR2" | "1SS" | "1BSC" | "1LS" | "1PS" | "1HP" | "1LA" | "1WCC" | "1NW" | "1US" | "1CLL";
export type PartOfTerm = "A" | "B" | "1";