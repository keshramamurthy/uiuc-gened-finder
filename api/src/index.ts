import express from "express";
import { AsyncDatabase } from "promised-sqlite3";
import { Course } from "./types/Course";
import path from "path";

// Constants
const DATABASE_PATH = "../sp24-courses.db"; // Change this to the database you saved to while scraping
const GENED_CATEGORIES = new Map();
    GENED_CATEGORIES.set("1QR1", "Quant Reasoning 1");
    GENED_CATEGORIES.set("1QR2", "Quant Reasoning 2")
    GENED_CATEGORIES.set("1SS", "Soc Sciences")
    GENED_CATEGORIES.set("1BSC", "Beh Sciences")
    GENED_CATEGORIES.set("1LS", "NatSci - Life Sciences")
    GENED_CATEGORIES.set("1PS", "NatSci - Physical Sciences")
    GENED_CATEGORIES.set("1HP", "Hum - Hist & Phil")
    GENED_CATEGORIES.set("1LA", "Hum - Lit & Arts")
    GENED_CATEGORIES.set("1WCC", "Cultural - Western")
    GENED_CATEGORIES.set("1NW", "Cultural - Non-Western")
    GENED_CATEGORIES.set("1US", "Cultural - US Minority")
    GENED_CATEGORIES.set("1CLL", "Adv Comp")

const app = express();
app.use(express.static(path.join(__dirname, "..", "public")));
app.use(express.json());

app.get("/", (req, res) => {
    res.redirect("geneds.html");
});

// This endpoint returns some general data on the semester which is viewed at the index.html page
app.get("/api/generalData", async (req, res) => {
    const db = await AsyncDatabase.open(DATABASE_PATH);

    const numRaw = (await db.get("SELECT COUNT(*) AS count FROM courses;")) as any;
    const num = numRaw.count;

    const largestRaw = await db.all("SELECT COUNT(*) AS count, subjectID FROM courses GROUP BY subjectID") as any[];
    const largestObj = largestRaw.sort((a, b) => b.count - a.count)[0]
    const largest = largestObj.subjectID;
    const largestCount = largestObj.count;

    const randomRaw = await db.get("SELECT * FROM courses ORDER BY RANDOM() LIMIT 1") as Course;
    const random = randomRaw.subjectID + " " + randomRaw.courseID;
    const randomUrl = `https://courses.illinois.edu/schedule/2024/spring/${randomRaw.subjectID}/${randomRaw.courseID}`;
    const randomDesc = randomRaw.courseTitle;

    const genEdRaw = await db.get("SELECT COUNT(*) AS count FROM courses WHERE genEds != \"\"") as any;
    const genEd = genEdRaw.count;
    
    const obj = {
        num,
        largest,
        largestCount,
        random,
        randomUrl,
        randomDesc,
        genEd
    };

    res.json(obj);
});

// This endpoint returns all general education courses fulfilling the categories, part of term
// and location specified
app.get("/api/genedData", async (req, res) => {
    const geneds = req.query.geneds as string;
    const pot = req.query.pot as string;
    const onlineStr = (req.query.online as string)

    // First input validation
    if (!geneds || !pot || !onlineStr || (geneds.length == 0 && pot.length == 0) || (onlineStr.toLowerCase() !== "true" && onlineStr.toLowerCase() !== "false")) {
        return res.status(400).json({
            message: "Invalid request"
        });
    }

    const queriedGeneds = geneds.split(",");
    const queriedPots = pot.split(",");
    const online = onlineStr === "true";

    // Input validation 2
    if (queriedGeneds.some(r => !GENED_CATEGORIES.has(r)) || queriedPots.some(r => !["A", "B", "1"].includes(r))) {
        return res.status(400).json({
            message: "Invalid request"
        });
    }

    const db = await AsyncDatabase.open(DATABASE_PATH);
    let genEdList = await db.all("SELECT * FROM courses WHERE genEds != \"\" AND pot is NOT NULL AND location is NOT NULL;") as Course[];

    // Internal separator is ~ for location and parts of term
    if (online) {
        genEdList = genEdList.filter(r => {
            return r.location.split("~").includes("ONLINE")
        });
    }
    genEdList = genEdList.filter(r => {
        return queriedPots.some(pot => r.pot.split("~").includes(pot));
    });

    // Internal separator is , for general education categories
    genEdList = genEdList.filter(r => {
        return queriedGeneds.every(gened => r.genEds.split(",").includes(gened));
    });
    
    if (genEdList.length == 0) {
        return res.status(400).json({
            message: "No courses found"
        });
    }

    return res.json(genEdList);
})

// Change this port if needed
app.listen(8080, () => {
    console.log("Server running on port 8080");
})